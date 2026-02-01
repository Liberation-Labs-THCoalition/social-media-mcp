"""Google Sheets integration for content queue and analytics.

Uses gspread with service account for direct API access.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

import config
from models import QueueItem, AnalyticsRecord, PostStatus


_gc: Optional[gspread.Client] = None


def _get_client() -> gspread.Client:
    global _gc
    if _gc is None:
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "")
        if creds_path:
            creds = Credentials.from_service_account_file(
                creds_path,
                scopes=[
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            _gc = gspread.authorize(creds)
        else:
            _gc = gspread.service_account()
    return _gc


def _get_queue_sheet() -> gspread.Worksheet:
    gc = _get_client()
    spreadsheet = gc.open_by_key(config.CONTENT_QUEUE_SHEET_ID)
    try:
        return spreadsheet.worksheet(config.QUEUE_TAB)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=config.QUEUE_TAB, rows=1000, cols=20)
        ws.append_row(QueueItem.header_row())
        return ws


def _get_analytics_sheet() -> gspread.Worksheet:
    gc = _get_client()
    spreadsheet = gc.open_by_key(config.CONTENT_QUEUE_SHEET_ID)
    try:
        return spreadsheet.worksheet(config.ANALYTICS_TAB)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=config.ANALYTICS_TAB, rows=1000, cols=15)
        ws.append_row(AnalyticsRecord.header_row())
        return ws


def get_queue_items(status_filter: str = "", limit: int = 50) -> list[dict]:
    """Read queue items from the sheet."""
    ws = _get_queue_sheet()
    rows = ws.get_all_values()
    if not rows:
        return []

    header = rows[0]
    items = []
    for i, row in enumerate(rows[1:], start=2):
        if status_filter and len(row) > 9 and row[9] != status_filter:
            continue
        item = dict(zip(header, row))
        item["_row"] = i
        items.append(item)
        if len(items) >= limit:
            break
    return items


def get_queue_item(row: int) -> Optional[dict]:
    """Read a single queue item by row number."""
    ws = _get_queue_sheet()
    header = ws.row_values(1)
    values = ws.row_values(row)
    if not values:
        return None
    return dict(zip(header, values))


def append_queue_item(item: QueueItem) -> int:
    """Add a new item to the queue. Returns the row number."""
    ws = _get_queue_sheet()
    rows = ws.get_all_values()
    if not rows:
        ws.append_row(QueueItem.header_row())
    ws.append_row(item.to_row())
    return len(ws.get_all_values())


def update_queue_row(row: int, updates: dict):
    """Update specific cells in a queue row."""
    ws = _get_queue_sheet()
    header = ws.row_values(1)
    for col_name, value in updates.items():
        if col_name in header:
            col_idx = header.index(col_name) + 1
            ws.update_cell(row, col_idx, value)


def get_analytics(platform: str = "", days: int = 30, limit: int = 100) -> list[dict]:
    """Read analytics records."""
    ws = _get_analytics_sheet()
    rows = ws.get_all_values()
    if not rows:
        return []

    header = rows[0]
    items = []
    for row in rows[1:]:
        record = dict(zip(header, row))
        if platform and record.get("platform") != platform:
            continue
        items.append(record)
        if len(items) >= limit:
            break
    return items


def get_analytics_for_post(post_id: str) -> Optional[dict]:
    """Find analytics record for a specific post ID."""
    ws = _get_analytics_sheet()
    rows = ws.get_all_values()
    if not rows:
        return None

    header = rows[0]
    for row in rows[1:]:
        record = dict(zip(header, row))
        if record.get("post_id") == post_id:
            return record
    return None


def get_recent_post_ids(limit: int = 20) -> list[tuple[str, str]]:
    """Get recent (post_id, platform) pairs from the queue sheet for analytics refresh."""
    ws = _get_queue_sheet()
    rows = ws.get_all_values()
    if not rows:
        return []

    header = rows[0]
    results = []
    for row in reversed(rows[1:]):
        item = dict(zip(header, row))
        if item.get("status") != PostStatus.POSTED.value:
            continue
        post_ids_str = item.get("post_ids", "")
        if not post_ids_str:
            continue
        try:
            post_ids = json.loads(post_ids_str)
            for plat, pid in post_ids.items():
                if pid:
                    results.append((pid, plat))
        except json.JSONDecodeError:
            continue
        if len(results) >= limit:
            break
    return results


def update_analytics(post_id: str, metrics: dict):
    """Update or append analytics for a post."""
    ws = _get_analytics_sheet()
    rows = ws.get_all_values()
    if not rows:
        ws.append_row(AnalyticsRecord.header_row())
        rows = ws.get_all_values()

    header = rows[0]
    # Find existing row
    for i, row in enumerate(rows[1:], start=2):
        record = dict(zip(header, row))
        if record.get("post_id") == post_id:
            # Update in place
            for key, val in metrics.items():
                if key in header:
                    col_idx = header.index(key) + 1
                    ws.update_cell(i, col_idx, str(val))
            # Update collected_at
            if "collected_at" in header:
                col_idx = header.index("collected_at") + 1
                ws.update_cell(i, col_idx, datetime.now().isoformat())
            return

    # Not found - append new row
    record = AnalyticsRecord(
        post_id=post_id,
        platform=metrics.get("platform", ""),
        content_id="",
        posted_at="",
        likes=metrics.get("likes", 0),
        reposts=metrics.get("reposts", 0),
        replies=metrics.get("replies", 0),
        impressions=metrics.get("impressions", 0),
        collected_at=datetime.now().isoformat(),
    )
    ws.append_row(record.to_row())


def append_analytics(records: list[AnalyticsRecord]):
    """Write analytics records to the sheet."""
    ws = _get_analytics_sheet()
    rows = ws.get_all_values()
    if not rows:
        ws.append_row(AnalyticsRecord.header_row())
    for record in records:
        ws.append_row(record.to_row())

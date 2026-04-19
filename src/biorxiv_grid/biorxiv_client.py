from __future__ import annotations

import json
from datetime import date, timedelta
from urllib import request

from .models import Preprint


class BioRxivClient:
    BASE_URL = "https://api.biorxiv.org/details"

    def fetch_latest(
        self,
        days_back: int = 1,
        max_records: int = 200,
        server: str = "biorxiv",
        end_lag_days: int = 1,
    ) -> list[Preprint]:
        if days_back < 0:
            raise ValueError("days_back must be >= 0")
        if end_lag_days < 0:
            raise ValueError("end_lag_days must be >= 0")

        # bioRxiv 当日数据有时尚未整理完整，因此默认回退 1 天作为结束日期。
        end = date.today() - timedelta(days=end_lag_days)
        start = end - timedelta(days=days_back)
        start_s = start.isoformat()
        end_s = end.isoformat()

        results: list[Preprint] = []
        cursor = 0

        while len(results) < max_records:
            url = f"{self.BASE_URL}/{server}/{start_s}/{end_s}/{cursor}"
            req = request.Request(url=url, method="GET")
            with request.urlopen(req, timeout=40) as resp:
                payload = json.loads(resp.read().decode("utf-8"))

            collection = payload.get("collection", [])
            if not collection:
                break

            for row in collection:
                results.append(Preprint.from_api_record(row, server=server))
                if len(results) >= max_records:
                    break

            messages = payload.get("messages", [])
            if not messages:
                break

            msg = messages[0]
            new_cursor = int(msg.get("cursor", cursor)) + len(collection)
            if new_cursor <= cursor:
                break
            cursor = new_cursor

        results.sort(key=lambda x: x.date, reverse=True)
        return results

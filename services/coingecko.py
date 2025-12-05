# services/coingecko.py
import asyncio
from typing import Any, Dict, List, Optional

import httpx

class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"
    # Demo key; replace with your own key if you have one
    HEADERS = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-Q39TEyPMhULwwxAzL45pQXkS"
    }

    # tune these as needed
    TIMEOUT = 10.0  # seconds
    MAX_CONNECTIONS = 10

    def __init__(self) -> None:
        limits = httpx.Limits(max_connections=self.MAX_CONNECTIONS, max_keepalive_connections=5)
        self._client = httpx.AsyncClient(headers=self.HEADERS, timeout=self.TIMEOUT, limits=limits)

    async def close(self) -> None:
        await self._client.aclose()

    # -----------------------------
    # List all coins (id, symbol, name)
    # -----------------------------
    async def list_coins(self) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/coins/list"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    # -----------------------------
    # List categories
    # -----------------------------
    async def list_categories(self) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/coins/categories/list"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    # -----------------------------
    # Fetch markets for one currency
    # -----------------------------
    async def _markets_for_currency(
        self,
        vs_currency: str,
        coin_id: Optional[str] = None,
        category: Optional[str] = None,
        page_num: int = 1,
        per_page: int = 10,
    ) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/coins/markets"
        params: Dict[str, Any] = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "sparkline": False,
            "page": page_num,
            "per_page": per_page
        }
        if coin_id:
            params["ids"] = coin_id
        if category:
            params["category"] = category

        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    # -----------------------------
    # Get market data in multiple currencies concurrently
    # -----------------------------
    async def get_market_data(
        self,
        coin_id: Optional[str] = None,
        category: Optional[str] = None,
        page_num: int = 1,
        per_page: int = 10,
    ) -> Dict[str, List[Dict[str, Any]]]:
        # CoinGecko supports only one vs_currency per call. We'll fetch both concurrently.
        tasks = [
            self._markets_for_currency("inr", coin_id, category, page_num, per_page),
            self._markets_for_currency("cad", coin_id, category, page_num, per_page),
        ]
        inr_list, cad_list = await asyncio.gather(*tasks)
        return {"inr": inr_list, "cad": cad_list}

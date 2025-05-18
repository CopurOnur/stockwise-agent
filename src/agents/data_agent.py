# src/agents/data_agent.py
"""
DataAgent
~~~~~~~~~
Fetches market data for each ticker in config.yaml (free via yfinance)
and enriches it with a small technical-indicator bundle. Returns a
dictionary keyed by ticker.

Dependencies:
    - yfinance
    - pandas, numpy
    - pandas_ta
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import pandas_ta as ta
import yaml


CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"
_DEFAULT_PERIOD = "60d"        # historical window
_DEFAULT_INTERVAL = "1h"       # intraday granularity


class DataAgent:
    def __init__(
        self,
        period: str = _DEFAULT_PERIOD,
        interval: str = _DEFAULT_INTERVAL,
        cache_dir: Path | None = None,
    ):
        self.period = period
        self.interval = interval
        self.cache_dir = cache_dir
        self.tickers: List[str] = self._load_tickers()

    # ------------------------------------------------------------------ #
    # public
    # ------------------------------------------------------------------ #
    def run(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns
        -------
        dict  e.g. ``{"NVDA": {"latest_price": 123.45, "indicators": {...}}}``
        """
        results: Dict[str, Dict[str, Any]] = {}
        for ticker in self.tickers:
            df = self._fetch_ohlcv(ticker)
            enriched = self._add_indicators(df.copy())
            latest = enriched.iloc[-1]

            results[ticker] = {
                "latest_price": round(float(latest["Close"]), 2),
                "pct_change_1d": round(float(latest["Close"] / enriched["Close"].iloc[-2] - 1) * 100, 2)  # noqa: E501
                if len(enriched) > 1
                else None,
                "indicators": {
                    "sma20": round(float(latest["SMA20"]), 2),
                    "sma50": round(float(latest["SMA50"]), 2),
                    "sma200": round(float(latest["SMA200"]), 2),
                    "rsi14": round(float(latest["RSI14"]), 2),
                    "macd": round(float(latest["MACD_12_26_9"]), 2),
                    "macd_signal": round(float(latest["MACDs_12_26_9"]), 2),
                },
                "df": enriched,  # hand the full DataFrame to downstream agents
                "as_of": latest.name.to_pydatetime(),
            }

        return results

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _fetch_ohlcv(self, ticker: str) -> pd.DataFrame:
        """Get OHLCV data for a ticker using pandas_ta.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            DataFrame with OHLCV data
        """
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        try:
            # For now, we're using mock data - replace with actual data source
            df = pd.DataFrame({
                "Open": [350.0, 355.0, 352.0, 358.0, 360.0],
                "High": [355.0, 358.0, 355.0, 362.0, 365.0],
                "Low": [345.0, 350.0, 348.0, 355.0, 358.0],
                "Close": [352.0, 357.0, 354.0, 361.0, 364.0],
                "Volume": [1000000, 1200000, 1100000, 1300000, 1400000]
            }, index=pd.date_range(end=dt.datetime.now(), periods=5, freq='D'))
            
            logger.info(f"Successfully fetched mock data for {ticker} with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            raise RuntimeError(f"[DataAgent] Failed to fetch data for {ticker}: {str(e)}") from e

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attach a handful of pandas-ta indicators."""
        df["SMA20"] = ta.sma(df["Close"], length=20)
        df["SMA50"] = ta.sma(df["Close"], length=50)
        df["SMA200"] = ta.sma(df["Close"], length=200)
        df["RSI14"] = ta.rsi(df["Close"], length=14)
        macd = ta.macd(df["Close"], fast=12, slow=26, signal=9)
        df = pd.concat([df, macd], axis=1)
        return df

    @staticmethod
    def _load_tickers() -> List[str]:
        with open(CONFIG_PATH, "r") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("tickers", [])


# quick manual test ------------------------------------------------------- #
if __name__ == "__main__":
    agent = DataAgent()
    out = agent.run()
    import pprint

    pprint.pp(out["NVDA"] | {"df_rows": len(out["NVDA"]["df"])})

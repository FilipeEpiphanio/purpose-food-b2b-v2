from __future__ import annotations

import pandas as pd

from .base import Strategy, Signal


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-12)
    return 100 - (100 / (1 + rs))


class MeanReversion(Strategy):
    def __init__(self, rsi_period: int = 14, low_thresh: int = 30, high_thresh: int = 70):
        super().__init__(name="MEAN_REVERSION", rsi_period=rsi_period, low=low_thresh, high=high_thresh)

    def generate_signals(self, df: pd.DataFrame):
        df = df.copy()
        df["rsi"] = rsi(df["close"], period=self.params["rsi_period"])
        df["sma"] = df["close"].rolling(window=20).mean()

        signals = []
        for ts, row in df.iterrows():
            price = float(row["close"])
            if pd.isna(row["rsi"]) or pd.isna(row["sma"]):
                continue
            if row["rsi"] < self.params["low"] and price >= row["sma"]:
                signals.append(Signal(timestamp=ts, action="buy", price=price))
            elif row["rsi"] > self.params["high"] and price <= row["sma"]:
                signals.append(Signal(timestamp=ts, action="sell", price=price))
        return signals
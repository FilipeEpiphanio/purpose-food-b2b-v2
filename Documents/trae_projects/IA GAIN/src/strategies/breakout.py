from __future__ import annotations

import pandas as pd

from .base import Strategy, Signal


class Breakout(Strategy):
    def __init__(self, window: int = 20):
        super().__init__(name="BREAKOUT", window=window)

    def generate_signals(self, df: pd.DataFrame):
        df = df.copy()
        w = int(self.params["window"])
        df["donchian_high"] = df["high"].rolling(window=w).max()
        df["donchian_low"] = df["low"].rolling(window=w).min()

        signals = []
        for ts, row in df.iterrows():
            if pd.isna(row["donchian_high"]) or pd.isna(row["donchian_low"]):
                continue
            price = float(row["close"])
            if price > row["donchian_high"]:
                signals.append(Signal(timestamp=ts, action="buy", price=price))
            elif price < row["donchian_low"]:
                signals.append(Signal(timestamp=ts, action="sell", price=price))
        return signals
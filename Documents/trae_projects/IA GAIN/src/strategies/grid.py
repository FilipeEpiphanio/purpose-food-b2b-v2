from __future__ import annotations

import math
import pandas as pd

from .base import Strategy, Signal


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    tr = (high.combine(close.shift(1), max) - low.combine(close.shift(1), min)).abs()
    return tr.ewm(alpha=1/period, adjust=False).mean()


class Grid(Strategy):
    def __init__(self, levels: int = 6, atr_mult: float = 0.5, base_period: int = 14):
        super().__init__(name="GRID", levels=levels, atr_mult=atr_mult, base_period=base_period)

    def generate_signals(self, df: pd.DataFrame):
        df = df.copy()
        df["atr"] = atr(df, period=self.params["base_period"]).fillna(method="bfill")
        mid = df["close"].ewm(span=self.params["base_period"], adjust=False).mean()
        step = df["atr"] * float(self.params["atr_mult"])  # grid spacing
        signals = []

        for ts, row in df.iterrows():
            if pd.isna(row["atr"]) or pd.isna(mid.loc[ts]) or pd.isna(row["close"]):
                continue
            price = float(row["close"])
            m = float(mid.loc[ts])
            s = float(step.loc[ts])
            if s <= 0:
                continue
            level_idx = math.floor((price - m) / s)
            # buy when price falls to even negative levels, sell on even positive levels
            if level_idx <= -1 and abs(level_idx) % 2 == 1:
                signals.append(Signal(timestamp=ts, action="buy", price=price))
            elif level_idx >= 1 and level_idx % 2 == 1:
                signals.append(Signal(timestamp=ts, action="sell", price=price))
        return signals
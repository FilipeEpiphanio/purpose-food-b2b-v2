from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class Signal:
    timestamp: pd.Timestamp
    action: str
    price: float


class Strategy:
    def __init__(self, name: str, **params: Any):
        self.name = name
        self.params: Dict[str, Any] = params

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        raise NotImplementedError

    def backtest(self, df: pd.DataFrame) -> Dict[str, float]:
        signals = self.generate_signals(df)
        if not signals:
            return {
                "trades": 0,
                "total_return": 0.0,
                "sharpe": 0.0,
                "win_rate": 0.0,
            }

        capital = 1.0
        position = 0.0
        entry_price: Optional[float] = None
        trade_returns: List[float] = []

        for s in signals:
            if s.action == "buy":
                if position == 0.0:
                    entry_price = float(s.price)
                    position = capital / max(entry_price, 1e-9)
            elif s.action == "sell":
                if position > 0.0 and entry_price:
                    exit_price = float(s.price)
                    pnl = position * (exit_price - entry_price)
                    capital += pnl
                    trade_returns.append(pnl / max(entry_price * position, 1e-9))
                    position = 0.0
                    entry_price = None

        if position > 0.0 and entry_price:
            last_price = float(df["close"].iloc[-1])
            pnl = position * (last_price - entry_price)
            capital += pnl
            trade_returns.append(pnl / max(entry_price * position, 1e-9))

        trades = len(trade_returns)
        total_return = capital - 1.0
        if trade_returns:
            avg = np.mean(trade_returns)
            std = np.std(trade_returns) if len(trade_returns) > 1 else 0.0
            sharpe = (avg / std) * np.sqrt(252) if std > 0 else 0.0
            win_rate = float(np.mean([r > 0 for r in trade_returns]))
        else:
            sharpe = 0.0
            win_rate = 0.0

        return {
            "trades": trades,
            "total_return": float(total_return),
            "sharpe": float(sharpe),
            "win_rate": float(win_rate),
        }

    def score(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = self.backtest(df)
        score = (
            0.5 * results.get("sharpe", 0.0)
            + 0.3 * results.get("win_rate", 0.0)
            + 0.2 * max(0.0, results.get("total_return", 0.0))
        )
        return {
            "strategy": self.name,
            "score": float(score),
            "trades": results.get("trades", 0),
            "total_return": results.get("total_return", 0.0),
            "sharpe": results.get("sharpe", 0.0),
            "win_rate": results.get("win_rate", 0.0),
        }


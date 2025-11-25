from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd

from .strategies.base import Strategy


class StrategyManager:
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    def evaluate_per_asset(self, assets_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for symbol, df in assets_data.items():
            per_strategy = []
            for strat in self.strategies:
                metrics = strat.score(df)
                per_strategy.append(metrics)
            # filtra estratégias com trades > 0
            per_strategy = [m for m in per_strategy if m.get("trades", 0) > 0]
            # normaliza score por ativo (min–max)
            if per_strategy:
                scores = [m.get("score", 0.0) for m in per_strategy]
                s_min, s_max = min(scores), max(scores)
                for m in per_strategy:
                    if s_max > s_min:
                        m["normalized_score"] = (m.get("score", 0.0) - s_min) / (s_max - s_min)
                    else:
                        m["normalized_score"] = 0.5
            # seleciona melhor pela normalized_score; fallback por retorno/sharpe
            best = None
            if per_strategy:
                best = sorted(
                    per_strategy,
                    key=lambda m: (
                        m.get("normalized_score", m.get("score", 0.0)),
                        m.get("total_return", 0.0),
                        m.get("sharpe", 0.0),
                    ),
                    reverse=True,
                )[0]
            results[symbol] = {
                "strategies": per_strategy,
                "best": best,
            }
        return results

    def save_report(self, evaluation: Dict[str, Dict[str, Any]], path: str | None = None) -> str:
        if path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"reports/strategy_selection_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(evaluation, f, indent=2)
        return path
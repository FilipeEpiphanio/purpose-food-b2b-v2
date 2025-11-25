"""
Combined Analyzer

Aggregates TechnicalAnalysis and FundamentalAnalysis into a single
decision output with configurable weights.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Sequence, Union

from .technical_analysis import TechnicalAnalysis
from .fundamental_analysis import FundamentalAnalysis


class CombinedAnalyzer:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.weights = cfg.get("weights", {"technical": 0.6, "fundamental": 0.4})
        self.tech = TechnicalAnalysis(config=cfg.get("technical", {}))
        self.fund = FundamentalAnalysis(config=cfg.get("fundamental", {}))

    def analyze(self, candles: Union[Sequence[Dict[str, Any]], "pd.DataFrame"], symbol: str) -> Dict[str, Any]:
        tech = self.tech.analyze(candles)
        fund = self.fund.analyze(symbol)

        tech_score = {
            "BUY": 1.0,
            "HOLD": 0.0,
            "SELL": -1.0,
        }.get(tech.get("signal", "HOLD"), 0.0)

        # Combine with weights
        w_t = float(self.weights.get("technical", 0.6))
        w_f = float(self.weights.get("fundamental", 0.4))
        combined_score = (tech_score * w_t) + (fund.get("bias_score", 0.0) * w_f)

        final_signal = "HOLD"
        if combined_score >= 0.25:
            final_signal = "BUY"
        elif combined_score <= -0.25:
            final_signal = "SELL"

        confidence = min(0.95, 0.5 + abs(combined_score))

        return {
            "technical": tech,
            "fundamental": fund,
            "score": combined_score,
            "signal": final_signal,
            "confidence": confidence,
        }
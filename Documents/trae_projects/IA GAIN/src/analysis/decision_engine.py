"""
Decision Engine

Aggregates multiple analyses (technical, momentum, patterns, sentiment)
to produce a comprehensive score per asset and select a top-N portfolio.

This module is designed to be lightweight glue that uses existing
analyzers where available and degrades gracefully when some components
are missing.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Sequence, Union, Tuple

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

from .technical_analysis import TechnicalAnalysis
from .combined_analyzer import CombinedAnalyzer

# Optional advanced modules
try:
    from .momentum_analyzer import AdvancedMomentumAnalyzer  # type: ignore
except Exception:
    AdvancedMomentumAnalyzer = None  # type: ignore

try:
    from .pattern_recognition import AdvancedPatternRecognition  # type: ignore
except Exception:
    AdvancedPatternRecognition = None  # type: ignore

try:
    from src.ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer  # type: ignore
except Exception:
    GenerativeSentimentAnalyzer = None  # type: ignore


def _ensure_df(candles: Union[Sequence[Dict[str, Any]], "pd.DataFrame"]) -> "pd.DataFrame":
    if pd is None:
        raise RuntimeError("pandas é necessário para decision_engine quando fornecido lista de candles")
    if isinstance(candles, pd.DataFrame):
        return candles
    return pd.DataFrame(candles)


class DecisionEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.cfg = config or {}
        self.tech = TechnicalAnalysis(config=self.cfg.get("technical", {}))
        self.combined = CombinedAnalyzer(config=self.cfg.get("combined", {}))
        self.momentum = AdvancedMomentumAnalyzer() if AdvancedMomentumAnalyzer else None
        self.patterns = AdvancedPatternRecognition() if AdvancedPatternRecognition else None
        self.sentiment = GenerativeSentimentAnalyzer() if GenerativeSentimentAnalyzer else None

        # Default weights for final score aggregation
        self.weights = self.cfg.get("weights", {
            "technical": 0.25,
            "combined": 0.25,
            "momentum": 0.25,
            "patterns": 0.15,
            "sentiment": 0.10,
        })

    def analyze_asset(self, candles: Union[Sequence[Dict[str, Any]], "pd.DataFrame"], symbol: str) -> Dict[str, Any]:
        df = _ensure_df(candles)

        # Technical baseline
        tech = self.tech.analyze(df)

        # Combined tech+fundamental baseline
        combined = self.combined.analyze(df, symbol)

        # Optional advanced momentum
        momentum_result: Dict[str, Any] = {}
        momentum_score = 0.0
        if self.momentum:
            try:
                momentum_result = self.momentum.analyze_momentum(df)  # type: ignore
                momentum_score = float(momentum_result.get("momentum_score", 0.0))
            except Exception:
                momentum_result = {}
                momentum_score = 0.0

        # Optional pattern recognition
        pattern_result: Dict[str, Any] = {}
        pattern_score = 0.0
        if self.patterns:
            try:
                pattern_result = self.patterns.analyze_patterns(df)  # type: ignore
                pattern_score = float(pattern_result.get("pattern_score", 0.0))
            except Exception:
                pattern_result = {}
                pattern_score = 0.0

        # Optional sentiment
        sentiment_result: Dict[str, Any] = {}
        sentiment_score = 0.0
        if self.sentiment:
            try:
                sentiment_result = self.sentiment.get_sentiment_summary(symbol, hours_back=168)  # type: ignore
                sentiment_score = float(sentiment_result.get("score", 0.0))
            except Exception:
                sentiment_result = {}
                sentiment_score = 0.0

        # Normalize signal scores
        tech_signal_score = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}.get(tech.get("signal", "HOLD"), 0.0)
        combined_score = float(combined.get("score", 0.0))

        # Aggregate final score
        w = self.weights
        final_score = (
            tech_signal_score * float(w.get("technical", 0.25))
            + combined_score * float(w.get("combined", 0.25))
            + momentum_score * float(w.get("momentum", 0.25))
            + pattern_score * float(w.get("patterns", 0.15))
            + sentiment_score * float(w.get("sentiment", 0.10))
        )

        final_signal = "HOLD"
        if final_score >= 0.25:
            final_signal = "BUY"
        elif final_score <= -0.25:
            final_signal = "SELL"

        return {
            "symbol": symbol,
            "technical": tech,
            "combined": combined,
            "momentum": momentum_result,
            "patterns": pattern_result,
            "sentiment": sentiment_result,
            "final_score": final_score,
            "signal": final_signal,
            "confidence": min(0.95, 0.5 + abs(final_score)),
        }

    def select_portfolio(
        self,
        assets_data: Dict[str, Union[Sequence[Dict[str, Any]], "pd.DataFrame"]],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        scored: List[Dict[str, Any]] = []
        for symbol, data in assets_data.items():
            try:
                result = self.analyze_asset(data, symbol)
                scored.append(result)
            except Exception:
                continue
        # Sort by absolute score strength (BUY then SELL) prioritizing BUY
        def sort_key(r: Dict[str, Any]) -> Tuple[int, float]:
            sig = r.get("signal", "HOLD")
            # BUY preferred: rank 2, HOLD:1, SELL:0
            rank = {"SELL": 0, "HOLD": 1, "BUY": 2}.get(sig, 1)
            return (rank, float(r.get("final_score", 0.0)))

        scored_sorted = sorted(scored, key=sort_key, reverse=True)
        return scored_sorted[:top_n]
"""
Fundamental Analysis module (lightweight facade)

This module provides a minimal interface to produce a fundamental
sentiment score and directional bias. It integrates with the
GenerativeSentimentAnalyzer if available, and otherwise falls back
to neutral sentiment.

Intended for:
- MT5 / FX demo trading setups where a simple, pluggable
  fundamental layer is useful but full macro ingestion is out of scope.
"""

from __future__ import annotations

from typing import Dict, Any, Optional


DEFAULT_PROMPT = (
    "Analise o sentimento macroeconômico e fundamental para o par {symbol}. "
    "Considere política monetária, inflação, emprego, PMI, risco geopolítico e fluxo de capitais. "
    "Resuma em 2-3 frases e forneça um viés (bullish/bearish/neutral)."
)


class FundamentalAnalysis:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.cfg = config or {}
        self.prompt = self.cfg.get("prompt", DEFAULT_PROMPT)

    def analyze(self, symbol: str) -> Dict[str, Any]:
        sentiment: Dict[str, Any] = {
            "summary": "Sentimento neutro por padrão; sem dados macro integrados.",
            "bias": "neutral",
            "confidence": 0.5,
        }
        try:
            # Lazy import to avoid hard dependency
            from src.ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer  # type: ignore
            analyzer = GenerativeSentimentAnalyzer(config=self.cfg.get("llm", {}))
            text = self.prompt.format(symbol=symbol)
            result = analyzer.analyze_text(text)
            # Expecting result like { 'category': 'bullish' | 'bearish' | 'neutral', 'confidence': float, 'summary': str }
            if isinstance(result, dict):
                sentiment = {
                    "summary": result.get("summary", sentiment["summary"]),
                    "bias": result.get("category", sentiment["bias"]).lower(),
                    "confidence": float(result.get("confidence", sentiment["confidence"])),
                }
        except Exception:
            # Fall back to neutral if analyzer isn't available
            pass

        bias = sentiment.get("bias", "neutral")
        bias_score = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}.get(bias, 0.0)
        return {
            "sentiment": sentiment,
            "bias_score": bias_score,
        }
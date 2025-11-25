"""
Technical Analysis module (lightweight)

Provides core technical indicators and a simple signal generator
that works with either pandas DataFrame or a list of OHLCV dicts.

Indicators:
- EMA (fast/slow)
- RSI (14)
- ATR (14)

Signal:
- BUY when EMA_fast > EMA_slow and RSI > 55
- SELL when EMA_fast < EMA_slow and RSI < 45
- otherwise HOLD
"""

from __future__ import annotations

from typing import List, Dict, Any, Sequence, Optional, Union


def _extract_closes(candles: Union[Sequence[Dict[str, Any]], "pd.DataFrame"]) -> List[float]:
    try:
        import pandas as pd  # type: ignore
        if isinstance(candles, pd.DataFrame):
            return [float(x) for x in candles["close"].tolist()]
    except Exception:
        pass
    return [float(c["close"]) for c in candles]  # type: ignore


def _extract_hlc(candles: Union[Sequence[Dict[str, Any]], "pd.DataFrame"]) -> Dict[str, List[float]]:
    try:
        import pandas as pd  # type: ignore
        if isinstance(candles, pd.DataFrame):
            return {
                "high": [float(x) for x in candles["high"].tolist()],
                "low": [float(x) for x in candles["low"].tolist()],
                "close": [float(x) for x in candles["close"].tolist()],
            }
    except Exception:
        pass
    return {
        "high": [float(c["high"]) for c in candles],  # type: ignore
        "low": [float(c["low"]) for c in candles],
        "close": [float(c["close"]) for c in candles],
    }


def ema(values: Sequence[float], period: int) -> List[float]:
    if period <= 1 or len(values) == 0:
        return [float(v) for v in values]
    k = 2.0 / (period + 1)
    out: List[float] = []
    prev = float(values[0])
    for v in values:
        prev = (float(v) * k) + (prev * (1 - k))
        out.append(prev)
    return out


def rsi(values: Sequence[float], period: int = 14) -> List[float]:
    if len(values) < period + 1:
        return [50.0] * len(values)
    gains = [0.0]
    losses = [0.0]
    for i in range(1, len(values)):
        change = float(values[i]) - float(values[i - 1])
        gains.append(max(0.0, change))
        losses.append(max(0.0, -change))
    avg_gain = sum(gains[1:period + 1]) / period
    avg_loss = sum(losses[1:period + 1]) / period
    rsi_vals = [50.0] * len(values)
    for i in range(period + 1, len(values)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi_vals[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_vals[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsi_vals


def atr(high: Sequence[float], low: Sequence[float], close: Sequence[float], period: int = 14) -> List[float]:
    if len(close) == 0:
        return []
    trs: List[float] = []
    prev_close = float(close[0])
    for h, l, c in zip(high, low, close):
        tr = max(float(h) - float(l), abs(float(h) - prev_close), abs(float(l) - prev_close))
        trs.append(tr)
        prev_close = float(c)
    # Simple moving average of TR
    atr_vals: List[float] = []
    window = []
    for tr in trs:
        window.append(tr)
        if len(window) > period:
            window.pop(0)
        atr_vals.append(sum(window) / len(window))
    return atr_vals


class TechnicalAnalysis:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.fast = int(cfg.get("ema_fast", 21))
        self.slow = int(cfg.get("ema_slow", 50))
        self.rsi_period = int(cfg.get("rsi_period", 14))
        self.buy_rsi = float(cfg.get("buy_rsi", 55.0))
        self.sell_rsi = float(cfg.get("sell_rsi", 45.0))

    def analyze(self, candles: Union[Sequence[Dict[str, Any]], "pd.DataFrame"]) -> Dict[str, Any]:
        closes = _extract_closes(candles)
        hlc = _extract_hlc(candles)
        ema_fast = ema(closes, self.fast)
        ema_slow = ema(closes, self.slow)
        rsi_vals = rsi(closes, self.rsi_period)
        atr_vals = atr(hlc["high"], hlc["low"], hlc["close"], 14)

        signal = "HOLD"
        confidence = 0.5
        if len(closes) >= 2:
            if ema_fast[-1] > ema_slow[-1] and rsi_vals[-1] >= self.buy_rsi:
                signal = "BUY"
                confidence = min(0.9, 0.6 + (rsi_vals[-1] - self.buy_rsi) / 50.0)
            elif ema_fast[-1] < ema_slow[-1] and rsi_vals[-1] <= self.sell_rsi:
                signal = "SELL"
                confidence = min(0.9, 0.6 + (self.sell_rsi - rsi_vals[-1]) / 50.0)

        return {
            "ema_fast": ema_fast[-1] if ema_fast else None,
            "ema_slow": ema_slow[-1] if ema_slow else None,
            "rsi": rsi_vals[-1] if rsi_vals else None,
            "atr": atr_vals[-1] if atr_vals else None,
            "signal": signal,
            "confidence": confidence,
        }
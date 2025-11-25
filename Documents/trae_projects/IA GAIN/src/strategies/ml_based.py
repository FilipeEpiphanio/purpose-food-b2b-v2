from __future__ import annotations

import pandas as pd

from .base import Strategy, Signal


def _feature_block(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"].astype(float)
    out["roc"] = close.pct_change()
    out["ema_fast"] = close.ewm(span=10, adjust=False).mean()
    out["ema_slow"] = close.ewm(span=30, adjust=False).mean()
    out["ema_diff"] = out["ema_fast"] - out["ema_slow"]
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/14, adjust=False).mean()
    ma_down = down.ewm(alpha=1/14, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-12)
    out["rsi"] = 100 - (100 / (1 + rs))
    out = out.fillna(0.0)
    return out


class MLBased(Strategy):
    def __init__(self, score_col: str | None = None, buy_thresh: float = 0.55, sell_thresh: float = 0.45):
        super().__init__(name="ML_BASED", score_col=score_col, buy=buy_thresh, sell=sell_thresh)

    def generate_signals(self, df: pd.DataFrame):
        # Mode A: use external ml score column (probability up)
        score_col = self.params.get("score_col")
        if score_col and score_col in df.columns:
            s = df[score_col].astype(float)
        else:
            # Mode B: heuristic ML-like score from features
            feat = _feature_block(df)
            # normalize
            z = (feat - feat.mean()) / (feat.std() + 1e-9)
            # weighted sum to produce pseudo-probability
            w = {
                "roc": 0.25,
                "ema_diff": 0.45,
                "rsi": 0.30,
            }
            score = (z[list(w.keys())] * pd.Series(w)).sum(axis=1)
            s = 1 / (1 + (-score).apply(lambda x: max(min(x, 10), -10)).apply(lambda x: pd.np.exp(x)))  # logistic

        signals = []
        for ts, val in s.items():
            price = float(df.loc[ts, "close"]) if "close" in df.columns else float("nan")
            if val >= float(self.params["buy"]):
                signals.append(Signal(timestamp=ts, action="buy", price=price))
            elif val <= float(self.params["sell"]):
                signals.append(Signal(timestamp=ts, action="sell", price=price))
        return signals
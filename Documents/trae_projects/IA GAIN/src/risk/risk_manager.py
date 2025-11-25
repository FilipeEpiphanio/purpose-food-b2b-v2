from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RiskConfig:
    balance_usd: float = 10000.0
    max_portfolio_risk: float = 0.05
    max_single_trade_risk: float = 0.02
    risk_reward_ratio: float = 2.0
    use_trailing_stop: bool = True
    trailing_stop_distance: float = 0.002  # 20 pips approx on majors
    max_concurrent_trades: int = 5


class RiskManager:
    """Basic risk controls for Forex autonomous trading.

    - Enforces per-trade risk as a fraction of `balance_usd`.
    - Provides trailing stop configuration.
    - Validates lot size and stop distance sanity.
    """

    def __init__(self, config: Dict):
        risk = config.get('risk', {})
        system = config.get('system', {})
        self.cfg = RiskConfig(
            balance_usd=float(risk.get('balance_usd', 10000.0)),
            max_portfolio_risk=float(risk.get('max_portfolio_risk', 0.05)),
            max_single_trade_risk=float(risk.get('max_single_trade_risk', 0.02)),
            risk_reward_ratio=float(risk.get('risk_reward_ratio', 2.0)),
            use_trailing_stop=bool(risk.get('use_trailing_stop', True)),
            trailing_stop_distance=float(risk.get('trailing_stop_distance', 0.002)),
            max_concurrent_trades=int(system.get('max_concurrent_trades', 5)),
        )

    def get_max_risk_per_trade(self) -> float:
        return self.cfg.balance_usd * self.cfg.max_single_trade_risk

    def get_trailing_stop_distance(self) -> Optional[float]:
        return self.cfg.trailing_stop_distance if self.cfg.use_trailing_stop else None

    def estimate_pip_value_per_lot(self, symbol: str) -> float:
        """Approximate pip value for 1.0 lot in USD terms.
        Assumptions:
        - Majors with USD as quote ~ $10 per pip per lot.
        - If USD is base or cross, use $7 as conservative estimate.
        """
        symbol = symbol.replace('-', '/').upper()
        base, quote = symbol.split('/') if '/' in symbol else (symbol[:3], symbol[3:])
        if quote == 'USD':
            return 10.0
        return 7.0

    def check_trade_risk(self, symbol: str, entry_price: float, stop_loss: float, lot_size: float) -> Dict:
        """Validate if proposed trade fits risk budget.

        Returns a dict with `ok` and `reason`.
        """
        try:
            if lot_size <= 0:
                return {"ok": False, "reason": "lot_size must be > 0"}

            pip_distance = abs(entry_price - stop_loss) * 10000  # pips
            if pip_distance < 5:
                return {"ok": False, "reason": "stop distance too tight (<5 pips)"}

            pip_value = self.estimate_pip_value_per_lot(symbol)
            risk_amount = pip_distance * pip_value * lot_size

            max_risk = self.get_max_risk_per_trade()
            if risk_amount > max_risk:
                return {
                    "ok": False,
                    "reason": f"risk ${risk_amount:.2f} exceeds max ${max_risk:.2f}",
                }

            return {"ok": True, "reason": "risk within limits"}

        except Exception as e:
            return {"ok": False, "reason": f"risk check failed: {e}"}
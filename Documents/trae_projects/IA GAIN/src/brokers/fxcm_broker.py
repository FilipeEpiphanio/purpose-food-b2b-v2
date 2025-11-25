from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, Optional

from loguru import logger

try:
    import fxcmpy
except Exception:  # pragma: no cover
    fxcmpy = None

from .base import Broker, BrokerTrade


def to_fxcm_symbol(symbol: str) -> str:
    # FXCM typically uses "EUR/USD" format; keep slash and uppercase
    s = symbol.replace("-", "/").upper()
    if "/" in s:
        return s
    # Best effort: insert slash between 3+3
    if len(s) == 6:
        return f"{s[:3]}/{s[3:]}"
    return s


def pip_size_for_symbol(symbol: str) -> float:
    s = to_fxcm_symbol(symbol)
    try:
        base, quote = s.split("/")
    except ValueError:
        # Fallback: assume non-JPY
        quote = "USD"
    return 0.01 if quote == "JPY" else 0.0001


class FXCMBroker(Broker):
    def __init__(self, config: Dict | None = None):
        self.config = config or {}
        self.logger = logger.bind(component="FXCMBroker")
        self.conn: Optional["fxcmpy.fxcmpy"] = None

    async def initialize(self) -> None:
        if fxcmpy is None:
            self.logger.error("fxcmpy not installed. Please add 'fxcmpy' to requirements and install.")
            return
        token = self.config.get("fxcm", {}).get("token")
        log_level = self.config.get("fxcm", {}).get("log_level", "error")
        server = self.config.get("fxcm", {}).get("server", "demo")
        try:
            # fxcmpy is synchronous; wrap in thread
            self.conn = await asyncio.to_thread(fxcmpy.fxcmpy, access_token=token, log_level=log_level, server=server)
            self.logger.info("FXCMBroker connected")
        except Exception as e:
            self.logger.error(f"FXCM connection failed: {e}")
            self.conn = None

    async def open_order(self, symbol: str, side: str, price: float, volume: float, sl: float, tp: float) -> BrokerTrade:
        if self.conn is None:
            await self.initialize()
        if self.conn is None:
            # Simulate
            return BrokerTrade(
                id=f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                symbol=symbol,
                side=side,
                volume=volume,
                entry_price=price,
                stop_loss=sl,
                take_profit=tp,
                open_time=datetime.now(),
            )
        fxcm_sym = to_fxcm_symbol(symbol)
        is_buy = 1 if side == "buy" else -1
        use_pips = bool(self.config.get("fxcm", {}).get("is_in_pips", False))
        stop_param = sl
        limit_param = tp
        extra_kwargs = {}
        if use_pips:
            pip = pip_size_for_symbol(symbol)
            if side == "buy":
                stop_pips = max(1, int(round((price - sl) / pip)))
                limit_pips = max(1, int(round((tp - price) / pip)))
            else:
                stop_pips = max(1, int(round((sl - price) / pip)))
                limit_pips = max(1, int(round((price - tp) / pip)))
            stop_param = stop_pips
            limit_param = limit_pips
            extra_kwargs["is_in_pips"] = True
        try:
            # place a market order; FXCM uses units, stop/limit distances in pips or price
            # Some accounts require stop/limit in pips via 'is_in_pips=True'. We send prices for simplicity.
            resp = await asyncio.to_thread(
                self.conn.open_trade,
                symbol=fxcm_sym,
                is_buy=is_buy,
                amount=volume,
                time_in_force="GTC",
                stop=stop_param,
                limit=limit_param,
                **extra_kwargs,
            )
            trade_id = str(getattr(resp, "tradeId", getattr(resp, "orderId", f"FXCM-{datetime.now().timestamp()}")))
            return BrokerTrade(
                id=trade_id,
                symbol=symbol,
                side=side,
                volume=volume,
                entry_price=price,
                stop_loss=sl,
                take_profit=tp,
                open_time=datetime.now(),
            )
        except Exception as e:
            self.logger.error(f"FXCM order failed: {e}")
            return BrokerTrade(
                id=f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                symbol=symbol,
                side=side,
                volume=volume,
                entry_price=price,
                stop_loss=sl,
                take_profit=tp,
                open_time=datetime.now(),
                status="error",
            )

    async def close_order(self, trade: BrokerTrade, price: float, reason: str = "Manual") -> BrokerTrade:
        if self.conn is None:
            # Simulate close
            trade.close_time = datetime.now()
            trade.close_price = price
            trade.status = "closed"
            sign = 1 if trade.side == "buy" else -1
            pip_move = (price - trade.entry_price) * 10000 * sign
            trade.pnl_usd = pip_move * 10.0 * trade.volume
            return trade
        try:
            await asyncio.to_thread(self.conn.close_all_for_symbol, to_fxcm_symbol(trade.symbol))
        except Exception as e:
            self.logger.error(f"FXCM close failed: {e}")
        trade.close_time = datetime.now()
        trade.close_price = price
        trade.status = "closed"
        sign = 1 if trade.side == "buy" else -1
        pip_move = (price - trade.entry_price) * 10000 * sign
        trade.pnl_usd = pip_move * 10.0 * trade.volume
        return trade
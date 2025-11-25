from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from loguru import logger

try:
    import MetaTrader5 as MT5
except Exception:  # pragma: no cover
    MT5 = None

from .base import Broker, BrokerTrade


def to_mt5_symbol(symbol: str) -> str:
    # Convert "EUR/USD" -> "EURUSD"
    s = symbol.replace("-", "/").upper()
    if "/" in s:
        base, quote = s.split("/")
        return f"{base}{quote}"
    return s


class MT5Broker(Broker):
    def __init__(self, config: Dict | None = None):
        self.config = config or {}
        self.logger = logger.bind(component="MT5Broker")
        self.initialized = False

    async def initialize(self) -> None:
        if MT5 is None:
            self.logger.error("MetaTrader5 package not installed. Please add 'MetaTrader5' to requirements and install.")
            return
        creds = self.config.get("mt5", {})
        login = creds.get("login")
        password = creds.get("password")
        server = creds.get("server")
        path = creds.get("path", "")
        # Initialize terminal (blocking), run in thread
        try:
            if path:
                ok = await asyncio.to_thread(MT5.initialize, path=path)
                # Fallback: se o caminho for diretório ou não apontar para terminal64.exe, tentar resolver
                if not ok and path and not str(path).lower().endswith("terminal64.exe"):
                    exe_path = path.rstrip("\\/") + "\\terminal64.exe"
                    ok = await asyncio.to_thread(MT5.initialize, path=exe_path)
            else:
                ok = await asyncio.to_thread(MT5.initialize)
        except Exception as e:
            self.logger.error(f"MT5 initialize exception: {e}")
            return
        if not ok:
            self.logger.error("MT5 initialize failed")
            return
        if login and server:
            authorized = await asyncio.to_thread(MT5.login, login, password, server)
            if not authorized:
                self.logger.error("MT5 login failed. Check credentials in config.mt5")
                return
        self.initialized = True
        self.logger.info("MT5Broker initialized")

    async def _ensure_symbol(self, symbol: str) -> Optional[str]:
        if not self.initialized:
            await self.initialize()
        if not self.initialized or MT5 is None:
            return None
        mt5_sym = to_mt5_symbol(symbol)
        selected = await asyncio.to_thread(MT5.symbol_select, mt5_sym, True)
        if not selected:
            # Fallback: tentar encontrar variações do símbolo disponíveis (ex: EURUSDm, EURUSD.i)
            try:
                symbols = await asyncio.to_thread(MT5.symbols_get)
                candidates = []
                for s in symbols or []:
                    name = getattr(s, "name", "")
                    if name.upper().startswith(mt5_sym):
                        candidates.append(name)
                if candidates:
                    for alt in candidates:
                        if await asyncio.to_thread(MT5.symbol_select, alt, True):
                            self.logger.info(f"Selecionado símbolo alternativo: {alt} para {mt5_sym}")
                            return alt
                self.logger.error(f"MT5 symbol not available: {mt5_sym}")
            except Exception as e:
                self.logger.error(f"MT5 symbol check failed: {e}")
            return None
        return mt5_sym

    async def open_order(self, symbol: str, side: str, price: float, volume: float, sl: float, tp: float) -> BrokerTrade:
        mt5_sym = await self._ensure_symbol(symbol)
        if not mt5_sym or MT5 is None:
            # Fallback: simulate
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

        # Obter preço atual e requisitos de stops para garantir validade
        info = await asyncio.to_thread(MT5.symbol_info, mt5_sym)
        tick = await asyncio.to_thread(MT5.symbol_info_tick, mt5_sym)
        if not info or not tick:
            self.logger.error("MT5 symbol info/tick unavailable")
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

        trade_type = MT5.ORDER_TYPE_BUY if side == "buy" else MT5.ORDER_TYPE_SELL
        entry_price = float(tick.ask) if side == "buy" else float(tick.bid)
        point = float(getattr(info, "point", 0.0) or 0.00001)
        stops_level = int(getattr(info, "trade_stops_level", 0) or 0)
        min_dist = stops_level * point

        # Ajustar SL/TP para respeitar distância mínima
        adj_sl = float(sl)
        adj_tp = float(tp)
        try:
            if side == "buy":
                # SL abaixo do preço por pelo menos min_dist, TP acima
                adj_sl = min(adj_sl, entry_price - max(min_dist, 0))
                adj_tp = max(adj_tp, entry_price + max(min_dist, 0))
            else:
                # SL acima do preço, TP abaixo
                adj_sl = max(adj_sl, entry_price + max(min_dist, 0))
                adj_tp = min(adj_tp, entry_price - max(min_dist, 0))
        except Exception:
            pass
        request = {
            "action": MT5.TRADE_ACTION_DEAL,
            "symbol": mt5_sym,
            "type": trade_type,
            "volume": float(volume),
            "price": float(entry_price),
            "deviation": int(self.config.get("mt5", {}).get("max_deviation", 10)),
            "sl": float(adj_sl),
            "tp": float(adj_tp),
            "type_filling": MT5.ORDER_FILLING_IOC,
        }
        result = await asyncio.to_thread(MT5.order_send, request)
        if result and result.retcode == MT5.TRADE_RETCODE_DONE:
            ticket = result.order
            return BrokerTrade(
                id=str(ticket),
                symbol=symbol,
                side=side,
                volume=volume,
                entry_price=price,
                stop_loss=sl,
                take_profit=tp,
                open_time=datetime.now(),
            )
        else:
            # Fallback: se falhar por stops inválidos, tentar sem SL/TP
            comment = getattr(result, "comment", "") if result else ""
            self.logger.error(f"MT5 order failed: {comment or 'unknown'}")
            try:
                if result and (getattr(result, "retcode", 0) == getattr(MT5, "TRADE_RETCODE_INVALID_STOPS", 0) or "Invalid stops" in str(comment)):
                    req2 = {
                        "action": MT5.TRADE_ACTION_DEAL,
                        "symbol": mt5_sym,
                        "type": trade_type,
                        "volume": float(volume),
                        "price": float(entry_price),
                        "deviation": int(self.config.get("mt5", {}).get("max_deviation", 10)),
                        "type_filling": MT5.ORDER_FILLING_IOC,
                    }
                    result2 = await asyncio.to_thread(MT5.order_send, req2)
                    if result2 and result2.retcode == MT5.TRADE_RETCODE_DONE:
                        ticket = result2.order
                        # Tentar aplicar SL/TP após a abertura para manter proteção
                        try:
                            await self._apply_stops_post_open(mt5_sym, ticket, side, sl, tp)
                            applied_sl, applied_tp = sl, tp
                        except Exception:
                            applied_sl, applied_tp = 0.0, 0.0
                        return BrokerTrade(
                            id=str(ticket),
                            symbol=symbol,
                            side=side,
                            volume=volume,
                            entry_price=price,
                            stop_loss=applied_sl,
                            take_profit=applied_tp,
                            open_time=datetime.now(),
                        )
            except Exception:
                pass
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
        if MT5 is None or not self.initialized:
            # Simulate close
            trade.close_time = datetime.now()
            trade.close_price = price
            trade.status = "closed"
            # Simple PnL estimate
            sign = 1 if trade.side == "buy" else -1
            pip_move = (price - trade.entry_price) * 10000 * sign
            trade.pnl_usd = pip_move * 10.0 * trade.volume
            return trade

        mt5_sym = to_mt5_symbol(trade.symbol)
        positions = await asyncio.to_thread(MT5.positions_get, symbol=mt5_sym)
        if positions:
            pos = positions[0]
            # Close position by sending opposite deal
            trade_type = MT5.ORDER_TYPE_SELL if trade.side == "buy" else MT5.ORDER_TYPE_BUY
            request = {
                "action": MT5.TRADE_ACTION_DEAL,
                "symbol": mt5_sym,
                "type": trade_type,
                "position": pos.ticket,
                "volume": float(trade.volume),
                "price": float(price),
                "deviation": int(self.config.get("mt5", {}).get("max_deviation", 10)),
                "type_filling": MT5.ORDER_FILLING_FOK,
            }
            result = await asyncio.to_thread(MT5.order_send, request)
            if result and result.retcode == MT5.TRADE_RETCODE_DONE:
                trade.close_time = datetime.now()
                trade.close_price = price
                trade.status = "closed"
                # Approximate PnL
                sign = 1 if trade.side == "buy" else -1
                pip_move = (price - trade.entry_price) * 10000 * sign
                trade.pnl_usd = pip_move * 10.0 * trade.volume
                return trade

        # Fallback simulate
        trade.close_time = datetime.now()
        trade.close_price = price
        trade.status = "closed"
        sign = 1 if trade.side == "buy" else -1
        pip_move = (price - trade.entry_price) * 10000 * sign
        trade.pnl_usd = pip_move * 10.0 * trade.volume
        return trade

    async def _apply_stops_post_open(self, mt5_symbol: str, ticket: int, side: str, sl: float, tp: float) -> None:
        """Aplica SL/TP em uma posição já aberta, ajustando ao mínimo exigido."""
        if MT5 is None:
            return
        info = await asyncio.to_thread(MT5.symbol_info, mt5_symbol)
        tick = await asyncio.to_thread(MT5.symbol_info_tick, mt5_symbol)
        if not info or not tick:
            return
        point = float(getattr(info, "point", 0.0) or 0.00001)
        stops_level = int(getattr(info, "trade_stops_level", 0) or 0)
        min_dist = stops_level * point
        entry_price = float(tick.ask) if side == "buy" else float(tick.bid)
        adj_sl = float(sl)
        adj_tp = float(tp)
        try:
            if side == "buy":
                adj_sl = min(adj_sl, entry_price - max(min_dist, 0))
                adj_tp = max(adj_tp, entry_price + max(min_dist, 0))
            else:
                adj_sl = max(adj_sl, entry_price + max(min_dist, 0))
                adj_tp = min(adj_tp, entry_price - max(min_dist, 0))
        except Exception:
            pass
        request = {
            "action": MT5.TRADE_ACTION_SLTP,
            "symbol": mt5_symbol,
            "position": int(ticket),
            "sl": float(adj_sl),
            "tp": float(adj_tp),
            "deviation": int(self.config.get("mt5", {}).get("max_deviation", 10)),
        }
        await asyncio.to_thread(MT5.order_send, request)
#!/usr/bin/env python3
"""
IA GAIN - Forex Backtest
Backtest completo para pares de moedas com seleção de estratégia,
gestão de portfólio, sizing por risco e relatório de operações.

Sem dependências externas (usa apenas biblioteca padrão)
"""

import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os
import sys

# Integração opcional com o ForexAnalyzer do projeto principal
_FOREX_ANALYZER_AVAILABLE = False
try:
    project_src = Path(__file__).parent / 'src'
    if project_src.exists():
        sys.path.append(str(project_src))
    from src.forex.forex_analyzer import ForexAnalyzer, ForexSignal  # type: ignore
    _FOREX_ANALYZER_AVAILABLE = True
    _FOREX_ANALYZER = ForexAnalyzer({})
except Exception:
    _FOREX_ANALYZER = None


# ----------------------------- Utilidades Forex -----------------------------

FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD",
    # Crosses para maior diversidade
    "EUR/JPY", "GBP/JPY", "EUR/GBP", "AUD/JPY", "CAD/JPY", "CHF/JPY"
]

def pip_value_per_lot(symbol: str) -> float:
    """Valor aproximado do pip para 1 lote em USD."""
    if symbol.endswith("JPY"):
        return 9.0
    if symbol.endswith("CHF"):
        return 9.5
    return 10.0


def pips_from_price_move(symbol: str, price_move: float) -> float:
    """Converter variação de preço em pips (aprox)."""
    if symbol.endswith("JPY"):
        return price_move * 100
    return price_move * 10000


def atr_pips(symbol: str, candles: List["Candle"], period: int = 14) -> float:
    """ATR aproximado em pips, usando True Range sobre OHLC."""
    if len(candles) < period + 1:
        return 15.0
    trs = []
    for i in range(-period, 0):
        cur = candles[i]
        prev_close = candles[i - 1].close
        tr = max(cur.high - cur.low, abs(cur.high - prev_close), abs(cur.low - prev_close))
        trs.append(tr)
    avg_tr = sum(trs) / len(trs)
    return max(15.0, pips_from_price_move(symbol, avg_tr))


# -------------------------- Confirmação externa (IA GAIN) -------------------

def external_analysis(symbol: str, candles: List["Candle"]) -> Optional[Dict]:
    """Usa ForexAnalyzer (se disponível) para validar direção e sugerir SL/TP.

    Retorna dict com chaves: signal, confidence, stop_loss_pips, take_profit_pips
    """
    if not _FOREX_ANALYZER_AVAILABLE or _FOREX_ANALYZER is None:
        return None
    try:
        # Tentativa defensiva: o ForexAnalyzer pode possuir diferentes métodos.
        # Vamos tentar métodos comuns que geram análise por símbolo.
        for method_name in ("generate_signal", "analyze_symbol", "analyze_market", "analyze_pair"):
            if hasattr(_FOREX_ANALYZER, method_name):
                method = getattr(_FOREX_ANALYZER, method_name)
                try:
                    analysis = method(symbol)
                    if analysis is None:
                        continue
                    return {
                        "signal": getattr(analysis, "signal", None),
                        "confidence": getattr(analysis, "confidence", 0.0),
                        "stop_loss_pips": getattr(analysis, "stop_loss_pips", 0.0),
                        "take_profit_pips": getattr(analysis, "take_profit_pips", 0.0),
                    }
                except Exception:
                    continue
        return None
    except Exception:
        return None


# --------------------------- Dados simulados (OHLC) --------------------------

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def generate_mock_forex_data(symbol: str, days: int = 30) -> List[Candle]:
    """Gerar dados horários realistas para Forex com volatilidade controlada."""
    data: List[Candle] = []

    # Preço base aproximado por par
    base_prices = {
        "EUR/USD": 1.10,
        "GBP/USD": 1.25,
        "USD/JPY": 150.0,
        "USD/CHF": 0.90,
        "AUD/USD": 0.65,
        "USD/CAD": 1.35,
        "NZD/USD": 0.60,
        # Novos crosses
        "EUR/JPY": 165.0,
        "GBP/JPY": 185.0,
        "EUR/GBP": 0.86,
        "AUD/JPY": 98.0,
        "CAD/JPY": 109.0,
        "CHF/JPY": 170.0,
    }
    base = base_prices.get(symbol, 1.0)

    # Volatilidade diária aproximada em porcentagem
    daily_vol = 0.006 if not symbol.endswith("JPY") else 0.004
    hourly_vol = daily_vol / 24

    current = datetime.now() - timedelta(days=days)
    price = base

    for _ in range(days * 24):
        # Random walk com leve tendência
        drift = random.uniform(-hourly_vol, hourly_vol)
        price *= (1 + drift)
        high = price * (1 + random.uniform(0.0, hourly_vol * 0.6))
        low = price * (1 - random.uniform(0.0, hourly_vol * 0.6))
        open_p = (price + low) / 2
        volume = random.uniform(5_000_000, 50_000_000)
        data.append(Candle(timestamp=current, open=open_p, high=high, low=low, close=price, volume=volume))
        current += timedelta(hours=1)

    return data


# ------------------------------- Estratégias --------------------------------

def momentum_signal(candles: List[Candle]) -> Tuple[str, float]:
    """Sinal de momentum com força bas. Usa retorno médio das últimas 24 horas."""
    if len(candles) < 25:
        return ("HOLD", 0.0)
    rets = []
    for i in range(len(candles) - 24, len(candles)):
        prev = candles[i - 1].close
        cur = candles[i].close
        rets.append((cur - prev) / prev)
    avg_ret = sum(rets) / len(rets)
    strength = min(abs(avg_ret) * 100, 1.0)
    if avg_ret > 0.0008:
        return ("BUY", strength)
    if avg_ret < -0.0008:
        return ("SELL", strength)
    return ("HOLD", 0.0)


def mean_reversion_signal(candles: List[Candle]) -> Tuple[str, float]:
    if len(candles) < 50:
        return ("HOLD", 0.0)
    closes = [c.close for c in candles[-50:]]
    mean = sum(closes) / len(closes)
    cur = closes[-1]
    dev = (cur - mean) / mean
    strength = min(abs(dev) * 200, 1.0)
    if dev < -0.0025:
        return ("BUY", strength)
    if dev > 0.0025:
        return ("SELL", strength)
    return ("HOLD", 0.0)


def breakout_signal(candles: List[Candle]) -> Tuple[str, float]:
    if len(candles) < 30:
        return ("HOLD", 0.0)
    closes = [c.close for c in candles[-30:]]
    recent_high = max(closes[:-3])
    recent_low = min(closes[:-3])
    cur = closes[-1]
    if cur > recent_high * 1.001:
        return ("BUY", 0.7)
    if cur < recent_low * 0.999:
        return ("SELL", 0.7)
    return ("HOLD", 0.0)


def trend_following_signal(candles: List[Candle]) -> Tuple[str, float]:
    if len(candles) < 40:
        return ("HOLD", 0.0)
    closes = [c.close for c in candles]
    ma_short = sum(closes[-12:]) / 12
    ma_long = sum(closes[-36:]) / 36
    cur = closes[-1]
    if ma_short > ma_long * 1.0008 and cur > ma_short:
        return ("BUY", 0.6)
    if ma_short < ma_long * 0.9992 and cur < ma_short:
        return ("SELL", 0.6)
    return ("HOLD", 0.0)


STRATEGIES = {
    "momentum": momentum_signal,
    "mean_reversion": mean_reversion_signal,
    "breakout": breakout_signal,
    "trend_following": trend_following_signal,
}


# ---------------------------- Gestão de Risco/Port ---------------------------

@dataclass
class Position:
    symbol: str
    side: str  # LONG/SHORT
    entry_price: float
    lot_size: float
    stop_loss_pips: float
    take_profit_pips: float
    open_time: datetime
    close_time: Optional[datetime] = None
    close_price: Optional[float] = None
    pnl_pips: float = 0.0
    pnl_value: float = 0.0
    close_reason: Optional[str] = None


class RiskPortfolio:
    def __init__(self, balance: float = 10_000.0, risk_per_trade: float = 0.02, max_portfolio_risk: float = 0.10):
        self.balance = balance
        self.risk_per_trade = risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.open_positions: List[Position] = []

    def available_risk_budget(self) -> float:
        used = sum(self.balance * self.risk_per_trade for _ in self.open_positions)
        return max(0.0, self.balance * self.max_portfolio_risk - used)

    def can_open_trade(self) -> bool:
        return self.available_risk_budget() >= self.balance * self.risk_per_trade

    def position_size(self, symbol: str, stop_loss_pips: float) -> float:
        risk_amount = self.balance * self.risk_per_trade
        pip_value = pip_value_per_lot(symbol)
        if stop_loss_pips <= 0:
            stop_loss_pips = 20
        lot = risk_amount / (stop_loss_pips * pip_value)
        return max(0.01, min(lot, 1.0))

    def register_open(self, pos: Position):
        self.open_positions.append(pos)

    def register_close(self, pos: Position):
        # remove by identity
        self.open_positions = [p for p in self.open_positions if p is not pos]


# ------------------------------ Motor de Backtest ----------------------------

def simulate_backtest_for_symbol(symbol: str, candles: List[Candle], strategy_name: str, portfolio: RiskPortfolio) -> Dict:
    strategy_fn = STRATEGIES[strategy_name]
    trades: List[Position] = []
    equity = portfolio.balance
    peak_equity = equity
    max_drawdown = 0.0

    # Clone portfolio state so symbols don't interfere
    local_portfolio = RiskPortfolio(balance=portfolio.balance, risk_per_trade=portfolio.risk_per_trade, max_portfolio_risk=portfolio.max_portfolio_risk)

    # iterate candles
    for i in range(50, len(candles)):
        window = candles[: i + 1]
        signal, strength = strategy_fn(window)
        cur_price = candles[i].close

        # Update open positions for SL/TP
        for pos in list(local_portfolio.open_positions):
            move = (cur_price - pos.entry_price)
            pips = pips_from_price_move(symbol, move)
            if pos.side == "SHORT":
                pips *= -1
            pos.pnl_pips = pips
            pos.pnl_value = pips * pip_value_per_lot(symbol) * pos.lot_size

            # Check TP/SL
            if pos.pnl_pips >= pos.take_profit_pips:
                pos.close_time = candles[i].timestamp
                pos.close_price = cur_price
                pos.close_reason = "TP"
                trades.append(pos)
                local_portfolio.register_close(pos)
                equity += pos.pnl_value
            elif pos.pnl_pips <= -pos.stop_loss_pips:
                pos.close_time = candles[i].timestamp
                pos.close_price = cur_price
                pos.close_reason = "SL"
                trades.append(pos)
                local_portfolio.register_close(pos)
                equity += pos.pnl_value

        # Risk metrics
        if equity > peak_equity:
            peak_equity = equity
        dd = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0.0
        max_drawdown = max(max_drawdown, dd)

        # Decide to open new position based on score and risk budget
        if signal in ("BUY", "SELL") and strength >= 0.60 and local_portfolio.can_open_trade():
            # Opcional: confirmar direção com análise externa (ForexAnalyzer)
            ext = external_analysis(symbol, window)
            external_ok = True
            ext_sl = None
            ext_tp = None
            ext_conf = None
            ext_sig = None
            if ext:
                ext_sig = ext.get("signal")
                ext_conf = ext.get("confidence", 0.0)
                ext_sl = ext.get("stop_loss_pips")
                ext_tp = ext.get("take_profit_pips")
                try:
                    buy_set = {"BUY", "STRONG_BUY"}
                    sell_set = {"SELL", "STRONG_SELL"}
                    if signal == "BUY" and (str(ext_sig) not in buy_set):
                        external_ok = False
                    if signal == "SELL" and (str(ext_sig) not in sell_set):
                        external_ok = False
                except Exception:
                    external_ok = True
            if not external_ok:
                continue
            # Stop/take baseados em ATR
            base_sl_pips = atr_pips(symbol, candles[: i + 1], period=14)
            tp_pips = base_sl_pips * 2.0
            # Misturar sugestões externas se existirem
            if isinstance(ext_sl, (int, float)) and ext_sl > 0:
                base_sl_pips = max(base_sl_pips, ext_sl)
            if isinstance(ext_tp, (int, float)) and ext_tp > 0:
                tp_pips = max(tp_pips, ext_tp)
            lot = local_portfolio.position_size(symbol, base_sl_pips)

            pos = Position(
                symbol=symbol,
                side="LONG" if signal == "BUY" else "SHORT",
                entry_price=cur_price,
                lot_size=lot,
                stop_loss_pips=base_sl_pips,
                take_profit_pips=tp_pips,
                open_time=candles[i].timestamp,
            )
            local_portfolio.register_open(pos)

    # Close remaining positions at last price
    last_price = candles[-1].close
    for pos in list(local_portfolio.open_positions):
        move = (last_price - pos.entry_price)
        pips = pips_from_price_move(symbol, move)
        if pos.side == "SHORT":
            pips *= -1
        pos.pnl_pips = pips
        pos.pnl_value = pips * pip_value_per_lot(symbol) * pos.lot_size
        pos.close_time = candles[-1].timestamp
        pos.close_price = last_price
        pos.close_reason = "EOD"
        trades.append(pos)
        local_portfolio.register_close(pos)
        equity += pos.pnl_value

    total_return = (equity - portfolio.balance) / portfolio.balance

    def _ser(t: Position) -> Dict:
        d = asdict(t)
        # serializar datetimes
        d["open_time"] = t.open_time.isoformat()
        d["close_time"] = t.close_time.isoformat() if t.close_time else None
        return d

    return {
        "symbol": symbol,
        "strategy": strategy_name,
        "trades": [_ser(t) for t in trades],
        "num_trades": len(trades),
        "equity_final": equity,
        "return_pct": total_return * 100,
        "max_drawdown_pct": max_drawdown * 100,
    }


def run_forex_backtest(days: int = 60) -> Dict:
    strategies = list(STRATEGIES.keys())
    portfolio = RiskPortfolio(balance=10_000.0, risk_per_trade=0.02, max_portfolio_risk=0.10)

    all_data: Dict[str, List[Candle]] = {pair: generate_mock_forex_data(pair, days) for pair in FOREX_PAIRS}

    results: Dict[str, Dict[str, Dict]] = {s: {} for s in strategies}
    best_overall = {"strategy": None, "symbol": None, "return_pct": -1e9}

    # Backtest por estratégia e par
    for strat in strategies:
        for pair, candles in all_data.items():
            res = simulate_backtest_for_symbol(pair, candles, strat, portfolio)
            results[strat][pair] = res
            if res["return_pct"] > best_overall["return_pct"]:
                best_overall = {"strategy": strat, "symbol": pair, "return_pct": res["return_pct"]}

    # Melhor ativo por estratégia
    best_per_strategy = {}
    for strat in strategies:
        best_pair = max(results[strat].values(), key=lambda r: r["return_pct"])
        best_per_strategy[strat] = {"symbol": best_pair["symbol"], "return_pct": best_pair["return_pct"], "num_trades": best_pair["num_trades"]}

    # Relatório consolidado
    report = {
        "timestamp": datetime.now().isoformat(),
        "period_days": days,
        "account_balance": portfolio.balance,
        "risk_per_trade": portfolio.risk_per_trade,
        "max_portfolio_risk": portfolio.max_portfolio_risk,
        "best_overall": best_overall,
        "best_per_strategy": best_per_strategy,
        "results": results,
    }

    # Persistir
    Path("reports").mkdir(exist_ok=True)
    fname = Path("reports") / f"forex_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)

    # Saída legível
    print("\n============================================================")
    print("📋 RELATÓRIO FINAL DO BACKTEST FOREX")
    print("============================================================")
    print(f"🏆 Melhor desempenho geral: {best_overall['strategy'].upper()} em {best_overall['symbol']} -> {best_overall['return_pct']:.2f}%")
    print("\n📊 Melhor ativo por estratégia:")
    for strat, info in best_per_strategy.items():
        print(f"  - {strat.upper()}: {info['symbol']} | Retorno: {info['return_pct']:.2f}% | Trades: {info['num_trades']}")

    print(f"\n💾 Relatório salvo em: {fname}")
    return report


def main():
    print("🎯 IA GAIN - Backtest Forex")
    print("=" * 50)
    report = run_forex_backtest(days=60)
    best = report["best_overall"]
    print(f"\n✅ Concluído. Melhor estratégia: {best['strategy']} | Ativo: {best['symbol']} | Retorno: {best['return_pct']:.2f}%")


if __name__ == "__main__":
    main()
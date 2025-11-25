#!/usr/bin/env python3
"""
IA GAIN - Multi-Asset Runner

Selects portfolio across crypto and forex, evaluates strategies, and
executes trades using AutomatedTrading (crypto) and MT5Broker (forex).

This runner uses the local ccxt stub with async methods.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
from loguru import logger

from src.data.data_collector import DataCollector
from src.analysis.decision_engine import DecisionEngine
from src.strategies.momentum import Momentum
from src.strategies.mean_reversion import MeanReversion
from src.strategies.trend_following import TrendFollowing
from src.strategy_manager import StrategyManager
from src.risk.risk_manager import RiskManager
from src.brokers.mt5_broker import MT5Broker
from src.trading.automated_trading import AutomatedTrading, TradingSignal


def load_config(path: str = "config.json") -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.warning("config.json não encontrado. Usando configuração padrão mínima.")
        return {
            "system": {"max_concurrent_trades": 5},
            "risk": {
                "balance_usd": 10000.0,
                "max_portfolio_risk": 0.05,
                "max_single_trade_risk": 0.02,
                "risk_reward_ratio": 2.0,
                "use_trailing_stop": True,
                "trailing_stop_distance": 0.002,
            },
        }


async def collect_assets(data: DataCollector, crypto_limit: int = 6) -> Dict[str, pd.DataFrame]:
    assets: Dict[str, pd.DataFrame] = {}

    # Forex majors
    forex_pairs = [
        "EUR/USD",
        "GBP/USD",
        "USD/JPY",
        "USD/CHF",
        "AUD/USD",
        "USD/CAD",
    ]
    for sym in forex_pairs:
        try:
            df = await data.get_historical_data(sym, timeframe="1h", limit=300)
            if not df.empty:
                assets[sym] = df
        except Exception as e:
            logger.warning(f"Erro ao coletar dados forex para {sym}: {e}")

    # Top crypto by market cap (via CoinGecko) mapped to /USDT
    try:
        top = await data.get_top_cryptocurrencies(limit=crypto_limit)
        for item in top:
            base = item.get("symbol", "").upper()
            if not base:
                continue
            sym = f"{base}/USDT"
            try:
                df = await data.get_historical_data(sym, timeframe="1h", limit=300)
                if not df.empty:
                    assets[sym] = df
            except Exception as e:
                logger.warning(f"Erro ao coletar dados cripto para {sym}: {e}")
    except Exception as e:
        logger.warning(f"Falha ao obter lista de criptos: {e}")

    return assets


def build_strategies() -> List:
    return [
        Momentum(macd_fast=12, macd_slow=26, macd_signal=9, adx_period=14, adx_min=18.0),
        MeanReversion(rsi_period=14, low_thresh=30, high_thresh=70),
        TrendFollowing(fast=20, slow=50),
    ]


def compute_sl_tp(price: float, rr: float, sl_dist: float) -> (float, float):
    # sl_dist is fraction of price (e.g., 0.002 ~ 20 pips on majors)
    sl = price * (1.0 - sl_dist)
    tp = price * (1.0 + sl_dist * rr)
    return sl, tp


async def execute_forex(symbol: str, df: pd.DataFrame, broker: MT5Broker, risk: RiskManager) -> None:
    try:
        price = float(df["close"].iloc[-1])
        sl_dist = float(risk.cfg.trailing_stop_distance)
        sl, tp = compute_sl_tp(price, risk.cfg.risk_reward_ratio, sl_dist)
        pip_distance = abs(price - sl) * 10000.0
        pip_value = risk.estimate_pip_value_per_lot(symbol)
        max_risk = risk.get_max_risk_per_trade()
        # lot = risk / (pip_distance * pip_value)
        lot = max(0.01, round(max_risk / (pip_distance * pip_value), 2))

        check = risk.check_trade_risk(symbol, price, sl, lot)
        if not check.get("ok", False):
            logger.info(f"Forex trade bloqueado por risco: {symbol} -> {check.get('reason')}")
            return

        trade = await broker.open_order(symbol, side="buy", price=price, volume=lot, sl=sl, tp=tp)
        logger.info(f"Forex ordem aberta: {trade.id} {symbol} lot={lot} SL={sl:.5f} TP={tp:.5f}")
    except Exception as e:
        logger.error(f"Erro ao executar forex {symbol}: {e}")


async def execute_crypto(symbol: str, df: pd.DataFrame, trader: AutomatedTrading, risk: RiskManager) -> None:
    try:
        price = float(df["close"].iloc[-1])
        sl_dist = float(risk.cfg.trailing_stop_distance)
        sl, tp = compute_sl_tp(price, risk.cfg.risk_reward_ratio, sl_dist)
        # Position sizing: use 1% of balance
        balance = float(risk.cfg.balance_usd)
        position_usd = balance * risk.cfg.max_single_trade_risk

        signal = TradingSignal(
            symbol=symbol,
            signal="buy",
            confidence=0.75,
            price=price,
            stop_loss=sl,
            take_profit=tp,
            position_size=position_usd / max(price, 1e-6),
            reasoning="DecisionEngine BUY with risk-managed sizing",
        )
        await trader.execute_single_trade(signal)
    except Exception as e:
        logger.error(f"Erro ao executar cripto {symbol}: {e}")


async def main():
    cfg = load_config()
    data = DataCollector()
    await data.initialize_exchanges()

    assets = await collect_assets(data)
    if not assets:
        logger.error("Nenhum ativo coletado")
        return

    engine = DecisionEngine()
    strategies = build_strategies()
    strat_mgr = StrategyManager(strategies)
    risk = RiskManager({"risk": cfg.get("risk", {}), "system": cfg.get("system", {})})

    # Score assets and select top portfolio
    selected = engine.select_portfolio(assets, top_n=6)
    logger.info(f"Selecionados: {[r['symbol'] for r in selected]}")

    # Evaluate per asset (optional report)
    eval_report = strat_mgr.evaluate_per_asset(assets)
    try:
        Path("reports").mkdir(exist_ok=True)
        strat_mgr.save_report(eval_report)
    except Exception:
        pass

    # Setup brokers
    forex_broker = MT5Broker(cfg)
    await forex_broker.initialize()
    crypto_trader = AutomatedTrading()
    await crypto_trader.initialize_exchanges()

    # Execute trades for selected assets
    for r in selected:
        sym = r.get("symbol", "")
        df = assets.get(sym)
        if df is None or df.empty:
            continue
        if "/" in sym and sym.split("/")[1] in {"USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"}:
            await execute_forex(sym, df, forex_broker, risk)
        else:
            await execute_crypto(sym, df, crypto_trader, risk)

    # Summary
    logger.info("Execução concluída")

    # Close resources
    await data.close()
    await crypto_trader.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
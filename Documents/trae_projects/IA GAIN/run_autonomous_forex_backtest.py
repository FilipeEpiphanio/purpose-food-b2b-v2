#!/usr/bin/env python3
"""
IA GAIN - Backtest no formato Autônomo (sem CSV)
Usa CCXT para dados OHLCV, integra StrategyManager e RiskManager.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from loguru import logger

from src.forex.autonomous_backtest import AutonomousForexBacktest


def load_config(path: str = "config.json") -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "system": {
            "update_interval": 300,
            "max_concurrent_trades": 5,
        },
        "forex": {
            "timeframe": "1h",
            "default_pairs": [
                "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
                "USD/CAD", "NZD/USD", "EUR/JPY", "GBP/JPY", "EUR/GBP",
            ],
        },
        "risk": {
            "balance_usd": 10000,
            "max_portfolio_risk": 0.05,
            "max_single_trade_risk": 0.02,
            "use_trailing_stop": True,
            "trailing_stop_distance": 0.002,
        },
        "logging": {
            "file": "logs/autonomous_forex_backtest.log",
            "level": "INFO",
        },
    }


async def main():
    parser = argparse.ArgumentParser(description="Autonomous Forex Backtest")
    parser.add_argument("--days", type=int, default=60, help="Período do backtest em dias")
    parser.add_argument("--timeframe", type=str, default=None, help="Timeframe CCXT (ex.: 1h, 4h)")
    parser.add_argument("--symbols", nargs="*", default=None, help="Lista de pares (ex.: EUR/USD GBP/USD)")
    args = parser.parse_args()

    cfg = load_config()
    if args.timeframe:
        cfg.setdefault("forex", {}).update({"timeframe": args.timeframe})

    log_file = cfg.get("logging", {}).get("file", "logs/autonomous_forex_backtest.log")
    Path(os.path.dirname(log_file) or ".").mkdir(parents=True, exist_ok=True)
    logger.add(log_file, level=cfg.get("logging", {}).get("level", "INFO"))

    # Banner
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         IA GAIN - Backtest Forex Autônomo                   ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    backtest = AutonomousForexBacktest(cfg)
    report = await backtest.run(days=args.days, symbols=args.symbols)

    best = report.get("best_overall", {})
    print(f"🏁 Melhor desempenho: {best.get('symbol')} -> {best.get('return_pct', 0):.2f}%")
    print("💾 Relatório salvo em ./reports/")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
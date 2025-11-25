#!/usr/bin/env python3
"""
Teste simplificado do IA GAIN System sem dependências externas
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Testar módulos básicos
def test_basic_modules():
    """Testa módulos básicos sem dependências externas"""
    print("🧪 Testando módulos básicos...")
    
    try:
        # Testar enums e dataclasses
        from ia_gain.core.base import SignalType, TimeFrame, TradingDirection
        from ia_gain.core.base import TradingSignal, MarketData
        
        print("✅ Módulos base carregados com sucesso")
        
        # Testar criação de sinais
        signal = TradingSignal(
            asset="EURUSD",
            direction=TradingDirection.BUY,
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1050,
            confidence=0.8
        )
        
        print(f"✅ Sinal criado: {signal.asset} {signal.direction.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos módulos básicos: {e}")
        return False

def test_strategy_modules():
    """Testa módulos de estratégia"""
    print("📈 Testando módulos de estratégia...")
    
    try:
        # Testar carregamento de estratégias
        from ia_gain.strategies.trading_strategies import MeanReversionStrategy
        from ia_gain.strategies.strategy_manager import StrategyManager
        
        print("✅ Módulos de estratégia carregados")
        
        # Testar criação de estratégia
        strategy = MeanReversionStrategy()
        print(f"✅ Estratégia criada: {strategy.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos módulos de estratégia: {e}")
        return False

def test_risk_management():
    """Testa módulo de gerenciamento de risco"""
    print("🛡️ Testando gerenciamento de risco...")
    
    try:
        from ia_gain.risk.risk_management import RiskManager, RiskParameters
        
        # Testar parâmetros de risco
        params = RiskParameters(
            max_risk_per_trade=0.02,
            max_daily_risk=0.06,
            max_drawdown=0.15
        )
        
        print(f"✅ Parâmetros de risco: {params.max_risk_per_trade:.1%} por trade")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no gerenciamento de risco: {e}")
        return False

def test_autonomous_operation():
    """Testa operação autônoma"""
    print("🧠 Testando operação autônoma...")
    
    try:
        from ia_gain.core.autonomous_operation import (
            AutonomousConfiguration, LearningMode,
            LearningDataCollector, AdaptiveLearningEngine
        )
        
        # Testar configuração autônoma
        config = AutonomousConfiguration(
            learning_mode=LearningMode.HYBRID,
            adaptation_interval=3600,
            learning_rate=0.01
        )
        
        print(f"✅ Configuração autônoma: {config.learning_mode.value}")
        
        # Testar coletor de dados
        collector = LearningDataCollector()
        print(f"✅ Coletor de dados criado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na operação autônoma: {e}")
        return False

async def test_system_integration():
    """Testa integração do sistema"""
    print("🔧 Testando integração do sistema...")
    
    try:
        # Testar configuração do sistema
        from ia_gain.core.ia_gain_system import SystemConfig
        
        config = SystemConfig(
            symbols=["EURUSD", "GBPUSD"],
            timeframes=["1h", "4h"],
            risk_percentage=0.02,
            max_positions=5,
            autonomous_enabled=True,
            autonomous_learning_mode="HYBRID"
        )
        
        print(f"✅ Configuração criada: {len(config.symbols)} símbolos")
        print(f"✅ Operação autônoma: {config.autonomous_enabled}")
        print(f"✅ Modo de aprendizado: {config.autonomous_learning_mode}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração do sistema: {e}")
        return False

def test_project_structure():
    """Testa estrutura do projeto"""
    print("📁 Testando estrutura do projeto...")
    
    required_dirs = [
        "ia_gain",
        "ia_gain/core",
        "ia_gain/analysis",
        "ia_gain/strategies",
        "ia_gain/ml",
        "ia_gain/backtesting",
        "ia_gain/risk",
        "ia_gain/trading",
        "ia_gain/integration",
        "ia_gain/multi_timeframe"
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if not full_path.exists():
            missing_dirs.append(dir_path)
        else:
            print(f"✅ {dir_path}")
    
    if missing_dirs:
        print(f"❌ Diretórios faltando: {missing_dirs}")
        return False
    
    print("✅ Estrutura do projeto completa")
    return True

async def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🚀 IA GAIN SYSTEM - TESTE SIMPLIFICADO")
    print("=" * 60)
    
    # Testar estrutura
    structure_ok = test_project_structure()
    
    if not structure_ok:
        print("❌ Estrutura do projeto incompleta")
        return
    
    # Testar módulos básicos
    basic_ok = test_basic_modules()
    
    # Testar estratégias
    strategy_ok = test_strategy_modules()
    
    # Testar risco
    risk_ok = test_risk_management()
    
    # Testar operação autônoma
    autonomous_ok = test_autonomous_operation()
    
    # Testar integração
    integration_ok = await test_system_integration()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    tests = [
        ("Estrutura do Projeto", structure_ok),
        ("Módulos Básicos", basic_ok),
        ("Módulos de Estratégia", strategy_ok),
        ("Gerenciamento de Risco", risk_ok),
        ("Operação Autônoma", autonomous_ok),
        ("Integração do Sistema", integration_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema IA GAIN está funcionando!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os módulos.")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Script de teste completo para o sistema IA GAIN
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from ia_gain.core.ia_gain_system import IAGainSystem, SystemConfig
from ia_gain.core.autonomous_operation import AutonomousConfiguration


async def test_ia_gain_system():
    """Testa o sistema IA GAIN completo"""
    print("🚀 Iniciando teste do IA GAIN System...")
    
    try:
        # Configuração do sistema
        config = SystemConfig(
            symbols=["EURUSD", "GBPUSD", "USDJPY"],
            timeframes=["1h", "4h", "1d"],
            risk_percentage=0.02,
            max_positions=5,
            
            # Análises habilitadas
            technical_enabled=True,
            fundamental_enabled=True,
            momentum_enabled=True,
            pattern_enabled=True,
            
            # Estratégias
            strategies_enabled=["mean_reversion", "trend_following", "momentum"],
            strategy_combination=True,
            
            # ML
            ml_enabled=True,
            ml_models=["random_forest", "gradient_boosting"],
            
            # Backtesting
            backtesting_enabled=True,
            backtest_period_days=30,
            
            # Risk Management
            risk_enabled=True,
            max_drawdown=0.10,
            max_daily_risk=0.05,
            
            # Integration
            mt5_enabled=False,  # Desabilitar para teste
            auto_trading=True,
            copy_trading=False,
            
            # Autonomous Operation
            autonomous_enabled=True,
            autonomous_learning_mode="HYBRID",
            autonomous_adaptation_interval=1800,  # 30 minutos
            autonomous_learning_rate=0.01,
            
            # System
            log_level="INFO"
        )
        
        # Criar sistema
        system = IAGainSystem(config)
        
        # Testar inicialização
        print("📊 Inicializando componentes...")
        init_success = await system.initialize()
        
        if not init_success:
            print("❌ Falha na inicialização do sistema")
            return False
        
        print("✅ Sistema inicializado com sucesso")
        
        # Testar backtesting
        print("📈 Executando backtesting...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # 7 dias de teste
        
        backtest_results = await system.run_backtest(start_date, end_date)
        
        if backtest_results:
            print(f"✅ Backtesting concluído: {len(backtest_results)} resultados")
            if 'summary' in backtest_results:
                summary = backtest_results['summary']
                print(f"📊 Retorno total: {summary.get('total_return', 0):.2%}")
                print(f"📊 Sharpe ratio: {summary.get('sharpe_ratio', 0):.2f}")
                print(f"📊 Máximo drawdown: {summary.get('max_drawdown', 0):.2%}")
        else:
            print("⚠️  Backtesting não retornou resultados")
        
        # Testar análise de mercado
        print("🔍 Testando análise de mercado...")
        
        # Simular dados de mercado
        test_data = {
            'EURUSD_1h': {
                'close': [1.1000, 1.1005, 1.1010, 1.1008, 1.1012],
                'open': [1.0998, 1.1000, 1.1005, 1.1010, 1.1008],
                'high': [1.1002, 1.1007, 1.1012, 1.1014, 1.1015],
                'low': [1.0995, 1.0998, 1.1003, 1.1006, 1.1005],
                'volume': [1000, 1200, 1100, 1300, 1250]
            }
        }
        
        # Forçar dados para teste
        system.current_data = test_data
        
        # Executar análise
        analysis = await system._analyze_market('EURUSD_1h', test_data['EURUSD_1h'])
        
        if analysis:
            print("✅ Análise de mercado executada com sucesso")
            print(f"📊 Análises disponíveis: {list(analysis.keys())}")
            
            # Verificar análise multi-timeframe
            if 'multi_timeframe' in analysis:
                print("✅ Análise multi-timeframe disponível")
            
            # Verificar feedback autônomo
            if 'autonomous_feedback' in analysis:
                print("✅ Feedback autônomo disponível")
        else:
            print("⚠️  Análise de mercado não retornou resultados")
        
        # Testar geração de decisões
        print("🎯 Testando geração de decisões de trading...")
        
        decisions = await system._generate_trading_decisions()
        
        if decisions:
            print(f"✅ {len(decisions)} decisões de trading geradas")
            for i, decision in enumerate(decisions[:3]):  # Mostrar primeiras 3
                print(f"📝 Decisão {i+1}: {decision.symbol} {decision.direction} "
                      f"(confiança: {decision.confidence:.2f})")
        else:
            print("⚠️  Nenhuma decisão de trading gerada")
        
        # Testar sistema de trading
        print("💰 Testando sistema de trading...")
        
        if system.trading_system:
            # Verificar se o sistema de trading está funcionando
            trading_status = system.trading_system.get_status()
            print(f"✅ Sistema de trading: {trading_status}")
            
            # Verificar operações autônomas
            if system.autonomous_manager:
                autonomous_status = system.autonomous_manager.get_status()
                print(f"✅ Operação autônoma: {autonomous_status}")
                
                metrics = system.autonomous_manager.get_performance_metrics()
                if metrics:
                    print(f"📊 Dados coletados: {metrics.get('total_data_points', 0)}")
                    print(f"📊 Taxa de aprendizado: {metrics.get('learning_rate', 0)}")
        
        # Testar salvamento de configuração
        print("💾 Testando salvamento de configuração...")
        
        config_file = "test_config.json"
        await system.save_config(config_file)
        
        if os.path.exists(config_file):
            print(f"✅ Configuração salva: {config_file}")
            os.remove(config_file)  # Limpar arquivo de teste
        else:
            print("⚠️  Falha ao salvar configuração")
        
        # Obter status do sistema
        print("📋 Status do sistema:")
        status = system.get_system_status()
        
        print(f"🔄 Sistema rodando: {status['running']}")
        print(f"📅 Timestamp: {status['timestamp']}")
        print(f"📊 Símbolos ativos: {len(status['active_symbols'])}")
        print(f"📝 Decisões recentes: {status['recent_decisions']}")
        
        if 'performance_metrics' in status and status['performance_metrics']:
            metrics = status['performance_metrics']
            print(f"📈 Cache de análise: {metrics.get('analysis_cache_size', 0)} itens")
            
            if 'autonomous_metrics' in metrics:
                auto_metrics = metrics['autonomous_metrics']
                print(f"🧠 Operação autônoma: {auto_metrics.get('status', 'unknown')}")
        
        print("\n🎉 Teste do IA GAIN System concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_autonomous_operation():
    """Testa especificamente a operação autônoma"""
    print("🧠 Testando sistema de operação autônoma...")
    
    try:
        # Criar configuração
        config = SystemConfig(
            symbols=["EURUSD"],
            timeframes=["1h"],
            autonomous_enabled=True,
            autonomous_learning_mode="REINFORCEMENT",
            autonomous_adaptation_interval=300,  # 5 minutos
            mt5_enabled=False
        )
        
        system = IAGainSystem(config)
        await system.initialize()
        
        if not system.autonomous_manager:
            print("❌ Gerenciador autônomo não inicializado")
            return False
        
        # Testar coleta de dados
        print("📊 Testando coleta de dados de aprendizado...")
        
        test_data = {
            'symbol': 'EURUSD',
            'timeframe': '1h',
            'direction': 'buy',
            'confidence': 0.75,
            'entry_price': 1.1000,
            'stop_loss': 1.0950,
            'take_profit': 1.1050,
            'position_size': 0.1,
            'strategy': 'mean_reversion',
            'analysis_scores': {
                'technical': 0.8,
                'momentum': 0.7,
                'patterns': 0.6
            },
            'metadata': {'test': True},
            'timestamp': datetime.now()
        }
        
        await system.autonomous_manager.collect_learning_data(test_data)
        print("✅ Dados de aprendizado coletados")
        
        # Testar feedback de mercado
        print("🎯 Testando feedback de mercado...")
        
        market_analysis = {
            'technical': {'score': 0.8},
            'momentum': {'score': 0.7},
            'patterns': [{'confidence': 0.6}]
        }
        
        feedback = system.autonomous_manager.get_market_feedback(
            'EURUSD', '1h', market_analysis
        )
        
        if feedback:
            print(f"✅ Feedback gerado: {feedback}")
        else:
            print("⚠️  Sem feedback gerado")
        
        # Testar adaptação
        print("🔄 Testando adaptação...")
        
        adaptation_result = await system.autonomous_manager.adapt_strategies()
        
        if adaptation_result:
            print(f"✅ Adaptação executada: {adaptation_result}")
        else:
            print("⚠️  Adaptação não retornou resultados")
        
        print("✅ Teste de operação autônoma concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste autônomo: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🚀 IA GAIN SYSTEM - TESTE COMPLETO")
    print("=" * 60)
    
    # Teste do sistema principal
    success = await test_ia_gain_system()
    
    if success:
        print("\n" + "=" * 60)
        print("🧠 TESTE DE OPERAÇÃO AUTÔNOMA")
        print("=" * 60)
        
        # Teste específico da operação autônoma
        await test_autonomous_operation()
    
    print("\n" + "=" * 60)
    print("🏁 Testes finalizados")
    print("=" * 60)


if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())
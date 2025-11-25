#!/usr/bin/env python3
"""
Teste de conexão MetaTrader 5 - Versão Simples
"""

import sys
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def testar_conexao_mt5():
    """Testa conexão com MetaTrader 5"""
    
    print("🚀 Testando conexão MetaTrader 5")
    print("=" * 40)
    
    try:
        # Importar MT5
        import MetaTrader5 as mt5
        logger.info("✅ Biblioteca MetaTrader5 importada com sucesso")
        
        # Tentar inicializar
        logger.info("Inicializando MT5...")
        if not mt5.initialize():
            error = mt5.last_error()
            logger.error(f"❌ Falha ao inicializar MT5: {error}")
            return False
        
        logger.info("✅ MT5 inicializado com sucesso")
        
        # Obter informações da conta (sem login)
        account_info = mt5.account_info()
        if account_info:
            print(f"\n📊 Informações da conta:")
            print(f"  Conta: {account_info.login}")
            print(f"  Nome: {account_info.name}")
            print(f"  Servidor: {account_info.server}")
            print(f"  Saldo: ${account_info.balance:.2f}")
            print(f"  Equity: ${account_info.equity:.2f}")
            print(f"  Moeda: {account_info.currency}")
            print(f"  Alavancagem: 1:{account_info.leverage}")
        else:
            logger.warning("⚠️  Sem informações de conta (pode estar desconectado)")
        
        # Testar terminal
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"\n🏢 Informações do terminal:")
            print(f"  Nome: {terminal_info.name}")
            print(f"  Empresa: {terminal_info.company}")
            print(f"  Versão: {getattr(terminal_info, 'version', 'N/A')}")
            print(f"  Path: {terminal_info.path}")
        
        # Obter símbolos disponíveis
        symbols = mt5.symbols_get()
        if symbols:
            print(f"\n📈 Símbolos disponíveis: {len(symbols)}")
            
            # Mostrar alguns símbolos populares
            forex_pairs = [s for s in symbols if 'USD' in s.name and len(s.name) == 6]
            if forex_pairs:
                print("  Principais pares Forex:")
                for pair in forex_pairs[:5]:
                    print(f"    - {pair.name}: {pair.description}")
        
        # Testar preços
        print(f"\n💰 Testando preços:")
        test_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        
        for symbol in test_symbols:
            # Selecionar símbolo
            if mt5.symbol_select(symbol, True):
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"  {symbol}: Bid={tick.bid:.5f} Ask={tick.ask:.5f} Spread={int((tick.ask-tick.bid)*100000)}pts")
                else:
                    print(f"  {symbol}: Sem dados de tick")
            else:
                print(f"  {symbol}: Não disponível")
        
        # Obter dados históricos
        print(f"\n📊 Testando dados históricos:")
        rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H1, 0, 5)
        
        if rates is not None and len(rates) > 0:
            print(f"  ✅ Dados históricos obtidos: {len(rates)} candles H1")
            
            # Mostrar último candle
            last_candle = rates[-1]
            candle_time = datetime.fromtimestamp(last_candle['time'])
            print(f"  Último candle ({candle_time}):")
            print(f"    Open: {last_candle['open']:.5f}")
            print(f"    High: {last_candle['high']:.5f}")
            print(f"    Low: {last_candle['low']:.5f}")
            print(f"    Close: {last_candle['close']:.5f}")
            print(f"    Volume: {last_candle['tick_volume']}")
        else:
            print("  ❌ Falha ao obter dados históricos")
        
        # Obter posições
        print(f"\n📍 Posições abertas:")
        positions = mt5.positions_get()
        if positions:
            print(f"  Encontradas {len(positions)} posições:")
            for pos in positions:
                pos_type = "COMPRA" if pos.type == mt5.ORDER_TYPE_BUY else "VENDA"
                profit_color = "🟢" if pos.profit >= 0 else "🔴"
                print(f"    {profit_color} {pos.symbol} {pos_type} vol={pos.volume:.2f} profit=${pos.profit:.2f}")
        else:
            print("  Nenhuma posição aberta")
        
        # Desconectar
        mt5.shutdown()
        print(f"\n✅ Teste concluído com sucesso!")
        print(f"✅ MetaTrader 5 está funcionando corretamente")
        print(f"✅ Pronto para integração com IA GAIN")
        
        return True
        
    except ImportError:
        logger.error("❌ Biblioteca MetaTrader5 não instalada")
        logger.info("Instale com: pip install MetaTrader5")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return False

def main():
    """Função principal"""
    
    # Testar conexão
    sucesso = testar_conexao_mt5()
    
    if sucesso:
        print(f"\n🎉 Sistema pronto para conexão MT5!")
        print(f"📋 Próximos passos:")
        print(f"   1. Configure suas credenciais MT5 em config_mt5.json")
        print(f"   2. Execute: python conectar_mt5.py")
        print(f"   3. Ou use o sistema IA GAIN com MT5 habilitado")
    else:
        print(f"\n❌ Problema detectado na conexão MT5")
        print(f"🔧 Verifique:")
        print(f"   - MetaTrader 5 está instalado")
        print(f"   - Terminal MT5 está aberto")
        print(f"   - Biblioteca instalada: pip install MetaTrader5")

if __name__ == "__main__":
    main()
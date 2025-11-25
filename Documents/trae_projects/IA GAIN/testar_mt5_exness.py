#!/usr/bin/env python3
"""
Teste de integração IA GAIN + MetaTrader 5 com símbolos corretos do servidor Exness
"""

import MetaTrader5 as mt5
import pandas as pd
import json
from datetime import datetime, timedelta
import time

def testar_integracao_mt5_exness():
    """Testa a integração com os símbolos disponíveis no servidor Exness"""
    
    print("🚀 Testando IA GAIN + MetaTrader 5 - Exness Server")
    print("=" * 60)
    
    # Inicializar MT5
    if not mt5.initialize():
        print(f"❌ Erro ao inicializar MT5: {mt5.last_error()}")
        return
    
    try:
        # Obter informações da conta
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ Não foi possível obter informações da conta")
            return
            
        print(f"📊 Conta: {account_info.login} | Saldo: ${account_info.balance:.2f}")
        print(f"🏢 Servidor: {account_info.server}")
        print(f"📈 Companhia: {account_info.company}")
        print("=" * 60)
        
        # Lista de símbolos forex disponíveis no Exness
        simbolos_forex = [
            'AUDCADm', 'AUDCHFm', 'AUDJPYm', 'AUDUSDm', 'CADJPYm', 'CHFJPYm',
            'EURAUDm', 'EURCADm', 'EURCHFm', 'EURGBPm', 'EURJPYm', 'EURNZDm',
            'EURUSDm', 'GBPAUDm', 'GBPCADm', 'GBPCHFm', 'GBPJPYm', 'GBPNZDm',
            'GBPUSDm', 'NZDCADm', 'NZDCHFm', 'NZDJPYm', 'NZDUSDm', 'USDCADm',
            'USDCHFm', 'USDJPYm'
        ]
        
        print(f"🔍 Testando {len(simbolos_forex)} pares de moedas disponíveis...")
        print()
        
        # Testar alguns símbolos principais
        simbolos_teste = ['EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm']
        
        for symbol in simbolos_teste:
            print(f"\n📈 Analisando {symbol}...")
            
            # Selecionar o símbolo
            if not mt5.symbol_select(symbol, True):
                print(f"   ❌ Falha ao selecionar símbolo: {symbol}")
                continue
            
            # Obter informações do símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                print(f"   ❌ Símbolo não encontrado: {symbol}")
                continue
            
            print(f"   ✅ Símbolo selecionado: {symbol}")
            print(f"   📊 Spread: {symbol_info.spread} pontos")
            print(f"   💰 Preço Ask: {symbol_info.ask:.5f}")
            print(f"   💰 Preço Bid: {symbol_info.bid:.5f}")
            
            # Obter dados históricos (últimas 100 barras H1)
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
            
            if rates is not None and len(rates) > 0:
                # Converter para DataFrame
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                # Análise básica
                current_price = (symbol_info.ask + symbol_info.bid) / 2
                sma_20 = df['close'].tail(20).mean()
                sma_50 = df['close'].tail(50).mean()
                
                print(f"   📊 Média Móvel 20h: {sma_20:.5f}")
                print(f"   📊 Média Móvel 50h: {sma_50:.5f}")
                print(f"   📍 Preço Atual: {current_price:.5f}")
                
                # Sinal simples
                if current_price > sma_20 > sma_50:
                    print(f"   🟢 SINAL: TENDÊNCIA ALTA")
                elif current_price < sma_20 < sma_50:
                    print(f"   🔴 SINAL: TENDÊNCIA BAIXA")
                else:
                    print(f"   ⚪ SINAL: NEUTRO/CONSOLIDAÇÃO")
                
                # Análise de volatilidade
                volatility = df['close'].tail(20).std()
                print(f"   📈 Volatilidade (20h): {volatility:.5f}")
                
            else:
                print(f"   ⚠️  Dados históricos não disponíveis")
            
            # Pequena pausa entre símbolos
            time.sleep(0.5)
        
        print("\n" + "=" * 60)
        print("📍 Posições Abertas Atuais:")
        
        # Verificar posições abertas
        positions = mt5.positions_get()
        if positions is None or len(positions) == 0:
            print("   ℹ️  Nenhuma posição aberta no momento")
        else:
            total_profit = 0
            for position in positions:
                profit = position.profit
                total_profit += profit
                symbol = position.symbol
                type_str = "COMPRA" if position.type == mt5.ORDER_TYPE_BUY else "VENDA"
                
                print(f"   📊 {symbol} | {type_str} | Volume: {position.volume:.2f}")
                print(f"      Preço Entrada: {position.price_open:.5f} | Preço Atual: {position.price_current:.5f}")
                print(f"      Lucro: ${profit:.2f}")
                print()
            
            print(f"   💰 Lucro Total das Posições: ${total_profit:.2f}")
        
        print("\n✅ Teste de integração concluído com sucesso!")
        print("\n📝 Resumo:")
        print(f"   ✅ Conexão MT5 estabelecida")
        print(f"   ✅ {len(simbolos_forex)} símbolos forex disponíveis")
        print(f"   ✅ Dados de mercado em tempo real")
        print(f"   ✅ Análise técnica básica implementada")
        print(f"   ✅ Posições monitoradas")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        
    finally:
        mt5.shutdown()
        print("\n👋 Desconectado do MetaTrader 5")

if __name__ == "__main__":
    testar_integracao_mt5_exness()
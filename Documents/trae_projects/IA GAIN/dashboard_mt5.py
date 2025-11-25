#!/usr/bin/env python3
"""
Dashboard de Monitoramento em Tempo Real - IA GAIN + MetaTrader 5
Interface interativa para monitoramento de trades e análise de mercado
"""

import MetaTrader5 as mt5
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os

class MT5Dashboard:
    def __init__(self):
        self.symbols = [
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm',
            'USDCADm', 'NZDUSDm', 'EURJPYm', 'GBPJPYm', 'AUDJPYm'
        ]
        self.running = False
        self.update_interval = 5  # segundos
        
    def clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def connect_mt5(self):
        """Conecta ao MetaTrader 5"""
        if not mt5.initialize():
            print(f"❌ Erro ao conectar MT5: {mt5.last_error()}")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ Não foi possível obter informações da conta")
            return False
            
        self.account_info = account_info
        return True
    
    def get_market_data(self, symbol):
        """Obtém dados de mercado para um símbolo"""
        # Selecionar símbolo
        if not mt5.symbol_select(symbol, True):
            return None
        
        # Obter informações do símbolo
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return None
        
        # Obter dados históricos (últimas 50 barras M5)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 50)
        if rates is None or len(rates) == 0:
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Análise técnica simples
        current_price = (symbol_info.ask + symbol_info.bid) / 2
        sma_10 = df['close'].tail(10).mean()
        sma_20 = df['close'].tail(20).mean()
        
        # Volatilidade
        volatility = df['close'].tail(20).std()
        
        # Sinal
        if current_price > sma_10 > sma_20:
            signal = "🟢 COMPRA"
            signal_color = "green"
        elif current_price < sma_10 < sma_20:
            signal = "🔴 VENDA"
            signal_color = "red"
        else:
            signal = "⚪ NEUTRO"
            signal_color = "yellow"
        
        return {
            'symbol': symbol,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'spread': symbol_info.spread,
            'current_price': current_price,
            'sma_10': sma_10,
            'sma_20': sma_20,
            'volatility': volatility,
            'signal': signal,
            'signal_color': signal_color,
            'last_update': datetime.now()
        }
    
    def get_account_summary(self):
        """Obtém resumo da conta"""
        account_info = mt5.account_info()
        if account_info is None:
            return None
        
        positions = mt5.positions_get()
        total_positions = len(positions) if positions else 0
        
        total_profit = 0
        if positions:
            for pos in positions:
                total_profit += pos.profit
        
        return {
            'login': account_info.login,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'leverage': account_info.leverage,
            'total_positions': total_positions,
            'total_profit': total_profit,
            'server': account_info.server
        }
    
    def get_positions_summary(self):
        """Obtém resumo das posições abertas"""
        positions = mt5.positions_get()
        if positions is None or len(positions) == 0:
            return []
        
        positions_summary = []
        for pos in positions:
            positions_summary.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'COMPRA' if pos.type == mt5.ORDER_TYPE_BUY else 'VENDA',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'sl': pos.sl if pos.sl != 0 else 'N/A',
                'tp': pos.tp if pos.tp != 0 else 'N/A'
            })
        
        return positions_summary
    
    def display_header(self):
        """Exibe cabeçalho do dashboard"""
        print("🚀 IA GAIN + MetaTrader 5 - Dashboard de Monitoramento")
        print("=" * 80)
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | "
              f"🔄 Atualização a cada {self.update_interval}s | "
              f"📊 Modo: {'🟢 ATIVO' if self.running else '🔴 PAUSADO'}")
        print("=" * 80)
    
    def display_account_info(self, account_summary):
        """Exibe informações da conta"""
        if account_summary is None:
            print("❌ Informações da conta não disponíveis")
            return
        
        print(f"💼 Conta: {account_summary['login']} | "
              f"🏢 Servidor: {account_summary['server']}")
        print(f"💰 Saldo: ${account_summary['balance']:,.2f} | "
              f"📊 Equidade: ${account_summary['equity']:,.2f} | "
              f"📉 Margem Livre: ${account_summary['free_margin']:,.2f}")
        print(f"📈 Alavancagem: 1:{account_summary['leverage']} | "
              f"📍 Posições: {account_summary['total_positions']} | "
              f"💵 Lucro Total: ${account_summary['total_profit']:,.2f}")
        print("-" * 80)
    
    def display_market_overview(self, market_data_list):
        """Exibe visão geral do mercado"""
        print("📈 ANÁLISE DE MERCADO EM TEMPO REAL:")
        print("-" * 80)
        
        if not market_data_list:
            print("❌ Dados de mercado não disponíveis")
            return
        
        # Ordenar por sinal (compra primeiro, depois venda, depois neutro)
        market_data_list.sort(key=lambda x: 0 if 'COMPRA' in x['signal'] else (1 if 'VENDA' in x['signal'] else 2))
        
        for data in market_data_list[:10]:  # Mostrar apenas 10 primeiros
            print(f"{data['signal']} {data['symbol']:8} | "
                  f"Bid: {data['bid']:.5f} | "
                  f"Ask: {data['ask']:.5f} | "
                  f"Spread: {data['spread']} | "
                  f"Vol: {data['volatility']:.5f}")
        
        print("-" * 80)
    
    def display_positions(self, positions):
        """Exibe posições abertas"""
        if not positions:
            print("📍 Nenhuma posição aberta no momento")
            return
        
        print("📍 POSIÇÕES ABERTAS:")
        print("-" * 80)
        
        for pos in positions:
            profit_color = "🟢" if pos['profit'] >= 0 else "🔴"
            print(f"{profit_color} {pos['symbol']:8} | {pos['type']:6} | "
                  f"Vol: {pos['volume']:.2f} | "
                  f"Entrada: {pos['price_open']:.5f} | "
                  f"Atual: {pos['price_current']:.5f} | "
                  f"Lucro: ${pos['profit']:,.2f}")
        
        total_profit = sum(pos['profit'] for pos in positions)
        profit_color = "🟢" if total_profit >= 0 else "🔴"
        print(f"\n{profit_color} Lucro Total das Posições: ${total_profit:,.2f}")
        print("-" * 80)
    
    def run_dashboard(self):
        """Executa o dashboard"""
        if not self.connect_mt5():
            return
        
        self.running = True
        
        try:
            while self.running:
                self.clear_screen()
                
                # Obter dados
                account_summary = self.get_account_summary()
                positions = self.get_positions_summary()
                
                # Obter dados de mercado para símbolos selecionados
                market_data_list = []
                for symbol in self.symbols:
                    data = self.get_market_data(symbol)
                    if data:
                        market_data_list.append(data)
                
                # Exibir dashboard
                self.display_header()
                self.display_account_info(account_summary)
                self.display_market_overview(market_data_list)
                self.display_positions(positions)
                
                print(f"\n⏰ Próxima atualização em {self.update_interval} segundos...")
                print("Pressione Ctrl+C para sair")
                
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            self.running = False
            print("\n\n🛑 Dashboard interrompido pelo usuário")
            
        finally:
            mt5.shutdown()
            print("👋 Desconectado do MetaTrader 5")

def main():
    """Função principal"""
    dashboard = MT5Dashboard()
    
    print("🚀 Iniciando Dashboard IA GAIN + MetaTrader 5")
    print("Este dashboard irá monitorar:")
    print("  ✅ Saldos e informações da conta")
    print("  ✅ Análise técnica de 10 pares de moedas")
    print("  ✅ Posições abertas em tempo real")
    print("  ✅ Sinais de compra/venda baseados em médias móveis")
    print()
    
    input("Pressione Enter para iniciar o dashboard...")
    
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
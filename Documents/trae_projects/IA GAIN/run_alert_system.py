#!/usr/bin/env python3
"""
IA GAIN - Alert System Executor
Script executável para sistema de alertas e notificações
"""

import os
import sys
import argparse
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime

def setup_environment():
    """Configurar ambiente e paths"""
    # Adicionar o diretório src ao path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('alert_system.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = [
        'python-telegram-bot', 'requests', 'python-dotenv', 'smtplib', 'email-validator'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'python-telegram-bot':
                import telegram
            elif package == 'email-validator':
                import email_validator
            elif package == 'smtplib':
                # smtplib é built-in, não precisa verificar
                continue
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install python-telegram-bot requests python-dotenv email-validator")
        return False
    
    return True

def check_config():
    """Verificar configuração de alertas"""
    config_file = 'config.json'
    
    if not os.path.exists(config_file):
        print("❌ Arquivo config.json não encontrado")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        alerts_config = config.get('alerts', {})
        
        # Verificar configurações de Telegram
        telegram_config = alerts_config.get('telegram', {})
        if telegram_config.get('enabled', False):
            if not telegram_config.get('bot_token') or not telegram_config.get('chat_id'):
                print("⚠️  Configuração do Telegram incompleta")
                return False
        
        # Verificar configurações de Email
        email_config = alerts_config.get('email', {})
        if email_config.get('enabled', False):
            if not email_config.get('smtp_server') or not email_config.get('smtp_port'):
                print("⚠️  Configuração de Email incompleta")
                return False
        
        print("✅ Configuração de alertas verificada")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

async def start_alert_system():
    """Iniciar sistema de alertas"""
    try:
        from alerts.alert_system import AlertSystem
        
        print("🚀 Iniciando sistema de alertas...")
        
        # Criar sistema de alertas
        alert_system = AlertSystem()
        
        # Iniciar monitoramento
        print("📊 Monitorando mercado...")
        await alert_system.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n⚠️ Sistema de alertas interrompido")
    except Exception as e:
        print(f"❌ Erro no sistema de alertas: {e}")
        raise

def send_test_alert(alert_type='all'):
    """Enviar alerta de teste"""
    try:
        from alerts.alert_system import AlertSystem
        
        print(f"🧪 Enviando alerta de teste ({alert_type})...")
        
        alert_system = AlertSystem()
        
        # Preparar mensagem de teste
        test_message = f"""
🧪 ALERTA DE TESTE - IA GAIN

📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Tipo: Teste de Sistema
✅ Status: Sistema funcionando corretamente

Este é um alerta de teste para verificar o funcionamento do sistema.
        """.strip()
        
        # Enviar alerta
        if alert_type == 'telegram':
            result = alert_system.send_telegram_alert(test_message)
        elif alert_type == 'email':
            result = alert_system.send_email_alert('Teste - IA GAIN', test_message)
        elif alert_type == 'all':
            result = alert_system.send_alert(test_message)
        else:
            print(f"❌ Tipo de alerta inválido: {alert_type}")
            return False
        
        if result:
            print(f"✅ Alerta de teste enviado com sucesso ({alert_type})")
        else:
            print(f"❌ Falha ao enviar alerta de teste ({alert_type})")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao enviar alerta de teste: {e}")
        return False

def create_price_alert(symbol, price_target, condition='above'):
    """Criar alerta de preço"""
    try:
        from alerts.alert_system import AlertSystem
        
        print(f"🎯 Criando alerta de preço para {symbol}...")
        print(f"Condição: {'Acima' if condition == 'above' else 'Abaixo'} de {price_target}")
        
        alert_system = AlertSystem()
        
        # Criar alerta
        alert_id = alert_system.create_price_alert(symbol, price_target, condition)
        
        if alert_id:
            print(f"✅ Alerta criado com ID: {alert_id}")
            print(f"📝 O alerta será disparado quando {symbol} ficar {condition} de {price_target}")
        else:
            print("❌ Falha ao criar alerta")
        
        return alert_id
        
    except Exception as e:
        print(f"❌ Erro ao criar alerta: {e}")
        return None

def list_active_alerts():
    """Listar alertas ativos"""
    try:
        from alerts.alert_system import AlertSystem
        
        print("📋 Listando alertas ativos...")
        
        alert_system = AlertSystem()
        alerts = alert_system.get_active_alerts()
        
        if not alerts:
            print("ℹ️  Nenhum alerta ativo encontrado")
            return
        
        print(f"\n🚨 {len(alerts)} alerta(s) ativo(s):")
        print("-" * 80)
        
        for alert in alerts:
            print(f"ID: {alert.get('id', 'N/A')}")
            print(f"Tipo: {alert.get('type', 'N/A')}")
            print(f"Símbolo: {alert.get('symbol', 'N/A')}")
            print(f"Condição: {alert.get('condition', 'N/A')}")
            print(f"Valor: {alert.get('target_value', 'N/A')}")
            print(f"Status: {'Ativo' if alert.get('active', False) else 'Inativo'}")
            print(f"Criado: {alert.get('created_at', 'N/A')}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Erro ao listar alertas: {e}")

def delete_alert(alert_id):
    """Deletar alerta"""
    try:
        from alerts.alert_system import AlertSystem
        
        print(f"🗑️  Deletando alerta {alert_id}...")
        
        alert_system = AlertSystem()
        
        if alert_system.delete_alert(alert_id):
            print(f"✅ Alerta {alert_id} deletado com sucesso")
        else:
            print(f"❌ Falha ao deletar alerta {alert_id}")
        
    except Exception as e:
        print(f"❌ Erro ao deletar alerta: {e}")

def monitor_portfolio():
    """Monitorar portfólio e enviar alertas"""
    try:
        from alerts.alert_system import AlertSystem
        
        print("💼 Monitorando portfólio...")
        
        alert_system = AlertSystem()
        
        # Obter informações do portfólio
        portfolio_alerts = alert_system.check_portfolio_alerts()
        
        if portfolio_alerts:
            print(f"🚨 {len(portfolio_alerts)} alerta(s) de portfólio disparado(s)")
            
            for alert in portfolio_alerts:
                print(f"📊 {alert['symbol']}: {alert['message']}")
        else:
            print("ℹ️  Nenhum alerta de portfólio disparado")
        
        return portfolio_alerts
        
    except Exception as e:
        print(f"❌ Erro ao monitorar portfólio: {e}")
        return []

def send_daily_report():
    """Enviar relatório diário"""
    try:
        from alerts.alert_system import AlertSystem
        
        print("📊 Gerando relatório diário...")
        
        alert_system = AlertSystem()
        
        # Gerar relatório
        report = alert_system.generate_daily_report()
        
        # Enviar relatório
        if alert_system.send_alert(report):
            print("✅ Relatório diário enviado com sucesso")
        else:
            print("❌ Falha ao enviar relatório diário")
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

async def main_async():
    """Função principal assíncrona"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - Alert System Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_alert_system.py --start                    # Iniciar sistema de alertas
  python run_alert_system.py --test                     # Enviar alerta de teste
  python run_alert_system.py --test telegram            # Testar apenas Telegram
  python run_alert_system.py --price BTC/USDT 50000    # Alertar quando BTC > 50000
  python run_alert_system.py --price BTC/USDT 40000 --below  # Alertar quando BTC < 40000
  python run_alert_system.py --list                    # Listar alertas ativos
  python run_alert_system.py --delete alert_123          # Deletar alerta
  python run_alert_system.py --portfolio                # Monitorar portfólio
  python run_alert_system.py --daily-report             # Enviar relatório diário
        """
    )
    
    parser.add_argument('--start',
                       action='store_true',
                       help='Iniciar sistema de alertas')
    parser.add_argument('--test',
                       nargs='?',
                       const='all',
                       choices=['all', 'telegram', 'email'],
                       help='Enviar alerta de teste')
    parser.add_argument('--price',
                       nargs=2,
                       metavar=('SYMBOL', 'PRICE'),
                       help='Criar alerta de preço (ex: BTC/USDT 50000)')
    parser.add_argument('--below',
                       action='store_true',
                       help='Alertar quando preço ficar ABAIXO do valor')
    parser.add_argument('--list',
                       action='store_true',
                       help='Listar alertas ativos')
    parser.add_argument('--delete',
                       metavar='ALERT_ID',
                       help='Deletar alerta por ID')
    parser.add_argument('--portfolio',
                       action='store_true',
                       help='Monitorar portfólio')
    parser.add_argument('--daily-report',
                       action='store_true',
                       help='Enviar relatório diário')
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar configuração e dependências')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║              IA GAIN - Alert System Executor               ║
║         Sistema de Alertas e Notificações                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar configuração
    if args.check:
        print("🔍 Verificando configuração...")
        
        if check_dependencies():
            print("✅ Dependências OK")
        else:
            print("❌ Problemas com dependências")
            sys.exit(1)
        
        if check_config():
            print("✅ Configuração OK")
        else:
            print("❌ Problemas com configuração")
            sys.exit(1)
        
        return
    
    # Verificar dependências antes de executar
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    try:
        if args.start:
            print("🚀 Iniciando sistema de alertas...")
            await start_alert_system()
            
        elif args.test:
            print(f"🧪 Enviando alerta de teste ({args.test})...")
            send_test_alert(args.test)
            
        elif args.price:
            symbol, price_str = args.price
            try:
                price = float(price_str)
                condition = 'below' if args.below else 'above'
                create_price_alert(symbol, price, condition)
            except ValueError:
                print(f"❌ Preço inválido: {price_str}")
                sys.exit(1)
            
        elif args.list:
            list_active_alerts()
            
        elif args.delete:
            delete_alert(args.delete)
            
        elif args.portfolio:
            monitor_portfolio()
            
        elif args.daily_report:
            send_daily_report()
            
        else:
            print("❌ Nenhuma ação especificada")
            print("Use --help para ver as opções disponíveis")
            sys.exit(1)
        
        print("\n✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

def main():
    """Função principal síncrona"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
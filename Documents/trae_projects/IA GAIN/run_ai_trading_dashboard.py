#!/usr/bin/env python3
"""
AI Trading Dashboard - Web Interface for Advanced Trading System
Provides real-time monitoring and control of AI trading operations
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import threading
import time

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import eventlet

# Import our trading components
from exchange.metatrader5_integration import MetaTrader5Integration
from trading.copy_trading import CopyTradingAPI
from analysis.momentum_analyzer import AdvancedMomentumAnalyzer
from analysis.pattern_recognition import AdvancedPatternRecognition
from ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AITradingDashboard:
    """AI Trading Dashboard with real-time monitoring and control"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'ai-trading-dashboard-secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
        
        # Trading components
        self.mt5_integration = MetaTrader5Integration()
        self.copy_trading_api = CopyTradingAPI()
        self.momentum_analyzer = AdvancedMomentumAnalyzer()
        self.pattern_recognizer = AdvancedPatternRecognition()
        self.sentiment_analyzer = GenerativeSentimentAnalyzer()
        
        # Dashboard state
        self.dashboard_state = {
            'connected': False,
            'active_trades': [],
            'account_info': {},
            'market_data': {},
            'ai_signals': {},
            'performance_metrics': {},
            'system_status': 'offline',
            'last_update': None
        }
        
        # Background tasks
        self.background_thread = None
        self.running = False
        
        # Initialize dashboard
        self.setup_routes()
        self.setup_websocket_handlers()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html', 
                                 dashboard_state=self.dashboard_state)
        
        @self.app.route('/trading')
        def trading():
            """Trading control panel"""
            return render_template('trading.html',
                                 account_info=self.dashboard_state['account_info'],
                                 active_trades=self.dashboard_state['active_trades'])
        
        @self.app.route('/analysis')
        def analysis():
            """AI analysis dashboard"""
            return render_template('analysis.html',
                                 ai_signals=self.dashboard_state['ai_signals'],
                                 market_data=self.dashboard_state['market_data'])
        
        @self.app.route('/copy-trading')
        def copy_trading():
            """Copy trading management"""
            return render_template('copy_trading.html',
                                 copy_trading_data=self.get_copy_trading_data())
        
        @self.app.route('/performance')
        def performance():
            """Performance metrics"""
            return render_template('performance.html',
                                 performance_metrics=self.dashboard_state['performance_metrics'])
        
        @self.app.route('/settings')
        def settings():
            """Settings page"""
            return render_template('settings.html',
                                 config=self.config.config)
        
        # API endpoints
        @self.app.route('/api/status')
        def api_status():
            """API status endpoint"""
            return jsonify(self.dashboard_state)
        
        @self.app.route('/api/start-trading', methods=['POST'])
        def api_start_trading():
            """Start trading endpoint"""
            try:
                result = self.start_trading()
                return jsonify({'success': result, 'message': 'Trading started' if result else 'Failed to start trading'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/stop-trading', methods=['POST'])
        def api_stop_trading():
            """Stop trading endpoint"""
            try:
                result = self.stop_trading()
                return jsonify({'success': result, 'message': 'Trading stopped' if result else 'Failed to stop trading'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/execute-trade', methods=['POST'])
        def api_execute_trade():
            """Execute trade endpoint"""
            try:
                data = request.json
                result = self.execute_trade(data)
                return jsonify({'success': result['success'], 'message': result['message']})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/close-trade', methods=['POST'])
        def api_close_trade():
            """Close trade endpoint"""
            try:
                data = request.json
                result = self.close_trade(data['ticket_id'])
                return jsonify({'success': result['success'], 'message': result['message']})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/update-settings', methods=['POST'])
        def api_update_settings():
            """Update settings endpoint"""
            try:
                data = request.json
                result = self.update_settings(data)
                return jsonify({'success': result, 'message': 'Settings updated' if result else 'Failed to update settings'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
    def setup_websocket_handlers(self):
        """Setup WebSocket handlers for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info("Client connected to dashboard")
            emit('connected', {'data': 'Connected to AI Trading Dashboard'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info("Client disconnected from dashboard")
        
        @self.socketio.on('request_update')
        def handle_request_update():
            """Handle update request"""
            emit('dashboard_update', self.dashboard_state)
        
        @self.socketio.on('subscribe_market_data')
        def handle_subscribe_market_data(data):
            """Handle market data subscription"""
            symbol = data.get('symbol')
            if symbol:
                self.subscribe_market_data(symbol)
                emit('subscription_confirmed', {'symbol': symbol})
        
        @self.socketio.on('unsubscribe_market_data')
        def handle_unsubscribe_market_data(data):
            """Handle market data unsubscription"""
            symbol = data.get('symbol')
            if symbol:
                self.unsubscribe_market_data(symbol)
                emit('unsubscription_confirmed', {'symbol': symbol})
        
    def start_background_tasks(self):
        """Start background tasks for real-time updates"""
        if self.background_thread is None or not self.background_thread.is_alive():
            self.running = True
            self.background_thread = threading.Thread(target=self.background_update_loop)
            self.background_thread.daemon = True
            self.background_thread.start()
            logger.info("Background tasks started")
    
    def stop_background_tasks(self):
        """Stop background tasks"""
        self.running = False
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=5)
            logger.info("Background tasks stopped")
    
    def background_update_loop(self):
        """Background update loop"""
        logger.info("Background update loop started")
        
        while self.running:
            try:
                # Update dashboard state
                self.update_dashboard_state()
                
                # Emit updates to connected clients
                self.socketio.emit('dashboard_update', self.dashboard_state)
                
                # Sleep before next update
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in background update loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def update_dashboard_state(self):
        """Update dashboard state with latest data"""
        try:
            # Update connection status
            self.dashboard_state['connected'] = self.mt5_integration.connected
            self.dashboard_state['system_status'] = 'online' if self.running else 'offline'
            self.dashboard_state['last_update'] = datetime.now().isoformat()
            
            # Update account info
            if self.mt5_integration.connected:
                account_info = self.mt5_integration.get_account_info()
                if account_info:
                    self.dashboard_state['account_info'] = {
                        'login': account_info.login,
                        'balance': account_info.balance,
                        'equity': account_info.equity,
                        'profit': account_info.profit,
                        'margin': account_info.margin,
                        'free_margin': account_info.margin_free,
                        'leverage': account_info.leverage,
                        'currency': account_info.currency
                    }
                
                # Update active trades
                positions = self.mt5_integration.get_positions()
                self.dashboard_state['active_trades'] = [
                    {
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == 0 else 'SELL',
                        'volume': pos.volume,
                        'price': pos.price_open,
                        'current_price': pos.price_current,
                        'profit': pos.profit,
                        'swap': pos.swap,
                        'time': datetime.fromtimestamp(pos.time).isoformat()
                    }
                    for pos in positions
                ]
                
                # Update market data
                self.update_market_data()
                
                # Update AI signals
                self.update_ai_signals()
                
                # Update performance metrics
                self.update_performance_metrics()
            
        except Exception as e:
            logger.error(f"Error updating dashboard state: {e}")
    
    def update_market_data(self):
        """Update market data"""
        try:
            symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'BTCUSD', 'ETHUSD', 'XAUUSD']
            
            for symbol in symbols:
                price_info = self.mt5_integration.get_current_price(symbol)
                if price_info:
                    self.dashboard_state['market_data'][symbol] = {
                        'bid': price_info['bid'],
                        'ask': price_info['ask'],
                        'spread': price_info['spread'],
                        'last_update': datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    def update_ai_signals(self):
        """Update AI trading signals"""
        try:
            # This would run AI analysis on key symbols
            symbols = ['EURUSD', 'GBPUSD', 'BTCUSD', 'XAUUSD']
            
            for symbol in symbols:
                # Simulate AI signal generation
                signal = self.generate_ai_signal(symbol)
                if signal:
                    self.dashboard_state['ai_signals'][symbol] = signal
        
        except Exception as e:
            logger.error(f"Error updating AI signals: {e}")
    
    def generate_ai_signal(self, symbol: str) -> Dict:
        """Generate AI trading signal for symbol"""
        try:
            # This would integrate with actual AI analysis
            # For now, return simulated signal
            import random
            
            signals = ['BUY', 'SELL', 'NEUTRAL']
            signal = random.choice(signals)
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': random.uniform(0.5, 0.95),
                'strength': random.uniform(0.1, 0.9),
                'timestamp': datetime.now().isoformat(),
                'reason': f"AI analysis indicates {signal.lower()} opportunity"
            }
        
        except Exception as e:
            logger.error(f"Error generating AI signal for {symbol}: {e}")
            return None
    
    def update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Calculate performance metrics
            if self.dashboard_state['active_trades']:
                total_profit = sum(trade['profit'] for trade in self.dashboard_state['active_trades'])
                total_volume = sum(trade['volume'] for trade in self.dashboard_state['active_trades'])
                
                self.dashboard_state['performance_metrics'] = {
                    'total_profit': total_profit,
                    'total_volume': total_volume,
                    'win_rate': 0.65,  # Simulated
                    'profit_factor': 1.5,  # Simulated
                    'sharpe_ratio': 1.2,  # Simulated
                    'max_drawdown': 5.2,  # Simulated
                    'last_update': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def get_copy_trading_data(self) -> Dict:
        """Get copy trading data"""
        try:
            # This would integrate with actual copy trading system
            return {
                'master_accounts': [
                    {'id': 1, 'name': 'Master Trader 1', 'balance': 10000, 'profit': 1500, 'win_rate': 0.72},
                    {'id': 2, 'name': 'Master Trader 2', 'balance': 25000, 'profit': 3200, 'win_rate': 0.68}
                ],
                'slave_accounts': [
                    {'id': 1, 'name': 'Slave Account 1', 'balance': 5000, 'copied_trades': 45, 'profit': 580},
                    {'id': 2, 'name': 'Slave Account 2', 'balance': 8000, 'copied_trades': 32, 'profit': 420}
                ],
                'copy_trades_today': 12,
                'total_volume_copied': 2.5
            }
        
        except Exception as e:
            logger.error(f"Error getting copy trading data: {e}")
            return {}
    
    def start_trading(self) -> bool:
        """Start trading operations"""
        try:
            self.start_background_tasks()
            logger.info("Trading operations started")
            return True
        
        except Exception as e:
            logger.error(f"Error starting trading operations: {e}")
            return False
    
    def stop_trading(self) -> bool:
        """Stop trading operations"""
        try:
            self.stop_background_tasks()
            logger.info("Trading operations stopped")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping trading operations: {e}")
            return False
    
    def execute_trade(self, trade_data: Dict) -> Dict:
        """Execute trade"""
        try:
            # This would integrate with actual trading system
            symbol = trade_data.get('symbol')
            trade_type = trade_data.get('type')  # 'buy' or 'sell'
            volume = trade_data.get('volume', 0.1)
            
            logger.info(f"Executing trade: {trade_type} {volume} {symbol}")
            
            # Simulate trade execution
            return {
                'success': True,
                'message': f'Trade executed: {trade_type.upper()} {volume} {symbol}',
                'ticket_id': '12345'
            }
        
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {'success': False, 'message': str(e)}
    
    def close_trade(self, ticket_id: str) -> Dict:
        """Close trade"""
        try:
            logger.info(f"Closing trade: {ticket_id}")
            
            # Simulate trade closure
            return {
                'success': True,
                'message': f'Trade {ticket_id} closed successfully'
            }
        
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            return {'success': False, 'message': str(e)}
    
    def update_settings(self, settings: Dict) -> bool:
        """Update settings"""
        try:
            # Update configuration
            self.config.update_config(settings)
            logger.info("Settings updated successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False
    
    def subscribe_market_data(self, symbol: str):
        """Subscribe to market data for symbol"""
        try:
            logger.info(f"Subscribed to market data for {symbol}")
        
        except Exception as e:
            logger.error(f"Error subscribing to market data for {symbol}: {e}")
    
    def unsubscribe_market_data(self, symbol: str):
        """Unsubscribe from market data for symbol"""
        try:
            logger.info(f"Unsubscribed from market data for {symbol}")
        
        except Exception as e:
            logger.error(f"Error unsubscribing from market data for {symbol}: {e}")
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the dashboard"""
        try:
            logger.info(f"Starting AI Trading Dashboard on {host}:{port}")
            
            # Start background tasks
            self.start_background_tasks()
            
            # Run Flask app with SocketIO
            self.socketio.run(self.app, host=host, port=port, debug=debug)
            
        except KeyboardInterrupt:
            logger.info("Dashboard stopped by user")
        except Exception as e:
            logger.error(f"Error running dashboard: {e}")
        finally:
            self.stop_background_tasks()

# Create HTML templates directory and files
def create_templates():
    """Create HTML templates for the dashboard"""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Main dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Dashboard</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .card { margin-bottom: 20px; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .signal-buy { color: #28a745; font-weight: bold; }
        .signal-sell { color: #dc3545; font-weight: bold; }
        .signal-neutral { color: #6c757d; font-weight: bold; }
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI Trading Dashboard</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">
                    Status: <span id="system-status" class="status-offline">Offline</span>
                </span>
                <button id="start-trading" class="btn btn-success btn-sm me-2">Start Trading</button>
                <button id="stop-trading" class="btn btn-danger btn-sm">Stop Trading</button>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Account Info -->
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Account Balance</h5>
                        <h3 id="account-balance">$0.00</h3>
                        <small>Equity: $<span id="account-equity">0.00</span></small>
                    </div>
                </div>
            </div>
            
            <!-- Active Trades -->
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Active Trades</h5>
                        <h3 id="active-trades-count">0</h3>
                        <small>Total Profit: $<span id="total-profit">0.00</span></small>
                    </div>
                </div>
            </div>
            
            <!-- Win Rate -->
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Win Rate</h5>
                        <h3 id="win-rate">0%</h3>
                        <small>Sharpe Ratio: <span id="sharpe-ratio">0.00</span></small>
                    </div>
                </div>
            </div>
            
            <!-- Max Drawdown -->
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Max Drawdown</h5>
                        <h3 id="max-drawdown">0%</h3>
                        <small>Profit Factor: <span id="profit-factor">0.00</span></small>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <!-- Market Data -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Market Data</h5>
                    </div>
                    <div class="card-body">
                        <div id="market-data" class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th>Bid</th>
                                        <th>Ask</th>
                                        <th>Spread</th>
                                    </tr>
                                </thead>
                                <tbody id="market-data-tbody">
                                    <tr><td colspan="4" class="text-center">No data available</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- AI Signals -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>AI Trading Signals</h5>
                    </div>
                    <div class="card-body">
                        <div id="ai-signals" class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th>Signal</th>
                                        <th>Confidence</th>
                                        <th>Strength</th>
                                    </tr>
                                </thead>
                                <tbody id="ai-signals-tbody">
                                    <tr><td colspan="4" class="text-center">No signals available</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <!-- Active Trades Table -->
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Active Trades</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Ticket</th>
                                        <th>Symbol</th>
                                        <th>Type</th>
                                        <th>Volume</th>
                                        <th>Open Price</th>
                                        <th>Current Price</th>
                                        <th>Profit</th>
                                        <th>Time</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody id="active-trades-tbody">
                                    <tr><td colspan="9" class="text-center">No active trades</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // WebSocket connection
        const socket = io();
        
        // Dashboard state
        let dashboardState = {};
        
        // Connect to server
        socket.on('connect', function() {
            console.log('Connected to dashboard server');
            socket.emit('request_update');
        });
        
        // Handle dashboard updates
        socket.on('dashboard_update', function(data) {
            dashboardState = data;
            updateDashboard();
        });
        
        // Update dashboard UI
        function updateDashboard() {
            // Update system status
            const statusElement = document.getElementById('system-status');
            statusElement.textContent = dashboardState.system_status;
            statusElement.className = dashboardState.connected ? 'status-online' : 'status-offline';
            
            // Update account info
            if (dashboardState.account_info) {
                document.getElementById('account-balance').textContent = '$' + (dashboardState.account_info.balance || 0).toFixed(2);
                document.getElementById('account-equity').textContent = (dashboardState.account_info.equity || 0).toFixed(2);
            }
            
            // Update active trades count
            document.getElementById('active-trades-count').textContent = dashboardState.active_trades.length;
            
            // Update performance metrics
            if (dashboardState.performance_metrics) {
                document.getElementById('win-rate').textContent = (dashboardState.performance_metrics.win_rate * 100 || 0).toFixed(1) + '%';
                document.getElementById('sharpe-ratio').textContent = (dashboardState.performance_metrics.sharpe_ratio || 0).toFixed(2);
                document.getElementById('profit-factor').textContent = (dashboardState.performance_metrics.profit_factor || 0).toFixed(2);
                document.getElementById('max-drawdown').textContent = (dashboardState.performance_metrics.max_drawdown || 0).toFixed(1) + '%';
                
                const totalProfit = dashboardState.active_trades.reduce((sum, trade) => sum + trade.profit, 0);
                document.getElementById('total-profit').textContent = totalProfit.toFixed(2);
            }
            
            // Update market data
            updateMarketData();
            
            // Update AI signals
            updateAISignals();
            
            // Update active trades table
            updateActiveTrades();
        }
        
        function updateMarketData() {
            const tbody = document.getElementById('market-data-tbody');
            tbody.innerHTML = '';
            
            if (dashboardState.market_data && Object.keys(dashboardState.market_data).length > 0) {
                for (const [symbol, data] of Object.entries(dashboardState.market_data)) {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td><strong>${symbol}</strong></td>
                        <td>${data.bid.toFixed(5)}</td>
                        <td>${data.ask.toFixed(5)}</td>
                        <td>${data.spread.toFixed(1)}</td>
                    `;
                }
            } else {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">No data available</td></tr>';
            }
        }
        
        function updateAISignals() {
            const tbody = document.getElementById('ai-signals-tbody');
            tbody.innerHTML = '';
            
            if (dashboardState.ai_signals && Object.keys(dashboardState.ai_signals).length > 0) {
                for (const [symbol, signal] of Object.entries(dashboardState.ai_signals)) {
                    const signalClass = signal.signal === 'BUY' ? 'signal-buy' : 
                                      signal.signal === 'SELL' ? 'signal-sell' : 'signal-neutral';
                    
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td><strong>${symbol}</strong></td>
                        <td class="${signalClass}">${signal.signal}</td>
                        <td>${(signal.confidence * 100).toFixed(1)}%</td>
                        <td>${signal.strength.toFixed(2)}</td>
                    `;
                }
            } else {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">No signals available</td></tr>';
            }
        }
        
        function updateActiveTrades() {
            const tbody = document.getElementById('active-trades-tbody');
            tbody.innerHTML = '';
            
            if (dashboardState.active_trades.length > 0) {
                dashboardState.active_trades.forEach(trade => {
                    const profitClass = trade.profit >= 0 ? 'text-success' : 'text-danger';
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${trade.ticket}</td>
                        <td><strong>${trade.symbol}</strong></td>
                        <td class="${trade.type === 'BUY' ? 'text-success' : 'text-danger'}">${trade.type}</td>
                        <td>${trade.volume}</td>
                        <td>${trade.price.toFixed(5)}</td>
                        <td>${trade.current_price.toFixed(5)}</td>
                        <td class="${profitClass}">$${trade.profit.toFixed(2)}</td>
                        <td>${new Date(trade.time).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-danger btn-sm" onclick="closeTrade(${trade.ticket})">Close</button>
                        </td>
                    `;
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="9" class="text-center">No active trades</td></tr>';
            }
        }
        
        // Trading controls
        document.getElementById('start-trading').addEventListener('click', function() {
            fetch('/api/start-trading', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        socket.emit('request_update');
                    }
                });
        });
        
        document.getElementById('stop-trading').addEventListener('click', function() {
            fetch('/api/stop-trading', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        socket.emit('request_update');
                    }
                });
        });
        
        function closeTrade(ticket) {
            if (confirm(`Close trade ${ticket}?`)) {
                fetch('/api/close-trade', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticket_id: ticket })
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        socket.emit('request_update');
                    }
                });
            }
        }
    </script>
</body>
</html>'''
    
    # Write dashboard template
    (templates_dir / 'dashboard.html').write_text(dashboard_html)
    
    # Create other templates (simplified versions)
    templates = {
        'trading.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Control - AI Trading Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI Trading Dashboard</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link active" href="/trading">Trading</a>
                <a class="nav-link" href="/analysis">Analysis</a>
                <a class="nav-link" href="/copy-trading">Copy Trading</a>
                <a class="nav-link" href="/performance">Performance</a>
                <a class="nav-link" href="/settings">Settings</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Trading Control Panel</h1>
        <p class="text-muted">Execute trades and manage positions</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Quick Trade</h5>
                    </div>
                    <div class="card-body">
                        <form id="quick-trade-form">
                            <div class="mb-3">
                                <label for="symbol" class="form-label">Symbol</label>
                                <select class="form-select" id="symbol" required>
                                    <option value="">Select Symbol</option>
                                    <option value="EURUSD">EURUSD</option>
                                    <option value="GBPUSD">GBPUSD</option>
                                    <option value="USDJPY">USDJPY</option>
                                    <option value="AUDUSD">AUDUSD</option>
                                    <option value="BTCUSD">BTCUSD</option>
                                    <option value="ETHUSD">ETHUSD</option>
                                    <option value="XAUUSD">XAUUSD</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="trade-type" class="form-label">Trade Type</label>
                                <select class="form-select" id="trade-type" required>
                                    <option value="buy">Buy</option>
                                    <option value="sell">Sell</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="volume" class="form-label">Volume</label>
                                <input type="number" class="form-control" id="volume" step="0.01" min="0.01" value="0.1" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Execute Trade</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Account Information</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Balance:</strong> $<span id="account-balance">{{ account_info.balance|default(0) }}</span></p>
                        <p><strong>Equity:</strong> $<span id="account-equity">{{ account_info.equity|default(0) }}</span></p>
                        <p><strong>Free Margin:</strong> $<span id="free-margin">{{ account_info.free_margin|default(0) }}</span></p>
                        <p><strong>Leverage:</strong> 1:{{ account_info.leverage|default(100) }}</p>
                        <p><strong>Currency:</strong> {{ account_info.currency|default('USD') }}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Active Positions</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Ticket</th>
                                        <th>Symbol</th>
                                        <th>Type</th>
                                        <th>Volume</th>
                                        <th>Open Price</th>
                                        <th>Current Price</th>
                                        <th>Profit</th>
                                        <th>Time</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody id="positions-tbody">
                                    {% for trade in active_trades %}
                                    <tr>
                                        <td>{{ trade.ticket }}</td>
                                        <td>{{ trade.symbol }}</td>
                                        <td class="{% if trade.type == 'BUY' %}text-success{% else %}text-danger{% endif %}">
                                            {{ trade.type }}
                                        </td>
                                        <td>{{ trade.volume }}</td>
                                        <td>{{ "%.5f"|format(trade.price) }}</td>
                                        <td>{{ "%.5f"|format(trade.current_price) }}</td>
                                        <td class="{% if trade.profit >= 0 %}text-success{% else %}text-danger{% endif %}">
                                            ${{ "%.2f"|format(trade.profit) }}
                                        </td>
                                        <td>{{ trade.time }}</td>
                                        <td>
                                            <button class="btn btn-danger btn-sm" onclick="closePosition({{ trade.ticket }})">Close</button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('quick-trade-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                symbol: document.getElementById('symbol').value,
                type: document.getElementById('trade-type').value,
                volume: parseFloat(document.getElementById('volume').value)
            };
            
            fetch('/api/execute-trade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    setTimeout(() => location.reload(), 1000);
                }
            })
            .catch(error => {
                alert('Error executing trade: ' + error.message);
            });
        });
        
        function closePosition(ticket) {
            if (confirm('Close position ' + ticket + '?')) {
                fetch('/api/close-trade', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticket_id: ticket })
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        setTimeout(() => location.reload(), 1000);
                    }
                })
                .catch(error => {
                    alert('Error closing position: ' + error.message);
                });
            }
        }
    </script>
</body>
</html>''',
        
        'analysis.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Analysis - AI Trading Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI Trading Dashboard</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/trading">Trading</a>
                <a class="nav-link active" href="/analysis">Analysis</a>
                <a class="nav-link" href="/copy-trading">Copy Trading</a>
                <a class="nav-link" href="/performance">Performance</a>
                <a class="nav-link" href="/settings">Settings</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>AI Analysis Dashboard</h1>
        <p class="text-muted">Advanced market analysis and trading signals</p>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Market Analysis</h5>
                    </div>
                    <div class="card-body">
                        <p>AI analysis features include:</p>
                        <ul>
                            <li>Momentum Analysis - Advanced momentum indicators and divergence detection</li>
                            <li>Pattern Recognition - Machine learning pattern detection and chart analysis</li>
                            <li>Sentiment Analysis - Generative AI sentiment analysis from news and social media</li>
                            <li>Risk Assessment - Comprehensive risk metrics and portfolio analysis</li>
                        </ul>
                        <button class="btn btn-primary" onclick="runAnalysis()">Run Analysis</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Analysis Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="analysis-results">
                            <p class="text-muted">Click "Run Analysis" to generate AI trading signals</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function runAnalysis() {
            document.getElementById('analysis-results').innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p>Running AI analysis...</p></div>';
            
            // Simulate analysis
            setTimeout(() => {
                document.getElementById('analysis-results').innerHTML = `
                    <div class="alert alert-success">
                        <h6>Analysis Complete</h6>
                        <p>AI analysis has been completed. Results are available in the advanced analysis reports.</p>
                        <p>Use the command line tools for detailed analysis:</p>
                        <ul>
                            <li><code>python run_advanced_analysis.py</code> - Run comprehensive AI analysis</li>
                            <li><code>python run_momentum_analysis.py</code> - Run momentum analysis</li>
                            <li><code>python run_pattern_recognition.py</code> - Run pattern recognition</li>
                        </ul>
                    </div>
                `;
            }, 2000);
        }
    </script>
</body>
</html>''',
        
        'copy_trading.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copy Trading - AI Trading Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI Trading Dashboard</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/trading">Trading</a>
                <a class="nav-link" href="/analysis">Analysis</a>
                <a class="nav-link active" href="/copy-trading">Copy Trading</a>
                <a class="nav-link" href="/performance">Performance</a>
                <a class="nav-link" href="/settings">Settings</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Copy Trading Management</h1>
        <p class="text-muted">Manage master/slave copy trading relationships</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Master Accounts</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Balance</th>
                                    <th>Profit</th>
                                    <th>Win Rate</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for master in copy_trading_data.master_accounts %}
                                <tr>
                                    <td>{{ master.name }}</td>
                                    <td>${{ master.balance }}</td>
                                    <td class="{% if master.profit >= 0 %}text-success{% else %}text-danger{% endif %}">
                                        ${{ master.profit }}
                                    </td>
                                    <td>{{ (master.win_rate * 100)|round(1) }}%</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Slave Accounts</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Balance</th>
                                    <th>Copied Trades</th>
                                    <th>Profit</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for slave in copy_trading_data.slave_accounts %}
                                <tr>
                                    <td>{{ slave.name }}</td>
                                    <td>${{ slave.balance }}</td>
                                    <td>{{ slave.copied_trades }}</td>
                                    <td class="{% if slave.profit >= 0 %}text-success{% else %}text-danger{% endif %}">
                                        ${{ slave.profit }}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Copy Trading Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4>{{ copy_trading_data.copy_trades_today }}</h4>
                                    <p class="text-muted">Trades Copied Today</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4>{{ copy_trading_data.total_volume_copied }}</h4>
                                    <p class="text-muted">Total Volume Copied</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4>{{ copy_trading_data.master_accounts|length }}</h4>
                                    <p class="text-muted">Master Accounts</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4>{{ copy_trading_data.slave_accounts|length }}</h4>
                                    <p class="text-muted">Slave Accounts</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Copy Trading Controls</h5>
                    </div>
                    <div class="card-body">
                        <p>Use the command line tools for advanced copy trading management:</p>
                        <ul>
                            <li><code>python run_copy_trading.py</code> - Start copy trading system</li>
                            <li><code>python run_copy_trading.py --add-master</code> - Add master account</li>
                            <li><code>python run_copy_trading.py --add-slave</code> - Add slave account</li>
                            <li><code>python run_copy_trading.py --performance</code> - View performance reports</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',
        
        'performance.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance - AI Trading Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI Trading Dashboard</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/trading">Trading</a>
                <a class="nav-link" href="/analysis">Analysis</a>
                <a class="nav-link" href="/copy-trading">Copy Trading</a>
                <a class="nav-link active" href="/performance">Performance</a>
                <a class="nav-link" href="/settings">Settings</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Performance Metrics</h1>
        <p class="text-muted">Trading performance and analytics</p>
        
        <div class="row">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Profit</h5>
                        <h3 class="text-success">${{ performance_metrics.total_profit|default(0)|round(2) }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Win Rate</h5>
                        <h3>{{ (performance_metrics.win_rate|default(0) * 100)|round(1) }}%</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Sharpe Ratio</h5>
                        <h3>{{ performance_metrics.sharpe_ratio|default(0)|round(2) }}</h3>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Performance Chart</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="performance-chart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Risk Metrics</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Profit Factor:</strong> {{ performance_metrics.profit_factor|default(0)|round(2) }}</p>
                        <p><strong>Max Drawdown:</strong> {{ performance_metrics.max_drawdown|default(0)|round(2) }}%</p>
                        <p><strong>Total Volume:</strong> {{ performance_metrics.total_volume|default(0)|round(2) }}</p>
                        <p><strong>Last Update:</strong> {{ performance_metrics.last_update|default('Never') }}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Performance Reports</h5>
                    </div>
                    <div class="card-body">
                        <p>Detailed performance reports are available in the reports directory:</p>
                        <ul>
                            <li><code>reports/performance/</code> - Performance analysis reports</li>
                            <li><code>logs/</code> - Trading logs and execution records</li>
                            <li><code>reports/advanced_analysis/</code> - AI analysis reports</li>
                        </ul>
                        <button class="btn btn-primary" onclick="generateReport()">Generate New Report</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Performance chart
        const ctx = document.getElementById('performance-chart').getContext('2d');
        const performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Cumulative Profit',
                    data: [0, 500, 1200, 800, 1500, 2000],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        function generateReport() {
            alert('Use command line tools to generate detailed reports:\\n\\n' +
                  'python run_advanced_analysis.py - Generate AI analysis report\\n' +
                  'python run_copy_trading.py --performance - Generate copy trading report\\n' +
                  'python run_metatrader_trading.py --report - Generate trading report');
        }
    </script>
</body>
</html>''',
        
        'settings.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - AI Trading Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI Trading Dashboard</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/trading">Trading</a>
                <a class="nav-link" href="/analysis">Analysis</a>
                <a class="nav-link" href="/copy-trading">Copy Trading</a>
                <a class="nav-link" href="/performance">Performance</a>
                <a class="nav-link active" href="/settings">Settings</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Settings</h1>
        <p class="text-muted">Configure AI trading system parameters</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Trading Settings</h5>
                    </div>
                    <div class="card-body">
                        <form id="settings-form">
                            <div class="mb-3">
                                <label for="max-risk" class="form-label">Maximum Risk (%)</label>
                                <input type="number" class="form-control" id="max-risk" value="2" min="0.1" max="10" step="0.1">
                            </div>
                            <div class="mb-3">
                                <label for="max-drawdown" class="form-label">Maximum Drawdown (%)</label>
                                <input type="number" class="form-control" id="max-drawdown" value="10" min="1" max="50" step="1">
                            </div>
                            <div class="mb-3">
                                <label for="lot-size" class="form-label">Default Lot Size</label>
                                <input type="number" class="form-control" id="lot-size" value="0.1" min="0.01" max="10" step="0.01">
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="auto-trading" checked>
                                    <label class="form-check-label" for="auto-trading">
                                        Enable Auto Trading
                                    </label>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">Save Settings</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>AI Settings</h5>
                    </div>
                    <div class="card-body">
                        <form id="ai-settings-form">
                            <div class="mb-3">
                                <label for="analysis-interval" class="form-label">Analysis Interval (hours)</label>
                                <input type="number" class="form-control" id="analysis-interval" value="6" min="1" max="24" step="1">
                            </div>
                            <div class="mb-3">
                                <label for="confidence-threshold" class="form-label">Signal Confidence Threshold (%)</label>
                                <input type="number" class="form-control" id="confidence-threshold" value="70" min="50" max="95" step="5">
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="sentiment-analysis" checked>
                                    <label class="form-check-label" for="sentiment-analysis">
                                        Enable Sentiment Analysis
                                    </label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="pattern-recognition" checked>
                                    <label class="form-check-label" for="pattern-recognition">
                                        Enable Pattern Recognition
                                    </label>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">Save AI Settings</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Configuration Management</h5>
                    </div>
                    <div class="card-body">
                        <p>Current configuration file: <code>config.json</code></p>
                        <button class="btn btn-secondary me-2" onclick="exportConfig()">Export Config</button>
                        <button class="btn btn-secondary me-2" onclick="importConfig()">Import Config</button>
                        <button class="btn btn-warning" onclick="resetConfig()">Reset to Defaults</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('settings-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const settings = {
                max_risk: parseFloat(document.getElementById('max-risk').value),
                max_drawdown: parseFloat(document.getElementById('max-drawdown').value),
                lot_size: parseFloat(document.getElementById('lot-size').value),
                auto_trading: document.getElementById('auto-trading').checked
            };
            
            saveSettings(settings);
        });
        
        document.getElementById('ai-settings-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const settings = {
                analysis_interval: parseInt(document.getElementById('analysis-interval').value),
                confidence_threshold: parseFloat(document.getElementById('confidence-threshold').value),
                sentiment_analysis: document.getElementById('sentiment-analysis').checked,
                pattern_recognition: document.getElementById('pattern-recognition').checked
            };
            
            saveSettings(settings);
        });
        
        function saveSettings(settings) {
            fetch('/api/update-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            })
            .catch(error => {
                alert('Error saving settings: ' + error.message);
            });
        }
        
        function exportConfig() {
            alert('Configuration export functionality would be implemented here');
        }
        
        function importConfig() {
            alert('Configuration import functionality would be implemented here');
        }
        
        function resetConfig() {
            if (confirm('Reset all settings to defaults? This cannot be undone.')) {
                alert('Configuration reset functionality would be implemented here');
            }
        }
    </script>
</body>
</html>'''
    }
    
    # Write all templates
    for filename, content in templates.items():
        (templates_dir / filename).write_text(content)
    
    logger.info("HTML templates created successfully")

async def main():
    """Main entry point"""
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('reports').mkdir(exist_ok=True)
    Path('templates').mkdir(exist_ok=True)
    
    # Create templates
    create_templates()
    
    # Create and run dashboard
    dashboard = AITradingDashboard()
    dashboard.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
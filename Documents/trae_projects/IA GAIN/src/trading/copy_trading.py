"""
Copy Trading System
Provides master/slave functionality for copying trades across multiple accounts
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CopyMode(Enum):
    FULL_COPY = "full_copy"  # Copy all trades exactly
    PROPORTIONAL = "proportional"  # Copy proportional to account size
    FIXED_SIZE = "fixed_size"  # Copy with fixed lot size
    RISK_ADJUSTED = "risk_adjusted"  # Copy with risk adjustment

class TradeStatus(Enum):
    PENDING = "pending"
    COPIED = "copied"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class CopyTrade:
    master_ticket: int
    slave_ticket: int
    symbol: str
    order_type: str
    volume: float
    price_open: float
    price_close: float
    sl: float
    tp: float
    status: TradeStatus
    timestamp: datetime
    profit: float
    commission: float
    swap: float
    comment: str
    magic: int

@dataclass
class MasterAccount:
    account_id: str
    name: str
    broker: str
    balance: float
    equity: float
    leverage: int
    is_active: bool
    copy_mode: CopyMode
    risk_multiplier: float
    max_slaves: int
    performance_fee: float
    minimum_balance: float
    created_at: datetime
    last_update: datetime

@dataclass
class SlaveAccount:
    account_id: str
    name: str
    broker: str
    balance: float
    equity: float
    leverage: int
    is_active: bool
    master_account_id: str
    copy_mode: CopyMode
    risk_multiplier: float
    max_trades: int
    max_lot_size: float
    minimum_balance: float
    performance_fee: float
    created_at: datetime
    last_update: datetime

class CopyTradingDatabase:
    """
    Database manager for copy trading system
    """
    
    def __init__(self, db_path: str = "copy_trading.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Master accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_accounts (
                account_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                broker TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                equity REAL DEFAULT 0.0,
                leverage INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT TRUE,
                copy_mode TEXT DEFAULT 'full_copy',
                risk_multiplier REAL DEFAULT 1.0,
                max_slaves INTEGER DEFAULT 10,
                performance_fee REAL DEFAULT 0.0,
                minimum_balance REAL DEFAULT 100.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Slave accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slave_accounts (
                account_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                broker TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                equity REAL DEFAULT 0.0,
                leverage INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT TRUE,
                master_account_id TEXT NOT NULL,
                copy_mode TEXT DEFAULT 'full_copy',
                risk_multiplier REAL DEFAULT 1.0,
                max_trades INTEGER DEFAULT 100,
                max_lot_size REAL DEFAULT 1.0,
                minimum_balance REAL DEFAULT 100.0,
                performance_fee REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (master_account_id) REFERENCES master_accounts (account_id)
            )
        ''')
        
        # Copy trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copy_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_ticket INTEGER NOT NULL,
                slave_ticket INTEGER,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                volume REAL NOT NULL,
                price_open REAL NOT NULL,
                price_close REAL,
                sl REAL,
                tp REAL,
                status TEXT DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profit REAL DEFAULT 0.0,
                commission REAL DEFAULT 0.0,
                swap REAL DEFAULT 0.0,
                comment TEXT,
                magic INTEGER DEFAULT 0,
                master_account_id TEXT NOT NULL,
                slave_account_id TEXT NOT NULL,
                FOREIGN KEY (master_account_id) REFERENCES master_accounts (account_id),
                FOREIGN KEY (slave_account_id) REFERENCES slave_accounts (account_id)
            )
        ''')
        
        # Performance tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                account_type TEXT NOT NULL,
                date DATE NOT NULL,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                profit_loss REAL DEFAULT 0.0,
                win_rate REAL DEFAULT 0.0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                max_drawdown REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES master_accounts (account_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_master_account(self, master: MasterAccount) -> bool:
        """Add master account to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO master_accounts 
                (account_id, name, broker, balance, equity, leverage, is_active, 
                 copy_mode, risk_multiplier, max_slaves, performance_fee, minimum_balance, 
                 created_at, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                master.account_id, master.name, master.broker, master.balance,
                master.equity, master.leverage, master.is_active, master.copy_mode.value,
                master.risk_multiplier, master.max_slaves, master.performance_fee,
                master.minimum_balance, master.created_at, master.last_update
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding master account: {e}")
            return False
    
    def add_slave_account(self, slave: SlaveAccount) -> bool:
        """Add slave account to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO slave_accounts 
                (account_id, name, broker, balance, equity, leverage, is_active, 
                 master_account_id, copy_mode, risk_multiplier, max_trades, 
                 max_lot_size, minimum_balance, performance_fee, created_at, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                slave.account_id, slave.name, slave.broker, slave.balance,
                slave.equity, slave.leverage, slave.is_active, slave.master_account_id,
                slave.copy_mode.value, slave.risk_multiplier, slave.max_trades,
                slave.max_lot_size, slave.minimum_balance, slave.performance_fee,
                slave.created_at, slave.last_update
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding slave account: {e}")
            return False
    
    def record_copy_trade(self, trade: CopyTrade, master_id: str, slave_id: str) -> bool:
        """Record copy trade in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO copy_trades 
                (master_ticket, slave_ticket, symbol, order_type, volume, 
                 price_open, price_close, sl, tp, status, timestamp, profit, 
                 commission, swap, comment, magic, master_account_id, slave_account_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.master_ticket, trade.slave_ticket, trade.symbol, trade.order_type,
                trade.volume, trade.price_open, trade.price_close, trade.sl, trade.tp,
                trade.status.value, trade.timestamp, trade.profit, trade.commission,
                trade.swap, trade.comment, trade.magic, master_id, slave_id
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error recording copy trade: {e}")
            return False
    
    def get_active_masters(self) -> List[MasterAccount]:
        """Get all active master accounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM master_accounts WHERE is_active = TRUE')
            rows = cursor.fetchall()
            conn.close()
            
            masters = []
            for row in rows:
                master = MasterAccount(
                    account_id=row[0],
                    name=row[1],
                    broker=row[2],
                    balance=row[3],
                    equity=row[4],
                    leverage=row[5],
                    is_active=row[6],
                    copy_mode=CopyMode(row[7]),
                    risk_multiplier=row[8],
                    max_slaves=row[9],
                    performance_fee=row[10],
                    minimum_balance=row[11],
                    created_at=row[12],
                    last_update=row[13]
                )
                masters.append(master)
            
            return masters
            
        except Exception as e:
            logger.error(f"Error getting active masters: {e}")
            return []
    
    def get_slave_accounts(self, master_id: str) -> List[SlaveAccount]:
        """Get all slave accounts for a master"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM slave_accounts WHERE master_account_id = ? AND is_active = TRUE', (master_id,))
            rows = cursor.fetchall()
            conn.close()
            
            slaves = []
            for row in rows:
                slave = SlaveAccount(
                    account_id=row[0],
                    name=row[1],
                    broker=row[2],
                    balance=row[3],
                    equity=row[4],
                    leverage=row[5],
                    is_active=row[6],
                    master_account_id=row[7],
                    copy_mode=CopyMode(row[8]),
                    risk_multiplier=row[9],
                    max_trades=row[10],
                    max_lot_size=row[11],
                    minimum_balance=row[12],
                    performance_fee=row[13],
                    created_at=row[14],
                    last_update=row[15]
                )
                slaves.append(slave)
            
            return slaves
            
        except Exception as e:
            logger.error(f"Error getting slave accounts: {e}")
            return []

class TradeCopier:
    """
    Main trade copier engine
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db = CopyTradingDatabase(config.get('db_path', 'copy_trading.db'))
        self.running = False
        self.threads = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.trade_callbacks = []
        self.error_handlers = []
        
        # Master account interfaces (will be populated with actual trading interfaces)
        self.master_interfaces = {}
        self.slave_interfaces = {}
    
    def add_trade_callback(self, callback: Callable):
        """Add callback for trade events"""
        self.trade_callbacks.append(callback)
    
    def add_error_handler(self, handler: Callable):
        """Add error handler"""
        self.error_handlers.append(handler)
    
    def calculate_copy_volume(self, master_volume: float, master_account: MasterAccount, 
                              slave_account: SlaveAccount, master_balance: float, 
                              slave_balance: float) -> float:
        """Calculate volume for slave account based on copy mode"""
        
        if slave_account.copy_mode == CopyMode.FULL_COPY:
            return master_volume
        
        elif slave_account.copy_mode == CopyMode.PROPORTIONAL:
            # Proportional to account balance
            ratio = slave_balance / master_balance
            return master_volume * ratio * slave_account.risk_multiplier
        
        elif slave_account.copy_mode == CopyMode.FIXED_SIZE:
            # Use fixed lot size from slave config
            return min(slave_account.max_lot_size, master_volume)
        
        elif slave_account.copy_mode == CopyMode.RISK_ADJUSTED:
            # Adjust based on risk parameters
            risk_ratio = min(slave_balance / master_balance, slave_account.risk_multiplier)
            return master_volume * risk_ratio
        
        return master_volume
    
    def validate_trade_conditions(self, slave_account: SlaveAccount, 
                                 proposed_volume: float, symbol: str) -> bool:
        """Validate if trade conditions are met for slave account"""
        
        # Check minimum balance
        if slave_account.equity < slave_account.minimum_balance:
            logger.warning(f"Slave {slave_account.account_id} below minimum balance")
            return False
        
        # Check maximum lot size
        if proposed_volume > slave_account.max_lot_size:
            logger.warning(f"Proposed volume {proposed_volume} exceeds max lot size {slave_account.max_lot_size}")
            return False
        
        # Check maximum trades (simplified check)
        # In real implementation, would check actual open trades
        if hasattr(slave_account, 'open_trades_count') and slave_account.open_trades_count >= slave_account.max_trades:
            logger.warning(f"Slave {slave_account.account_id} at max trades limit")
            return False
        
        return True
    
    def copy_trade_to_slave(self, master_trade: Dict, master_account: MasterAccount, 
                           slave_account: SlaveAccount) -> bool:
        """Copy a single trade to slave account"""
        
        try:
            # Calculate volume for slave
            slave_volume = self.calculate_copy_volume(
                master_trade['volume'], 
                master_account, 
                slave_account,
                master_account.balance,
                slave_account.balance
            )
            
            # Validate trade conditions
            if not self.validate_trade_conditions(slave_account, slave_volume, master_trade['symbol']):
                return False
            
            # Create copy trade object
            copy_trade = CopyTrade(
                master_ticket=master_trade['ticket'],
                slave_ticket=None,  # Will be filled after execution
                symbol=master_trade['symbol'],
                order_type=master_trade['type'],
                volume=slave_volume,
                price_open=master_trade['price_open'],
                price_close=0.0,
                sl=master_trade['sl'],
                tp=master_trade['tp'],
                status=TradeStatus.PENDING,
                timestamp=datetime.now(),
                profit=0.0,
                commission=0.0,
                swap=0.0,
                comment=f"Copied from master {master_account.account_id}",
                magic=master_trade.get('magic', 0)
            )
            
            # Execute trade on slave account (placeholder - would use actual trading interface)
            # In real implementation, would call slave trading interface here
            logger.info(f"Would execute trade on slave {slave_account.account_id}: "
                       f"{copy_trade.symbol} {copy_trade.order_type} {copy_trade.volume}")
            
            # Record trade in database
            copy_trade.status = TradeStatus.COPIED
            self.db.record_copy_trade(copy_trade, master_account.account_id, slave_account.account_id)
            
            # Trigger callbacks
            for callback in self.trade_callbacks:
                callback(copy_trade, master_account, slave_account)
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying trade to slave {slave_account.account_id}: {e}")
            
            # Trigger error handlers
            for handler in self.error_handlers:
                handler(e, master_trade, master_account, slave_account)
            
            return False
    
    def process_master_trades(self, master_account: MasterAccount):
        """Process trades from master account"""
        
        try:
            # Get master trades (placeholder - would use actual trading interface)
            # In real implementation, would fetch actual trades from master account
            master_trades = self.get_master_trades(master_account)
            
            # Get slave accounts for this master
            slave_accounts = self.db.get_slave_accounts(master_account.account_id)
            
            # Process each trade
            for trade in master_trades:
                # Copy to each slave account
                self.executor.submit(self.copy_trade_to_slave, trade, master_account, slave)
            
        except Exception as e:
            logger.error(f"Error processing master trades for {master_account.account_id}: {e}")
    
    def get_master_trades(self, master_account: MasterAccount) -> List[Dict]:
        """Get trades from master account (placeholder implementation)"""
        # In real implementation, would fetch actual trades from master trading interface
        return []
    
    def start_copying(self):
        """Start the copy trading engine"""
        if self.running:
            logger.warning("Copy trading engine is already running")
            return
        
        self.running = True
        logger.info("Starting copy trading engine")
        
        # Start main copying thread
        copy_thread = threading.Thread(target=self.copying_loop, daemon=True)
        copy_thread.start()
        self.threads.append(copy_thread)
        
        # Start performance monitoring thread
        monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        monitor_thread.start()
        self.threads.append(monitor_thread)
    
    def stop_copying(self):
        """Stop the copy trading engine"""
        self.running = False
        logger.info("Stopping copy trading engine")
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Copy trading engine stopped")
    
    def copying_loop(self):
        """Main copying loop"""
        copy_interval = self.config.get('copy_interval', 1)  # seconds
        
        while self.running:
            try:
                # Get active master accounts
                master_accounts = self.db.get_active_masters()
                
                # Process each master account
                for master in master_accounts:
                    self.process_master_trades(master)
                
                # Sleep before next iteration
                time.sleep(copy_interval)
                
            except Exception as e:
                logger.error(f"Error in copying loop: {e}")
                time.sleep(copy_interval)
    
    def monitoring_loop(self):
        """Performance monitoring loop"""
        monitor_interval = self.config.get('monitor_interval', 300)  # 5 minutes
        
        while self.running:
            try:
                # Update account balances and performance metrics
                self.update_account_metrics()
                
                # Check for any issues or alerts
                self.check_alerts()
                
                # Sleep before next iteration
                time.sleep(monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(monitor_interval)
    
    def update_account_metrics(self):
        """Update account performance metrics"""
        # Placeholder implementation
        pass
    
    def check_alerts(self):
        """Check for alerts and issues"""
        # Placeholder implementation
        pass
    
    def get_performance_report(self, account_id: str, days: int = 30) -> Dict:
        """Get performance report for account"""
        # Placeholder implementation
        return {
            'account_id': account_id,
            'period_days': days,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }
    
    def get_copy_statistics(self) -> Dict:
        """Get overall copy trading statistics"""
        masters = self.db.get_active_masters()
        total_slaves = 0
        total_copied_trades = 0
        
        for master in masters:
            slaves = self.db.get_slave_accounts(master.account_id)
            total_slaves += len(slaves)
        
        return {
            'active_masters': len(masters),
            'total_slaves': total_slaves,
            'total_copied_trades': total_copied_trades,
            'is_running': self.running,
            'timestamp': datetime.now()
        }

# Web API for remote copy trading
class CopyTradingAPI:
    """
    REST API for copy trading system
    """
    
    def __init__(self, trade_copier: TradeCopier, host: str = "0.0.0.0", port: int = 8080):
        self.trade_copier = trade_copier
        self.host = host
        self.port = port
        self.app = None
    
    def setup_routes(self):
        """Setup API routes"""
        from flask import Flask, request, jsonify
        
        self.app = Flask(__name__)
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'copying_active': self.trade_copier.running
            })
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            stats = self.trade_copier.get_copy_statistics()
            return jsonify(stats)
        
        @self.app.route('/api/masters', methods=['GET'])
        def get_masters():
            masters = self.trade_copier.db.get_active_masters()
            return jsonify([asdict(m) for m in masters])
        
        @self.app.route('/api/masters/<master_id>/slaves', methods=['GET'])
        def get_master_slaves(master_id: str):
            slaves = self.trade_copier.db.get_slave_accounts(master_id)
            return jsonify([asdict(s) for s in slaves])
        
        @self.app.route('/api/performance/<account_id>', methods=['GET'])
        def get_performance(account_id: str):
            days = request.args.get('days', 30, type=int)
            report = self.trade_copier.get_performance_report(account_id, days)
            return jsonify(report)
    
    def start(self):
        """Start the API server"""
        self.setup_routes()
        if self.app:
            self.app.run(host=self.host, port=self.port, debug=False)

# Example usage
def example_usage():
    """
    Example usage of the copy trading system
    """
    
    # Configuration
    config = {
        'copy_interval': 1,  # seconds
        'monitor_interval': 300,  # 5 minutes
        'db_path': 'copy_trading.db'
    }
    
    # Create trade copier
    copier = TradeCopier(config)
    
    # Add callbacks
    def on_trade_copied(trade: CopyTrade, master: MasterAccount, slave: SlaveAccount):
        print(f"Trade copied: {trade.symbol} {trade.volume} from master {master.account_id} to slave {slave.account_id}")
    
    def on_error(error: Exception, master_trade: Dict, master: MasterAccount, slave: SlaveAccount):
        print(f"Error copying trade: {error}")
    
    copier.add_trade_callback(on_trade_copied)
    copier.add_error_handler(on_error)
    
    # Create sample master account
    master = MasterAccount(
        account_id="master_001",
        name="Master Account 1",
        broker="MetaTrader",
        balance=10000.0,
        equity=10500.0,
        leverage=100,
        is_active=True,
        copy_mode=CopyMode.PROPORTIONAL,
        risk_multiplier=1.0,
        max_slaves=10,
        performance_fee=0.1,
        minimum_balance=1000.0,
        created_at=datetime.now(),
        last_update=datetime.now()
    )
    
    # Create sample slave account
    slave = SlaveAccount(
        account_id="slave_001",
        name="Slave Account 1",
        broker="MetaTrader",
        balance=5000.0,
        equity=5200.0,
        leverage=100,
        is_active=True,
        master_account_id="master_001",
        copy_mode=CopyMode.PROPORTIONAL,
        risk_multiplier=0.8,
        max_trades=50,
        max_lot_size=1.0,
        minimum_balance=500.0,
        performance_fee=0.05,
        created_at=datetime.now(),
        last_update=datetime.now()
    )
    
    # Add accounts to database
    copier.db.add_master_account(master)
    copier.db.add_slave_account(slave)
    
    # Start copying
    print("Starting copy trading...")
    copier.start_copying()
    
    # Let it run for a while
    time.sleep(10)
    
    # Get statistics
    stats = copier.get_copy_statistics()
    print(f"Copy statistics: {stats}")
    
    # Stop copying
    print("Stopping copy trading...")
    copier.stop_copying()

if __name__ == "__main__":
    example_usage()
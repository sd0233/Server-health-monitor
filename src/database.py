"""
Database operations for Server Health Monitor
Uses SQLite for simplicity
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import config

logger = logging.getLogger(__name__)


class Database:
    """SQLite Database Handler"""
    
    def __init__(self, db_path: str = None):
        """Initialize database"""
        self.db_path = db_path or config.DB_PATH
        self._create_tables()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Servers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_server 
                ON metrics(server_id, collected_at)
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    is_resolved INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            conn.commit()
            logger.info("Database tables created successfully")
    
    # ========== SERVER OPERATIONS ==========
    
    def add_server(self, hostname: str, ip_address: str = None) -> int:
        """Add server or return existing ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute(
                'SELECT id FROM servers WHERE hostname = ?', 
                (hostname,)
            )
            row = cursor.fetchone()
            
            if row:
                return row['id']
            
            # Insert new
            cursor.execute(
                'INSERT INTO servers (hostname, ip_address) VALUES (?, ?)',
                (hostname, ip_address)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_all_servers(self) -> List[Dict]:
        """Get all servers"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM servers')
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== METRICS OPERATIONS ==========
    
    def save_metrics(self, server_id: int, metrics: Dict[str, float]):
        """Save multiple metrics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for metric_type, value in metrics.items():
                cursor.execute('''
                    INSERT INTO metrics (server_id, metric_type, metric_value)
                    VALUES (?, ?, ?)
                ''', (server_id, metric_type, value))
            
            conn.commit()
            logger.debug(f"Saved {len(metrics)} metrics for server {server_id}")
    
    def get_latest_metrics(self, server_id: int) -> Dict:
        """Get latest metrics for a server"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metric_type, metric_value, collected_at
                FROM metrics
                WHERE server_id = ?
                ORDER BY collected_at DESC
                LIMIT 10
            ''', (server_id,))
            
            result = {}
            for row in cursor.fetchall():
                if row['metric_type'] not in result:
                    result[row['metric_type']] = {
                        'value': row['metric_value'],
                        'collected_at': row['collected_at']
                    }
            
            return result
    
    def get_metric_history(self, server_id: int, metric_type: str, 
                          hours: int = 24) -> List[Dict]:
        """Get metric history"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metric_value, collected_at
                FROM metrics
                WHERE server_id = ?
                AND metric_type = ?
                AND collected_at >= datetime('now', ?)
                ORDER BY collected_at ASC
            ''', (server_id, metric_type, f'-{hours} hours'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== ALERT OPERATIONS ==========
    
    def create_alert(self, server_id: int, alert_type: str, 
                    severity: str, message: str) -> int:
        """Create new alert"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (server_id, alert_type, severity, message)
                VALUES (?, ?, ?, ?)
            ''', (server_id, alert_type, severity, message))
            
            conn.commit()
            logger.warning(f"Alert created: {severity} - {message}")
            return cursor.lastrowid
    
    def get_unresolved_alerts(self) -> List[Dict]:
        """Get all unresolved alerts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.*, s.hostname
                FROM alerts a
                JOIN servers s ON a.server_id = s.id
                WHERE a.is_resolved = 0
                ORDER BY a.created_at DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
    
    # ========== DASHBOARD ==========
    
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Server count
            cursor.execute('SELECT COUNT(*) as count FROM servers')
            server_count = cursor.fetchone()['count']
            
            # Unresolved alerts
            cursor.execute(
                'SELECT COUNT(*) as count FROM alerts WHERE is_resolved = 0'
            )
            alert_count = cursor.fetchone()['count']
            
            return {
                'total_servers': server_count,
                'unresolved_alerts': alert_count
            }


# Test the database
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    # Create database instance
    db = Database('test.db')
    
    # Add a server
    server_id = db.add_server('localhost', '127.0.0.1')
    print(f"Server ID: {server_id}")
    
    # Save metrics
    db.save_metrics(server_id, {
        'cpu_usage': 45.5,
        'memory_usage': 62.3,
        'disk_usage': 55.0
    })
    
    # Get metrics
    metrics = db.get_latest_metrics(server_id)
    print(f"Metrics: {metrics}")
    
    # Get summary
    summary = db.get_dashboard_summary()
    print(f"Summary: {summary}")
    
    print("✅ Database test passed!")
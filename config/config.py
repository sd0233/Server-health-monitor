"""
Configuration settings for Server Health Monitor
"""

import os

class Config:
    """Application configuration"""
    
    # Database (using SQLite for simplicity)
    DB_PATH = os.getenv('DB_PATH', 'monitoring.db')
    
    # Alert Thresholds
    CPU_WARNING = float(os.getenv('CPU_WARNING', 70))
    CPU_CRITICAL = float(os.getenv('CPU_CRITICAL', 90))
    MEMORY_WARNING = float(os.getenv('MEMORY_WARNING', 75))
    MEMORY_CRITICAL = float(os.getenv('MEMORY_CRITICAL', 90))
    DISK_WARNING = float(os.getenv('DISK_WARNING', 80))
    DISK_CRITICAL = float(os.getenv('DISK_CRITICAL', 95))
    
    # Monitoring interval (seconds)
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))
    
    # Services to monitor
    SERVICES_TO_MONITOR = ['ssh', 'cron']
    
    # Slack Configuration
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_DEBUG = os.getenv('API_DEBUG', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')


# Create instance
config = Config()
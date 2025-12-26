"""
Main application - Server Health Monitor
"""

import time
import logging
import signal
import sys
import os

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from src.database import Database
from src.metrics_collector import MetricsCollector
from src.alerting import AlertManager

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
db = Database()
collector = MetricsCollector()
alert_manager = AlertManager()

# Flag for graceful shutdown
running = True


def signal_handler(sig, frame):
    """Handle shutdown"""
    global running
    logger.info("Shutting down...")
    running = False


def print_metrics(metrics):
    """Print metrics to console"""
    print("\n" + "=" * 50)
    print(f"🖥️  Server: {metrics['hostname']}")
    print(f"📅 Time: {metrics['timestamp']}")
    print("-" * 50)
    print(f"💻 CPU Usage:    {metrics['metrics']['cpu_usage']:.1f}%")
    print(f"🧠 Memory Usage: {metrics['metrics']['memory_usage']:.1f}%")
    print(f"💾 Disk Usage:   {metrics['metrics']['disk_usage']:.1f}%")
    print(f"📊 Load Average: {metrics['metrics']['load_average']['load_1min']}")
    print(f"⏱️  Uptime:       {metrics['metrics']['uptime']}")
    print("=" * 50)


def monitoring_loop():
    """Main monitoring loop"""
    global running
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    iteration = 0
    
    while running:
        iteration += 1
        logger.info(f"Monitoring iteration #{iteration}")
        
        try:
            # Collect metrics
            metrics = collector.collect_all()
            
            # Print to console
            print_metrics(metrics)
            
            # Add server to database
            server_id = db.add_server(
                metrics['hostname'],
                metrics['ip_address']
            )
            
            # Save metrics
            db.save_metrics(server_id, {
                'cpu_usage': metrics['metrics']['cpu_usage'],
                'memory_usage': metrics['metrics']['memory_usage'],
                'disk_usage': metrics['metrics']['disk_usage']
            })
            
            # Check thresholds
            alerts = alert_manager.check_thresholds(metrics['metrics'])
            
            # Check services
            services = collector.check_services(config.SERVICES_TO_MONITOR)
            service_alerts = alert_manager.check_services(services)
            alerts.extend(service_alerts)
            
            # Process alerts
            for alert in alerts:
                db.create_alert(
                    server_id,
                    alert['type'],
                    alert['severity'],
                    alert['message']
                )
                alert_manager.send_alert(alert, metrics['hostname'])
            
            # Status
            if alerts:
                print(f"\n⚠️  Generated {len(alerts)} alerts")
            else:
                print("\n✅ All systems normal")
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        
        # Wait for next check
        if running:
            print(f"\n⏳ Next check in {config.CHECK_INTERVAL} seconds...")
            print("   Press Ctrl+C to stop")
            time.sleep(config.CHECK_INTERVAL)
    
    logger.info("Monitoring stopped.")


def main():
    """Entry point"""
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║       🖥️  SERVER HEALTH MONITOR v1.0                 ║
║                                                       ║
║       Monitoring: CPU, Memory, Disk, Services        ║
║       Press Ctrl+C to stop                           ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    logger.info("Starting Server Health Monitor...")
    logger.info(f"Check interval: {config.CHECK_INTERVAL} seconds")
    
    monitoring_loop()


if __name__ == '__main__':
    main()
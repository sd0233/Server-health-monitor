"""
Alerting module - Check thresholds and send alerts
"""

import requests
import logging
from typing import Dict, List
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import config

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.slack_webhook = config.SLACK_WEBHOOK_URL
    
    def check_thresholds(self, metrics: Dict) -> List[Dict]:
        """Check metrics against thresholds"""
        alerts = []
        
        cpu = metrics.get('cpu_usage', 0)
        memory = metrics.get('memory_usage', 0)
        disk = metrics.get('disk_usage', 0)
        
        # Check CPU
        if cpu >= config.CPU_CRITICAL:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'critical',
                'message': f'CPU usage critical: {cpu}%'
            })
        elif cpu >= config.CPU_WARNING:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f'CPU usage warning: {cpu}%'
            })
        
        # Check Memory
        if memory >= config.MEMORY_CRITICAL:
            alerts.append({
                'type': 'memory_high',
                'severity': 'critical',
                'message': f'Memory usage critical: {memory}%'
            })
        elif memory >= config.MEMORY_WARNING:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f'Memory usage warning: {memory}%'
            })
        
        # Check Disk
        if disk >= config.DISK_CRITICAL:
            alerts.append({
                'type': 'disk_high',
                'severity': 'critical',
                'message': f'Disk usage critical: {disk}%'
            })
        elif disk >= config.DISK_WARNING:
            alerts.append({
                'type': 'disk_high',
                'severity': 'warning',
                'message': f'Disk usage warning: {disk}%'
            })
        
        return alerts
    
    def check_services(self, services: Dict[str, str]) -> List[Dict]:
        """Check service status"""
        alerts = []
        
        for service, status in services.items():
            if status != 'active':
                alerts.append({
                    'type': 'service_down',
                    'severity': 'critical',
                    'message': f'Service {service} is {status}'
                })
        
        return alerts
    
    def send_slack_alert(self, alert: Dict, hostname: str) -> bool:
        """Send alert to Slack"""
        if not self.slack_webhook:
            logger.debug("Slack webhook not configured")
            return False
        
        try:
            emoji = '🚨' if alert['severity'] == 'critical' else '⚠️'
            color = '#FF0000' if alert['severity'] == 'critical' else '#FFA500'
            
            message = {
                "attachments": [{
                    "color": color,
                    "title": f"{emoji} Server Alert",
                    "fields": [
                        {"title": "Server", "value": hostname, "short": True},
                        {"title": "Severity", "value": alert['severity'], "short": True},
                        {"title": "Message", "value": alert['message'], "short": False}
                    ],
                    "footer": f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            }
            
            response = requests.post(self.slack_webhook, json=message, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Slack alert sent: {alert['message']}")
                return True
            
        except Exception as e:
            logger.error(f"Slack error: {e}")
        
        return False
    
    def send_alert(self, alert: Dict, hostname: str):
        """Send alert through all channels"""
        # Console output
        severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️"
        print(f"\n{severity_icon} ALERT: {alert['message']}")
        
        # Slack
        self.send_slack_alert(alert, hostname)


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    alert_manager = AlertManager()
    
    # Test with high values
    test_metrics = {
        'cpu_usage': 85,
        'memory_usage': 92,
        'disk_usage': 70
    }
    
    alerts = alert_manager.check_thresholds(test_metrics)
    
    print("Generated Alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['message']}")
    
    print("\n✅ Alerting test passed!")
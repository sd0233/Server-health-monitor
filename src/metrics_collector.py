"""
Metrics collection module
Collects system metrics using Python
"""

import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects system metrics"""
    
    def __init__(self):
        self.hostname = self._get_hostname()
        self.ip_address = self._get_ip()
    
    def _run_command(self, command: str) -> str:
        """Run shell command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return ""
    
    def _get_hostname(self) -> str:
        """Get system hostname"""
        return self._run_command("hostname") or "unknown"
    
    def _get_ip(self) -> str:
        """Get IP address"""
        return self._run_command("hostname -I | awk '{print $1}'") or "unknown"
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            output = self._run_command(
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"
            )
            return float(output) if output else 0.0
        except ValueError:
            return 0.0
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage"""
        try:
            output = self._run_command("free -m | awk 'NR==2'")
            parts = output.split()
            
            if len(parts) >= 3:
                total = int(parts[1])
                used = int(parts[2])
                percent = round((used / total) * 100, 1) if total > 0 else 0
                
                return {
                    'total_mb': total,
                    'used_mb': used,
                    'free_mb': total - used,
                    'usage_percent': percent
                }
        except Exception as e:
            logger.error(f"Memory error: {e}")
        
        return {'usage_percent': 0}
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage"""
        try:
            output = self._run_command("df -BG / | awk 'NR==2'")
            parts = output.split()
            
            if len(parts) >= 5:
                total = int(parts[1].replace('G', ''))
                used = int(parts[2].replace('G', ''))
                percent = int(parts[4].replace('%', ''))
                
                return {
                    'total_gb': total,
                    'used_gb': used,
                    'free_gb': total - used,
                    'usage_percent': percent
                }
        except Exception as e:
            logger.error(f"Disk error: {e}")
        
        return {'usage_percent': 0}
    
    def get_load_average(self) -> Dict[str, float]:
        """Get system load average"""
        try:
            output = self._run_command("cat /proc/loadavg")
            parts = output.split()
            
            return {
                'load_1min': float(parts[0]),
                'load_5min': float(parts[1]),
                'load_15min': float(parts[2])
            }
        except:
            return {'load_1min': 0, 'load_5min': 0, 'load_15min': 0}
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        return self._run_command("uptime -p") or "unknown"
    
    def get_process_count(self) -> int:
        """Get running process count"""
        try:
            output = self._run_command("ps aux | wc -l")
            return int(output) - 1
        except:
            return 0
    
    def check_service(self, service_name: str) -> str:
        """Check if service is running"""
        try:
            result = subprocess.run(
                f"systemctl is-active {service_name}",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def check_services(self, services: List[str]) -> Dict[str, str]:
        """Check multiple services"""
        return {svc: self.check_service(svc) for svc in services}
    
    def collect_all(self) -> Dict[str, Any]:
        """Collect all metrics"""
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        
        return {
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'metrics': {
                'cpu_usage': self.get_cpu_usage(),
                'memory_usage': memory.get('usage_percent', 0),
                'memory_details': memory,
                'disk_usage': disk.get('usage_percent', 0),
                'disk_details': disk,
                'load_average': self.get_load_average(),
                'uptime': self.get_uptime(),
                'process_count': self.get_process_count()
            }
        }


# Test
if __name__ == '__main__':
    import json
    
    collector = MetricsCollector()
    
    print("Testing Metrics Collector...")
    print(f"Hostname: {collector.hostname}")
    print(f"CPU: {collector.get_cpu_usage()}%")
    print(f"Memory: {collector.get_memory_usage()}")
    print(f"Disk: {collector.get_disk_usage()}")
    print(f"Load: {collector.get_load_average()}")
    print(f"Uptime: {collector.get_uptime()}")
    
    print("\nAll metrics:")
    all_metrics = collector.collect_all()
    print(json.dumps(all_metrics, indent=2))
    
    print("\n✅ Metrics collector test passed!")
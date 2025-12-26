#!/bin/bash
# ============================================
# Script: collect_metrics.sh
# Description: Collects system metrics
# Author: Your Name
# ============================================

# Get CPU usage
get_cpu() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'.' -f1
}

# Get Memory usage
get_memory() {
    free | awk 'NR==2{printf "%.1f", $3*100/$2}'
}

# Get Disk usage
get_disk() {
    df -h / | awk 'NR==2{print $5}' | tr -d '%'
}

# Get hostname
get_hostname() {
    hostname
}

# Main output as JSON
cat << EOF
{
    "hostname": "$(get_hostname)",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "cpu_usage": $(get_cpu),
    "memory_usage": $(get_memory),
    "disk_usage": $(get_disk)
}
EOF
# 🖥️ Server Health Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Shell](https://img.shields.io/badge/Shell_Script-Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A comprehensive real-time server monitoring solution with REST API and intelligent alerting system**

[Features](#-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[API Documentation](#-api-documentation) •
[Project Structure](#-project-structure)

</div>

---

## 📋 Overview

Server Health Monitor is a production-ready monitoring solution that tracks system metrics, detects anomalies, and sends real-time alerts. Built with Python, Shell scripting, and Flask, it demonstrates real-world application support and DevOps skills.

### 🎯 What This Project Does

- **Collects Metrics**: CPU, Memory, Disk usage in real-time
- **Stores Data**: SQLite database for historical analysis
- **REST API**: Query metrics and manage alerts programmatically
- **Smart Alerting**: Configurable thresholds with Slack notifications
- **Service Monitoring**: Track critical services (SSH, MySQL, etc.)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Real-time Metrics** | Monitor CPU, Memory, Disk, Load Average, Process Count |
| 🔔 **Smart Alerts** | Configurable warning/critical thresholds |
| 📡 **REST API** | 10+ endpoints for metrics, alerts, and dashboard |
| 💾 **Data Persistence** | SQLite database with optimized queries |
| 🔧 **Service Monitoring** | Track status of critical system services |
| 📱 **Slack Integration** | Real-time alert notifications |
| 📈 **Historical Data** | Query trends and patterns over time |
| ⚙️ **Configurable** | Environment variables for easy customization |

---

## 🛠️ Technologies Used

<table>
<tr>
<td align="center" width="150">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="50" height="50"/>
<br><b>Python 3.8+</b>
<br><sub>Core Application</sub>
</td>
<td align="center" width="150">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" width="50" height="50"/>
<br><b>Flask</b>
<br><sub>REST API</sub>
</td>
<td align="center" width="150">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" width="50" height="50"/>
<br><b>SQLite</b>
<br><sub>Database</sub>
</td>
<td align="center" width="150">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bash/bash-original.svg" width="50" height="50"/>
<br><b>Shell Script</b>
<br><sub>Metrics Collection</sub>
</td>
<td align="center" width="150">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg" width="50" height="50"/>
<br><b>Linux</b>
<br><sub>System Monitoring</sub>
</td>
</tr>
</table>

---

## 📁 Project Structure
server-health-monitor/
│
├── 📁 config/
│ └── config.py # Configuration settings
│
├── 📁 scripts/
│ └── collect_metrics.sh # Shell script for metrics collection
│
├── 📁 src/
│ ├── init.py
│ ├── main.py # Main monitoring application
│ ├── database.py # Database operations (SQLite)
│ ├── metrics_collector.py # Python metrics collection
│ ├── alerting.py # Alert management & notifications
│ └── api.py # Flask REST API
│
├── 📁 sql/
│ ├── create_tables.sql # Database schema
│ └── queries.sql # Common SQL queries
│
├── 📁 tests/
│ └── api.http # API test requests
│
├── 📁 logs/
│ └── app.log # Application logs
│
├── 📁 docs/
│ └── architecture.md # System architecture
│
├── requirements.txt # Python dependencies
├── .gitignore # Git ignore rules
└── README.md # This file


---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Linux/WSL environment
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/server-health-monitor.git
cd server-health-monitor


Endpoints

Method	Endpoint	Description
GET	/	API information and available endpoints
GET	/health	Health check endpoint
GET	/api/metrics	Get current server metrics
GET	/api/metrics/history/<type>	Get historical metrics
GET	/api/servers	List all monitored servers
GET	/api/alerts	Get unresolved alerts
POST	/api/alerts/<id>/resolve	Resolve an alert
GET	/api/dashboard	Get dashboard summary
GET	/api/services	Get service status
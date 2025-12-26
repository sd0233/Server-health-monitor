"""
REST API for Server Health Monitor
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import os
import sys

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from src.database import Database
from src.metrics_collector import MetricsCollector

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize components
db = Database()
collector = MetricsCollector()

logger = logging.getLogger(__name__)


# ============ API ROUTES ============

@app.route('/')
def home():
    """API Home"""
    return jsonify({
        'name': 'Server Health Monitor API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'GET /': 'This message',
            'GET /health': 'Health check',
            'GET /api/metrics': 'Current metrics',
            'GET /api/metrics/history/<type>': 'Metric history',
            'GET /api/servers': 'List servers',
            'GET /api/alerts': 'Unresolved alerts',
            'POST /api/alerts/<id>/resolve': 'Resolve alert',
            'GET /api/dashboard': 'Dashboard data'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/metrics')
def get_metrics():
    """Get current server metrics"""
    try:
        metrics = collector.collect_all()
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metrics/history/<metric_type>')
def get_metric_history(metric_type):
    """Get historical data for a metric"""
    try:
        hours = request.args.get('hours', 24, type=int)
        server_id = request.args.get('server_id', 1, type=int)
        
        history = db.get_metric_history(server_id, metric_type, hours)
        
        return jsonify({
            'success': True,
            'data': {
                'metric_type': metric_type,
                'hours': hours,
                'history': history
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/servers')
def get_servers():
    """Get all servers"""
    try:
        servers = db.get_all_servers()
        return jsonify({
            'success': True,
            'data': servers
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts')
def get_alerts():
    """Get unresolved alerts"""
    try:
        alerts = db.get_unresolved_alerts()
        return jsonify({
            'success': True,
            'data': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        db.resolve_alert(alert_id)
        return jsonify({
            'success': True,
            'message': f'Alert {alert_id} resolved'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard')
def get_dashboard():
    """Get dashboard summary"""
    try:
        summary = db.get_dashboard_summary()
        current = collector.collect_all()
        alerts = db.get_unresolved_alerts()
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'current_metrics': current['metrics'],
                'recent_alerts': alerts[:5],
                'timestamp': current['timestamp']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services')
def get_services():
    """Get service status"""
    try:
        services = collector.check_services(config.SERVICES_TO_MONITOR)
        return jsonify({
            'success': True,
            'data': services
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Server error'}), 500


# Run
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print("\n🚀 Starting Server Health Monitor API...")
    print(f"📡 API running at: http://localhost:{config.API_PORT}")
    print("📋 Endpoints: http://localhost:5000/")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.API_DEBUG
    )
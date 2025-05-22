#!/usr/bin/env python3

"""
LogLama Web Interface

This module provides a Flask web application for viewing and querying logs stored in SQLite database.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from flask import Flask, render_template, request, jsonify, g

from loglama.config.env_loader import load_env, get_env
from loglama.core.logger import setup_logging, get_logger


def get_db(db_path: str):
    """Get database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db


def create_app(db_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Flask:
    """Create Flask application for LogLama web interface.
    
    Args:
        db_path: Path to SQLite database file. If None, it will be loaded from environment variables.
        config: Additional configuration options.
        
    Returns:
        Flask application instance.
    """
    # Load environment variables
    load_env(verbose=False)
    
    # Initialize logging
    logger = setup_logging(name="loglama_web", level="INFO")
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DB_PATH=db_path or get_env("LOGLAMA_DB_PATH", "./logs/loglama.db"),
        PAGE_SIZE=int(get_env("LOGLAMA_WEB_PAGE_SIZE", "100")),
        DEBUG=get_env("LOGLAMA_WEB_DEBUG", "false").lower() in ("true", "yes", "1"),
    )
    
    # Apply additional configuration if provided
    if config:
        app.config.update(config)
    
    # Ensure database exists
    db_path = app.config["DB_PATH"]
    if not os.path.exists(db_path):
        logger.warning(f"Database file not found at {db_path}")
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created directory {db_dir}")
    
    # Register teardown function
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
    
    # Routes
    @app.route('/')
    def index():
        """Main page."""
        return render_template('index.html')
    
    @app.route('/api/logs')
    def get_logs():
        """Get logs from database."""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', app.config['PAGE_SIZE']))
            level = request.args.get('level', None)
            search = request.args.get('search', None)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            component = request.args.get('component', None)
            
            # Build query
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if level:
                query += " AND level = ?"
                params.append(level.upper())
            
            if search:
                query += " AND (message LIKE ? OR logger_name LIKE ? OR context LIKE ?)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            if component:
                query += " AND logger_name LIKE ?"
                params.append(f"{component}%")
            
            # Add ordering and pagination
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])
            
            # Execute query
            db = get_db(app.config['DB_PATH'])
            cursor = db.cursor()
            cursor.execute(query, params)
            logs = [dict(row) for row in cursor.fetchall()]
            
            # Get total count for pagination
            count_query = query.replace("SELECT *", "SELECT COUNT(*)").split("ORDER BY")[0]
            cursor.execute(count_query, params[:-2])
            total = cursor.fetchone()[0]
            
            return jsonify({
                'logs': logs,
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            })
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def get_stats():
        """Get log statistics."""
        try:
            db = get_db(app.config['DB_PATH'])
            cursor = db.cursor()
            
            # Get level counts
            cursor.execute("SELECT level, COUNT(*) as count FROM logs GROUP BY level")
            level_counts = {row['level']: row['count'] for row in cursor.fetchall()}
            
            # Get component counts
            cursor.execute("SELECT logger_name, COUNT(*) as count FROM logs GROUP BY logger_name")
            component_counts = {row['logger_name']: row['count'] for row in cursor.fetchall()}
            
            # Get date range
            cursor.execute("SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM logs")
            date_range = dict(cursor.fetchone())
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM logs")
            total = cursor.fetchone()['count']
            
            return jsonify({
                'level_counts': level_counts,
                'component_counts': component_counts,
                'date_range': date_range,
                'total': total
            })
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/levels')
    def get_levels():
        """Get available log levels."""
        try:
            db = get_db(app.config['DB_PATH'])
            cursor = db.cursor()
            cursor.execute("SELECT DISTINCT level FROM logs")
            levels = [row['level'] for row in cursor.fetchall()]
            return jsonify(levels)
        except Exception as e:
            logger.error(f"Error getting levels: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/components')
    def get_components():
        """Get available components (logger names)."""
        try:
            db = get_db(app.config['DB_PATH'])
            cursor = db.cursor()
            cursor.execute("SELECT DISTINCT logger_name FROM logs")
            components = [row['logger_name'] for row in cursor.fetchall()]
            return jsonify(components)
        except Exception as e:
            logger.error(f"Error getting components: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/log/<int:log_id>')
    def get_log(log_id):
        """Get log details by ID."""
        try:
            db = get_db(app.config['DB_PATH'])
            cursor = db.cursor()
            cursor.execute("SELECT * FROM logs WHERE id = ?", [log_id])
            log = dict(cursor.fetchone() or {})
            return jsonify(log)
        except Exception as e:
            logger.error(f"Error getting log {log_id}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/logs/clear', methods=['POST'])
    def clear_logs():
        """Clear all logs from the database."""
        try:
            db = get_db(app.config['DB_PATH'])
            cursor = db.cursor()
            cursor.execute("DELETE FROM logs")
            db.commit()
            logger.info("All logs cleared from database")
            return jsonify({'success': True, 'message': 'All logs cleared successfully'})
        except Exception as e:
            logger.error(f"Error clearing logs: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    logger.info(f"LogLama Web Interface initialized with database at {db_path}")
    return app


def run_app(host: str = '127.0.0.1', port: int = 5000, db_path: Optional[str] = None):
    """Run the LogLama web interface.
    
    Args:
        host: Host to bind to.
        port: Port to listen on.
        db_path: Path to SQLite database file.
    """
    app = create_app(db_path=db_path)
    app.run(host=host, port=port, debug=app.config['DEBUG'])


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='LogLama Web Interface')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--db', help='Path to SQLite database file')
    
    args = parser.parse_args()
    run_app(host=args.host, port=args.port, db_path=args.db)

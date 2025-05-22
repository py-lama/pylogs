#!/usr/bin/env python3

"""
Integration tests for PyLogs web interface.
"""

import os
import sys
import unittest
import tempfile
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pylogs.web.app import create_app
from pylogs.core.logger import setup_logging


class TestWebInterface(unittest.TestCase):
    """Test the PyLogs web interface."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for logs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.temp_dir.name, "test.db")
        
        # Create a test database with sample logs
        self.create_test_database()
        
        # Create a Flask test client
        self.app = create_app(db_path=self.db_file, config={'TESTING': True})
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def create_test_database(self):
        """Create a test database with sample logs."""
        # Create the database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create the logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            logger_name TEXT NOT NULL,
            message TEXT NOT NULL,
            thread_name TEXT,
            process_name TEXT,
            context TEXT,
            file_path TEXT,
            line_number INTEGER
        )
        """)
        
        # Insert sample logs
        now = datetime.now().isoformat()
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        sample_logs = [
            (now, "DEBUG", "test.component1", "Debug message from component 1", "MainThread", "Main", "{}", "test.py", 10),
            (now, "INFO", "test.component1", "Info message from component 1", "MainThread", "Main", "{}", "test.py", 11),
            (now, "WARNING", "test.component1", "Warning message from component 1", "MainThread", "Main", "{}", "test.py", 12),
            (now, "ERROR", "test.component1", "Error message from component 1", "MainThread", "Main", "{\"user\": \"test_user\", \"request_id\": \"12345\"}", "test.py", 13),
            (now, "CRITICAL", "test.component1", "Critical message from component 1", "MainThread", "Main", "{\"user\": \"test_user\", \"request_id\": \"12345\"}", "test.py", 14),
            (yesterday, "INFO", "test.component2", "Info message from component 2", "WorkerThread", "Worker", "{}", "worker.py", 20),
            (yesterday, "WARNING", "test.component2", "Warning message from component 2", "WorkerThread", "Worker", "{}", "worker.py", 21),
            (yesterday, "ERROR", "test.component2", "Error message from component 2", "WorkerThread", "Worker", "{\"operation\": \"test_operation\"}", "worker.py", 22),
        ]
        
        cursor.executemany("""
        INSERT INTO logs (timestamp, level, logger_name, message, thread_name, process_name, context, file_path, line_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_logs)
        
        conn.commit()
        conn.close()
    
    def test_index_page(self):
        """Test the index page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PyLogs Viewer', response.data)
    
    def test_get_logs_api(self):
        """Test the logs API endpoint."""
        response = self.client.get('/api/logs')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('logs', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('page_size', data)
        self.assertIn('pages', data)
        
        # Check that we got all logs
        self.assertEqual(data['total'], 8)
        self.assertEqual(len(data['logs']), 8)
    
    def test_get_logs_with_filters(self):
        """Test the logs API with filters."""
        # Test level filter
        response = self.client.get('/api/logs?level=ERROR')
        data = json.loads(response.data)
        self.assertEqual(len(data['logs']), 2)
        for log in data['logs']:
            self.assertEqual(log['level'], 'ERROR')
        
        # Test component filter
        response = self.client.get('/api/logs?component=test.component1')
        data = json.loads(response.data)
        self.assertEqual(len(data['logs']), 5)
        for log in data['logs']:
            self.assertEqual(log['logger_name'], 'test.component1')
        
        # Test search filter
        response = self.client.get('/api/logs?search=Critical')
        data = json.loads(response.data)
        self.assertEqual(len(data['logs']), 1)
        self.assertIn('Critical', data['logs'][0]['message'])
        
        # Test combined filters
        response = self.client.get('/api/logs?level=ERROR&component=test.component2')
        data = json.loads(response.data)
        self.assertEqual(len(data['logs']), 1)
        self.assertEqual(data['logs'][0]['level'], 'ERROR')
        self.assertEqual(data['logs'][0]['logger_name'], 'test.component2')
    
    def test_get_stats_api(self):
        """Test the stats API endpoint."""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('level_counts', data)
        self.assertIn('component_counts', data)
        self.assertIn('date_range', data)
        self.assertIn('total', data)
        
        # Check level counts
        self.assertEqual(data['level_counts']['DEBUG'], 1)
        self.assertEqual(data['level_counts']['INFO'], 2)
        self.assertEqual(data['level_counts']['WARNING'], 2)
        self.assertEqual(data['level_counts']['ERROR'], 2)
        self.assertEqual(data['level_counts']['CRITICAL'], 1)
        
        # Check component counts
        self.assertEqual(data['component_counts']['test.component1'], 5)
        self.assertEqual(data['component_counts']['test.component2'], 3)
        
        # Check total
        self.assertEqual(data['total'], 8)
    
    def test_get_levels_api(self):
        """Test the levels API endpoint."""
        response = self.client.get('/api/levels')
        self.assertEqual(response.status_code, 200)
        
        levels = json.loads(response.data)
        self.assertIsInstance(levels, list)
        self.assertEqual(len(levels), 5)
        self.assertIn('DEBUG', levels)
        self.assertIn('INFO', levels)
        self.assertIn('WARNING', levels)
        self.assertIn('ERROR', levels)
        self.assertIn('CRITICAL', levels)
    
    def test_get_components_api(self):
        """Test the components API endpoint."""
        response = self.client.get('/api/components')
        self.assertEqual(response.status_code, 200)
        
        components = json.loads(response.data)
        self.assertIsInstance(components, list)
        self.assertEqual(len(components), 2)
        self.assertIn('test.component1', components)
        self.assertIn('test.component2', components)
    
    def test_get_log_detail_api(self):
        """Test the log detail API endpoint."""
        # Get the ID of a log with context
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM logs WHERE message LIKE ? LIMIT 1", ("%Critical%",))
        log_id = cursor.fetchone()['id']
        conn.close()
        
        # Get the log detail
        response = self.client.get(f'/api/log/{log_id}')
        self.assertEqual(response.status_code, 200)
        
        log = json.loads(response.data)
        self.assertEqual(log['id'], log_id)
        self.assertEqual(log['level'], 'CRITICAL')
        self.assertEqual(log['logger_name'], 'test.component1')
        self.assertIn('Critical message', log['message'])
        
        # Check context
        context = json.loads(log['context'])
        self.assertEqual(context['user'], 'test_user')
        self.assertEqual(context['request_id'], '12345')
    
    def test_pagination(self):
        """Test pagination of logs."""
        # Add more logs to test pagination
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        additional_logs = []
        for i in range(50):
            additional_logs.append((now, "INFO", "test.pagination", f"Pagination test log {i}", "MainThread", "Main", "{}", "test.py", 100 + i))
        
        cursor.executemany("""
        INSERT INTO logs (timestamp, level, logger_name, message, thread_name, process_name, context, file_path, line_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, additional_logs)
        
        conn.commit()
        conn.close()
        
        # Test first page with page_size=10
        response = self.client.get('/api/logs?page=1&page_size=10')
        data = json.loads(response.data)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 10)
        self.assertEqual(len(data['logs']), 10)
        self.assertEqual(data['total'], 58)  # 8 original + 50 new logs
        self.assertEqual(data['pages'], 6)  # 58 logs / 10 per page = 6 pages
        
        # Test second page
        response = self.client.get('/api/logs?page=2&page_size=10')
        data = json.loads(response.data)
        self.assertEqual(data['page'], 2)
        self.assertEqual(len(data['logs']), 10)
        
        # Test last page
        response = self.client.get('/api/logs?page=6&page_size=10')
        data = json.loads(response.data)
        self.assertEqual(data['page'], 6)
        self.assertEqual(len(data['logs']), 8)  # Only 8 logs on the last page


if __name__ == "__main__":
    unittest.main()

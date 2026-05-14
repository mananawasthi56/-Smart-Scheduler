"""
Phase 4: Historical Data Collection & Persistence
Stores collected metrics for trend analysis and AI model training
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import os


class HistoricalDataCollector:
    """Stores real metrics over time for analysis and training"""
    
    def __init__(self, db_path: str = 'container_metrics.db'):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Container metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS container_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    container_id TEXT NOT NULL,
                    container_name TEXT,
                    cpu_usage REAL,
                    cpu_normalized REAL,
                    memory_usage_mb REAL,
                    memory_limit_mb REAL,
                    memory_percent REAL,
                    image TEXT,
                    status TEXT
                )
            ''')
            
            # Pod placement table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pod_placements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pod_name TEXT NOT NULL,
                    namespace TEXT,
                    node TEXT,
                    cpu_request REAL,
                    memory_request REAL,
                    phase TEXT
                )
            ''')
            
            # Scheduler comparison table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduler_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    comparison_id TEXT,
                    container_id TEXT,
                    current_placement TEXT,
                    ai_recommended_placement TEXT,
                    power_saved_percent REAL,
                    efficiency_gain REAL
                )
            ''')
            
            # Aggregated metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aggregated_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_containers INTEGER,
                    total_cpu_used REAL,
                    total_memory_used_mb REAL,
                    node_capacity_cpu REAL,
                    node_capacity_memory_mb REAL,
                    cpu_utilization_percent REAL,
                    memory_utilization_percent REAL
                )
            ''')
            
            self.conn.commit()
            print("✅ Database initialized successfully")
        
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def save_container_metrics(self, containers: List[Dict]):
        """Save collected container metrics to database"""
        if not self.conn or not containers:
            return
        
        try:
            cursor = self.conn.cursor()
            
            for container in containers:
                cursor.execute('''
                    INSERT INTO container_metrics 
                    (container_id, container_name, cpu_usage, cpu_normalized, 
                     memory_usage_mb, memory_limit_mb, memory_percent, image, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    container.get('id', ''),
                    container.get('name', ''),
                    container.get('cpu_real_percent', 0),
                    container.get('cpu_normalized', 0),
                    container.get('memory_usage_mb', 0),
                    container.get('memory_limit_mb', 0),
                    container.get('memory_percent', 0),
                    container.get('image', ''),
                    container.get('status', '')
                ))
            
            self.conn.commit()
            print(f"✅ Saved {len(containers)} container metrics")
        
        except Exception as e:
            print(f"❌ Error saving container metrics: {e}")
    
    def save_pod_placements(self, pods: List[Dict]):
        """Save pod placement data to database"""
        if not self.conn or not pods:
            return
        
        try:
            cursor = self.conn.cursor()
            
            for pod in pods:
                cursor.execute('''
                    INSERT INTO pod_placements
                    (pod_name, namespace, node, cpu_request, memory_request, phase)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pod.get('pod_name', ''),
                    pod.get('namespace', ''),
                    pod.get('node', ''),
                    pod.get('cpu_request', 0),
                    pod.get('memory_request', 0),
                    pod.get('phase', '')
                ))
            
            self.conn.commit()
            print(f"✅ Saved {len(pods)} pod placements")
        
        except Exception as e:
            print(f"❌ Error saving pod placements: {e}")
    
    def save_aggregated_metrics(self, stats: Dict):
        """Save node-level aggregated statistics"""
        if not self.conn or not stats:
            return
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO aggregated_metrics
                (total_containers, total_cpu_used, total_memory_used_mb,
                 node_capacity_cpu, node_capacity_memory_mb,
                 cpu_utilization_percent, memory_utilization_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats.get('total_containers', 0),
                stats.get('total_cpu_used', 0),
                stats.get('total_memory_used_mb', 0),
                stats.get('node_capacity_cpu', 0),
                stats.get('node_capacity_memory_mb', 0),
                stats.get('utilization_cpu_percent', 0),
                stats.get('utilization_memory_percent', 0)
            ))
            
            self.conn.commit()
            print("✅ Saved aggregated metrics")
        
        except Exception as e:
            print(f"❌ Error saving aggregated metrics: {e}")
    
    def save_comparison_results(self, comparison_id: str, results: Dict):
        """Save scheduler comparison results"""
        if not self.conn or not results:
            return
        
        try:
            cursor = self.conn.cursor()
            
            improvements = results.get('estimated_improvements', [])
            
            for improvement in improvements:
                cursor.execute('''
                    INSERT INTO scheduler_comparisons
                    (comparison_id, container_id, current_placement, 
                     ai_recommended_placement, efficiency_gain)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    comparison_id,
                    improvement.get('pod', ''),
                    improvement.get('current_node', ''),
                    improvement.get('ai_recommended_node', ''),
                    float(improvement.get('estimated_efficiency_gain', '0%').replace('%', '')) / 100
                ))
            
            self.conn.commit()
            print(f"✅ Saved {len(improvements)} comparison results")
        
        except Exception as e:
            print(f"❌ Error saving comparison results: {e}")
    
    def get_historical_data(self, days: int = 7, table: str = 'container_metrics') -> List[Dict]:
        """Retrieve historical data for analysis"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            
            query = f'''
                SELECT * FROM {table}
                WHERE timestamp > datetime('now', '-{days} days')
                ORDER BY timestamp DESC
            '''
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            print(f"❌ Error retrieving historical data: {e}")
            return []
    
    def get_metrics_trend(self, days: int = 7) -> Dict:
        """Get trend analysis for CPU and memory utilization"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # CPU trend
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    AVG(cpu_utilization_percent) as avg_cpu,
                    MAX(cpu_utilization_percent) as max_cpu,
                    MIN(cpu_utilization_percent) as min_cpu
                FROM aggregated_metrics
                WHERE timestamp > datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (days,))
            
            cpu_trend = [dict(row) for row in cursor.fetchall()]
            
            # Memory trend
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    AVG(memory_utilization_percent) as avg_memory,
                    MAX(memory_utilization_percent) as max_memory,
                    MIN(memory_utilization_percent) as min_memory
                FROM aggregated_metrics
                WHERE timestamp > datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (days,))
            
            memory_trend = [dict(row) for row in cursor.fetchall()]
            
            return {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend,
                'period_days': days
            }
        
        except Exception as e:
            print(f"❌ Error calculating trends: {e}")
            return {}
    
    def get_database_statistics(self) -> Dict:
        """Get overall database statistics"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            stats = {}
            
            # Count records in each table
            for table in ['container_metrics', 'pod_placements', 'scheduler_comparisons', 'aggregated_metrics']:
                cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
                count = cursor.fetchone()['count']
                stats[table] = count
            
            # Get date range
            cursor.execute('SELECT MIN(timestamp) as oldest, MAX(timestamp) as newest FROM container_metrics')
            date_range = cursor.fetchone()
            stats['date_range'] = {
                'oldest': date_range['oldest'],
                'newest': date_range['newest']
            }
            
            # Get database size
            db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # Convert to MB
            stats['database_size_mb'] = db_size
            
            return stats
        
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

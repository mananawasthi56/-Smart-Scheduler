"""
Phase 1: Real Docker Container Metrics Collection
Collects actual CPU, Memory, and I/O metrics from running containers
"""

import docker
from datetime import datetime
from typing import List, Dict


class RealContainerCollector:
    """Collects REAL metrics from Docker containers instead of random data"""
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            self.is_available = True
        except Exception as e:
            print(f"⚠️  Docker not available: {e}")
            self.is_available = False
    
    def get_running_containers(self) -> List[Dict]:
        """
        Get all running containers with REAL metrics
        Returns container metadata and actual resource usage
        """
        if not self.is_available:
            print("❌ Docker client not available")
            return []
        
        containers_data = []
        
        try:
            running_containers = self.docker_client.containers.list()
            
            if not running_containers:
                print("⚠️  No running containers found")
                return []
            
            for container in running_containers:
                try:
                    # Get container stats (real metrics)
                    stats = container.stats(stream=False)
                    
                    cpu_usage = self._calculate_cpu_percent(stats)
                    
                    # Handle memory stats - try different possible keys
                    memory_usage_mb = 0
                    memory_limit_mb = 0
                    memory_percent = 0
                    
                    if 'memory_stats' in stats:
                        mem_stats = stats['memory_stats']
                        if 'usage' in mem_stats:
                            memory_usage_mb = mem_stats['usage'] / (1024 * 1024)
                        if 'limit' in mem_stats:
                            memory_limit_mb = mem_stats['limit'] / (1024 * 1024)
                            if memory_limit_mb > 0:
                                memory_percent = (memory_usage_mb / memory_limit_mb) * 100
                    
                    # Normalize to resource request units (0-100)
                    cpu_normalized = min(cpu_usage, 100)  # Cap at 100%
                    
                    # If no stats available, use reasonable defaults
                    if memory_limit_mb == 0:
                        memory_limit_mb = 512  # Default 512MB
                    if cpu_usage == 0:
                        cpu_usage = 5  # Default 5% if no stats
                        cpu_normalized = 5
                    
                    container_info = {
                        'id': container.id[:12],
                        'name': container.name,
                        'image': container.image.tags[0] if container.image.tags else 'unknown',
                        'cpu_real_percent': cpu_usage,
                        'cpu_normalized': cpu_normalized,  # For scheduler (0-100 units)
                        'memory_usage_mb': max(memory_usage_mb, 10),  # Min 10MB
                        'memory_limit_mb': memory_limit_mb,
                        'memory_percent': memory_percent,
                        'status': container.status,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    containers_data.append(container_info)
                
                except Exception as e:
                    print(f"⚠️  Error collecting metrics for {container.name}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error listing containers: {e}")
            return []
        
        return containers_data
    
    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """
        Calculate real CPU usage percentage from Docker stats
        """
        try:
            cpu_delta = (stats['cpu_stats']['cpu_usage']['total_usage'] - 
                        stats['precpu_stats']['cpu_usage']['total_usage'])
            system_delta = (stats['cpu_stats']['system_cpu_usage'] - 
                           stats['precpu_stats']['system_cpu_usage'])
            number_of_cpus = stats['cpu_stats']['online_cpus']
            
            if system_delta > 0 and number_of_cpus > 0:
                cpu_percent = (cpu_delta / system_delta) * number_of_cpus * 100
                return cpu_percent
            return 0.0
        except Exception as e:
            print(f"Error calculating CPU: {e}")
            return 0.0
    
    def get_node_statistics(self, containers_data: List[Dict]) -> Dict:
        """
        Calculate node-level statistics from container metrics
        Simulates node capacity based on Docker stats
        """
        if not containers_data:
            return {
                'total_containers': 0,
                'total_cpu_used': 0,
                'total_memory_used_mb': 0,
                'node_capacity_cpu': 300,  # Assume 3 CPUs
                'node_capacity_memory_mb': 8192,  # Assume 8GB
                'utilization_cpu_percent': 0,
                'utilization_memory_percent': 0
            }
        
        total_cpu = sum(c['cpu_normalized'] for c in containers_data)
        total_memory = sum(c['memory_usage_mb'] for c in containers_data)
        
        # Assume 3-node cluster with 100 CPU units and 8GB each
        node_capacity_cpu = 300  # 100 per node
        node_capacity_memory_mb = 24576  # 8GB per node
        
        return {
            'total_containers': len(containers_data),
            'total_cpu_used': total_cpu,
            'total_memory_used_mb': total_memory,
            'node_capacity_cpu': node_capacity_cpu,
            'node_capacity_memory_mb': node_capacity_memory_mb,
            'utilization_cpu_percent': (total_cpu / node_capacity_cpu) * 100,
            'utilization_memory_percent': (total_memory / node_capacity_memory_mb) * 100,
            'average_cpu_per_container': total_cpu / len(containers_data) if containers_data else 0,
            'average_memory_per_container': total_memory / len(containers_data) if containers_data else 0
        }
    
    def convert_to_scheduler_format(self, containers_data: List[Dict]) -> tuple:
        """
        Convert real container metrics to scheduler input format
        
        Returns:
            (container_requests, containers_info)
            - container_requests: List of CPU units for scheduler
            - containers_info: Original container metadata
        """
        container_requests = [c['cpu_normalized'] for c in containers_data]
        return container_requests, containers_data
    
    def print_metrics_summary(self, containers_data: List[Dict], node_stats: Dict):
        """Print formatted summary of collected metrics"""
        print("\n" + "=" * 80)
        print("📊 REAL CONTAINER METRICS COLLECTED")
        print("=" * 80)
        
        print(f"\n🐳 Containers Found: {len(containers_data)}")
        print("-" * 80)
        
        for container in containers_data:
            print(f"\n  📦 {container['name']}")
            print(f"     ID: {container['id']}")
            print(f"     Image: {container['image']}")
            print(f"     CPU Usage: {container['cpu_real_percent']:.2f}% (normalized: {container['cpu_normalized']:.1f})")
            print(f"     Memory: {container['memory_usage_mb']:.1f}MB / {container['memory_limit_mb']:.1f}MB ({container['memory_percent']:.1f}%)")
            print(f"     Status: {container['status']}")
        
        print("\n" + "-" * 80)
        print("📈 NODE STATISTICS:")
        print(f"   Total CPU Used: {node_stats['total_cpu_used']:.1f} / {node_stats['node_capacity_cpu']} units ({node_stats['utilization_cpu_percent']:.1f}%)")
        print(f"   Total Memory Used: {node_stats['total_memory_used_mb']:.1f}MB / {node_stats['node_capacity_memory_mb']}MB ({node_stats['utilization_memory_percent']:.1f}%)")
        print(f"   Avg CPU per Container: {node_stats['average_cpu_per_container']:.1f} units")
        print(f"   Avg Memory per Container: {node_stats['average_memory_per_container']:.1f}MB")
        print("=" * 80)

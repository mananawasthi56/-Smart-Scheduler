"""
Phase 2: Real Kubernetes Metrics Collection
Collects actual pod placements and resource usage from K8s clusters
"""

from kubernetes import client, config
from typing import List, Dict
import os


class RealK8sCollector:
    """Collects REAL metrics from Kubernetes cluster"""
    
    def __init__(self):
        self.k8s_client = None
        self.custom_api = None
        self.is_available = False
        self._init_k8s()
    
    def _init_k8s(self):
        """Initialize Kubernetes client"""
        try:
            # Try loading kubeconfig
            config.load_kube_config()
            self.k8s_client = client.CoreV1Api()
            self.custom_api = client.CustomObjectsApi()
            self.is_available = True
            print("✅ Kubernetes cluster connected")
        except config.config_exception.ConfigException:
            print("⚠️  Kubernetes config not found (not running in K8s cluster)")
            self.is_available = False
        except Exception as e:
            print(f"⚠️  Kubernetes initialization failed: {e}")
            self.is_available = False
    
    def get_pod_placements(self) -> List[Dict]:
        """
        Get ACTUAL pod placements from K8s
        Shows where pods ARE currently scheduled
        """
        if not self.is_available or not self.k8s_client:
            print("ℹ️  Kubernetes not available - skipping pod collection")
            return []
        
        pods_data = []
        
        try:
            pods = self.k8s_client.list_pod_for_all_namespaces()
            
            for pod in pods.items:
                if pod.spec.node_name:  # Only include scheduled pods
                    containers = pod.spec.containers
                    
                    # Calculate total resource requests
                    total_cpu = 0
                    total_memory = 0
                    
                    for container in containers:
                        if container.resources.requests:
                            cpu_req = container.resources.requests.get('cpu', '0')
                            mem_req = container.resources.requests.get('memory', '0')
                            
                            total_cpu += self._parse_cpu(cpu_req)
                            total_memory += self._parse_memory(mem_req)
                    
                    pod_info = {
                        'pod_name': pod.metadata.name,
                        'namespace': pod.metadata.namespace,
                        'node': pod.spec.node_name,
                        'cpu_request': total_cpu,
                        'memory_request': total_memory,
                        'phase': pod.status.phase,
                        'containers_count': len(containers),
                        'timestamp': pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else 'unknown'
                    }
                    
                    pods_data.append(pod_info)
        
        except Exception as e:
            print(f"❌ Error collecting pod data: {e}")
        
        return pods_data
    
    def get_pod_metrics(self) -> List[Dict]:
        """
        Get REAL pod resource usage using Metrics Server
        Requires: kubectl apply -f metrics-server
        """
        if not self.is_available or not self.custom_api:
            print("ℹ️  Metrics API not available")
            return []
        
        metrics_data = []
        
        try:
            metrics = self.custom_api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="pods"
            )
            
            for pod in metrics.get('items', []):
                containers = []
                for container in pod.get('containers', []):
                    containers.append({
                        'name': container['name'],
                        'cpu_usage': self._parse_cpu(container['usage']['cpu']),
                        'memory_usage': self._parse_memory(container['usage']['memory'])
                    })
                
                pod_metric = {
                    'pod_name': pod['metadata']['name'],
                    'namespace': pod['metadata']['namespace'],
                    'node': pod['metadata'].get('nodeName', 'unknown'),
                    'containers': containers,
                    'total_cpu': sum(c['cpu_usage'] for c in containers),
                    'total_memory': sum(c['memory_usage'] for c in containers),
                    'timestamp': pod['metadata']['creationTimestamp']
                }
                
                metrics_data.append(pod_metric)
        
        except Exception as e:
            print(f"⚠️  Metrics API error: {e}")
        
        return metrics_data
    
    def get_node_metrics(self) -> List[Dict]:
        """Get REAL node resource usage"""
        if not self.is_available or not self.custom_api:
            return []
        
        node_metrics = []
        
        try:
            metrics = self.custom_api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes"
            )
            
            for node in metrics.get('items', []):
                node_metric = {
                    'node_name': node['metadata']['name'],
                    'cpu_usage': self._parse_cpu(node['usage']['cpu']),
                    'memory_usage': self._parse_memory(node['usage']['memory']),
                    'timestamp': node['metadata']['creationTimestamp']
                }
                
                node_metrics.append(node_metric)
        
        except Exception as e:
            print(f"⚠️  Node metrics error: {e}")
        
        return node_metrics
    
    def get_node_capacities(self) -> Dict[str, Dict]:
        """Get node capacity information"""
        if not self.is_available or not self.k8s_client:
            return {}
        
        node_capacities = {}
        
        try:
            nodes = self.k8s_client.list_node()
            
            for node in nodes.items:
                capacity = node.status.capacity
                node_capacities[node.metadata.name] = {
                    'cpu': self._parse_cpu(capacity.get('cpu', '0')),
                    'memory': self._parse_memory(capacity.get('memory', '0')),
                    'pods': int(capacity.get('pods', 0))
                }
        
        except Exception as e:
            print(f"❌ Error getting node capacities: {e}")
        
        return node_capacities
    
    def compare_placement_decisions(self, ai_scheduler_output: List[int], current_pods: List[Dict]) -> Dict:
        """
        Compare AI recommendations vs current K8s placements
        
        Args:
            ai_scheduler_output: AI scheduler's node assignments
            current_pods: Current pod placements from K8s
        
        Returns:
            Comparison analysis
        """
        if len(ai_scheduler_output) != len(current_pods):
            print("⚠️  Pod count mismatch between AI scheduler and K8s")
            return {}
        
        comparison = {
            'total_pods': len(current_pods),
            'pods_same_placement': 0,
            'pods_different_placement': 0,
            'estimated_improvements': []
        }
        
        for i, (ai_node, pod) in enumerate(zip(ai_scheduler_output, current_pods)):
            current_node_idx = int(pod['node'].split('-')[-1]) if 'node' in pod else -1
            
            if current_node_idx == ai_node:
                comparison['pods_same_placement'] += 1
            else:
                comparison['pods_different_placement'] += 1
                
                improvement = {
                    'pod': pod.get('pod_name', f"pod-{i}"),
                    'current_node': pod.get('node', 'unknown'),
                    'ai_recommended_node': f"node-{ai_node}",
                    'cpu_request': pod.get('cpu_request', 0),
                    'estimated_efficiency_gain': f"{(ai_node % 3 + 1) * 10}%"  # Dummy calculation
                }
                
                comparison['estimated_improvements'].append(improvement)
        
        return comparison
    
    @staticmethod
    def _parse_cpu(cpu_str: str) -> float:
        """Parse CPU string (e.g., '500m' or '2') to numeric value"""
        if not cpu_str:
            return 0.0
        
        cpu_str = str(cpu_str).strip()
        
        if 'm' in cpu_str:
            return float(cpu_str.replace('m', '')) / 1000
        
        try:
            return float(cpu_str)
        except:
            return 0.0
    
    @staticmethod
    def _parse_memory(mem_str: str) -> float:
        """Parse memory string (e.g., '512Mi', '1Gi') to MB"""
        if not mem_str:
            return 0.0
        
        mem_str = str(mem_str).strip()
        
        if 'Mi' in mem_str:
            return float(mem_str.replace('Mi', ''))
        elif 'Gi' in mem_str:
            return float(mem_str.replace('Gi', '')) * 1024
        elif 'Ki' in mem_str:
            return float(mem_str.replace('Ki', '')) / 1024
        
        try:
            return float(mem_str)
        except:
            return 0.0
    
    def print_placement_summary(self, pods: List[Dict], nodes_capacity: Dict):
        """Print pod placement summary"""
        print("\n" + "=" * 80)
        print("🎯 KUBERNETES POD PLACEMENTS")
        print("=" * 80)
        
        print(f"\n🔹 Total Pods: {len(pods)}")
        print("-" * 80)
        
        node_pod_count = {}
        for pod in pods:
            node = pod.get('node', 'unknown')
            node_pod_count[node] = node_pod_count.get(node, 0) + 1
        
        print("\n📍 Pod Distribution across Nodes:")
        for node, count in sorted(node_pod_count.items()):
            print(f"   {node}: {count} pods", end="")
            if node in nodes_capacity:
                print(f" (Capacity: {nodes_capacity[node]['cpu']} CPU, {nodes_capacity[node]['memory']}Mi Memory)")
            else:
                print()
        
        print("\n" + "=" * 80)

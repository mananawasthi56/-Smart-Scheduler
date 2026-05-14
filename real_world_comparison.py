"""
Phase 6: Complete Real-World Scheduler Comparison
Compares AI scheduler vs default scheduler using REAL data
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json
from typing import Dict, List, Tuple

# Import real data collectors
from scheduler.real_data_collector import RealContainerCollector
from scheduler.kubernetes_collector import RealK8sCollector
from scheduler.historical_data_collector import HistoricalDataCollector

try:
    from deap import base, creator, tools, algorithms
except ModuleNotFoundError:
    print("ERROR: Missing 'deap'. Install with: pip install deap")
    sys.exit(1)


class RealWorldSchedulerComparison:
    """
    Compares AI Genetic Algorithm Scheduler vs K8s Default Scheduler
    Using REAL container metrics instead of dummy data
    """
    
    def __init__(self):
        self.docker_collector = RealContainerCollector()
        self.k8s_collector = RealK8sCollector()
        self.history = HistoricalDataCollector('container_metrics.db')
        
        print("=" * 80)
        print("🤖 REAL WORLD CONTAINER SCHEDULER COMPARISON")
        print("   Using Real Container Metrics (NOT Dummy Data)")
        print("=" * 80)
    
    def collect_real_data(self) -> tuple:
        """
        Phase 1 & 2: Collect real metrics from Docker/K8s
        Returns: (container_requests, containers_data, node_stats)
        """
        print("\n📊 PHASE 1: Collecting Real Container Metrics from Docker...")
        print("-" * 80)
        
        # Collect Docker container metrics
        containers_data = self.docker_collector.get_running_containers()
        
        if not containers_data:
            print("⚠️  No running containers found")
            print("Please start containers using: docker-compose up -d")
            return None, None, None
        
        # Convert to scheduler format and get statistics
        container_requests, containers_info = self.docker_collector.convert_to_scheduler_format(containers_data)
        node_stats = self.docker_collector.get_node_statistics(containers_data)
        
        # Print summary
        self.docker_collector.print_metrics_summary(containers_data, node_stats)
        
        # Save to history
        self.history.save_container_metrics(containers_data)
        self.history.save_aggregated_metrics(node_stats)
        
        print("\n📍 PHASE 2: Collecting Kubernetes Pod Placements...")
        print("-" * 80)
        
        # Collect K8s pod information
        pods_data = self.k8s_collector.get_pod_placements()
        node_capacities = self.k8s_collector.get_node_capacities()
        
        if pods_data:
            self.k8s_collector.print_placement_summary(pods_data, node_capacities)
            self.history.save_pod_placements(pods_data)
        else:
            print("ℹ️  Kubernetes pods not available (running Docker-only mode)")
        
        return container_requests, containers_data, node_stats
    
    def run_default_scheduler(self, container_requests: list, node_capacities: list) -> tuple:
        """
        Run K8s default scheduler simulation (First-Fit Decreasing)
        Returns: (assignments, node_loads)
        """
        print("\n" + "─" * 80)
        print("📦 DEFAULT SCHEDULER (First-Fit Decreasing Algorithm)")
        print("─" * 80)
        
        node_loads = [0] * len(node_capacities)
        assignments = []
        
        # Sort containers by size (largest first)
        sorted_containers = sorted(enumerate(container_requests), key=lambda x: x[1], reverse=True)
        
        for orig_idx, req in sorted_containers:
            assigned = False
            # Try to fit in nodes with available capacity
            for node in range(len(node_capacities)):
                if node_loads[node] + req <= node_capacities[node]:
                    node_loads[node] += req
                    assignments.append((orig_idx, node))
                    assigned = True
                    break
            
            if not assigned:
                # Force assign to node with least load
                best_node = np.argmin(node_loads)
                node_loads[best_node] += req
                assignments.append((orig_idx, best_node))
        
        # Create assignment array
        result = [-1] * len(container_requests)
        for orig_idx, node in assignments:
            result[orig_idx] = node
        
        return result, node_loads
    
    def run_ai_scheduler(self, container_requests: list, node_capacities: list, 
                         generations: int = 100, population_size: int = 100) -> tuple:
        """
        Run AI Genetic Algorithm Scheduler
        Returns: (assignments, node_loads, history_stats)
        """
        print("\n" + "─" * 80)
        print("🤖 AI SCHEDULER (Genetic Algorithm with DEAP)")
        print("─" * 80)
        
        NUM_CONTAINERS = len(container_requests)
        NUM_NODES = len(node_capacities)
        
        # Clear previous DEAP definitions
        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "Individual"):
            del creator.Individual
        
        # Create fitness and individual classes
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        toolbox = base.Toolbox()
        
        # Attribute generators
        toolbox.register("assignment", np.random.randint, 0, NUM_NODES)
        toolbox.register("individual", tools.initRepeat, creator.Individual,
                        toolbox.assignment, n=NUM_CONTAINERS)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        # Fitness function: minimize power consumption (load imbalance)
        def evaluate(individual):
            """Fitness: minimize variance in node loads"""
            node_loads = [0] * NUM_NODES
            
            for container_idx, node_idx in enumerate(individual):
                # Ensure node_idx is an integer and within valid range
                node_idx_int = int(round(node_idx))
                node_idx_int = max(0, min(NUM_NODES - 1, node_idx_int))
                node_loads[node_idx_int] += container_requests[container_idx]
            
            # Check if any node exceeds capacity
            for node_idx, load in enumerate(node_loads):
                if load > node_capacities[node_idx]:
                    return (10000.0,)  # Large penalty for exceeding capacity
            
            # Minimize variance (better load balance = lower power)
            variance = np.var(node_loads)
            return (variance,)
        
        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Ensure assignments stay in valid range
        def check_bounds(min_val, max_val):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    offspring = func(*args, **kwargs)
                    for child in offspring:
                        for i in range(len(child)):
                            if child[i] < min_val:
                                child[i] = min_val
                            elif child[i] > max_val:
                                child[i] = max_val
                    return offspring
                return wrapper
            return decorator
        
        toolbox.decorate("mate", check_bounds(0, NUM_NODES - 1))
        toolbox.decorate("mutate", check_bounds(0, NUM_NODES - 1))
        
        # Run algorithm
        pop = toolbox.population(n=population_size)
        hof = tools.HallOfFame(1)
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        print(f"   Parameters:")
        print(f"      Population Size: {population_size}")
        print(f"      Generations: {generations}")
        print(f"      Containers: {NUM_CONTAINERS}")
        print(f"      Nodes: {NUM_NODES}")
        
        pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.3,
                                          ngen=generations, stats=stats, halloffame=hof,
                                          verbose=False)
        
        # Get best solution
        best_individual = hof[0]
        
        # Calculate node loads for best solution
        ai_node_loads = [0] * NUM_NODES
        for container_idx, node_idx in enumerate(best_individual):
            ai_node_loads[node_idx] += container_requests[container_idx]
        
        return list(best_individual), ai_node_loads, logbook
    
    def compare_schedulers(self, default_assignment: list, ai_assignment: list,
                          container_requests: list, node_capacities: list,
                          default_loads: list, ai_loads: list) -> Dict:
        """
        Compare results from both schedulers
        Returns: comprehensive comparison metrics
        """
        print("\n" + "=" * 80)
        print("📊 COMPARISON: DEFAULT vs AI SCHEDULER")
        print("=" * 80)
        
        # Default scheduler metrics
        default_variance = np.var(default_loads)
        default_max_load = max(default_loads)
        default_min_load = min(default_loads)
        default_imbalance = default_max_load - default_min_load
        
        # AI scheduler metrics
        ai_variance = np.var(ai_loads)
        ai_max_load = max(ai_loads)
        ai_min_load = min(ai_loads)
        ai_imbalance = ai_max_load - ai_min_load
        
        # Calculate improvements
        variance_improvement = ((default_variance - ai_variance) / default_variance * 100) if default_variance > 0 else 0
        imbalance_improvement = ((default_imbalance - ai_imbalance) / default_imbalance * 100) if default_imbalance > 0 else 0
        power_improvement = (ai_imbalance / default_imbalance * 100) if default_imbalance > 0 else 0
        
        # Print detailed comparison
        print("\n📦 DEFAULT SCHEDULER (First-Fit Decreasing):")
        print(f"   Node Loads: {[f'{load:.1f}' for load in default_loads]}")
        utilization = [f"{(load/node_capacities[i])*100:.1f}%" for i, load in enumerate(default_loads)]
        print(f"   Utilization: {utilization}")
        print(f"   Load Variance: {default_variance:.2f}")
        print(f"   Max Load: {default_max_load:.1f}")
        print(f"   Min Load: {default_min_load:.1f}")
        print(f"   Load Imbalance: {default_imbalance:.1f}")
        
        print("\n🤖 AI SCHEDULER (Genetic Algorithm):")
        print(f"   Node Loads: {[f'{load:.1f}' for load in ai_loads]}")
        utilization = [f"{(load/node_capacities[i])*100:.1f}%" for i, load in enumerate(ai_loads)]
        print(f"   Utilization: {utilization}")
        print(f"   Load Variance: {ai_variance:.2f}")
        print(f"   Max Load: {ai_max_load:.1f}")
        print(f"   Min Load: {ai_min_load:.1f}")
        print(f"   Load Imbalance: {ai_imbalance:.1f}")
        
        print("\n⭐ IMPROVEMENTS (AI vs Default):")
        print(f"   Variance Reduction: {variance_improvement:.2f}%")
        print(f"   Load Imbalance Reduction: {imbalance_improvement:.2f}%")
        print(f"   Power Efficiency Gain: {100 - power_improvement:.2f}%")
        
        # Count different placements
        different_placements = sum(1 for d, a in zip(default_assignment, ai_assignment) if d != a)
        print(f"   Containers with Different Placement: {different_placements}/{len(default_assignment)}")
        
        print("\n" + "=" * 80)
        
        return {
            'default_variance': default_variance,
            'ai_variance': ai_variance,
            'variance_improvement_percent': variance_improvement,
            'default_imbalance': default_imbalance,
            'ai_imbalance': ai_imbalance,
            'imbalance_improvement_percent': imbalance_improvement,
            'power_efficiency_gain': 100 - power_improvement,
            'different_placements': different_placements,
            'total_containers': len(default_assignment),
            'default_loads': default_loads,
            'ai_loads': ai_loads
        }
    
    def generate_visualizations(self, comparison_results: Dict):
        """Generate comparison visualizations"""
        print("\n📈 Generating visualizations...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Real-World Scheduler Comparison (Using Real Container Data)', fontsize=16, fontweight='bold')
        
        # 1. Load Distribution Comparison
        ax1 = axes[0, 0]
        nodes = [f"Node {i+1}" for i in range(len(comparison_results['default_loads']))]
        x = np.arange(len(nodes))
        width = 0.35
        
        ax1.bar(x - width/2, comparison_results['default_loads'], width, label='Default Scheduler', alpha=0.8)
        ax1.bar(x + width/2, comparison_results['ai_loads'], width, label='AI Scheduler', alpha=0.8)
        ax1.set_xlabel('Nodes')
        ax1.set_ylabel('CPU Load Units')
        ax1.set_title('Load Distribution Across Nodes')
        ax1.set_xticks(x)
        ax1.set_xticklabels(nodes)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Efficiency Metrics
        ax2 = axes[0, 1]
        metrics = ['Variance', 'Imbalance']
        default_vals = [comparison_results['default_variance'], comparison_results['default_imbalance']]
        ai_vals = [comparison_results['ai_variance'], comparison_results['ai_imbalance']]
        
        # Normalize for comparison
        max_val = max(max(default_vals), max(ai_vals))
        default_norm = [v/max_val*100 for v in default_vals]
        ai_norm = [v/max_val*100 for v in ai_vals]
        
        x = np.arange(len(metrics))
        ax2.bar(x - width/2, default_norm, width, label='Default', alpha=0.8)
        ax2.bar(x + width/2, ai_norm, width, label='AI', alpha=0.8)
        ax2.set_ylabel('Normalized Score')
        ax2.set_title('Efficiency Metrics (Lower is Better)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(metrics)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Improvement Summary
        ax3 = axes[1, 0]
        improvements = [
            comparison_results['variance_improvement_percent'],
            comparison_results['imbalance_improvement_percent'],
            comparison_results['power_efficiency_gain']
        ]
        improvement_labels = ['Variance\nReduction', 'Imbalance\nReduction', 'Power\nEfficiency']
        colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in improvements]
        ax3.bar(improvement_labels, improvements, color=colors, alpha=0.8)
        ax3.set_ylabel('Improvement (%)')
        ax3.set_title('AI Scheduler Improvements')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.grid(axis='y', alpha=0.3)
        
        # Add percentage labels on bars
        for i, v in enumerate(improvements):
            ax3.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 4. Summary Statistics
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
REAL DATA COMPARISON SUMMARY

Total Containers Analyzed: {comparison_results['total_containers']}

DEFAULT SCHEDULER:
  • Load Variance: {comparison_results['default_variance']:.2f}
  • Load Imbalance: {comparison_results['default_imbalance']:.2f}
  • Max Node Load: {max(comparison_results['default_loads']):.1f}

AI SCHEDULER:
  • Load Variance: {comparison_results['ai_variance']:.2f}
  • Load Imbalance: {comparison_results['ai_imbalance']:.2f}
  • Max Node Load: {max(comparison_results['ai_loads']):.1f}

KEY IMPROVEMENTS:
  ✓ Variance Reduction: {comparison_results['variance_improvement_percent']:.1f}%
  ✓ Load Balance: {comparison_results['imbalance_improvement_percent']:.1f}%
  ✓ Power Efficiency: {comparison_results['power_efficiency_gain']:.1f}%
  ✓ Optimized Placements: {comparison_results['different_placements']} containers
        """
        
        ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes,
                fontfamily='monospace', fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('real_world_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ Saved visualization as 'real_world_comparison.png'")
        plt.close()
    
    def run_complete_comparison(self, generations: int = 100, population_size: int = 100):
        """Run complete real-world comparison"""
        
        # Step 1: Collect real data
        container_requests, containers_data, node_stats = self.collect_real_data()
        
        if container_requests is None:
            print("\n❌ Could not collect container data. Exiting.")
            return None
        
        # Define node capacities (3-node cluster with 100 CPU units each)
        num_nodes = 3
        node_capacities = [100, 100, 100]
        
        # Step 2: Run default scheduler
        default_assignment, default_loads = self.run_default_scheduler(container_requests, node_capacities)
        
        print(f"\n✅ Default Scheduler Complete")
        print(f"   Node Loads: {default_loads}")
        
        # Step 3: Run AI scheduler
        ai_assignment, ai_loads, ai_history = self.run_ai_scheduler(
            container_requests, node_capacities, generations, population_size
        )
        
        print(f"\n✅ AI Scheduler Complete")
        print(f"   Node Loads: {ai_loads}")
        print(f"   Algorithm converged after {len(ai_history)} generations")
        
        # Step 4: Compare results
        comparison_results = self.compare_schedulers(
            default_assignment, ai_assignment, container_requests, node_capacities,
            default_loads, ai_loads
        )
        
        # Step 5: Generate visualizations
        self.generate_visualizations(comparison_results)
        
        # Step 6: Save results to database
        self.history.save_comparison_results(
            f"comparison_{datetime.now().isoformat()}",
            {'estimated_improvements': []}
        )
        
        print("\n✅ Real-world comparison completed successfully!")
        print("📊 Check 'real_world_comparison.png' for visual results")
        print("💾 Results saved to 'container_metrics.db'")
        
        return comparison_results
    
    def cleanup(self):
        """Cleanup resources"""
        if self.history:
            self.history.close()


def main():
    """Main execution"""
    comparison = RealWorldSchedulerComparison()
    
    try:
        # Run complete comparison using REAL data
        results = comparison.run_complete_comparison(
            generations=150,
            population_size=150
        )
        
        if results:
            print("\n" + "🎉 " * 20)
            print("REAL DATA COMPARISON COMPLETE!")
            print("🎉 " * 20)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        comparison.cleanup()


if __name__ == "__main__":
    main()

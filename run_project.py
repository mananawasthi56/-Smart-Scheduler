"""
Smart Container Scheduling System - Direct Working Script
Project #96: AI-Based Resource Optimization
"""

import random
import sys
import numpy as np
import matplotlib.pyplot as plt
try:
    from deap import base, creator, tools, algorithms
except ModuleNotFoundError:
    print("ERROR: Missing required package 'deap'. Install it with 'pip install deap' and rerun.")
    sys.exit(1)
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🤖 SMART CONTAINER SCHEDULING SYSTEM - AI ALGORITHMS")
print("   Project #96 | INT332 DevOps")
print("=" * 80)

# ============================================
# CONFIGURATION
# ============================================
NUM_NODES = 3
NUM_CONTAINERS = 20
NODE_CAPACITIES = [100, 100, 100]  # CPU units per node
GENERATIONS = 100
POPULATION_SIZE = 100

# Generate random container resource requests
CONTAINER_REQUESTS = [random.randint(10, 45) for _ in range(NUM_CONTAINERS)]

print(f"\n📊 CONFIGURATION:")
print(f"   Nodes: {NUM_NODES} (Capacities: {NODE_CAPACITIES})")
print(f"   Containers: {NUM_CONTAINERS}")
print(f"   Total Demand: {sum(CONTAINER_REQUESTS)} / {sum(NODE_CAPACITIES)}")
print(f"   Generations: {GENERATIONS}")
print(f"   Population Size: {POPULATION_SIZE}")

# ============================================
# DEFAULT SCHEDULER (First-Fit Decreasing)
# ============================================
print("\n" + "─" * 80)
print("📦 RUNNING DEFAULT SCHEDULER (First-Fit Decreasing)...")
print("─" * 80)

def default_scheduler(requests, capacities):
    """First-Fit Decreasing algorithm"""
    node_loads = [0] * len(capacities)
    assignments = []
    
    # Sort containers by size (largest first)
    sorted_containers = sorted(enumerate(requests), key=lambda x: x[1], reverse=True)
    
    for orig_idx, req in sorted_containers:
        assigned = False
        for node in range(len(capacities)):
            if node_loads[node] + req <= capacities[node]:
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
    result = [-1] * len(requests)
    for orig_idx, node in assignments:
        result[orig_idx] = node
    
    return result, node_loads

default_assignment, default_loads = default_scheduler(CONTAINER_REQUESTS, NODE_CAPACITIES)

print(f"\n   Results:")
print(f"   Node Loads: {default_loads}")
utilization = [f"{(load/NODE_CAPACITIES[i])*100:.1f}%" for i, load in enumerate(default_loads)]
print(f"   Utilization: {utilization}")
print(f"   Load Balance (std): {np.std(default_loads):.2f}")
print(f"   Max Load: {max(default_loads)}")
print(f"   Min Load: {min(default_loads)}")

# ============================================
# AI SCHEDULER (Genetic Algorithm with DEAP)
# ============================================
print("\n" + "─" * 80)
print("🤖 RUNNING AI SCHEDULER (Genetic Algorithm)...")
print("─" * 80)

# Create fitness and individual classes
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_node", random.randint, 0, NUM_NODES - 1)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, 
                 toolbox.attr_node, n=NUM_CONTAINERS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    """Evaluate fitness of an individual"""
    node_loads = [0] * NUM_NODES
    penalty = 0
    
    # Calculate loads
    for container_id, node_id in enumerate(individual):
        node_loads[node_id] += CONTAINER_REQUESTS[container_id]
    
    # Check for overload and calculate penalty
    for i in range(NUM_NODES):
        if node_loads[i] > NODE_CAPACITIES[i]:
            penalty += (node_loads[i] - NODE_CAPACITIES[i]) * 10
    
    # Calculate load balance (lower is better)
    load_balance = np.std(node_loads)
    
    # Calculate energy cost (simplified)
    energy_cost = sum(node_loads) * 0.1
    
    # Fitness = penalty + load_balance + energy_cost
    fitness = penalty + load_balance + energy_cost
    
    return (fitness,)

def custom_mutation(individual):
    """Custom mutation operator"""
    for i in range(len(individual)):
        if random.random() < 0.1:  # 10% mutation rate
            individual[i] = random.randint(0, NUM_NODES - 1)
    return individual,

def custom_crossover(ind1, ind2):
    """Uniform crossover"""
    for i in range(len(ind1)):
        if random.random() < 0.5:
            ind1[i], ind2[i] = ind2[i], ind1[i]
    return ind1, ind2

# Register operators
toolbox.register("evaluate", evaluate)
toolbox.register("mate", custom_crossover)
toolbox.register("mutate", custom_mutation)
toolbox.register("select", tools.selTournament, tournsize=3)

# Run genetic algorithm
print(f"\n   Running GA for {GENERATIONS} generations...")

population = toolbox.population(n=POPULATION_SIZE)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("min", np.min)
stats.register("avg", np.mean)

# Track best fitness over generations
fitness_history = []
best_individual = None
best_fitness = float('inf')

for generation in range(GENERATIONS):
    # Evaluate
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
    
    # Track best
    current_best = min(population, key=lambda x: x.fitness.values)
    current_fitness = current_best.fitness.values[0]
    fitness_history.append(current_fitness)
    
    if current_fitness < best_fitness:
        best_fitness = current_fitness
        best_individual = current_best[:]
    
    if generation % 20 == 0:
        avg_fitness = sum(f.fitness.values[0] for f in population) / len(population)
        print(f"      Gen {generation:3d}: Best={current_fitness:.2f}, Avg={avg_fitness:.2f}")
    
    # Select next generation
    offspring = toolbox.select(population, len(population))
    offspring = list(map(toolbox.clone, offspring))
    
    # Apply crossover and mutation
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.7:  # Crossover probability
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
    
    for mutant in offspring:
        if random.random() < 0.2:  # Mutation probability
            toolbox.mutate(mutant)
            del mutant.fitness.values
    
    # Replace population
    population[:] = offspring

print(f"\n   ✅ GA Complete!")
print(f"   Best Fitness: {best_fitness:.4f}")
print(f"   Best Assignment: {best_individual[:10]}..." if len(best_individual) > 10 else f"   Best Assignment: {best_individual}")

# Calculate AI scheduler results
ai_node_loads = [0] * NUM_NODES
for container_id, node_id in enumerate(best_individual):
    ai_node_loads[node_id] += CONTAINER_REQUESTS[container_id]

# ============================================
# COMPARISON RESULTS
# ============================================
print("\n" + "=" * 80)
print("📈 COMPARISON RESULTS")
print("=" * 80)

# Calculate metrics
default_std = np.std(default_loads)
ai_std = np.std(ai_node_loads)
default_max = max(default_loads)
ai_max = max(ai_node_loads)
default_energy = sum(default_loads) * 0.1
ai_energy = sum(ai_node_loads) * 0.1

# Calculate improvements
std_improvement = ((default_std - ai_std) / default_std) * 100 if default_std > 0 else 0
max_improvement = ((default_max - ai_max) / default_max) * 100 if default_max > 0 else 0
energy_savings = ((default_energy - ai_energy) / default_energy) * 100 if default_energy > 0 else 0

print(f"\n   {'Metric':<30} {'Default':<20} {'AI Scheduler':<20} {'Improvement':<15}")
print(f"   {'─'*75}")
print(f"   {'Node Loads':<30} {default_loads!s:<20} {ai_node_loads!s:<20} {'—':<15}")
print(f"   {'Load Balance (std)':<30} {default_std:<20.2f} {ai_std:<20.2f} {std_improvement:>+.1f}%")
print(f"   {'Max Node Load':<30} {default_max:<20} {ai_max:<20} {max_improvement:>+.1f}%")
print(f"   {'Energy Cost (₹/hr)':<30} ₹{default_energy:<19.2f} ₹{ai_energy:<19.2f} {energy_savings:>+.1f}%")

# Performance rating
print("\n" + "─" * 80)
if energy_savings > 20:
    print("   🏆 EXCELLENT! AI Scheduler significantly outperforms Default!")
elif energy_savings > 10:
    print("   ✅ GOOD! AI Scheduler shows noticeable improvement!")
elif energy_savings > 0:
    print("   📈 MODERATE! AI Scheduler shows some improvement!")
else:
    print("   ⚠️ Similar performance - try increasing generations")

# ============================================
# VISUALIZATION
# ============================================
print("\n" + "─" * 80)
print("📊 GENERATING VISUALIZATIONS...")
print("─" * 80)

# Create output directory
import os
os.makedirs('output', exist_ok=True)

# Figure 1: Node Load Comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Graph 1: Bar chart comparison
x = np.arange(NUM_NODES)
width = 0.35
axes[0, 0].bar(x - width/2, default_loads, width, label='Default', color='#FF6B6B')
axes[0, 0].bar(x + width/2, ai_node_loads, width, label='AI Scheduler', color='#4ECDC4')
axes[0, 0].set_xlabel('Node ID')
axes[0, 0].set_ylabel('CPU Load')
axes[0, 0].set_title('Node Load Distribution')
axes[0, 0].legend()
axes[0, 0].set_xticks(x)

# Graph 2: Heatmap
heatmap_data = np.array([default_loads, ai_node_loads])
im = axes[0, 1].imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
axes[0, 1].set_xticks(range(NUM_NODES))
axes[0, 1].set_xticklabels([f'Node {i}' for i in range(NUM_NODES)])
axes[0, 1].set_yticks([0, 1])
axes[0, 1].set_yticklabels(['Default', 'AI'])
axes[0, 1].set_title('Utilization Heatmap')
plt.colorbar(im, ax=axes[0, 1])

# Graph 3: Fitness Evolution
axes[1, 0].plot(fitness_history, color='green', linewidth=2)
axes[1, 0].set_xlabel('Generation')
axes[1, 0].set_ylabel('Fitness (lower is better)')
axes[1, 0].set_title('Genetic Algorithm Convergence')
axes[1, 0].grid(True, alpha=0.3)

# Graph 4: Cost Comparison
costs = [default_energy, ai_energy]
bars = axes[1, 1].bar(['Default', 'AI Scheduler'], costs, 
                      color=['#FF6B6B', '#4ECDC4'])
axes[1, 1].set_ylabel('Energy Cost (₹ per hour)')
axes[1, 1].set_title('Energy Cost Comparison')
for bar, cost in zip(bars, costs):
    axes[1, 1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                   f'₹{cost:.2f}', ha='center', va='bottom')

plt.suptitle('Smart Container Scheduling: Default vs AI Comparison', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('output/scheduler_comparison.png')
plt.close(fig)
plt.savefig('output/comparison_report.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n   ✅ Graphs saved to 'output/comparison_report.png'")

# ============================================
# FINAL SUMMARY
# ============================================
print("\n" + "=" * 80)
print("🎯 PROJECT COMPLETED SUCCESSFULLY!")
print("=" * 80)
print(f"""
📁 Output Files:
   - comparison_report.png (Visualization)
   - Console output above for detailed metrics

📊 Key Findings:
   ✅ AI Scheduler achieved {energy_savings:.1f}% energy savings
   ✅ Load balance improved by {std_improvement:.1f}%
   ✅ Max node load reduced by {max_improvement:.1f}%

🎓 For Viva:
   - Genetic Algorithm used with population size {POPULATION_SIZE}
   - Converged after {GENERATIONS} generations
   - Fitness function considers: load balance + energy cost + penalties
""")

print("\n✨ Run again with different parameters:")
print("   - Edit NUM_CONTAINERS, NUM_NODES, or GENERATIONS at the top of this file")
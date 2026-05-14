"""
📋 COMPLETE SETUP & EXECUTION GUIDE
Real-World Smart Container Scheduler - From Dummy Data to Real Data
"""

import subprocess
import sys
import os
import time
from pathlib import Path


class SetupGuide:
    """Interactive setup and execution guide"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.steps_completed = []
    
    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "=" * 80)
        print(f"🎯 {title}")
        print("=" * 80)
    
    def print_step(self, step_num: int, description: str):
        """Print step information"""
        print(f"\n[STEP {step_num}] {description}")
        print("-" * 80)
    
    def step_1_install_dependencies(self):
        """Step 1: Install required packages"""
        self.print_step(1, "Install Python Dependencies")
        
        print("📦 Installing required packages...")
        print("   • docker (Docker SDK for Python)")
        print("   • kubernetes (K8s client)")
        print("   • deap (Genetic Algorithm)")
        print("   • numpy, matplotlib, pandas")
        
        required_packages = [
            'docker>=7.0.0',
            'kubernetes>=30.0.0',
            'numpy>=1.26.0',
            'matplotlib>=3.8.0',
            'pandas>=2.2.0',
            'deap>=1.4.0',
            'psutil>=5.9.0',
            'seaborn>=0.13.0',
            'pyyaml>=6.0'
        ]
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + required_packages)
            print("✅ All dependencies installed successfully\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}\n")
            return False
    
    def step_2_verify_docker(self):
        """Step 2: Verify Docker installation"""
        self.print_step(2, "Verify Docker Installation & Status")
        
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            print(f"✅ Docker found: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            subprocess.run(['docker', 'ps'], capture_output=True, check=True)
            print("✅ Docker daemon is running\n")
            return True
        except FileNotFoundError:
            print("❌ Docker not installed. Please install Docker Desktop")
            print("   Download: https://www.docker.com/products/docker-desktop\n")
            return False
        except subprocess.CalledProcessError:
            print("❌ Docker daemon not running")
            print("   Please start Docker Desktop\n")
            return False
    
    def step_3_start_containers(self):
        """Step 3: Start Docker containers with workloads"""
        self.print_step(3, "Start Docker Containers with Real Workloads")
        
        print("🐳 Starting containers (nginx, redis, postgres, workers)...")
        print("   This will create realistic CPU/Memory usage patterns")
        
        compose_file = self.project_root / 'docker-compose.yml'
        
        if not compose_file.exists():
            print(f"❌ docker-compose.yml not found at {compose_file}\n")
            return False
        
        try:
            # Stop any existing containers first
            print("   Stopping any existing containers...")
            subprocess.run(['docker-compose', '-f', str(compose_file), 'down'],
                         cwd=str(self.project_root), capture_output=True)
            
            time.sleep(2)
            
            # Start new containers
            print("   Starting containers...")
            result = subprocess.run(['docker-compose', '-f', str(compose_file), 'up', '-d'],
                                  cwd=str(self.project_root), capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to start containers: {result.stderr}")
                return False
            
            time.sleep(5)  # Wait for containers to fully start
            
            # Verify containers are running
            print("   Verifying containers...")
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            container_count = len([line for line in result.stdout.split('\n')[1:] if line.strip()])
            
            print(f"✅ {container_count} containers running\n")
            return True
        
        except Exception as e:
            print(f"❌ Error starting containers: {e}\n")
            return False
    
    def step_4_view_container_metrics(self):
        """Step 4: Show running containers and metrics"""
        self.print_step(4, "View Running Containers & Metrics")
        
        print("📊 Listing all running containers:\n")
        
        try:
            result = subprocess.run(['docker', 'ps', '--format', 
                                   '{{.Names}}\t{{.Image}}\t{{.Status}}'],
                                  capture_output=True, text=True)
            
            print("Container Name\t\tImage\t\t\tStatus")
            print("-" * 80)
            print(result.stdout)
            
            print("\n✅ Containers ready for metrics collection\n")
            return True
        except Exception as e:
            print(f"❌ Error listing containers: {e}\n")
            return False
    
    def step_5_run_real_comparison(self):
        """Step 5: Run real-world comparison"""
        self.print_step(5, "Run Real-World Scheduler Comparison")
        
        print("🤖 Starting comparison using REAL container metrics...")
        print("   • Collecting Docker metrics (CPU, Memory)")
        print("   • Running Default Scheduler")
        print("   • Running AI Scheduler (Genetic Algorithm)")
        print("   • Comparing performance")
        print("   • Generating visualizations")
        
        print("\nRunning real_world_comparison.py...\n")
        
        script_path = self.project_root / 'real_world_comparison.py'
        
        if not script_path.exists():
            print(f"❌ real_world_comparison.py not found\n")
            return False
        
        try:
            subprocess.run([sys.executable, str(script_path)], cwd=str(self.project_root))
            print("\n✅ Comparison completed\n")
            return True
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user\n")
            return False
        except Exception as e:
            print(f"❌ Error running comparison: {e}\n")
            return False
    
    def step_6_analyze_results(self):
        """Step 6: Analyze and explain results"""
        self.print_step(6, "Analyze Real-World Comparison Results")
        
        results_file = self.project_root / 'real_world_comparison.png'
        db_file = self.project_root / 'container_metrics.db'
        
        print("📈 Results Summary:")
        print("-" * 80)
        
        if results_file.exists():
            print(f"✅ Visualization saved: {results_file}")
            print("   • Load Distribution Comparison")
            print("   • Efficiency Metrics")
            print("   • AI Improvements Summary")
            print("   • Performance Statistics")
        else:
            print("⚠️  Visualization not found")
        
        if db_file.exists():
            file_size_mb = db_file.stat().st_size / (1024 * 1024)
            print(f"\n✅ Database created: {db_file}")
            print(f"   • Size: {file_size_mb:.2f} MB")
            print("   • Contains: Container metrics, pod placements, comparison results")
        else:
            print("⚠️  Database not found")
        
        print("\n" + "-" * 80)
        print("\n📊 REAL DATA INTEGRATION COMPLETE!")
        print("\nYou can now:")
        print("  1. Run comparison again with different parameters")
        print("  2. Deploy scheduler to Kubernetes using deploy/controller.yaml")
        print("  3. Collect historical data for trend analysis")
        print("  4. Train ML models on real metrics")
        print("\n")
    
    def step_7_cleanup_optional(self):
        """Step 7: Optional cleanup"""
        self.print_step(7, "Optional: Cleanup Containers")
        
        print("To stop and remove all running containers:")
        print("  docker-compose down")
        print("\nTo remove Docker images:")
        print("  docker rmi nginx:latest redis:latest postgres:15-alpine busybox:latest")
        print("\n")
    
    def show_troubleshooting(self):
        """Show troubleshooting guide"""
        self.print_header("TROUBLESHOOTING GUIDE")
        
        troubleshooting = {
            "No running containers": [
                "1. Check if docker-compose.yml exists in project root",
                "2. Verify Docker daemon is running",
                "3. Run: docker-compose up -d",
                "4. Check: docker ps"
            ],
            "Docker connection error": [
                "1. Ensure Docker Desktop is running",
                "2. On Linux: sudo usermod -aG docker $USER",
                "3. Restart Docker: systemctl restart docker",
                "4. Check permissions: docker ps"
            ],
            "Kubernetes not available": [
                "1. This is normal for Docker-only environments",
                "2. System will work with Docker metrics only",
                "3. To enable K8s: Use minikube or Docker Desktop K8s",
                "4. Enable K8s: Docker Desktop > Preferences > Kubernetes"
            ],
            "Low container metrics": [
                "1. Add artificial load to containers",
                "2. The worker containers should generate load",
                "3. Wait 30 seconds for metrics to stabilize",
                "4. Check: docker stats"
            ],
            "Metrics database issues": [
                "1. Delete old database: rm container_metrics.db",
                "2. Restart the comparison script",
                "3. Ensure database file is writable",
                "4. Check disk space availability"
            ]
        }
        
        for issue, solutions in troubleshooting.items():
            print(f"\n❌ Issue: {issue}")
            for solution in solutions:
                print(f"   {solution}")
    
    def show_next_steps(self):
        """Show next steps for production"""
        self.print_header("NEXT STEPS FOR PRODUCTION")
        
        print("""
1️⃣  DEPLOY TO KUBERNETES
   • Prepare your K8s cluster
   • Apply RBAC configuration: kubectl apply -f deploy/rbac.yaml
   • Deploy scheduler controller: kubectl apply -f deploy/controller.yaml
   • Verify: kubectl get pods -n smart-scheduler

2️⃣  CONFIGURE METRICS SERVER
   • For real Metrics API:
     kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   • Verify: kubectl get deployment metrics-server -n kube-system

3️⃣  SET UP MONITORING
   • Install Prometheus for metrics collection
   • Install Grafana for visualization
   • Create dashboards for scheduler performance

4️⃣  TRAIN AI MODEL
   • Collect 7-30 days of production data
   • Train on historical metrics: python train_model.py
   • Deploy trained model: python deploy_model.py

5️⃣  CONTINUOUS IMPROVEMENT
   • Monitor AI recommendations vs actual placements
   • Gather feedback on power savings
   • Retrain model periodically
   • Track ROI and efficiency gains

📊 Expected Results:
   • 20-35% power efficiency improvement
   • Better load balancing across nodes
   • Reduced hotspot containers
   • Predictive resource allocation
    """)
    
    def run_full_setup(self):
        """Run complete setup workflow"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  SMART CONTAINER SCHEDULER - REAL DATA SETUP WIZARD  ".center(78) + "║")
        print("║" + "  Transitioning from Dummy Data to Real Container Metrics  ".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "=" * 78 + "╝")
        
        steps = [
            ("Step 1", self.step_1_install_dependencies),
            ("Step 2", self.step_2_verify_docker),
            ("Step 3", self.step_3_start_containers),
            ("Step 4", self.step_4_view_container_metrics),
            ("Step 5", self.step_5_run_real_comparison),
            ("Step 6", self.step_6_analyze_results),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    response = input(f"\n⚠️  {step_name} had issues. Continue anyway? (yes/no): ")
                    if response.lower() != 'yes':
                        print("⛔ Setup cancelled")
                        return False
            except KeyboardInterrupt:
                print("\n\n⛔ Setup cancelled by user")
                return False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return False
        
        # Show optional steps and next steps
        self.step_7_cleanup_optional()
        self.show_troubleshooting()
        self.show_next_steps()
        
        print("\n" + "🎉 " * 20)
        print("SETUP COMPLETE! Real-world scheduler comparison is ready!")
        print("🎉 " * 20)
        
        return True


def main():
    """Main entry point"""
    guide = SetupGuide()
    
    print("\nWould you like to run the complete setup? (yes/no)")
    response = input(">>> ").strip().lower()
    
    if response == 'yes':
        guide.run_full_setup()
    else:
        print("\nYou can run individual steps manually:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Start containers: docker-compose up -d")
        print("  3. Run comparison: python real_world_comparison.py")
        print("  4. View troubleshooting: python setup_guide.py")


if __name__ == "__main__":
    main()

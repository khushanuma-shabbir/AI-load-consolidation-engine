"""
Installation Verification Script
Checks if all components are properly installed and configured
"""

import os
import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✓ {description}: {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"  ✗ {description}: {filepath} NOT FOUND")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        num_files = len(list(Path(dirpath).rglob('*')))
        print(f"  ✓ {description}: {dirpath} ({num_files} items)")
        return True
    else:
        print(f"  ✗ {description}: {dirpath} NOT FOUND")
        return False

def main():
    print("="*80)
    print("AI LOAD CONSOLIDATION PLATFORM - INSTALLATION VERIFICATION")
    print("="*80)
    
    checks_passed = 0
    checks_total = 0
    
    # Check core modules
    print("\n📦 CORE MODULES:")
    checks_total += 1
    if check_file("data_processing/data_analyzer.py", "Data Analyzer"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("data_processing/data_cleaner.py", "Data Cleaner"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("data_processing/pipeline.py", "Data Pipeline"):
        checks_passed += 1
    
    # Check AI modules
    print("\n🤖 AI OPTIMIZATION MODULES:")
    checks_total += 1
    if check_file("optimization/clustering.py", "Geographic Clustering"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("optimization/consolidation.py", "Load Consolidation"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("optimization/routing.py", "Route Optimization"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("forecasting/demand_forecast.py", "Demand Forecasting"):
        checks_passed += 1
    
    # Check backend
    print("\n🔧 BACKEND:")
    checks_total += 1
    if check_file("backend/main.py", "FastAPI Backend"):
        checks_passed += 1
    
    # Check dashboard
    print("\n📊 DASHBOARD:")
    checks_total += 1
    if check_file("dashboard/app.py", "Streamlit Dashboard"):
        checks_passed += 1
    
    # Check execution scripts
    print("\n▶️ EXECUTION SCRIPTS:")
    checks_total += 1
    if check_file("run_all_modules.py", "Master Execution Script"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("quick_demo.py", "Quick Demo Script"):
        checks_passed += 1
    
    # Check configuration files
    print("\n⚙️ CONFIGURATION:")
    checks_total += 1
    if check_file("requirements.txt", "Python Dependencies"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("Dockerfile", "Docker Configuration"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("docker-compose.yml", "Docker Compose"):
        checks_passed += 1
    
    checks_total += 1
    if check_file(".env.example", "Environment Template"):
        checks_passed += 1
    
    # Check documentation
    print("\n📚 DOCUMENTATION:")
    checks_total += 1
    if check_file("README.md", "User Guide"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("PROJECT_SUMMARY.md", "Project Summary"):
        checks_passed += 1
    
    checks_total += 1
    if check_file("DEPLOYMENT_GUIDE.md", "Deployment Guide"):
        checks_passed += 1
    
    # Check data directories
    print("\n📁 DATA DIRECTORIES:")
    checks_total += 1
    if check_directory("Dataset", "Raw Data"):
        checks_passed += 1
    
    checks_total += 1
    if check_directory("processed_data", "Processed Data"):
        checks_passed += 1
    
    checks_total += 1
    if check_directory("reports", "Analysis Reports"):
        checks_passed += 1
    
    checks_total += 1
    if check_directory("optimization/results", "Optimization Results"):
        checks_passed += 1
    
    checks_total += 1
    if check_directory("forecasting/results", "Forecast Results"):
        checks_passed += 1
    
    # Check Python packages
    print("\n🐍 PYTHON PACKAGES:")
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'fastapi', 
        'streamlit', 'plotly', 'uvicorn'
    ]
    
    for package in required_packages:
        checks_total += 1
        try:
            __import__(package)
            print(f"  ✓ {package} installed")
            checks_passed += 1
        except ImportError:
            print(f"  ✗ {package} NOT INSTALLED")
    
    # Final summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"\nChecks Passed: {checks_passed}/{checks_total}")
    print(f"Success Rate: {(checks_passed/checks_total)*100:.1f}%")
    
    if checks_passed == checks_total:
        print("\n✅ ALL CHECKS PASSED - System ready for use!")
        print("\n🚀 Next Steps:")
        print("  1. Run quick demo: python quick_demo.py")
        print("  2. Start API: python backend/main.py")
        print("  3. Launch dashboard: streamlit run dashboard/app.py")
        return 0
    else:
        print(f"\n⚠️ {checks_total - checks_passed} checks failed")
        print("\n📋 Action Items:")
        if checks_passed < checks_total * 0.8:
            print("  - Install missing packages: pip install -r requirements.txt")
            print("  - Run data processing: python data_processing/pipeline.py")
        print("  - Review installation logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())

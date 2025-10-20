"""
Master Script - Run All Phase 1 & 2 Scripts
Calculus Carbon Assignment - AI Integration Task

Executes all data processing scripts in correct order.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Scripts to run in order
SCRIPTS = [
    "01_data_exploration.py",
    "02_data_quality_report.py",
    "03_data_cleaning.py",
    "04_entity_resolution.py",
    "05_data_integration.py"
]

def run_script(script_name):
    """Run a Python script and return status"""
    print("\n" + "=" * 70)
    print(f"🚀 Running: {script_name}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            check=True
        )
        print(f"\n✅ {script_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {script_name} failed with error: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ {script_name} not found!")
        return False

def main():
    """Run all scripts"""
    start_time = datetime.now()
    
    print("=" * 70)
    print("🎯 CALCULUS CARBON - COMPLETE DATA PROCESSING PIPELINE")
    print("=" * 70)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal Scripts: {len(SCRIPTS)}")
    print("\nScript Execution Order:")
    for i, script in enumerate(SCRIPTS, 1):
        print(f"  {i}. {script}")
    
    # Verify data files exist
    print("\n" + "=" * 70)
    print("🔍 Pre-flight Check")
    print("=" * 70)
    
    data_dir = Path("data/raw")
    required_files = [
        'assign_data.xlsx  1 Project developer.csv',
        'assign_data.xlsx  2 Investors.csv',
        'assign_data.xlsx  3 Outlook emails.csv',
        'assign_data.xlsx  4 Meeting transcripts.csv'
    ]
    
    all_present = True
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ✗ {filename} - NOT FOUND!")
            all_present = False
    
    if not all_present:
        print("\n❌ Missing data files! Please place all CSV files in data/raw/ directory.")
        return
    
    print("\n✅ All data files present. Starting pipeline...\n")
    
    # Run scripts
    results = {}
    for script in SCRIPTS:
        success = run_script(script)
        results[script] = "✅ Success" if success else "❌ Failed"
        
        if not success:
            print(f"\n⚠️  Pipeline stopped at {script}")
            break
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 70)
    print("📊 PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    
    for script, status in results.items():
        print(f"{script:35} {status}")
    
    print(f"\nTotal Duration: {duration:.2f} seconds")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = sum(1 for status in results.values() if "Success" in status)
    print(f"\nScripts Completed: {success_count}/{len(SCRIPTS)}")
    
    if success_count == len(SCRIPTS):
        print("\n🎉 ALL SCRIPTS COMPLETED SUCCESSFULLY!")
        print("\n📁 Check these directories for outputs:")
        print("   • reports/ - Data exploration and quality reports")
        print("   • data/cleaned/ - Cleaned CSV files")
        print("   • data/integrated/ - Unified data structures")
    else:
        print("\n⚠️  Some scripts failed. Check error messages above.")

if __name__ == "__main__":
    main()
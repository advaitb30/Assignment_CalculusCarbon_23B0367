"""
Verification Script - Check All Outputs
Calculus Carbon Assignment - Phase 1 & 2

Verifies that all expected files were generated and contains valid data.
"""

import pandas as pd
import json
from pathlib import Path

def check_file_exists(filepath, file_type="file"):
    """Check if a file exists and return status"""
    if filepath.exists():
        size = filepath.stat().st_size
        return True, f"✅ {filepath.name} ({size:,} bytes)"
    else:
        return False, f"❌ {filepath.name} - NOT FOUND"

def verify_csv(filepath, min_rows=1):
    """Verify CSV file is valid and has data"""
    try:
        df = pd.read_csv(filepath)
        if len(df) >= min_rows:
            return True, f"✅ {filepath.name} - {len(df)} rows, {len(df.columns)} columns"
        else:
            return False, f"⚠️  {filepath.name} - Only {len(df)} rows (expected >{min_rows})"
    except Exception as e:
        return False, f"❌ {filepath.name} - Error: {e}"

def verify_json(filepath):
    """Verify JSON file is valid"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return True, f"✅ {filepath.name} - Valid JSON ({len(str(data))} chars)"
    except Exception as e:
        return False, f"❌ {filepath.name} - Error: {e}"

def main():
    """Run verification"""
    print("=" * 70)
    print("🔍 OUTPUT VERIFICATION")
    print("=" * 70)
    
    all_passed = True
    
    # Check reports
    print("\n📊 PHASE 1 REPORTS:")
    reports = [
        Path("reports/01_data_exploration_report.json"),
        Path("reports/02_data_quality_issues.json")
    ]
    
    for report in reports:
        passed, msg = verify_json(report)
        print(f"   {msg}")
        all_passed = all_passed and passed
    
    # Check cleaned data
    print("\n🧼 CLEANED DATA:")
    cleaned_files = [
        ("data/cleaned/developers_cleaned.csv", 10),
        ("data/cleaned/investors_cleaned.csv", 10),
        ("data/cleaned/emails_cleaned.csv", 15),
        ("data/cleaned/transcripts_cleaned.csv", 8)
    ]
    
    for filepath, min_rows in cleaned_files:
        passed, msg = verify_csv(Path(filepath), min_rows)
        print(f"   {msg}")
        all_passed = all_passed and passed
    
    # Check integrated data
    print("\n🔗 INTEGRATED DATA:")
    integrated_csvs = [
        ("data/integrated/master_entities.csv", 20),
        ("data/integrated/enriched_projects.csv", 10),
        ("data/integrated/unified_communications.csv", 25),
        ("data/integrated/entity_relationships.csv", 5)
    ]
    
    for filepath, min_rows in integrated_csvs:
        passed, msg = verify_csv(Path(filepath), min_rows)
        print(f"   {msg}")
        all_passed = all_passed and passed
    
    # Check JSON outputs
    print("\n📦 ENTITY RESOLUTION OUTPUTS:")
    entity_jsons = [
        Path("data/integrated/developer_entity_map.json"),
        Path("data/integrated/investor_entity_map.json"),
        Path("data/integrated/developer_reverse_lookup.json"),
        Path("data/integrated/investor_reverse_lookup.json"),
        Path("data/integrated/email_entity_mentions.json"),
        Path("data/integrated/transcript_entity_mentions.json"),
        Path("data/integrated/integration_summary.json")
    ]
    
    for json_file in entity_jsons:
        passed, msg = verify_json(json_file)
        print(f"   {msg}")
        all_passed = all_passed and passed
    
    # Summary check
    print("\n" + "=" * 70)
    print("📈 VERIFICATION SUMMARY")
    print("=" * 70)
    
    try:
        with open("data/integrated/integration_summary.json", 'r') as f:
            summary = json.load(f)
        
        print(f"\nIntegration Date: {summary.get('integration_date', 'N/A')}")
        print(f"\nSource Datasets:")
        for name, count in summary.get('source_datasets', {}).items():
            print(f"  • {name.title()}: {count} records")
        
        print(f"\nIntegrated Tables:")
        for name, count in summary.get('integrated_tables', {}).items():
            print(f"  • {name.replace('_', ' ').title()}: {count} records")
        
        print(f"\nData Quality:")
        for metric, value in summary.get('data_quality', {}).items():
            print(f"  • {metric.replace('_', ' ').title()}: {value}")
    
    except Exception as e:
        print(f"\n⚠️  Could not read integration summary: {e}")
        all_passed = False
    
    # Final verdict
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL VERIFICATION CHECKS PASSED!")
        print("\n🎉 Phase 1 & 2 complete! Ready for Phase 3 (Query System)")
    else:
        print("⚠️  SOME CHECKS FAILED!")
        print("\n📝 Review error messages above and re-run failed scripts")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
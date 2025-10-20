"""
Phase 1: Data Exploration Script
Calculus Carbon Assignment - AI Integration Task

This script performs initial data profiling on all 4 datasets:
- Project Developers
- Investors
- Emails
- Meeting Transcripts
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# Configuration
DATA_DIR = Path("data/raw")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True, parents=True)

# File mappings
FILES = {
    'developers': 'assign_data.xlsx  1 Project developer.csv',
    'investors': 'assign_data.xlsx  2 Investors.csv',
    'emails': 'assign_data.xlsx  3 Outlook emails.csv',
    'transcripts': 'assign_data.xlsx  4 Meeting transcripts.csv'
}

def load_dataset(filename):
    """Load dataset with proper header handling"""
    df = pd.read_csv(f"{DATA_DIR}/{filename}")
    
    # First row contains actual headers, rest is unnamed
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    # Remove any completely empty columns
    df = df.loc[:, df.columns.notna()]
    
    return df

def profile_dataset(df, dataset_name):
    """Generate detailed profile for a dataset"""
    profile = {
        'dataset': dataset_name,
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': {},
        'sample_records': df.head(2).to_dict('records')
    }
    
    # Missing value analysis
    for col in df.columns:
        null_count = df[col].isna().sum()
        empty_count = (df[col] == '').sum() if df[col].dtype == 'object' else 0
        total_missing = null_count + empty_count
        
        if total_missing > 0:
            profile['missing_values'][col] = {
                'count': int(total_missing),
                'percentage': round(total_missing / len(df) * 100, 2)
            }
    
    return profile

def main():
    """Run data exploration"""
    print("=" * 70)
    print("🔍 CALCULUS CARBON - DATA EXPLORATION")
    print("=" * 70)
    
    all_profiles = {}
    
    for name, filename in FILES.items():
        print(f"\n📊 Loading {name.upper()}...")
        
        try:
            df = load_dataset(filename)
            profile = profile_dataset(df, name)
            all_profiles[name] = profile
            
            print(f"   ✓ Records: {profile['rows']}")
            print(f"   ✓ Columns: {profile['columns']}")
            
            if profile['missing_values']:
                print(f"   ⚠ Missing values in {len(profile['missing_values'])} columns")
            else:
                print("   ✓ No missing values")
                
        except Exception as e:
            print(f"   ✗ Error loading {name}: {e}")
            continue
    
    # Save comprehensive report
    report_path = REPORT_DIR / "01_data_exploration_report.json"
    with open(report_path, 'w') as f:
        json.dump(all_profiles, f, indent=2)
    
    print(f"\n✅ Exploration complete! Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("📈 SUMMARY")
    print("=" * 70)
    for name, profile in all_profiles.items():
        print(f"{name.upper():15} | {profile['rows']:3} records | {profile['columns']:2} columns")
    
    return all_profiles

if __name__ == "__main__":
    profiles = main()
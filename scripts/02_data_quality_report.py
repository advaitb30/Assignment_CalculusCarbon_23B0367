"""
Phase 1: Data Quality Analysis Script
Calculus Carbon Assignment - AI Integration Task

Identifies specific data quality issues:
- Name variations and inconsistencies
- Data type mismatches
- Multi-language content
- Entity cross-references
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from collections import defaultdict

# Configuration
DATA_DIR = Path("data/raw")
REPORT_DIR = Path("reports")

FILES = {
    'developers': 'assign_data.xlsx  1 Project developer.csv',
    'investors': 'assign_data.xlsx  2 Investors.csv',
    'emails': 'assign_data.xlsx  3 Outlook emails.csv',
    'transcripts': 'assign_data.xlsx  4 Meeting transcripts.csv'
}

def load_dataset(filename):
    """Load dataset with proper header handling"""
    df = pd.read_csv(DATA_DIR / filename)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    df = df.loc[:, df.columns.notna()]
    return df

def analyze_name_variations(df):
    """Identify name variations in developers"""
    variations = []
    if 'DeveloperName' in df.columns and 'AlternateNames' in df.columns:
        for _, row in df.iterrows():
            if pd.notna(row['AlternateNames']):
                variations.append({
                    'canonical': row['DeveloperName'],
                    'alternates': row['AlternateNames'],
                    'id': row.get('DeveloperID', 'N/A')
                })
    return variations

def analyze_numeric_issues(df):
    """Find numeric fields stored as strings"""
    issues = []
    numeric_candidates = ['Hectares', 'EstimatedAnnualCredits', 'TicketSizeMin', 'TicketSizeMax']
    
    for col in numeric_candidates:
        if col in df.columns:
            for idx, val in df[col].items():
                if pd.notna(val) and isinstance(val, str):
                    # Check if it contains numeric patterns with commas
                    if re.search(r'\d+,\d+', str(val)):
                        issues.append({
                            'column': col,
                            'row': int(idx),
                            'value': str(val),
                            'type': 'comma_separated'
                        })
    return issues

def detect_multi_language(text):
    """Simple language detection (checks for Spanish keywords)"""
    if pd.isna(text):
        return None
    spanish_indicators = ['busca', 'prefiere', 'proyectos', 'sindicada', 'deuda', 'también']
    text_lower = str(text).lower()
    for indicator in spanish_indicators:
        if indicator in text_lower:
            return 'mixed_language'
    return 'english'

def analyze_language_mixing(df):
    """Identify multi-language content"""
    issues = []
    text_columns = ['InvestmentMandateText', 'Notes', 'Body', 'TranscriptText']
    
    for col in text_columns:
        if col in df.columns:
            for idx, text in df[col].items():
                lang = detect_multi_language(text)
                if lang == 'mixed_language':
                    issues.append({
                        'column': col,
                        'row': int(idx),
                        'snippet': str(text)[:100] + '...' if len(str(text)) > 100 else str(text)
                    })
    return issues

def find_entity_references(datasets):
    """Find cross-references between entities"""
    references = defaultdict(list)
    
    # Extract entity names
    developer_names = set(datasets['developers']['DeveloperName'].dropna())
    investor_names = set(datasets['investors']['FundName'].dropna())
    project_ids = set(datasets['developers']['ProjectID'].dropna())
    
    # Search in emails
    for idx, row in datasets['emails'].iterrows():
        body = str(row.get('Body', ''))
        subject = str(row.get('Subject', ''))
        combined = body + ' ' + subject
        
        for dev_name in developer_names:
            if dev_name.lower() in combined.lower():
                references['emails_mention_developers'].append({
                    'email_id': row.get('EmailID'),
                    'entity': dev_name,
                    'subject': subject
                })
        
        for inv_name in investor_names:
            if inv_name.lower() in combined.lower():
                references['emails_mention_investors'].append({
                    'email_id': row.get('EmailID'),
                    'entity': inv_name,
                    'subject': subject
                })
    
    return dict(references)

def main():
    """Generate comprehensive data quality report"""
    print("=" * 70)
    print("🔬 CALCULUS CARBON - DATA QUALITY ANALYSIS")
    print("=" * 70)
    
    # Load all datasets
    datasets = {}
    for name, filename in FILES.items():
        print(f"\n📂 Loading {name}...")
        datasets[name] = load_dataset(filename)
    
    # Run analyses
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    # 1. Name variations
    print("\n1️⃣ NAME VARIATIONS:")
    name_vars = analyze_name_variations(datasets['developers'])
    for var in name_vars[:5]:  # Show first 5
        print(f"   {var['canonical']} → {var['alternates']}")
    print(f"   ... Total: {len(name_vars)} developers with variations")
    
    # 2. Numeric issues
    print("\n2️⃣ NUMERIC FORMATTING ISSUES:")
    numeric_issues = analyze_numeric_issues(datasets['developers'])
    for issue in numeric_issues[:5]:
        print(f"   {issue['column']} (row {issue['row']}): \"{issue['value']}\"")
    print(f"   ... Total: {len(numeric_issues)} issues found")
    
    # 3. Language mixing
    print("\n3️⃣ MULTI-LANGUAGE CONTENT:")
    lang_issues = analyze_language_mixing(datasets['investors'])
    for issue in lang_issues[:3]:
        print(f"   Row {issue['row']}: {issue['snippet']}")
    print(f"   ... Total: {len(lang_issues)} instances found")
    
    # 4. Entity references
    print("\n4️⃣ ENTITY CROSS-REFERENCES:")
    refs = find_entity_references(datasets)
    for ref_type, items in refs.items():
        print(f"   {ref_type}: {len(items)} references")
    
    # Save detailed report
    report = {
        'name_variations': name_vars,
        'numeric_issues': numeric_issues,
        'language_issues': lang_issues,
        'entity_references': refs
    }
    
    report_path = REPORT_DIR / "02_data_quality_issues.json"
    pd.Series(report).to_json(report_path, indent=2)
    
    print(f"\n✅ Quality analysis complete! Report saved to: {report_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Name variations found:      {len(name_vars)}")
    print(f"Numeric format issues:      {len(numeric_issues)}")
    print(f"Multi-language instances:   {len(lang_issues)}")
    print(f"Cross-references found:     {sum(len(v) for v in refs.values())}")
    
    return report

if __name__ == "__main__":
    report = main()
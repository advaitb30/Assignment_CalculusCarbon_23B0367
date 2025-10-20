"""
Phase 2: Data Cleaning Script
Calculus Carbon Assignment - AI Integration Task

Performs comprehensive data cleaning:
- Standardize text (whitespace, encoding, case)
- Fix numeric fields (remove commas, convert types)
- Normalize dates
- Handle missing values
- Clean and standardize location/country names
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from unidecode import unidecode

# Configuration
DATA_DIR = Path("data/raw")
CLEAN_DIR = Path("data/cleaned")
CLEAN_DIR.mkdir(exist_ok=True, parents=True)

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

def clean_text(text):
    """Standardize text: strip whitespace, handle encoding"""
    if pd.isna(text):
        return None
    text = str(text).strip()
    text = ' '.join(text.split())  # Normalize whitespace
    text = unidecode(text)  # Handle special characters
    return text if text else None

def clean_numeric(value):
    """Convert numeric strings to actual numbers"""
    if pd.isna(value):
        return None
    
    # If already a number, return it
    if isinstance(value, (int, float)):
        return value
    
    # Convert string
    value_str = str(value).strip()
    
    # Handle 'NA', 'N/A', etc.
    if value_str.upper() in ['NA', 'N/A', 'NONE', '']:
        return None
    
    # Remove commas and convert
    value_str = value_str.replace(',', '')
    
    try:
        # Try integer first
        if '.' not in value_str:
            return int(value_str)
        return float(value_str)
    except:
        return None

def standardize_country(country):
    """Standardize country names"""
    if pd.isna(country):
        return None
    
    country_map = {
        'brasil': 'Brazil',
        'peru': 'Peru',
        'perú': 'Peru',
        'kenya': 'Kenya',
        'india': 'India',
        'philippines': 'Philippines',
        'philippines': 'Philippines',
        'mexico': 'Mexico',
        'méxico': 'Mexico',
        'argentina': 'Argentina',
        'ghana': 'Ghana',
        'vietnam': 'Vietnam',
        'viet nam': 'Vietnam',
        'ethiopia': 'Ethiopia',
        'uganda': 'Uganda',
        'colombia': 'Colombia'
    }
    
    country_clean = clean_text(country).lower()
    return country_map.get(country_clean, country.strip().title())

def standardize_project_type(proj_type):
    """Standardize project type abbreviations"""
    if pd.isna(proj_type):
        return None
    
    type_map = {
        'arr': 'ARR',
        'a&r': 'ARR',
        'redd+': 'REDD+',
        'redd': 'REDD+',
        'ild': 'ILD',
        'methane': 'Methane',
        'biochar': 'Biochar',
        'regenerative ag': 'Regenerative Agriculture',
        'regen ag': 'Regenerative Agriculture'
    }
    
    type_clean = clean_text(proj_type).lower()
    return type_map.get(type_clean, proj_type.strip())

def clean_developers(df):
    """Clean developers dataset"""
    print("   🧹 Cleaning developers...")
    
    df = df.copy()
    
    # Text columns
    text_cols = ['DeveloperName', 'Country', 'Status', 'LandTenure', 
                 'FPICStatus', 'PrimaryContactName', 'PrimaryContactEmail']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Standardize country
    if 'Country' in df.columns:
        df['Country'] = df['Country'].apply(standardize_country)
    
    # Standardize project type
    if 'ProjectType' in df.columns:
        df['ProjectType'] = df['ProjectType'].apply(standardize_project_type)
    
    # Numeric columns
    if 'Hectares' in df.columns:
        df['Hectares'] = df['Hectares'].apply(clean_numeric)
    
    if 'EstimatedAnnualCredits' in df.columns:
        df['EstimatedAnnualCredits'] = df['EstimatedAnnualCredits'].apply(clean_numeric)
    
    # Email standardization
    if 'PrimaryContactEmail' in df.columns:
        df['PrimaryContactEmail'] = df['PrimaryContactEmail'].str.lower()
    
    print(f"      ✓ Cleaned {len(df)} developer records")
    return df

def clean_investors(df):
    """Clean investors dataset"""
    print("   🧹 Cleaning investors...")
    
    df = df.copy()
    
    # Text columns
    text_cols = ['FundName', 'RegionFocus', 'SectorFocus', 'PreferredStructures',
                 'PrimaryContactName', 'PrimaryContactEmail']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Numeric columns
    if 'TicketSizeMin' in df.columns:
        df['TicketSizeMin'] = df['TicketSizeMin'].apply(clean_numeric)
    
    if 'TicketSizeMax' in df.columns:
        df['TicketSizeMax'] = df['TicketSizeMax'].apply(clean_numeric)
    
    # Email standardization
    if 'PrimaryContactEmail' in df.columns:
        df['PrimaryContactEmail'] = df['PrimaryContactEmail'].str.lower()
    
    # Currency standardization
    if 'TicketSizeCurrency' in df.columns:
        df['TicketSizeCurrency'] = df['TicketSizeCurrency'].str.upper()
    
    print(f"      ✓ Cleaned {len(df)} investor records")
    return df

def clean_emails(df):
    """Clean emails dataset"""
    print("   🧹 Cleaning emails...")
    
    df = df.copy()
    
    # Text columns
    text_cols = ['From', 'To', 'Subject']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Email standardization
    for col in ['From', 'To', 'Cc']:
        if col in df.columns:
            df[col] = df[col].str.lower()
    
    # Date handling
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    print(f"      ✓ Cleaned {len(df)} email records")
    return df

def clean_transcripts(df):
    """Clean transcripts dataset"""
    print("   🧹 Cleaning transcripts...")
    
    df = df.copy()
    
    # Clean transcript text
    if 'TranscriptText' in df.columns:
        df['TranscriptText'] = df['TranscriptText'].apply(clean_text)
    
    print(f"      ✓ Cleaned {len(df)} transcript records")
    return df

def main():
    """Run data cleaning pipeline"""
    print("=" * 70)
    print("🧼 CALCULUS CARBON - DATA CLEANING")
    print("=" * 70)
    
    cleaning_funcs = {
        'developers': clean_developers,
        'investors': clean_investors,
        'emails': clean_emails,
        'transcripts': clean_transcripts
    }
    
    cleaned_datasets = {}
    
    for name, filename in FILES.items():
        print(f"\n📂 Processing {name.upper()}...")
        
        # Load
        df = load_dataset(filename)
        print(f"   📊 Loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Clean
        df_clean = cleaning_funcs[name](df)
        
        # Save
        output_file = CLEAN_DIR / f"{name}_cleaned.csv"
        df_clean.to_csv(output_file, index=False)
        print(f"   💾 Saved to: {output_file}")
        
        cleaned_datasets[name] = df_clean
    
    print("\n" + "=" * 70)
    print("✅ DATA CLEANING COMPLETE")
    print("=" * 70)
    print(f"\nCleaned files saved in: {CLEAN_DIR}/")
    
    return cleaned_datasets

if __name__ == "__main__":
    cleaned = main()
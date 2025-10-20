"""
Phase 2: Data Integration Script
Calculus Carbon Assignment - AI Integration Task

Creates unified data structures:
- Master entities table (developers + investors)
- Enriched projects table
- Communications table (emails + transcripts)
- Relationships table (entity-to-entity connections)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Configuration
CLEAN_DIR = Path("data/cleaned")
INTEGRATED_DIR = Path("data/integrated")
INTEGRATED_DIR.mkdir(exist_ok=True, parents=True)

def load_cleaned_data():
    """Load all cleaned datasets"""
    datasets = {}
    for filename in CLEAN_DIR.glob("*_cleaned.csv"):
        name = filename.stem.replace('_cleaned', '')
        datasets[name] = pd.read_csv(filename)
    return datasets

def load_entity_maps():
    """Load entity resolution outputs"""
    with open(INTEGRATED_DIR / 'developer_entity_map.json', 'r') as f:
        dev_map = json.load(f)
    
    with open(INTEGRATED_DIR / 'investor_entity_map.json', 'r') as f:
        inv_map = json.load(f)
    
    with open(INTEGRATED_DIR / 'email_entity_mentions.json', 'r') as f:
        email_mentions = json.load(f)
    
    with open(INTEGRATED_DIR / 'transcript_entity_mentions.json', 'r') as f:
        transcript_mentions = json.load(f)
    
    return dev_map, inv_map, email_mentions, transcript_mentions

def create_master_entities_table(datasets, dev_map, inv_map):
    """Create unified entities table"""
    
    entities = []
    
    # Add developers
    for idx, row in datasets['developers'].iterrows():
        entity_id = row['DeveloperID']
        entities.append({
            'entity_id': entity_id,
            'entity_type': 'developer',
            'canonical_name': row['DeveloperName'],
            'alternate_names': dev_map.get(entity_id, {}).get('alternate_names', []),
            'primary_contact': row.get('PrimaryContactName'),
            'email': row.get('PrimaryContactEmail'),
            'country': row.get('Country'),
            'metadata': json.dumps({
                'project_type': row.get('ProjectType'),
                'status': row.get('Status'),
                'hectares': row.get('Hectares'),
                'credits': row.get('EstimatedAnnualCredits')
            })
        })
    
    # Add investors
    for idx, row in datasets['investors'].iterrows():
        entity_id = row['InvestorID']
        entities.append({
            'entity_id': entity_id,
            'entity_type': 'investor',
            'canonical_name': row['FundName'],
            'alternate_names': inv_map.get(entity_id, {}).get('alternate_names', []),
            'primary_contact': row.get('PrimaryContactName'),
            'email': row.get('PrimaryContactEmail'),
            'country': None,  # Investors don't have country in source
            'metadata': json.dumps({
                'region_focus': row.get('RegionFocus'),
                'sector_focus': row.get('SectorFocus'),
                'ticket_min': row.get('TicketSizeMin'),
                'ticket_max': row.get('TicketSizeMax'),
                'currency': row.get('TicketSizeCurrency')
            })
        })
    
    return pd.DataFrame(entities)

def create_enriched_projects_table(datasets):
    """Create enriched projects table with all available metadata"""
    
    projects = datasets['developers'].copy()
    
    # Add derived fields
    projects['last_updated'] = datetime.now().isoformat()
    
    # Parse alternate names into list
    if 'AlternateNames' in projects.columns:
        projects['alternate_names_list'] = projects['AlternateNames'].apply(
            lambda x: [name.strip() for name in str(x).split(';')] if pd.notna(x) else []
        )
    
    return projects

def create_communications_table(datasets, email_mentions, transcript_mentions):
    """Unified communications table"""
    
    communications = []
    
    # Add emails
    for idx, row in datasets['emails'].iterrows():
        email_id = row['EmailID']
        
        # Find entity mentions for this email
        mentions = next((m for m in email_mentions if m['email_id'] == email_id), None)
        
        developer_ids = []
        investor_ids = []
        
        if mentions:
            developer_ids = [d['entity_id'] for d in mentions.get('developers', [])]
            investor_ids = [i['entity_id'] for i in mentions.get('investors', [])]
        
        communications.append({
            'communication_id': email_id,
            'communication_type': 'email',
            'date': row.get('Date'),
            'from': row.get('From'),
            'to': row.get('To'),
            'subject': row.get('Subject'),
            'body': row.get('Body'),
            'mentioned_developers': json.dumps(developer_ids),
            'mentioned_investors': json.dumps(investor_ids)
        })
    
    # Add transcripts
    for idx, row in datasets['transcripts'].iterrows():
        transcript_id = row['TranscriptID']
        
        # Find entity mentions
        mentions = next((m for m in transcript_mentions if m['transcript_id'] == transcript_id), None)
        
        developer_ids = []
        investor_ids = []
        
        if mentions:
            developer_ids = [d['entity_id'] for d in mentions.get('developers', [])]
            investor_ids = [i['entity_id'] for i in mentions.get('investors', [])]
        
        communications.append({
            'communication_id': transcript_id,
            'communication_type': 'transcript',
            'date': None,  # Transcripts don't have dates in source
            'from': None,
            'to': None,
            'subject': None,
            'body': row.get('TranscriptText'),
            'mentioned_developers': json.dumps(developer_ids),
            'mentioned_investors': json.dumps(investor_ids)
        })
    
    return pd.DataFrame(communications)

def create_relationships_table(datasets, email_mentions, transcript_mentions):
    """Entity relationship table"""
    
    relationships = []
    
    # Relationships from emails
    for mention in email_mentions:
        email_id = mention['email_id']
        
        developers = mention.get('developers', [])
        investors = mention.get('investors', [])
        
        # Developer-Investor relationships
        for dev in developers:
            for inv in investors:
                relationships.append({
                    'entity_1': dev['entity_id'],
                    'entity_1_name': dev['entity_name'],
                    'entity_2': inv['entity_id'],
                    'entity_2_name': inv['entity_name'],
                    'relationship_type': 'mentioned_together',
                    'source_type': 'email',
                    'source_id': email_id
                })
    
    # Relationships from transcripts
    for mention in transcript_mentions:
        transcript_id = mention['transcript_id']
        
        developers = mention.get('developers', [])
        investors = mention.get('investors', [])
        
        # Developer-Investor relationships
        for dev in developers:
            for inv in investors:
                relationships.append({
                    'entity_1': dev['entity_id'],
                    'entity_1_name': dev['entity_name'],
                    'entity_2': inv['entity_id'],
                    'entity_2_name': inv['entity_name'],
                    'relationship_type': 'mentioned_together',
                    'source_type': 'transcript',
                    'source_id': transcript_id
                })
    
    # Add relationships from investor prior interactions
    for idx, row in datasets['investors'].iterrows():
        if pd.notna(row.get('PriorInteractions')):
            # Extract project/developer mentions from prior interactions text
            # This is a simplified version - could be enhanced with NLP
            interactions_text = str(row['PriorInteractions'])
            
            # Look for project IDs (P001, P002, etc.)
            import re
            project_ids = re.findall(r'P\d{3}', interactions_text)
            
            for project_id in project_ids:
                # Find corresponding developer
                dev_row = datasets['developers'][datasets['developers']['ProjectID'] == project_id]
                if not dev_row.empty:
                    developer_id = dev_row.iloc[0]['DeveloperID']
                    relationships.append({
                        'entity_1': row['InvestorID'],
                        'entity_1_name': row['FundName'],
                        'entity_2': developer_id,
                        'entity_2_name': dev_row.iloc[0]['DeveloperName'],
                        'relationship_type': 'prior_interaction',
                        'source_type': 'investor_notes',
                        'source_id': row['InvestorID']
                    })
    
    df = pd.DataFrame(relationships)
    
    # Deduplicate
    if not df.empty:
        df = df.drop_duplicates(subset=['entity_1', 'entity_2', 'relationship_type'])
    
    return df

def main():
    """Run data integration"""
    print("=" * 70)
    print("🔗 CALCULUS CARBON - DATA INTEGRATION")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading cleaned data and entity maps...")
    datasets = load_cleaned_data()
    dev_map, inv_map, email_mentions, transcript_mentions = load_entity_maps()
    
    # Create unified tables
    print("\n🏗️  Creating unified data structures...")
    
    print("   1️⃣ Master entities table...")
    entities = create_master_entities_table(datasets, dev_map, inv_map)
    entities.to_csv(INTEGRATED_DIR / 'master_entities.csv', index=False)
    print(f"      ✓ {len(entities)} entities")
    
    print("   2️⃣ Enriched projects table...")
    projects = create_enriched_projects_table(datasets)
    projects.to_csv(INTEGRATED_DIR / 'enriched_projects.csv', index=False)
    print(f"      ✓ {len(projects)} projects")
    
    print("   3️⃣ Communications table...")
    communications = create_communications_table(datasets, email_mentions, transcript_mentions)
    communications.to_csv(INTEGRATED_DIR / 'unified_communications.csv', index=False)
    print(f"      ✓ {len(communications)} communications")
    
    print("   4️⃣ Relationships table...")
    relationships = create_relationships_table(datasets, email_mentions, transcript_mentions)
    relationships.to_csv(INTEGRATED_DIR / 'entity_relationships.csv', index=False)
    print(f"      ✓ {len(relationships)} relationships")
    
    # Create summary report
    print("\n📊 Generating integration summary...")
    
    summary = {
        'integration_date': datetime.now().isoformat(),
        'source_datasets': {
            'developers': len(datasets['developers']),
            'investors': len(datasets['investors']),
            'emails': len(datasets['emails']),
            'transcripts': len(datasets['transcripts'])
        },
        'integrated_tables': {
            'master_entities': len(entities),
            'enriched_projects': len(projects),
            'unified_communications': len(communications),
            'entity_relationships': len(relationships)
        },
        'data_quality': {
            'total_entities': len(entities),
            'developers': len(entities[entities['entity_type'] == 'developer']),
            'investors': len(entities[entities['entity_type'] == 'investor']),
            'communications_with_entities': len(communications[
                (communications['mentioned_developers'] != '[]') | 
                (communications['mentioned_investors'] != '[]')
            ])
        }
    }
    
    with open(INTEGRATED_DIR / 'integration_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📈 INTEGRATION SUMMARY")
    print("=" * 70)
    print(f"\nSource Data:")
    print(f"  • Developers:  {summary['source_datasets']['developers']}")
    print(f"  • Investors:   {summary['source_datasets']['investors']}")
    print(f"  • Emails:      {summary['source_datasets']['emails']}")
    print(f"  • Transcripts: {summary['source_datasets']['transcripts']}")
    
    print(f"\nIntegrated Tables:")
    print(f"  • Master Entities:        {summary['integrated_tables']['master_entities']}")
    print(f"  • Enriched Projects:      {summary['integrated_tables']['enriched_projects']}")
    print(f"  • Unified Communications: {summary['integrated_tables']['unified_communications']}")
    print(f"  • Entity Relationships:   {summary['integrated_tables']['entity_relationships']}")
    
    print(f"\nData Quality:")
    print(f"  • Total unique entities: {summary['data_quality']['total_entities']}")
    print(f"  • Communications with entity mentions: {summary['data_quality']['communications_with_entities']}")
    
    print(f"\n💾 All outputs saved to: {INTEGRATED_DIR}/")
    print("\n✅ DATA INTEGRATION COMPLETE!")
    
    return summary

if __name__ == "__main__":
    summary = main()
"""
Phase 2: Entity Resolution Script
Calculus Carbon Assignment - AI Integration Task

Performs entity resolution using fuzzy matching:
- Create canonical entity IDs
- Handle name variations (VerdeNova vs Verde Nova)
- Build entity mapping tables
- Resolve duplicate/similar entities
"""

import pandas as pd
import numpy as np
from pathlib import Path
from rapidfuzz import fuzz, process
import json

# Configuration
CLEAN_DIR = Path("data/cleaned")
OUTPUT_DIR = Path("data/integrated")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Fuzzy matching thresholds
SIMILARITY_THRESHOLD = 85  # 85% similarity to be considered a match

def load_cleaned_data():
    """Load cleaned datasets"""
    datasets = {}
    for filename in CLEAN_DIR.glob("*_cleaned.csv"):
        name = filename.stem.replace('_cleaned', '')
        datasets[name] = pd.read_csv(filename)
    return datasets

def normalize_name(name):
    """Normalize name for comparison"""
    if pd.isna(name):
        return ""
    
    name = str(name).lower()
    # Remove common suffixes
    name = name.replace(' ltd', '').replace(' llc', '').replace(' inc', '')
    name = name.replace(' solutions', '').replace(' agro', '').replace(' capital', '')
    # Remove punctuation
    name = name.replace('.', '').replace(',', '').replace('-', ' ')
    # Normalize spaces
    name = ' '.join(name.split())
    return name

def build_entity_mapping(df, id_col, name_col, alt_names_col=None):
    """Build entity ID to canonical name mapping with alternates"""
    
    entity_map = {}
    
    for idx, row in df.iterrows():
        entity_id = row[id_col]
        canonical_name = row[name_col]
        
        # Start with canonical name
        names = [canonical_name]
        
        # Add alternates if available
        if alt_names_col and alt_names_col in df.columns and pd.notna(row[alt_names_col]):
            alternates = str(row[alt_names_col]).split(';')
            alternates = [alt.strip() for alt in alternates if alt.strip()]
            names.extend(alternates)
        
        # Normalize all names
        normalized_names = [normalize_name(n) for n in names]
        
        entity_map[entity_id] = {
            'canonical_name': canonical_name,
            'alternate_names': names[1:] if len(names) > 1 else [],
            'normalized_variants': list(set(normalized_names))
        }
    
    return entity_map

def find_similar_entities(entity_map, threshold=SIMILARITY_THRESHOLD):
    """Find potentially duplicate entities using fuzzy matching"""
    
    potential_duplicates = []
    entity_ids = list(entity_map.keys())
    
    for i, id1 in enumerate(entity_ids):
        for id2 in entity_ids[i+1:]:
            
            entity1 = entity_map[id1]
            entity2 = entity_map[id2]
            
            # Compare all name variants
            max_similarity = 0
            best_match = None
            
            for name1 in entity1['normalized_variants']:
                for name2 in entity2['normalized_variants']:
                    similarity = fuzz.ratio(name1, name2)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_match = (name1, name2)
            
            if max_similarity >= threshold:
                potential_duplicates.append({
                    'id1': id1,
                    'entity1': entity1['canonical_name'],
                    'id2': id2,
                    'entity2': entity2['canonical_name'],
                    'similarity': max_similarity,
                    'matched_variants': best_match
                })
    
    return potential_duplicates

def create_reverse_lookup(entity_map):
    """Create reverse lookup: any name variant → entity ID"""
    
    reverse_map = {}
    
    for entity_id, data in entity_map.items():
        # Add canonical name
        canonical_norm = normalize_name(data['canonical_name'])
        reverse_map[canonical_norm] = entity_id
        
        # Add all normalized variants
        for variant in data['normalized_variants']:
            if variant:  # Skip empty
                reverse_map[variant] = entity_id
    
    return reverse_map

def find_entity_in_text(text, entity_map):
    """Find entity mentions in unstructured text"""
    
    if pd.isna(text):
        return []
    
    text_lower = str(text).lower()
    found_entities = []
    
    for entity_id, data in entity_map.items():
        # Check canonical name
        if data['canonical_name'].lower() in text_lower:
            found_entities.append({
                'entity_id': entity_id,
                'entity_name': data['canonical_name'],
                'matched_text': data['canonical_name']
            })
            continue
        
        # Check alternates
        for alt_name in data['alternate_names']:
            if alt_name.lower() in text_lower:
                found_entities.append({
                    'entity_id': entity_id,
                    'entity_name': data['canonical_name'],
                    'matched_text': alt_name
                })
                break
    
    return found_entities

def main():
    """Run entity resolution"""
    print("=" * 70)
    print("🔗 CALCULUS CARBON - ENTITY RESOLUTION")
    print("=" * 70)
    
    # Load cleaned data
    print("\n📂 Loading cleaned datasets...")
    datasets = load_cleaned_data()
    
    # Build entity mappings
    print("\n🏗️  Building entity mappings...")
    
    developer_map = build_entity_mapping(
        datasets['developers'],
        id_col='DeveloperID',
        name_col='DeveloperName',
        alt_names_col='AlternateNames'
    )
    print(f"   ✓ Developer entities: {len(developer_map)}")
    
    investor_map = build_entity_mapping(
        datasets['investors'],
        id_col='InvestorID',
        name_col='FundName',
        alt_names_col=None  # Investors don't have alt names in data
    )
    print(f"   ✓ Investor entities: {len(investor_map)}")
    
    # Find potential duplicates
    print("\n🔍 Detecting potential duplicates...")
    
    dev_duplicates = find_similar_entities(developer_map, threshold=SIMILARITY_THRESHOLD)
    print(f"   ⚠  Found {len(dev_duplicates)} potential developer duplicates")
    
    if dev_duplicates:
        print("\n   Sample duplicates:")
        for dup in dev_duplicates[:3]:
            print(f"      • {dup['entity1']} ≈ {dup['entity2']} ({dup['similarity']}% similar)")
    
    inv_duplicates = find_similar_entities(investor_map, threshold=SIMILARITY_THRESHOLD)
    print(f"   ⚠  Found {len(inv_duplicates)} potential investor duplicates")
    
    # Create reverse lookups
    print("\n🗺️  Creating reverse lookups...")
    dev_reverse = create_reverse_lookup(developer_map)
    inv_reverse = create_reverse_lookup(investor_map)
    print(f"   ✓ Developer name variants: {len(dev_reverse)}")
    print(f"   ✓ Investor name variants: {len(inv_reverse)}")
    
    # Find entity mentions in emails and transcripts
    print("\n🔎 Finding entity mentions in communications...")
    
    email_mentions = []
    for idx, row in datasets['emails'].iterrows():
        text = str(row.get('Subject', '')) + ' ' + str(row.get('Body', ''))
        
        devs_found = find_entity_in_text(text, developer_map)
        invs_found = find_entity_in_text(text, investor_map)
        
        if devs_found or invs_found:
            email_mentions.append({
                'email_id': row.get('EmailID'),
                'developers': devs_found,
                'investors': invs_found
            })
    
    print(f"   ✓ Emails with entity mentions: {len(email_mentions)}")
    
    transcript_mentions = []
    for idx, row in datasets['transcripts'].iterrows():
        text = str(row.get('TranscriptText', ''))
        
        devs_found = find_entity_in_text(text, developer_map)
        invs_found = find_entity_in_text(text, investor_map)
        
        if devs_found or invs_found:
            transcript_mentions.append({
                'transcript_id': row.get('TranscriptID'),
                'developers': devs_found,
                'investors': invs_found
            })
    
    print(f"   ✓ Transcripts with entity mentions: {len(transcript_mentions)}")
    
    # Save outputs
    print("\n💾 Saving entity resolution outputs...")
    
    # Save entity maps
    with open(OUTPUT_DIR / 'developer_entity_map.json', 'w') as f:
        json.dump(developer_map, f, indent=2)
    
    with open(OUTPUT_DIR / 'investor_entity_map.json', 'w') as f:
        json.dump(investor_map, f, indent=2)
    
    # Save reverse lookups
    with open(OUTPUT_DIR / 'developer_reverse_lookup.json', 'w') as f:
        json.dump(dev_reverse, f, indent=2)
    
    with open(OUTPUT_DIR / 'investor_reverse_lookup.json', 'w') as f:
        json.dump(inv_reverse, f, indent=2)
    
    # Save duplicate findings
    pd.DataFrame(dev_duplicates).to_csv(OUTPUT_DIR / 'potential_developer_duplicates.csv', index=False)
    pd.DataFrame(inv_duplicates).to_csv(OUTPUT_DIR / 'potential_investor_duplicates.csv', index=False)
    
    # Save entity mentions
    with open(OUTPUT_DIR / 'email_entity_mentions.json', 'w') as f:
        json.dump(email_mentions, f, indent=2)
    
    with open(OUTPUT_DIR / 'transcript_entity_mentions.json', 'w') as f:
        json.dump(transcript_mentions, f, indent=2)
    
    print(f"   ✓ Files saved to: {OUTPUT_DIR}/")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ENTITY RESOLUTION SUMMARY")
    print("=" * 70)
    print(f"Total developer entities:        {len(developer_map)}")
    print(f"Total investor entities:         {len(investor_map)}")
    print(f"Potential duplicates found:      {len(dev_duplicates) + len(inv_duplicates)}")
    print(f"Emails with entity mentions:     {len(email_mentions)}")
    print(f"Transcripts with entity mentions: {len(transcript_mentions)}")
    
    print("\n✅ Entity resolution complete!")
    
    return {
        'developer_map': developer_map,
        'investor_map': investor_map,
        'email_mentions': email_mentions,
        'transcript_mentions': transcript_mentions
    }

if __name__ == "__main__":
    result = main()
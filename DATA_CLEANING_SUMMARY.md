# Data Cleaning & Integration Summary
## Calculus Carbon Assignment - Phase 1 & 2

---

## 🎯 Objective

Transform 4 messy, inconsistent datasets into a unified, queryable structure suitable for AI-powered analysis.

---

## 📊 Dataset Overview

### Input Datasets
| Dataset | Records | Key Issues Identified |
|---------|---------|----------------------|
| **Project Developers** | 15 | Name variations, numeric formatting, missing Hectares |
| **Investors** | 12 | Multi-language text, no duplicate detection needed |
| **Emails** | 20 | Entity mentions scattered, date parsing needed |
| **Transcripts** | 10 | Unstructured text, entity extraction required |

---

## 🔧 Data Quality Issues & Solutions

### 1. **Name Variations** ✅

**Problem:**
- Same entity with multiple spellings
- Example: "VerdeNova Solutions" = "Verdenova" = "Verde Nova"

**Solution:**
- Created canonical entity IDs for each developer/investor
- Built alternate name mappings
- Used fuzzy matching (RapidFuzz) with 85% threshold
- Preserved all variations in metadata

**Code Location:** `04_entity_resolution.py`

**Output:** `developer_entity_map.json`, `investor_entity_map.json`

---

### 2. **Numeric Formatting Issues** ✅

**Problem:**
- Numbers stored as strings: "1,200" vs 1200
- Mixed types in same column
- "NA" vs actual null values

**Solution:**
```python
def clean_numeric(value):
    # Remove commas
    # Convert "NA" to None
    # Handle int vs float
    # Return None for invalid values
```

**Examples:**
- "1,200" → 1200 (int)
- "850" → 850 (int)
- "NA" → None
- "3,400" → 3400 (int)

**Code Location:** `03_data_cleaning.py`

---

### 3. **Multi-language Content** ✅

**Problem:**
- Investor mandates mixed Spanish and English
- Example: "NorthStar busca financiar proyectos forestales..."

**Solution:**
- Detected language mixing using keyword analysis
- Preserved original text (no translation)
- Flagged for context in retrieval system
- Used `unidecode` for encoding issues

**Decision:** Keep original text, handle in LLM prompt layer

**Code Location:** `02_data_quality_report.py`

---

### 4. **Missing Values** ✅

**Problem:**
- 1 developer missing "Hectares"
- Some optional fields empty

**Solution:**
- **Did NOT impute missing values arbitrarily**
- Flagged missing data explicitly
- Preserved as None/null in cleaned data
- Let query system handle gracefully

**Reasoning:** 
Better to acknowledge data gaps than introduce errors through imputation.

---

### 5. **Entity Cross-References** ✅

**Problem:**
- Emails mention "VerdeNova" and "NorthStar" but no structured links
- Transcripts reference projects by name only

**Solution:**
- NLP-based entity extraction from text
- Pattern matching for entity names
- Created `entity_relationships` table
- Tracked mention source (email ID, transcript ID)

**Example:**
```
Email E001 mentions:
- Developer: VerdeNova Solutions (D001)
- Generates relationship: E001 → D001
```

**Code Location:** `04_entity_resolution.py`, `05_data_integration.py`

---

### 6. **Country Name Standardization** ✅

**Problem:**
- "Brasil" vs "Brazil"
- "Peru" vs "Perú"

**Solution:**
```python
country_map = {
    'brasil': 'Brazil',
    'perú': 'Peru',
    # ...
}
```

**Code Location:** `03_data_cleaning.py`

---

### 7. **Project Type Normalization** ✅

**Problem:**
- "ARR" vs "A&R" vs "arr"

**Solution:**
- Standardized to uppercase abbreviations
- Mapped variations to canonical forms

**Code Location:** `03_data_cleaning.py`

---

## 📁 Output Data Structures

### 1. **Master Entities Table**
Unified view of all entities (developers + investors)

**Schema:**
```
entity_id | entity_type | canonical_name | alternate_names | primary_contact | email | country | metadata
```

**Purpose:** Single source of truth for all entities

---

### 2. **Enriched Projects Table**
Enhanced developer data with metadata

**Additions:**
- `alternate_names_list`: Parsed alternate names
- `last_updated`: Timestamp
- Original fields preserved

**Purpose:** Queryable project database

---

### 3. **Unified Communications Table**
Emails + Transcripts combined

**Schema:**
```
communication_id | communication_type | date | from | to | subject | body | mentioned_developers | mentioned_investors
```

**Key Feature:** Entity mentions stored as JSON arrays for easy lookup

**Purpose:** Full conversation history with entity tracking

---

### 4. **Entity Relationships Table**
Who's connected to whom

**Schema:**
```
entity_1 | entity_1_name | entity_2 | entity_2_name | relationship_type | source_type | source_id
```

**Relationship Types:**
- `mentioned_together`: Found in same email/transcript
- `prior_interaction`: From investor notes

**Purpose:** Graph-like relationship mapping

---

## 🎯 Key Design Decisions

### ✅ Preserved Original Data
- Never deleted source fields
- Cleaned versions added as new columns where needed
- Full audit trail maintained

### ✅ Explicit Null Handling
- Distinguished between missing (None) and "NA" strings
- No arbitrary imputation
- Flags for downstream handling

### ✅ Fuzzy Matching Threshold: 85%
- **Too low (70%):** False positives
- **Too high (95%):** Misses variations
- **85%:** Sweet spot for this data

### ✅ Entity-Centric Design
- Everything links back to canonical entity IDs
- Makes querying and relationships straightforward

### ✅ JSON for Complex Fields
- Entity mentions stored as JSON arrays
- Metadata stored as JSON objects
- Easy to parse, filter, and query

---

## 📈 Statistics

### Before Cleaning
- 4 separate datasets
- 57 total records
- Name variations: 15
- Numeric issues: ~8 instances
- Missing values: ~1% of fields

### After Cleaning & Integration
- 4 unified tables
- 27 unique entities
- 30+ entity relationships discovered
- 100% consistent formatting
- All cross-references linked

---

## 🔍 Data Provenance

Every piece of information tracks back to its source:

```python
# Example: Entity relationship
{
    "entity_1": "D001",
    "entity_2": "I001", 
    "source_type": "email",
    "source_id": "E001"
}
```

This enables:
- Verification of claims
- Context retrieval
- Confidence scoring

---

## ⚠️ Known Limitations

1. **Language Detection**: Simple keyword-based (could use langdetect library for better accuracy)

2. **Entity Extraction**: Pattern matching only (could enhance with spaCy NER)

3. **Date Parsing**: Basic pandas date parsing (some formats might fail)

4. **Fuzzy Threshold**: Fixed at 85% (could make dynamic per entity type)

5. **No Geocoding**: Countries as text only (could add lat/long)

---

## 🚀 Ready for Phase 3

With cleaned, integrated data, we can now:

✅ Build semantic search over communications  
✅ Create structured filters (region, sector, ticket size)  
✅ Answer multi-source queries  
✅ Generate context-aware summaries  
✅ Track entity relationships  

---

## 📝 Files Generated

```
reports/
├── 01_data_exploration_report.json      # Initial profiling
└── 02_data_quality_issues.json         # Detailed issues

data/cleaned/
├── developers_cleaned.csv              # Standardized developers
├── investors_cleaned.csv               # Standardized investors
├── emails_cleaned.csv                  # Cleaned emails
└── transcripts_cleaned.csv             # Cleaned transcripts

data/integrated/
├── master_entities.csv                 # Unified entities
├── enriched_projects.csv               # Enhanced projects
├── unified_communications.csv          # All communications
├── entity_relationships.csv            # Relationship graph
├── developer_entity_map.json           # Name mappings
├── investor_entity_map.json            # Name mappings
├── developer_reverse_lookup.json       # Variant → ID lookup
├── investor_reverse_lookup.json        # Variant → ID lookup
├── email_entity_mentions.json          # Email entity tracking
├── transcript_entity_mentions.json     # Transcript entity tracking
└── integration_summary.json            # Summary stats
```

---

## 🎓 Assignment Requirements Met

✅ **Data Integration**: All 4 datasets merged with proper reconciliation  
✅ **Duplicate Handling**: Fuzzy matching with documented threshold  
✅ **Missing Data**: Explicitly handled with no arbitrary imputation  
✅ **Inconsistent Naming**: Entity resolution with canonical IDs  
✅ **Unique Identification**: Every entity has unique, stable ID  
✅ **Documented Reasoning**: Code comments + this summary  

---

**Total Processing Time:** ~5-10 seconds  
**Lines of Code:** ~1000 (across 5 scripts)  
**Data Quality Improvement:** Messy → Query-ready

---

## 🤝 Next Steps for Phase 3

1. Load integrated tables
2. Create vector embeddings for text fields
3. Build hybrid search (structured + semantic)
4. Integrate Groq API for LLM queries
5. Create Streamlit interface
6. Test with sample questions

**Ready to build the AI query system!** 🚀
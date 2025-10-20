# Quick Reference Guide
## Calculus Carbon Assignment - Phase 1 & 2

---

## 🚀 Quick Start (3 Steps)

```bash
# 1. Setup
python setup_project.py
pip install -r requirements.txt

# 2. Add data files to data/raw/

# 3. Run everything
python run_all_scripts.py
```

---

## 📋 Script Execution Order

| Order | Script | Purpose | Output |
|-------|--------|---------|--------|
| 1 | `01_data_exploration.py` | Profile data | `reports/01_*.json` |
| 2 | `02_data_quality_report.py` | Find issues | `reports/02_*.json` |
| 3 | `03_data_cleaning.py` | Clean data | `data/cleaned/*.csv` |
| 4 | `04_entity_resolution.py` | Resolve duplicates | `data/integrated/*.json` |
| 5 | `05_data_integration.py` | Merge datasets | `data/integrated/*.csv` |

---

## 🔧 Individual Script Usage

### Run single script:
```bash
cd scripts
python 01_data_exploration.py
```

### Check outputs:
```bash
python verify_outputs.py
```

---

## 📊 Key Output Files

### Must Have for Assignment:
✅ `master_entities.csv` - All entities unified  
✅ `enriched_projects.csv` - Enhanced project data  
✅ `unified_communications.csv` - All communications  
✅ `entity_relationships.csv` - Entity connections  

### Supporting Files:
- `developer_entity_map.json` - Name variations  
- `integration_summary.json` - Stats  

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `FileNotFoundError` | Check files in `data/raw/` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Empty outputs | Run scripts in order (01→05) |
| Encoding errors | Ensure UTF-8 encoding |

---

## 📈 Expected Results

After successful run:
- ✅ 2 JSON reports in `reports/`
- ✅ 4 cleaned CSVs in `data/cleaned/`
- ✅ 11 files in `data/integrated/`
- ✅ 27 unique entities identified
- ✅ 30+ relationships discovered

---

## 🎯 Sample Queries (For Phase 3)

Once data is clean, you can answer:

```python
# Which developers have ARR projects in Latin America?
df = pd.read_csv('data/integrated/enriched_projects.csv')
arr_latam = df[
    (df['ProjectType'] == 'ARR') & 
    (df['Country'].isin(['Brazil', 'Peru', 'Mexico']))
]

# Which investors match Project P001?
# (Use entity_relationships.csv)

# Summarize all communication about VerdeNova
# (Use unified_communications.csv + filter by mentioned_developers)
```

---

## 🔑 Key Data Quality Decisions

| Issue | Decision | Rationale |
|-------|----------|-----------|
| Name variations | Canonical IDs | Enables fuzzy matching |
| Missing values | Keep as None | Better than imputation |
| Numeric strings | Convert to int/float | Enable calculations |
| Multi-language | Preserve original | LLM handles in context |
| Duplicates | 85% threshold | Balance precision/recall |

---

## 📁 Directory Structure

```
AI_Integration_Assignment_CalculusCarbon_<Name>_<Roll>/
├── data/
│   ├── raw/          # Original CSVs (input)
│   ├── cleaned/      # Cleaned CSVs (output)
│   └── integrated/   # Final tables (output)
├── reports/          # JSON reports (output)
├── scripts/          # All Python scripts
├── requirements.txt
└── README.md
```

---

## ⏱️ Estimated Execution Time

| Script | Time |
|--------|------|
| 01 | ~1 sec |
| 02 | ~1 sec |
| 03 | ~1 sec |
| 04 | ~2 sec |
| 05 | ~1 sec |
| **Total** | **~6 sec** |

---

## 🎓 Assignment Checklist

Before submission:
- [ ] All 5 scripts run successfully
- [ ] `verify_outputs.py` passes all checks
- [ ] `integration_summary.json` shows expected stats
- [ ] All output files present
- [ ] README and documentation complete

---

## 🆘 Need Help?

1. Check `DATA_CLEANING_SUMMARY.md` for detailed explanations
2. Review code comments in scripts
3. Verify folder structure with `setup_project.py`
4. Run `verify_outputs.py` to check what's missing

---

## 🚀 Ready for Phase 3?

✅ Clean, integrated data  
✅ Entity resolution complete  
✅ Relationships mapped  

**Next:** Build query layer + chatbot interface!
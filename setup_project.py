"""
Project Setup Script
Calculus Carbon Assignment - AI Integration Task

Creates the required folder structure for the assignment.
"""

from pathlib import Path

def create_folder_structure():
    """Create all required directories"""
    
    folders = [
        "data/raw",
        "data/cleaned",
        "data/integrated",
        "reports",
        "scripts",
        "notebooks"
    ]
    
    print("=" * 70)
    print("📁 CREATING PROJECT STRUCTURE")
    print("=" * 70)
    
    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ Created: {folder}/")
    
    # Create .gitkeep files to preserve empty directories
    gitkeep_dirs = [
        "data/raw",
        "data/cleaned",
        "data/integrated",
        "reports"
    ]
    
    for folder in gitkeep_dirs:
        gitkeep = Path(folder) / ".gitkeep"
        gitkeep.touch()
    
    print("\n✅ Folder structure created successfully!")
    print("\n📝 Next Steps:")
    print("   1. Place your 4 CSV files in data/raw/")
    print("   2. Run: python run_all_scripts.py")
    print("   3. Or run scripts individually in order:")
    print("      - python 01_data_exploration.py")
    print("      - python 02_data_quality_report.py")
    print("      - python 03_data_cleaning.py")
    print("      - python 04_entity_resolution.py")
    print("      - python 05_data_integration.py")
    
    # Create a README in data/raw
    readme_content = """# Raw Data Directory

Place your 4 CSV files here:
1. assign_data.xlsx  1 Project developer.csv
2. assign_data.xlsx  2 Investors.csv
3. assign_data.xlsx  3 Outlook emails.csv
4. assign_data.xlsx  4 Meeting transcripts.csv

These are the original, unmodified files from the assignment.
"""
    
    with open("data/raw/README.md", "w") as f:
        f.write(readme_content)
    
    print("\n   ✓ Created README in data/raw/")

if __name__ == "__main__":
    create_folder_structure()
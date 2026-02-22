"""
Cleanup and organize the IPL Analytics project
Consolidate multiple scripts into organized structure
"""

import os
import shutil

def cleanup_project():
    """Organize project files into a cleaner structure"""
    
    print("🧹 Cleaning up IPL Analytics project...")
    
    # Create organized directories
    directories = {
        'scripts': 'Individual analysis scripts (archived)',
        'data': 'Data files',
        'docs': 'Documentation'
    }
    
    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"📁 Created {dir_name}/ - {description}")
    
    # Files to move to scripts/ (archive)
    scripts_to_archive = [
        'analyze_years.py',
        'ball_position_analysis.py', 
        'compare_seasons.py',
        'filter_mens_ipl.py',
        'test_api.py',
        'test_query.py',
        'validate_data.py'
    ]
    
    # Files to move to data/
    data_files = [
        'ipl_data_2024.csv',
        'ipl_data_2025.csv', 
        'ipl_data_mens_only.csv',
        'ipl_data_original_backup.csv'
    ]
    
    # Files to move to docs/
    doc_files = [
        'IPL_DATA_SCHEMA_FOR_GEMINI.txt',
        'GEMINI_LEARNING_COMPLETE.txt'
    ]
    
    # Move files
    moved_count = 0
    
    for script in scripts_to_archive:
        if os.path.exists(script):
            shutil.move(script, f'scripts/{script}')
            print(f"📦 Moved {script} to scripts/")
            moved_count += 1
    
    for data_file in data_files:
        if os.path.exists(data_file):
            shutil.move(data_file, f'data/{data_file}')
            print(f"📊 Moved {data_file} to data/")
            moved_count += 1
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            shutil.move(doc_file, f'docs/{doc_file}')
            print(f"📚 Moved {doc_file} to docs/")
            moved_count += 1
    
    # Show final structure
    print(f"\n✅ Cleanup complete! Moved {moved_count} files")
    print("\n📁 New project structure:")
    print("├── 🏏 MAIN FILES (keep these)")
    print("│   ├── enhanced_gemini_ipl_backend.py")
    print("│   ├── enhanced_gemini_streamlit_app.py") 
    print("│   ├── ipl_analytics_toolkit.py (NEW - consolidated)")
    print("│   ├── run_app.py")
    print("│   ├── setup.py")
    print("│   ├── ipl_data.csv")
    print("│   ├── .env")
    print("│   └── requirements.txt")
    print("│")
    print("├── 📁 scripts/ (archived individual scripts)")
    print("├── 📁 data/ (backup and seasonal data)")
    print("└── 📁 docs/ (documentation)")
    
    print(f"\n🎯 RECOMMENDED USAGE:")
    print(f"1. Use 'python ipl_analytics_toolkit.py' for quick analysis")
    print(f"2. Use 'python run_app.py' for the web interface")
    print(f"3. Individual scripts are archived in scripts/ folder")

def show_current_files():
    """Show current files in directory"""
    print("📋 Current files in project:")
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for file in sorted(files):
        size = os.path.getsize(file)
        print(f"  {file} ({size} bytes)")

if __name__ == "__main__":
    print("🏏 IPL Analytics Project Cleanup")
    print("=" * 40)
    
    show_current_files()
    
    print(f"\n" + "=" * 40)
    response = input("Proceed with cleanup? (y/n): ").lower().strip()
    
    if response == 'y':
        cleanup_project()
    else:
        print("❌ Cleanup cancelled")
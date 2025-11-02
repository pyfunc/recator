#!/usr/bin/env python3
"""
Quick Start Guide for Recator Library
"""

from recator import Recator
import sys

def quick_example():
    """Quick example of using Recator"""
    
    print("""
╔════════════════════════════════════════════╗
║       RECATOR - Quick Start Example        ║
╚════════════════════════════════════════════╝
    """)
    
    # Get project path from command line or use current directory
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
        print("💡 Tip: You can specify a project path as argument")
        print(f"   Using current directory: {project_path}\n")
    
    # Configure Recator
    config = {
        'min_lines': 4,              # Minimum duplicate size
        'min_tokens': 30,            # Minimum tokens
        'similarity_threshold': 0.85, # 85% similarity threshold
        'languages': ['python', 'javascript', 'java'],  # Languages to analyze
        'safe_mode': True            # Don't modify original files
    }
    
    try:
        # Initialize Recator
        print(f"🔍 Initializing Recator for: {project_path}")
        recator = Recator(project_path, config)
        
        # Analyze for duplicates
        print("📊 Analyzing for code duplicates...")
        results = recator.analyze()
        
        # Display results
        print("\n📈 Analysis Results:")
        print(f"  ├─ Files scanned: {results['total_files']}")
        print(f"  ├─ Files analyzed: {results['parsed_files']}")
        print(f"  └─ Duplicates found: {results['duplicates_found']}")
        
        if results['duplicates_found'] > 0:
            # Show top 3 duplicates
            print("\n🔝 Top duplicates found:")
            for i, dup in enumerate(results['duplicates'][:3], 1):
                print(f"\n  [{i}] {dup.get('type', 'Unknown').replace('_', ' ').title()}")
                
                if 'files' in dup:
                    print(f"      Files involved: {len(dup['files'])}")
                    for file in dup['files'][:2]:
                        print(f"        • {file}")
                    if len(dup['files']) > 2:
                        print(f"        • ... and {len(dup['files']) - 2} more")
                
                if 'confidence' in dup:
                    print(f"      Confidence: {dup['confidence']:.0%}")
                
                if 'lines' in dup:
                    print(f"      Size: {dup['lines']} lines")
            
            # Preview refactoring
            print("\n🔧 Generating refactoring suggestions...")
            preview = recator.refactor_duplicates(dry_run=True)
            
            print("\n💡 Refactoring Suggestions:")
            print(f"  ├─ Suggested actions: {preview.get('total_actions', 0)}")
            print(f"  ├─ Potential LOC reduction: {preview.get('estimated_loc_reduction', 0)} lines")
            print(f"  └─ Files to modify: {len(preview.get('affected_files', []))}")
            
            if preview.get('actions'):
                print("\n📝 Recommended actions:")
                for i, action in enumerate(preview['actions'][:3], 1):
                    print(f"  {i}. {action['description']}")
            
            print("\n💬 Next steps:")
            print("  1. Review the detected duplicates")
            print("  2. Use 'recator --refactor' to see detailed refactoring plan")
            print("  3. Use 'recator --refactor --apply' to apply changes (creates .refactored files)")
            
        else:
            print("\n✨ Great! No code duplicates found in your project.")
            print("   Your code is clean and DRY (Don't Repeat Yourself)!")
        
    except FileNotFoundError:
        print(f"❌ Error: Directory '{project_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("For more information, run: recator --help")
    print("="*50)


if __name__ == "__main__":
    quick_example()

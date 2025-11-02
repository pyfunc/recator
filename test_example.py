#!/usr/bin/env python3
"""
Example usage of Recator library
"""

import os
import tempfile
import shutil
from pathlib import Path
from recator import Recator


def create_test_project():
    """Create a test project with duplicate code"""
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="recator_test_")
    print(f"Created test project at: {test_dir}")
    
    # Create Python file with duplicates
    python_file1 = Path(test_dir) / "module1.py"
    python_file1.write_text('''
def validate_email(email):
    """Validate email address"""
    if not email:
        raise ValueError("Email is required")
    if "@" not in email:
        raise ValueError("Invalid email format")
    if not email.endswith(".com") and not email.endswith(".org"):
        raise ValueError("Invalid email domain")
    return True

def process_user_registration(username, email, password):
    """Process user registration"""
    # Duplicate validation code
    if not email:
        raise ValueError("Email is required")
    if "@" not in email:
        raise ValueError("Invalid email format")
    if not email.endswith(".com") and not email.endswith(".org"):
        raise ValueError("Invalid email domain")
    
    # Process registration
    print(f"Registering user: {username}")
    return {"username": username, "email": email}

def calculate_discount(price, customer_type):
    """Calculate discount based on customer type"""
    if customer_type == "premium":
        return price * 0.8
    elif customer_type == "regular":
        return price * 0.95
    else:
        return price
''')
    
    # Create another Python file with similar code
    python_file2 = Path(test_dir) / "module2.py"
    python_file2.write_text('''
def update_user_email(user_id, new_email):
    """Update user email"""
    # Duplicate validation code (exact same)
    if not new_email:
        raise ValueError("Email is required")
    if "@" not in new_email:
        raise ValueError("Invalid email format")
    if not new_email.endswith(".com") and not new_email.endswith(".org"):
        raise ValueError("Invalid email domain")
    
    print(f"Updating email for user {user_id}")
    return True

def calculate_price_with_discount(base_price, user_type):
    """Calculate price with discount - similar to calculate_discount"""
    if user_type == "premium":
        return base_price * 0.8
    elif user_type == "regular":
        return base_price * 0.95
    else:
        return base_price

def another_function():
    """Some other functionality"""
    data = []
    for i in range(10):
        data.append(i * 2)
    return data
''')
    
    # Create JavaScript file with duplicates
    js_file = Path(test_dir) / "utils.js"
    js_file.write_text('''
function validateInput(input) {
    if (!input) {
        throw new Error("Input is required");
    }
    if (input.length < 3) {
        throw new Error("Input too short");
    }
    return true;
}

function processForm(formData) {
    // Duplicate validation
    if (!formData.name) {
        throw new Error("Input is required");
    }
    if (formData.name.length < 3) {
        throw new Error("Input too short");
    }
    
    console.log("Processing form:", formData);
    return formData;
}

const calculateTotal = (items) => {
    let total = 0;
    for (let item of items) {
        total += item.price * item.quantity;
    }
    return total;
};

// Similar function with slight differences
const computeSum = (products) => {
    let sum = 0;
    for (let product of products) {
        sum += product.cost * product.amount;
    }
    return sum;
};
''')
    
    return test_dir


def test_basic_analysis():
    """Test basic duplicate analysis"""
    print("\n" + "="*60)
    print("TESTING RECATOR - Basic Analysis")
    print("="*60)
    
    # Create test project
    test_dir = create_test_project()
    
    try:
        # Initialize Recator
        config = {
            'min_lines': 3,
            'min_tokens': 20,
            'similarity_threshold': 0.8,
            'languages': ['python', 'javascript'],
            'safe_mode': True
        }
        
        recator = Recator(test_dir, config)
        
        # Analyze for duplicates
        print("\n🔍 Analyzing test project...")
        results = recator.analyze()
        
        print(f"\n📊 Results:")
        print(f"  • Total files: {results['total_files']}")
        print(f"  • Parsed files: {results['parsed_files']}")
        print(f"  • Duplicates found: {results['duplicates_found']}")
        
        # Show duplicate details
        if results['duplicates_found'] > 0:
            print(f"\n📋 Duplicate Details:")
            for i, dup in enumerate(results['duplicates'][:5], 1):
                print(f"\n  Duplicate #{i}:")
                print(f"    Type: {dup.get('type', 'unknown')}")
                
                if 'files' in dup:
                    files = [Path(f).name for f in dup['files']]
                    print(f"    Files: {', '.join(files)}")
                
                if 'blocks' in dup and isinstance(dup['blocks'], list):
                    print(f"    Blocks: {len(dup['blocks'])} occurrences")
                
                if 'confidence' in dup:
                    print(f"    Confidence: {dup['confidence']:.1%}")
                
                if 'lines' in dup:
                    print(f"    Lines: {dup['lines']}")
        
        # Test refactoring preview
        print("\n🔧 Testing refactoring preview...")
        preview = recator.refactor_duplicates(dry_run=True)
        
        print(f"\n📝 Refactoring Plan:")
        print(f"  • Total actions: {preview.get('total_actions', 0)}")
        print(f"  • Estimated LOC reduction: {preview.get('estimated_loc_reduction', 0)}")
        print(f"  • Affected files: {len(preview.get('affected_files', []))}")
        
        if preview.get('actions'):
            print(f"\n  Planned Actions:")
            for action in preview['actions'][:3]:
                print(f"    • {action['strategy']}: {action['description']}")
        
        print("\n✅ Test completed successfully!")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")


def test_specific_languages():
    """Test language-specific duplicate detection"""
    print("\n" + "="*60)
    print("TESTING RECATOR - Language Specific")
    print("="*60)
    
    test_dir = create_test_project()
    
    try:
        # Test Python only
        print("\n🐍 Testing Python-only analysis...")
        recator_py = Recator(test_dir, {'languages': ['python'], 'min_lines': 3})
        results_py = recator_py.analyze()
        print(f"  Python files: {results_py['parsed_files']}")
        print(f"  Python duplicates: {results_py['duplicates_found']}")
        
        # Test JavaScript only
        print("\n📜 Testing JavaScript-only analysis...")
        recator_js = Recator(test_dir, {'languages': ['javascript'], 'min_lines': 3})
        results_js = recator_js.analyze()
        print(f"  JavaScript files: {results_js['parsed_files']}")
        print(f"  JavaScript duplicates: {results_js['duplicates_found']}")
        
    finally:
        shutil.rmtree(test_dir)


def test_different_algorithms():
    """Test different detection algorithms"""
    print("\n" + "="*60)
    print("TESTING RECATOR - Detection Algorithms")
    print("="*60)
    
    test_dir = create_test_project()
    
    try:
        config = {
            'min_lines': 3,
            'min_tokens': 15,
            'similarity_threshold': 0.7
        }
        
        recator = Recator(test_dir, config)
        
        # Access detector directly for testing
        from recator.scanner import CodeScanner
        from recator.analyzer import CodeAnalyzer
        from recator.detector import DuplicateDetector
        
        scanner = CodeScanner(config)
        analyzer = CodeAnalyzer(config)
        detector = DuplicateDetector(config)
        
        # Scan and parse files
        files = scanner.scan_directory(test_dir)
        parsed = analyzer.parse_files(files)
        
        # Test individual algorithms
        print("\n🔍 Testing individual algorithms:")
        
        # Exact duplicates
        exact = detector.find_exact_duplicates(parsed)
        print(f"  • Exact duplicates: {len(exact)}")
        
        # Token duplicates
        token = detector.find_token_duplicates(parsed)
        print(f"  • Token duplicates: {len(token)}")
        
        # Fuzzy duplicates
        fuzzy = detector.find_fuzzy_duplicates(parsed)
        print(f"  • Fuzzy duplicates: {len(fuzzy)}")
        
        # Structural duplicates
        structural = detector.find_structural_duplicates(parsed)
        print(f"  • Structural duplicates: {len(structural)}")
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════╗
║     RECATOR LIBRARY - TEST EXAMPLES       ║
╚═══════════════════════════════════════════╝
    """)
    
    # Run tests
    test_basic_analysis()
    test_specific_languages()
    test_different_algorithms()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
    
    print("""
📚 To use Recator in your project:

1. Install the library:
   pip install -e .

2. Use from command line:
   recator /path/to/your/project

3. Use in Python code:
   from recator import Recator
   recator = Recator('/path/to/project')
   results = recator.analyze()
    """)

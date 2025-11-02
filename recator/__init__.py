"""
Recator - A Python library for detecting and refactoring code duplicates
"""

from .scanner import CodeScanner
from .detector import DuplicateDetector
from .refactor import CodeRefactor
from .analyzer import CodeAnalyzer

__version__ = "0.1.3"
__all__ = ["CodeScanner", "DuplicateDetector", "CodeRefactor", "CodeAnalyzer", "Recator"]


class Recator:
    """Main class for code duplicate detection and refactoring"""
    
    def __init__(self, project_path, config=None):
        """
        Initialize Recator with project path
        
        Args:
            project_path: Path to the project directory
            config: Optional configuration dictionary
        """
        self.project_path = project_path
        self.config = config or self._get_default_config()
        
        self.scanner = CodeScanner(self.config)
        self.detector = DuplicateDetector(self.config)
        self.refactor = CodeRefactor(self.config)
        self.analyzer = CodeAnalyzer(self.config)
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'min_lines': 4,  # Minimum lines for duplicate detection
            'min_tokens': 30,  # Minimum tokens for duplicate detection
            'similarity_threshold': 0.85,  # Similarity threshold (0-1)
            'languages': ['python', 'javascript', 'java', 'cpp', 'c', 'html', 'css'],
            'exclude_patterns': ['*.min.js', '*.min.css', 'node_modules/*', '.git/*'],
            'safe_mode': True,  # Don't modify files automatically, create .refactored versions
        }
    
    def analyze(self):
        """
        Analyze project for code duplicates
        
        Returns:
            Dictionary with analysis results
        """
        # Scan all files
        files = self.scanner.scan_directory(self.project_path)
        
        # Parse and tokenize files
        parsed_files = self.analyzer.parse_files(files)
        
        # Detect duplicates
        duplicates = self.detector.find_duplicates(parsed_files)
        
        return {
            'total_files': len(files),
            'parsed_files': len(parsed_files),
            'duplicates_found': len(duplicates),
            'duplicates': duplicates
        }
    
    def refactor_duplicates(self, duplicates=None, dry_run=True):
        """
        Refactor detected duplicates
        
        Args:
            duplicates: List of duplicates to refactor (if None, detect first)
            dry_run: If True, only show what would be done
            
        Returns:
            Dictionary with refactoring results
        """
        if duplicates is None:
            analysis = self.analyze()
            duplicates = analysis['duplicates']
        
        refactoring_plan = self.refactor.create_refactoring_plan(duplicates)
        
        if not dry_run:
            results = self.refactor.apply_refactoring(refactoring_plan)
        else:
            results = self.refactor.preview_refactoring(refactoring_plan)
        
        return results

"""
Code scanner module for finding and reading source files
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Tuple


class CodeScanner:
    """Scanner for finding and reading source code files"""
    
    # Language extensions mapping
    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass', '.less', '.styl'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
        'c': ['.c', '.h'],
        'csharp': ['.cs'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'go': ['.go'],
        'rust': ['.rs'],
        'kotlin': ['.kt'],
        'swift': ['.swift'],
    }
    
    def __init__(self, config):
        self.config = config
        self.languages = config.get('languages', ['python', 'javascript', 'java'])
        self.exclude_patterns = config.get('exclude_patterns', [])
        self.extensions = self._get_extensions()
    
    def _get_extensions(self):
        """Get file extensions for configured languages"""
        extensions = set()
        for lang in self.languages:
            if lang in self.LANGUAGE_EXTENSIONS:
                extensions.update(self.LANGUAGE_EXTENSIONS[lang])
        return extensions
    
    def scan_directory(self, path: str) -> List[Dict]:
        """
        Scan directory for source code files
        
        Args:
            path: Directory path to scan
            
        Returns:
            List of file information dictionaries
        """
        files = []
        path = Path(path)
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and self._should_process_file(file_path):
                file_info = self._get_file_info(file_path)
                if file_info:
                    files.append(file_info)
        
        return files
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Check extension
        if file_path.suffix not in self.extensions:
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(str(file_path), pattern):
                return False
        
        return True
    
    def _get_file_info(self, file_path: Path) -> Dict:
        """Get file information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix,
                'language': self._detect_language(file_path),
                'content': content,
                'lines': content.splitlines(),
                'size': file_path.stat().st_size,
                'line_count': len(content.splitlines())
            }
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        suffix = file_path.suffix
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return lang
        
        return 'unknown'
    
    def filter_files(self, files: List[Dict], min_lines: int = 10) -> List[Dict]:
        """
        Filter files by minimum line count
        
        Args:
            files: List of file info dictionaries
            min_lines: Minimum number of lines
            
        Returns:
            Filtered list of files
        """
        return [f for f in files if f['line_count'] >= min_lines]

"""
Code analyzer module for parsing and tokenizing source code
"""

import re
import hashlib
from typing import List, Dict, Tuple
import ast
import json


class CodeAnalyzer:
    """Analyzer for parsing and tokenizing source code"""
    
    def __init__(self, config):
        self.config = config
        self.tokenizers = {
            'python': PythonTokenizer(),
            'javascript': JavaScriptTokenizer(),
            'java': JavaTokenizer(),
            'cpp': CppTokenizer(),
            'c': CTokenizer(),
            'default': GenericTokenizer()
        }
    
    def parse_files(self, files: List[Dict]) -> List[Dict]:
        """
        Parse and tokenize source files
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            List of parsed file data
        """
        parsed = []
        
        for file_info in files:
            language = file_info.get('language', 'default')
            tokenizer = self.tokenizers.get(language, self.tokenizers['default'])
            
            try:
                tokens = tokenizer.tokenize(file_info['content'])
                blocks = self.extract_code_blocks(file_info['content'], language)
                
                parsed.append({
                    **file_info,
                    'tokens': tokens,
                    'blocks': blocks,
                    'token_count': len(tokens),
                    'hash': self.compute_hash(tokens)
                })
            except Exception as e:
                print(f"Error parsing {file_info['path']}: {e}")
                
        return parsed
    
    def extract_code_blocks(self, content: str, language: str) -> List[Dict]:
        """
        Extract code blocks (functions, methods, classes)
        
        Args:
            content: Source code content
            language: Programming language
            
        Returns:
            List of code blocks
        """
        blocks = []
        
        if language == 'python':
            blocks = self._extract_python_blocks(content)
        elif language in ['javascript', 'typescript']:
            blocks = self._extract_js_blocks(content)
        elif language == 'java':
            blocks = self._extract_java_blocks(content)
        else:
            blocks = self._extract_generic_blocks(content)
        
        return blocks
    
    def _extract_python_blocks(self, content: str) -> List[Dict]:
        """Extract Python code blocks using AST"""
        blocks = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    block = {
                        'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                        'name': node.name,
                        'start_line': node.lineno,
                        'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        'body': ast.unparse(node) if hasattr(ast, 'unparse') else None
                    }
                    blocks.append(block)
        except:
            pass
        
        return blocks
    
    def _extract_js_blocks(self, content: str) -> List[Dict]:
        """Extract JavaScript code blocks using regex"""
        blocks = []
        
        # Function pattern
        function_pattern = r'(function\s+(\w+)\s*\([^)]*\)\s*{|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|(\w+)\s*:\s*(?:async\s*)?function\s*\([^)]*\)\s*{)'
        
        for match in re.finditer(function_pattern, content):
            name = match.group(2) or match.group(3) or match.group(4) or 'anonymous'
            start = content[:match.start()].count('\n') + 1
            
            blocks.append({
                'type': 'function',
                'name': name,
                'start_line': start,
                'end_line': start + 10,  # Approximate
                'body': None
            })
        
        # Class pattern
        class_pattern = r'class\s+(\w+)'
        
        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            start = content[:match.start()].count('\n') + 1
            
            blocks.append({
                'type': 'class',
                'name': name,
                'start_line': start,
                'end_line': start + 20,  # Approximate
                'body': None
            })
        
        return blocks
    
    def _extract_java_blocks(self, content: str) -> List[Dict]:
        """Extract Java code blocks using regex"""
        blocks = []
        
        # Method pattern
        method_pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*{' 
        
        for match in re.finditer(method_pattern, content):
            name = match.group(3)
            start = content[:match.start()].count('\n') + 1
            
            blocks.append({
                'type': 'method',
                'name': name,
                'start_line': start,
                'end_line': start + 10,  # Approximate
                'body': None
            })
        
        # Class pattern
        class_pattern = r'(public\s+)?class\s+(\w+)'
        
        for match in re.finditer(class_pattern, content):
            name = match.group(2)
            start = content[:match.start()].count('\n') + 1
            
            blocks.append({
                'type': 'class',
                'name': name,
                'start_line': start,
                'end_line': start + 30,  # Approximate
                'body': None
            })
        
        return blocks
    
    def _extract_generic_blocks(self, content: str) -> List[Dict]:
        """Extract generic code blocks using indentation and braces"""
        blocks = []
        lines = content.splitlines()
        
        # Simple heuristic: look for functions/methods
        for i, line in enumerate(lines):
            if re.match(r'^\s*(def|function|func|method|class)\s+(\w+)', line):
                match = re.match(r'^\s*(def|function|func|method|class)\s+(\w+)', line)
                blocks.append({
                    'type': 'block',
                    'name': match.group(2) if match else 'unknown',
                    'start_line': i + 1,
                    'end_line': min(i + 20, len(lines)),
                    'body': None
                })
        
        return blocks
    
    def compute_hash(self, tokens: List[str]) -> str:
        """Compute hash for token sequence"""
        token_str = ' '.join(tokens)
        return hashlib.md5(token_str.encode()).hexdigest()


class GenericTokenizer:
    """Generic tokenizer for any language"""
    
    def tokenize(self, content: str) -> List[str]:
        """Tokenize source code"""
        # Remove comments (simple heuristic)
        content = re.sub(r'//.*?\n', '\n', content)  # C-style single line
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # C-style multi-line
        content = re.sub(r'#.*?\n', '\n', content)  # Python/Shell style
        
        # Tokenize by splitting on non-alphanumeric
        tokens = re.findall(r'\w+|[^\w\s]', content)
        
        # Filter out very short tokens
        tokens = [t for t in tokens if len(t) > 1 or not t.isspace()]
        
        return tokens


class PythonTokenizer(GenericTokenizer):
    """Python-specific tokenizer"""
    
    def tokenize(self, content: str) -> List[str]:
        """Tokenize Python source code"""
        try:
            # Try to use Python's tokenize module
            import tokenize
            import io
            
            tokens = []
            readline = io.StringIO(content).readline
            
            for tok in tokenize.generate_tokens(readline):
                if tok.type not in [tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE]:
                    tokens.append(tok.string)
            
            return tokens
        except:
            # Fall back to generic tokenizer
            return super().tokenize(content)


class JavaScriptTokenizer(GenericTokenizer):
    """JavaScript-specific tokenizer"""
    
    def tokenize(self, content: str) -> List[str]:
        """Tokenize JavaScript source code"""
        # Remove ES6 template literals
        content = re.sub(r'`[^`]*`', '""', content)
        
        # Handle arrow functions
        content = re.sub(r'=>', 'function', content)
        
        return super().tokenize(content)


class JavaTokenizer(GenericTokenizer):
    """Java-specific tokenizer"""
    
    def tokenize(self, content: str) -> List[str]:
        """Tokenize Java source code"""
        # Remove annotations
        content = re.sub(r'@\w+(?:\([^)]*\))?', '', content)
        
        return super().tokenize(content)


class CppTokenizer(GenericTokenizer):
    """C++-specific tokenizer"""
    
    def tokenize(self, content: str) -> List[str]:
        """Tokenize C++ source code"""
        # Remove preprocessor directives
        content = re.sub(r'#\s*\w+[^\n]*\n', '\n', content)
        
        return super().tokenize(content)


class CTokenizer(CppTokenizer):
    """C-specific tokenizer (inherits from C++)"""
    pass

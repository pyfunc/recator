"""
Duplicate detection module using various algorithms
"""

import re
import difflib
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from .hashing import stable_hash_text, stable_hash_tokens


class DuplicateDetector:
    """Detector for finding code duplicates"""
    
    def __init__(self, config):
        self.config = config
        self.min_lines = config.get('min_lines', 4)
        self.min_tokens = config.get('min_tokens', 30)
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        self.algorithms = {
            'exact': self.find_exact_duplicates,
            'token': self.find_token_duplicates,
            'fuzzy': self.find_fuzzy_duplicates,
            'structural': self.find_structural_duplicates
        }
    
    def find_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """
        Find all types of duplicates
        
        Args:
            parsed_files: List of parsed file data
            
        Returns:
            List of duplicate groups
        """
        duplicates = []
        
        # Run different detection algorithms
        exact = self.find_exact_duplicates(parsed_files)
        token = self.find_token_duplicates(parsed_files)
        fuzzy = self.find_fuzzy_duplicates(parsed_files)
        structural = self.find_structural_duplicates(parsed_files)
        css_dups = self.find_css_duplicates(parsed_files)
        
        # Merge and deduplicate results
        all_duplicates = exact + token + fuzzy + structural + css_dups
        duplicates = self._merge_duplicate_groups(all_duplicates)
        
        return duplicates
    
    def find_exact_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find exact code duplicates using hash comparison"""
        hash_groups = defaultdict(list)
        
        # Group files by content hash
        for file_data in parsed_files:
            content_hash = self._compute_content_hash(file_data['content'])
            hash_groups[content_hash].append(file_data)
        
        # Find duplicate groups
        duplicates = []
        for hash_val, files in hash_groups.items():
            if len(files) > 1:
                duplicates.append({
                    'type': 'exact',
                    'hash': hash_val,
                    'files': [f['path'] for f in files],
                    'count': len(files),
                    'lines': files[0]['line_count'],
                    'confidence': 1.0
                })
        
        # Also check for exact duplicate blocks within files
        block_duplicates = self._find_exact_block_duplicates(parsed_files)
        duplicates.extend(block_duplicates)
        
        return duplicates
    
    def _find_exact_block_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find exact duplicate code blocks within and across files"""
        block_hashes = defaultdict(list)
        duplicates = []
        
        for file_data in parsed_files:
            lines = file_data['lines']
            
            # Use sliding window to find duplicate blocks
            for i in range(len(lines) - self.min_lines + 1):
                block = lines[i:i + self.min_lines]
                
                # Skip blocks with too much whitespace
                if sum(1 for line in block if line.strip()) < self.min_lines * 0.5:
                    continue
                
                block_text = '\n'.join(block)
                block_hash = stable_hash_text(block_text)
                
                block_hashes[block_hash].append({
                    'file': file_data['path'],
                    'start_line': i + 1,
                    'end_line': i + self.min_lines,
                    'content': block_text
                })
        
        # Find duplicate blocks
        for hash_val, blocks in block_hashes.items():
            if len(blocks) > 1:
                duplicates.append({
                    'type': 'exact_block',
                    'hash': hash_val,
                    'blocks': blocks,
                    'count': len(blocks),
                    'lines': self.min_lines,
                    'confidence': 1.0
                })
        
        return duplicates
    
    def find_token_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find duplicates based on token sequences"""
        token_groups = defaultdict(list)
        duplicates = []
        
        for file_data in parsed_files:
            if 'tokens' not in file_data:
                continue
            
            tokens = file_data['tokens']
            
            # Create token subsequences
            for i in range(len(tokens) - self.min_tokens + 1):
                subseq = tokens[i:i + self.min_tokens]
                subseq_hash = stable_hash_tokens(subseq)
                
                token_groups[subseq_hash].append({
                    'file': file_data['path'],
                    'tokens': subseq,
                    'position': i
                })
        
        # Find duplicate token sequences
        for hash_val, groups in token_groups.items():
            if len(groups) > 1:
                duplicates.append({
                    'type': 'token_sequence',
                    'hash': hash_val,
                    'groups': groups,
                    'count': len(groups),
                    'token_count': self.min_tokens,
                    'confidence': 0.9
                })
        
        return duplicates
    
    def find_fuzzy_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find fuzzy/near duplicates using similarity metrics"""
        duplicates = []
        
        # Compare all pairs of files
        for i, file1 in enumerate(parsed_files):
            for j, file2 in enumerate(parsed_files[i+1:], i+1):
                similarity = self._calculate_similarity(file1, file2)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append({
                        'type': 'fuzzy',
                        'files': [file1['path'], file2['path']],
                        'similarity': similarity,
                        'confidence': similarity
                    })
        
        # Find similar code blocks
        block_duplicates = self._find_similar_blocks(parsed_files)
        duplicates.extend(block_duplicates)
        
        return duplicates
    
    def _find_similar_blocks(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find similar (but not exact) code blocks"""
        duplicates = []
        all_blocks = []
        
        # Collect all code blocks
        for file_data in parsed_files:
            if 'blocks' in file_data:
                for block in file_data['blocks']:
                    all_blocks.append({
                        'file': file_data['path'],
                        'block': block,
                        'tokens': self._get_block_tokens(file_data, block)
                    })
        
        # Compare blocks
        for i, block1 in enumerate(all_blocks):
            for j, block2 in enumerate(all_blocks[i+1:], i+1):
                if block1['tokens'] and block2['tokens']:
                    similarity = self._token_similarity(block1['tokens'], block2['tokens'])
                    
                    if similarity >= self.similarity_threshold:
                        duplicates.append({
                            'type': 'similar_block',
                            'blocks': [
                                {'file': block1['file'], 'name': block1['block']['name']},
                                {'file': block2['file'], 'name': block2['block']['name']}
                            ],
                            'similarity': similarity,
                            'confidence': similarity
                        })
        
        return duplicates
    
    def _get_block_tokens(self, file_data: Dict, block: Dict) -> List[str]:
        """Extract tokens for a code block"""
        if 'tokens' not in file_data:
            return []
        
        # This is a simplified version - in reality, you'd map tokens to line numbers
        start = block.get('start_line', 0)
        end = block.get('end_line', start + 10)
        
        # Approximate token extraction based on line numbers
        lines = file_data['lines'][start-1:end]
        block_text = '\n'.join(lines)
        
        # Simple tokenization
        import re
        tokens = re.findall(r'\w+', block_text)
        
        return tokens
    
    def find_structural_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find structurally similar code (same structure, different names)"""
        duplicates = []
        
        for file_data in parsed_files:
            if 'blocks' not in file_data:
                continue
            
            for block in file_data['blocks']:
                normalized = self._normalize_block(block, file_data)
                if normalized:
                    # Compare with other blocks
                    for other_file in parsed_files:
                        if other_file == file_data:
                            continue
                        
                        for other_block in other_file.get('blocks', []):
                            other_normalized = self._normalize_block(other_block, other_file)
                            
                            if normalized == other_normalized:
                                duplicates.append({
                                    'type': 'structural',
                                    'blocks': [
                                        {'file': file_data['path'], 'block': block['name']},
                                        {'file': other_file['path'], 'block': other_block['name']}
                                    ],
                                    'confidence': 0.85
                                })
        
        return self._deduplicate_results(duplicates)
    
    def _normalize_block(self, block: Dict, file_data: Dict) -> str:
        """Normalize a code block by replacing identifiers with placeholders"""
        if 'body' not in block or not block['body']:
            return ''
        
        normalized = block['body']
        
        # Replace variable names with VAR
        import re
        normalized = re.sub(r'\b[a-z_][a-zA-Z0-9_]*\b', 'VAR', normalized)
        
        # Replace function names with FUNC
        normalized = re.sub(r'\b[A-Z][a-zA-Z0-9_]*\b', 'FUNC', normalized)
        
        # Replace numbers with NUM
        normalized = re.sub(r'\b\d+\b', 'NUM', normalized)
        
        # Replace strings with STR
        normalized = re.sub(r'"[^"]*"', 'STR', normalized)
        normalized = re.sub(r"'[^']*'", 'STR', normalized)
        
        return normalized
    
    def _calculate_similarity(self, file1: Dict, file2: Dict) -> float:
        """Calculate similarity between two files"""
        # Token-based similarity
        if 'tokens' in file1 and 'tokens' in file2:
            return self._token_similarity(file1['tokens'], file2['tokens'])
        
        # Fall back to line-based similarity
        return self._line_similarity(file1['lines'], file2['lines'])
    
    def _token_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """Calculate token-based similarity using Jaccard index"""
        set1 = set(tokens1)
        set2 = set(tokens2)
        
        if not set1 and not set2:
            return 0.0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _line_similarity(self, lines1: List[str], lines2: List[str]) -> float:
        """Calculate line-based similarity using SequenceMatcher"""
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return matcher.ratio()
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute hash of content"""
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', content.strip())
        return stable_hash_text(normalized)

    # ---------------- CSS duplicate detection -----------------

    def find_css_duplicates(self, parsed_files: List[Dict]) -> List[Dict]:
        """Find exact CSS duplicate blocks across file types (.css, <style> in HTML, CSS-in-JS in TS/JS).
        Uses normalization to ignore whitespace and comments.
        """
        groups = defaultdict(list)
        for file_data in parsed_files:
            segments = self._extract_css_segments(file_data)
            for seg in segments:
                text = seg['content']
                if not text:
                    continue
                line_count = text.count('\n') + 1
                if line_count < self.min_lines:
                    continue
                norm = self._normalize_css_text(text)
                if not norm.strip():
                    continue
                h = stable_hash_text(norm)
                groups[h].append({
                    'file': file_data['path'],
                    'start_line': seg['start_line'],
                    'end_line': seg['end_line'],
                    'content': text.strip(),
                })

        duplicates = []
        for h, blocks in groups.items():
            if len(blocks) > 1:
                duplicates.append({
                    'type': 'css_block',
                    'hash': h,
                    'blocks': blocks,
                    'count': len(blocks),
                    'lines': max(1, blocks[0]['end_line'] - blocks[0]['start_line'] + 1),
                    'confidence': 1.0,
                })
        return duplicates

    def _extract_css_segments(self, file_data: Dict) -> List[Dict]:
        """Extract CSS segments from different file types.
        Returns list of dicts with keys: start_line, end_line, content
        """
        content = file_data.get('content', '')
        ext = (file_data.get('extension') or '').lower()
        language = file_data.get('language', '')
        segments = []

        # Whole CSS-like files
        if ext in {'.css', '.scss', '.sass', '.less', '.styl'}:
            lines = content.splitlines()
            segments.append({'start_line': 1, 'end_line': len(lines) or 1, 'content': content})
            return segments

        # HTML: <style>...</style>
        if ext in {'.html', '.htm'} or language == 'html':
            for m in re.finditer(r'<style[^>]*>(.*?)</style>', content, flags=re.DOTALL | re.IGNORECASE):
                inner = m.group(1)
                start_line = content[:m.start(1)].count('\n') + 1
                end_line = start_line + inner.count('\n')
                segments.append({'start_line': start_line, 'end_line': end_line, 'content': inner})

        # JS/TS: CSS-in-JS template literals: css`...`, styled.*`...`, or any backtick string that looks like CSS
        if language == 'javascript' or ext in {'.js', '.jsx', '.ts', '.tsx'}:
            for m in re.finditer(r'(?:css\s*|styled\.[a-zA-Z_]\w*\s*)?`([^`]*)`', content, flags=re.DOTALL):
                inner = m.group(1)
                # Heuristic: treat as CSS if contains braces and colons (property: value)
                if re.search(r':\s*[^;\n]+;?', inner) and ('{' in inner and '}' in inner):
                    start_line = content[:m.start(1)].count('\n') + 1
                    end_line = start_line + inner.count('\n')
                    segments.append({'start_line': start_line, 'end_line': end_line, 'content': inner})

        return segments

    def _normalize_css_text(self, css: str) -> str:
        """Normalize CSS to aid exact duplicate detection across contexts.
        - remove comments
        - collapse whitespace
        - remove spaces around punctuation like : ; { } ,
        """
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Collapse whitespace
        css = re.sub(r'\s+', ' ', css.strip())
        # Remove spaces around punctuation
        css = re.sub(r'\s*([:{};,{}])\s*', r'\1', css)
        return css
    
    def _merge_duplicate_groups(self, all_duplicates: List[Dict]) -> List[Dict]:
        """Merge overlapping duplicate groups"""
        # Simple deduplication - in real implementation, would be more sophisticated
        seen = set()
        merged = []
        
        for dup in all_duplicates:
            # Create a unique key for the duplicate
            if 'files' in dup:
                key = tuple(sorted(dup['files']))
            elif 'blocks' in dup:
                key = tuple(str(b) for b in dup['blocks'])
            else:
                key = str(dup)
            
            if key not in seen:
                seen.add(key)
                merged.append(dup)
        
        return merged
    
    def _deduplicate_results(self, duplicates: List[Dict]) -> List[Dict]:
        """Remove duplicate entries from results"""
        seen = set()
        unique = []
        
        for dup in duplicates:
            key = str(sorted(str(b) for b in dup.get('blocks', [])))
            if key not in seen:
                seen.add(key)
                unique.append(dup)
        
        return unique

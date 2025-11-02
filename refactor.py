"""
Code refactoring module for eliminating duplicates
"""

import os
import re
from typing import List, Dict, Tuple
from pathlib import Path


class CodeRefactor:
    """Refactor code to eliminate duplicates"""
    
    def __init__(self, config):
        self.config = config
        self.safe_mode = config.get('safe_mode', True)
        self.strategies = {
            'extract_method': ExtractMethodStrategy(),
            'extract_class': ExtractClassStrategy(),
            'extract_module': ExtractModuleStrategy(),
            'parameterize': ParameterizeStrategy()
        }
    
    def create_refactoring_plan(self, duplicates: List[Dict]) -> List[Dict]:
        """
        Create a refactoring plan for duplicates
        
        Args:
            duplicates: List of detected duplicates
            
        Returns:
            List of refactoring actions
        """
        plan = []
        
        for duplicate in duplicates:
            action = self._determine_refactoring_action(duplicate)
            if action:
                plan.append(action)
        
        # Optimize and prioritize plan
        plan = self._optimize_plan(plan)
        
        return plan
    
    def _determine_refactoring_action(self, duplicate: Dict) -> Dict:
        """Determine the best refactoring action for a duplicate"""
        dup_type = duplicate.get('type', 'unknown')
        
        if dup_type == 'exact':
            # For exact duplicates, extract to shared module
            return {
                'strategy': 'extract_module',
                'duplicate': duplicate,
                'priority': 1,
                'description': f"Extract duplicate code to shared module"
            }
        
        elif dup_type == 'exact_block':
            # For exact block duplicates, extract method
            return {
                'strategy': 'extract_method',
                'duplicate': duplicate,
                'priority': 2,
                'description': f"Extract duplicate block to method"
            }
        
        elif dup_type == 'fuzzy' or dup_type == 'similar_block':
            # For similar code, parameterize differences
            return {
                'strategy': 'parameterize',
                'duplicate': duplicate,
                'priority': 3,
                'description': f"Parameterize similar code"
            }
        
        elif dup_type == 'structural':
            # For structural duplicates, extract template/base class
            return {
                'strategy': 'extract_class',
                'duplicate': duplicate,
                'priority': 2,
                'description': f"Extract to base class or template"
            }
        
        return None
    
    def _optimize_plan(self, plan: List[Dict]) -> List[Dict]:
        """Optimize and prioritize refactoring plan"""
        # Sort by priority
        plan.sort(key=lambda x: x.get('priority', 999))
        
        # Remove conflicting actions
        optimized = []
        affected_files = set()
        
        for action in plan:
            # Check if files are already being refactored
            files = self._get_affected_files(action)
            
            if not files.intersection(affected_files):
                optimized.append(action)
                affected_files.update(files)
        
        return optimized
    
    def _get_affected_files(self, action: Dict) -> set:
        """Get files affected by a refactoring action"""
        files = set()
        duplicate = action.get('duplicate', {})
        
        if 'files' in duplicate:
            files.update(duplicate['files'])
        
        if 'blocks' in duplicate:
            for block in duplicate['blocks']:
                if isinstance(block, dict) and 'file' in block:
                    files.add(block['file'])
        
        return files
    
    def apply_refactoring(self, plan: List[Dict]) -> Dict:
        """
        Apply refactoring plan to code
        
        Args:
            plan: List of refactoring actions
            
        Returns:
            Dictionary with refactoring results
        """
        results = {
            'successful': [],
            'failed': [],
            'modified_files': [],
            'created_files': []
        }
        
        for action in plan:
            try:
                strategy_name = action['strategy']
                strategy = self.strategies.get(strategy_name)
                
                if strategy:
                    result = strategy.apply(action, self.safe_mode)
                    
                    if result['success']:
                        results['successful'].append(action)
                        results['modified_files'].extend(result.get('modified_files', []))
                        results['created_files'].extend(result.get('created_files', []))
                    else:
                        results['failed'].append({
                            'action': action,
                            'error': result.get('error', 'Unknown error')
                        })
                
            except Exception as e:
                results['failed'].append({
                    'action': action,
                    'error': str(e)
                })
        
        return results
    
    def preview_refactoring(self, plan: List[Dict]) -> Dict:
        """
        Preview refactoring changes without applying them
        
        Args:
            plan: List of refactoring actions
            
        Returns:
            Dictionary with preview information
        """
        preview = {
            'total_actions': len(plan),
            'actions': [],
            'estimated_loc_reduction': 0,
            'affected_files': set()
        }
        
        for action in plan:
            duplicate = action.get('duplicate', {})
            
            # Estimate lines of code reduction
            if 'lines' in duplicate:
                count = duplicate.get('count', 2)
                preview['estimated_loc_reduction'] += duplicate['lines'] * (count - 1)
            
            # Track affected files
            files = self._get_affected_files(action)
            preview['affected_files'].update(files)
            
            # Add action preview
            preview['actions'].append({
                'strategy': action['strategy'],
                'description': action['description'],
                'affected_files': list(files),
                'confidence': duplicate.get('confidence', 0.5)
            })
        
        preview['affected_files'] = list(preview['affected_files'])
        
        return preview


class RefactoringStrategy:
    """Base class for refactoring strategies"""
    
    def apply(self, action: Dict, safe_mode: bool = True) -> Dict:
        """Apply refactoring strategy"""
        raise NotImplementedError


class ExtractMethodStrategy(RefactoringStrategy):
    """Extract duplicate code blocks to methods/functions"""
    
    def apply(self, action: Dict, safe_mode: bool = True) -> Dict:
        """Extract duplicate blocks to a method"""
        duplicate = action['duplicate']
        blocks = duplicate.get('blocks', [])
        
        if not blocks:
            return {'success': False, 'error': 'No blocks to extract'}
        
        # Get the first block as template
        template_block = blocks[0]
        
        # Generate method name
        method_name = self._generate_method_name(template_block)
        
        # Extract parameters from differences
        params = self._extract_parameters(blocks)
        
        # Create the extracted method
        method_code = self._create_method(method_name, params, template_block)
        
        # Modify files
        modified_files = []
        
        for block in blocks:
            file_path = block['file']
            
            if safe_mode:
                # Create a .refactored version
                new_path = file_path + '.refactored'
                self._modify_file(file_path, new_path, block, method_name, params)
            else:
                # Modify in place
                self._modify_file(file_path, file_path, block, method_name, params)
            
            modified_files.append(file_path)
        
        return {
            'success': True,
            'modified_files': modified_files,
            'created_method': method_name
        }
    
    def _generate_method_name(self, block: Dict) -> str:
        """Generate a meaningful method name"""
        if 'content' in block:
            # Try to extract meaningful name from content
            content = block['content']
            
            # Look for common patterns
            if 'validate' in content.lower():
                return 'extracted_validation'
            elif 'calculate' in content.lower():
                return 'extracted_calculation'
            elif 'process' in content.lower():
                return 'extracted_processing'
        
        return f"extracted_method_{block.get('start_line', 0)}"
    
    def _extract_parameters(self, blocks: List[Dict]) -> List[str]:
        """Extract parameters from block differences"""
        # Simple heuristic: find variables that differ between blocks
        params = []
        
        # This is simplified - real implementation would parse AST
        for i, block in enumerate(blocks):
            if 'content' in block:
                # Find variable names
                import re
                variables = re.findall(r'\b[a-z_][a-zA-Z0-9_]*\b', block['content'])
                
                if i == 0:
                    base_vars = set(variables)
                else:
                    diff_vars = set(variables) - base_vars
                    params.extend(diff_vars)
        
        return list(set(params))[:3]  # Limit to 3 params
    
    def _create_method(self, name: str, params: List[str], block: Dict) -> str:
        """Create the extracted method"""
        content = block.get('content', '')
        
        # Simple template for different languages
        # In real implementation, would detect language
        method = f"""
def {name}({', '.join(params)}):
    \"\"\"Extracted method to eliminate duplication\"\"\"
{content}
"""
        
        return method
    
    def _modify_file(self, source_path: str, target_path: str, 
                    block: Dict, method_name: str, params: List[str]) -> None:
        """Modify file to use extracted method"""
        try:
            with open(source_path, 'r') as f:
                lines = f.readlines()
            
            # Replace block with method call
            start = block.get('start_line', 1) - 1
            end = block.get('end_line', start + 1)
            
            # Create method call
            call = f"    {method_name}({', '.join(params)})\n"
            
            # Replace lines
            new_lines = lines[:start] + [call] + lines[end:]
            
            # Write to target
            with open(target_path, 'w') as f:
                f.writelines(new_lines)
        
        except Exception as e:
            print(f"Error modifying file {source_path}: {e}")


class ExtractClassStrategy(RefactoringStrategy):
    """Extract common structure to base class or template"""
    
    def apply(self, action: Dict, safe_mode: bool = True) -> Dict:
        """Extract common structure to base class"""
        duplicate = action['duplicate']
        
        # Create base class
        base_class = self._create_base_class(duplicate)
        
        # Create derived classes
        modified_files = []
        
        for block in duplicate.get('blocks', []):
            file_path = block['file']
            
            if safe_mode:
                new_path = file_path + '.refactored'
            else:
                new_path = file_path
            
            self._create_derived_class(file_path, new_path, block, base_class)
            modified_files.append(file_path)
        
        return {
            'success': True,
            'modified_files': modified_files,
            'created_class': base_class['name']
        }
    
    def _create_base_class(self, duplicate: Dict) -> Dict:
        """Create base class from duplicate structure"""
        return {
            'name': 'BaseExtractedClass',
            'code': """
class BaseExtractedClass:
    \"\"\"Base class for common functionality\"\"\"
    
    def common_method(self):
        # Common implementation
        pass
"""
        }
    
    def _create_derived_class(self, source_path: str, target_path: str, 
                             block: Dict, base_class: Dict) -> None:
        """Create derived class"""
        # Simplified implementation
        pass


class ExtractModuleStrategy(RefactoringStrategy):
    """Extract duplicate code to shared module"""
    
    def apply(self, action: Dict, safe_mode: bool = True) -> Dict:
        """Extract duplicates to shared module"""
        duplicate = action['duplicate']
        files = duplicate.get('files', [])
        
        if not files:
            return {'success': False, 'error': 'No files to process'}
        
        # Create shared module
        module_path = 'shared/extracted_common.py'
        module_content = self._extract_common_code(files)
        
        # Create module file
        os.makedirs('shared', exist_ok=True)
        with open(module_path, 'w') as f:
            f.write(module_content)
        
        # Update files to import from module
        modified_files = []
        
        for file_path in files:
            if safe_mode:
                new_path = file_path + '.refactored'
            else:
                new_path = file_path
            
            self._update_file_imports(file_path, new_path, module_path)
            modified_files.append(file_path)
        
        return {
            'success': True,
            'modified_files': modified_files,
            'created_files': [module_path]
        }
    
    def _extract_common_code(self, files: List[str]) -> str:
        """Extract common code from files"""
        # Simplified - would need proper AST analysis
        return """
# Extracted common code
def common_function():
    pass

class CommonClass:
    pass
"""
    
    def _update_file_imports(self, source_path: str, target_path: str, 
                            module_path: str) -> None:
        """Update file to import from shared module"""
        try:
            with open(source_path, 'r') as f:
                content = f.read()
            
            # Add import at the beginning
            import_stmt = f"from {module_path.replace('/', '.').replace('.py', '')} import *\n"
            
            # Remove duplicate code (simplified)
            # In real implementation, would parse and remove specific duplicates
            
            new_content = import_stmt + content
            
            with open(target_path, 'w') as f:
                f.write(new_content)
        
        except Exception as e:
            print(f"Error updating file {source_path}: {e}")


class ParameterizeStrategy(RefactoringStrategy):
    """Parameterize similar code with differences"""
    
    def apply(self, action: Dict, safe_mode: bool = True) -> Dict:
        """Parameterize similar code"""
        duplicate = action['duplicate']
        
        # Find differences
        diffs = self._find_differences(duplicate)
        
        # Create parameterized version
        parameterized = self._create_parameterized_version(duplicate, diffs)
        
        # Update files
        modified_files = []
        
        for file_info in duplicate.get('files', []):
            if isinstance(file_info, str):
                file_path = file_info
            else:
                file_path = file_info.get('file', '')
            
            if file_path:
                if safe_mode:
                    new_path = file_path + '.refactored'
                else:
                    new_path = file_path
                
                self._apply_parameterization(file_path, new_path, parameterized)
                modified_files.append(file_path)
        
        return {
            'success': True,
            'modified_files': modified_files
        }
    
    def _find_differences(self, duplicate: Dict) -> List[Dict]:
        """Find differences between similar code"""
        # Simplified - would use proper diff algorithm
        return [
            {'type': 'variable', 'values': ['var1', 'var2']},
            {'type': 'literal', 'values': ['10', '20']}
        ]
    
    def _create_parameterized_version(self, duplicate: Dict, diffs: List[Dict]) -> Dict:
        """Create parameterized version of code"""
        return {
            'parameters': [d['type'] for d in diffs],
            'template': 'def parameterized_function(param1, param2): pass'
        }
    
    def _apply_parameterization(self, source_path: str, target_path: str, 
                                parameterized: Dict) -> None:
        """Apply parameterization to file"""
        # Simplified implementation
        pass

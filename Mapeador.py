#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ai_code_mapper.py

Automatically generates a comprehensive Markdown report (AI_CODE_MAP.md) containing:
- 🌲 Directory tree with files, classes, functions, and sub-functions
- Detailed analysis per file: classes, methods, functions, docstrings, calls, imports and external references
- Code complexity metrics and AI-friendly structural information
- Cross-references and dependency mapping

Usage:
    python ai_code_mapper.py --root PROJECT/PATH [--output AI_CODE_MAP.md]
"""

import ast
import os
import argparse
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

IGNORE_FOLDERS = {'.git', '__pycache__', '.venv', 'env', 'build', 'dist', '.pytest_cache', 'node_modules', '.idea', '.vscode'}
IGNORE_FILES = {'__init__.py'}
CURRENT_SCRIPT_NAME = Path(__file__).name  # Self-awareness for skipping

@dataclass
class VariableInfo:
    """Information about variables and their usage."""
    name: str
    type_hint: Optional[str] = None
    assigned_values: List[str] = field(default_factory=list)
    usage_count: int = 0
    line_number: int = 0

@dataclass
class FunctionInfo:
    """Comprehensive information about a function or method."""
    name: str
    params: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    doc: str = ""
    subfunctions: List[str] = field(default_factory=list)
    calls: Set[str] = field(default_factory=set)
    variables: List[VariableInfo] = field(default_factory=list)
    line_number: int = 0
    end_line_number: int = 0
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    complexity_score: int = 0
    raises_exceptions: List[str] = field(default_factory=list)
    yields: bool = False

@dataclass
class ClassInfo:
    """Comprehensive information about a class."""
    name: str
    bases: List[str] = field(default_factory=list)
    doc: str = ""
    methods: List[FunctionInfo] = field(default_factory=list)
    class_variables: List[VariableInfo] = field(default_factory=list)
    line_number: int = 0
    end_line_number: int = 0
    decorators: List[str] = field(default_factory=list)
    is_abstract: bool = False
    metaclass: Optional[str] = None

@dataclass
class FileInfo:
    """Comprehensive information about a Python file."""
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    from_imports: Dict[str, List[str]] = field(default_factory=dict)
    external_references: Set[str] = field(default_factory=set)
    all_calls: Set[str] = field(default_factory=set)
    global_variables: List[VariableInfo] = field(default_factory=list)
    constants: List[VariableInfo] = field(default_factory=list)
    file_docstring: str = ""
    total_lines: int = 0
    complexity_score: int = 0
    dependencies: Set[str] = field(default_factory=set)
    exports: List[str] = field(default_factory=list)

class ComprehensiveAnalyzer(ast.NodeVisitor):
    """Advanced AST analyzer with scope awareness and comprehensive code mapping."""
    
    def __init__(self):
        self.file_info = FileInfo()
        self.current_scope = []  # Stack of current scopes (function/class)
        self.scope_calls = defaultdict(set)  # Calls per scope
        self.scope_variables = defaultdict(list)  # Variables per scope
        self.complexity_stack = [0]  # Complexity tracking per scope
        self.class_stack = []  # Track nested classes
        
    def visit_Module(self, node):
        """Analyze module-level constructs."""
        self.file_info.file_docstring = ast.get_docstring(node, clean=True) or ''
        self.file_info.total_lines = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')] + [0])
        self.generic_visit(node)
        self.file_info.complexity_score = self.complexity_stack[0]

    def visit_Import(self, node):
        """Process import statements."""
        for alias in node.names:
            import_name = alias.asname if alias.asname else alias.name
            self.file_info.imports.append(import_name)
            self.file_info.dependencies.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Process from...import statements."""
        module = node.module or ''
        names = []
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            names.append(name)
            if name == '*':
                self.file_info.from_imports[module] = ['*']
            else:
                self.file_info.from_imports.setdefault(module, []).append(name)
        
        if module:
            self.file_info.dependencies.add(module.split('.')[0])
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Track variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_info = VariableInfo(
                    name=target.id,
                    assigned_values=[self._safe_unparse(node.value)],
                    line_number=node.lineno
                )
                
                # Determine if it's a constant (uppercase naming convention)
                if target.id.isupper():
                    self.file_info.constants.append(var_info)
                elif not self.current_scope:  # Global variable
                    self.file_info.global_variables.append(var_info)
                else:  # Local variable
                    scope_key = '.'.join(self.current_scope)
                    self.scope_variables[scope_key].append(var_info)
        
        self.generic_visit(node)

    def visit_Call(self, node):
        """Analyze function calls."""
        func_name = self._get_call_name(node)
        if func_name:
            self.file_info.all_calls.add(func_name)
            
            # Add call to current scope
            current_scope_key = '.'.join(self.current_scope) if self.current_scope else '__module__'
            self.scope_calls[current_scope_key].add(func_name)
            
            # Track external references
            if '.' in func_name and not func_name.startswith('self.'):
                self.file_info.external_references.add(func_name)
                
        self.generic_visit(node)

    def visit_Raise(self, node):
        """Track raised exceptions."""
        if self.current_scope:
            exc_name = self._get_exception_name(node)
            if exc_name:
                scope_key = '.'.join(self.current_scope)
                # Find current function to add exception info
                # This is simplified - in a full implementation, you'd need better scope tracking

    def _get_exception_name(self, node) -> Optional[str]:
        """Extract exception name from raise statement."""
        if node.exc:
            return self._safe_unparse(node.exc)
        return None

    def _get_call_name(self, node) -> Optional[str]:
        """Extract function call name robustly."""
        try:
            return ast.unparse(node.func)
        except Exception:
            if isinstance(node.func, ast.Attribute):
                try:
                    value = ast.unparse(node.func.value)
                    return f"{value}.{node.func.attr}"
                except:
                    return f"<unknown>.{node.func.attr}"
            elif isinstance(node.func, ast.Name):
                return node.func.id
            return None

    def visit_ClassDef(self, node):
        """Analyze class definitions comprehensively."""
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Check if abstract class
        is_abstract = any('abc' in str(base) or 'ABC' in str(base) for base in node.bases)
        
        class_info = ClassInfo(
            name=node.name,
            bases=[self._safe_unparse(b) for b in node.bases],
            doc=ast.get_docstring(node, clean=True) or '',
            line_number=node.lineno,
            end_line_number=self._get_end_line(node),
            decorators=[d for d in decorators if d],
            is_abstract=is_abstract
        )
        
        # Enter class scope
        self.current_scope.append(node.name)
        self.class_stack.append(node.name)
        
        # Analyze methods and nested classes
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                method_info = self._analyze_function(child, is_method=True)
                class_info.methods.append(method_info)
            elif isinstance(child, ast.Assign):
                # Track class variables
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        var_info = VariableInfo(
                            name=target.id,
                            assigned_values=[self._safe_unparse(child.value)],
                            line_number=child.lineno
                        )
                        class_info.class_variables.append(var_info)
        
        self.file_info.classes.append(class_info)
        
        # Visit remaining children
        for child in node.body:
            if not isinstance(child, ast.FunctionDef):
                self.visit(child)
        
        # Exit class scope
        self.current_scope.pop()
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        """Analyze function definitions."""
        # Only process if not inside a class (methods are handled separately)
        if not self.class_stack:
            func_info = self._analyze_function(node)
            self.file_info.functions.append(func_info)
        
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Handle async functions."""
        if not self.class_stack:
            func_info = self._analyze_function(node, is_async=True)
            self.file_info.functions.append(func_info)
        
        self.generic_visit(node)

    def _analyze_function(self, node, is_method=False, is_async=False) -> FunctionInfo:
        """Comprehensively analyze a function or method."""
        # Extract parameters with type hints
        params = []
        for arg in node.args.args:
            param_str = arg.arg
            if arg.annotation:
                param_str += f": {self._safe_unparse(arg.annotation)}"
            params.append(param_str)
        
        # Add *args and **kwargs
        if node.args.vararg:
            vararg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg_str += f": {self._safe_unparse(node.args.vararg.annotation)}"
            params.append(vararg_str)
            
        if node.args.kwarg:
            kwarg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg_str += f": {self._safe_unparse(node.args.kwarg.annotation)}"
            params.append(kwarg_str)
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._safe_unparse(node.returns)
        
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Detect subfunctions and nested definitions
        subfunctions = []
        for child in ast.walk(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child != node:
                if child.lineno > node.lineno:
                    subfunctions.append(child.name)
        
        # Check if function yields (generator)
        yields = any(isinstance(child, (ast.Yield, ast.YieldFrom)) for child in ast.walk(node))
        
        func_info = FunctionInfo(
            name=node.name,
            params=params,
            return_type=return_type,
            doc=ast.get_docstring(node, clean=True) or '',
            subfunctions=list(set(subfunctions)),
            line_number=node.lineno,
            end_line_number=self._get_end_line(node),
            is_async=is_async or isinstance(node, ast.AsyncFunctionDef),
            decorators=[d for d in decorators if d],
            yields=yields
        )
        
        # Calculate complexity score
        func_info.complexity_score = self._calculate_complexity(node)
        
        # Enter function scope for detailed analysis
        scope_key = f"{'.'.join(self.current_scope)}.{node.name}" if self.current_scope else node.name
        self.current_scope.append(node.name)
        
        # Visit function body
        for child in node.body:
            self.visit(child)
        
        # Assign scope-specific data
        func_info.calls = self.scope_calls.get(scope_key, set())
        func_info.variables = self.scope_variables.get(scope_key, [])
        
        # Exit function scope
        self.current_scope.pop()
        
        return func_info

    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        return complexity

    def _get_end_line(self, node) -> int:
        """Get the end line number of a node."""
        end_line = node.lineno
        for child in ast.walk(node):
            if hasattr(child, 'lineno') and child.lineno > end_line:
                end_line = child.lineno
        return end_line

    def _get_decorator_name(self, decorator) -> Optional[str]:
        """Extract decorator name."""
        try:
            return ast.unparse(decorator)
        except:
            if isinstance(decorator, ast.Name):
                return decorator.id
            return None

    def _safe_unparse(self, node) -> str:
        """Safe unparsing that doesn't fail."""
        try:
            return ast.unparse(node)
        except:
            return "<unparseable>"

def analyze_python_file(path: Path) -> Optional[FileInfo]:
    """Analyze a Python file and return its comprehensive structure."""
    try:
        content = path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        analyzer = ComprehensiveAnalyzer()
        analyzer.visit(tree)
        return analyzer.file_info
    except UnicodeDecodeError:
        logger.warning(f"Encoding error reading {path}")
        return None
    except SyntaxError as e:
        logger.warning(f"Syntax error in {path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error analyzing {path}: {e}")
        return None

def build_project_tree(data: Dict[str, FileInfo]) -> Dict[str, Any]:
    """Build comprehensive project tree structure."""
    tree = {}
    
    for file_path, info in data.items():
        parts = file_path.split('/')
        node = tree
        
        # Navigate/create directory structure
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        
        # Add file with comprehensive definitions
        filename = parts[-1]
        node[filename] = {
            '_metadata': {
                'classes': [(c.name, c.line_number, len(c.methods), c.is_abstract) for c in info.classes],
                'functions': [(f.name, f.line_number, f.complexity_score, f.is_async) for f in info.functions],
                'total_lines': info.total_lines,
                'complexity_score': info.complexity_score,
                'dependencies': list(info.dependencies),
                'imports_count': len(info.imports) + len(info.from_imports)
            }
        }
    
    return tree

def generate_tree_visualization(tree: Dict[str, Any], prefix: str = "") -> List[str]:
    """Generate comprehensive tree visualization."""
    lines = []
    keys = sorted([k for k in tree.keys() if k != '_metadata'])
    
    for idx, key in enumerate(keys):
        is_last = idx == len(keys) - 1
        connector = '└── ' if is_last else '├── '
        
        child = tree[key]
        metadata = child.get('_metadata', {})
        
        if metadata:  # It's a file
            # File info with complexity and size indicators
            complexity = metadata.get('complexity_score', 0)
            lines_count = metadata.get('total_lines', 0)
            classes_count = len(metadata.get('classes', []))
            functions_count = len(metadata.get('functions', []))
            
            complexity_indicator = "🔴" if complexity > 20 else "🟡" if complexity > 10 else "🟢"
            size_indicator = "📚" if lines_count > 500 else "📄" if lines_count > 100 else "📃"
            
            lines.append(f"{prefix}{connector}{size_indicator} {key} {complexity_indicator} "
                        f"({lines_count} lines, complexity: {complexity})")
            
            # Show classes with method counts
            for cls_name, line_num, method_count, is_abstract in metadata.get('classes', []):
                abstract_indicator = "🔶" if is_abstract else "🏛️"
                lines.append(f"{prefix}{'    ' if is_last else '│   '}├── {abstract_indicator} {cls_name} "
                           f"(line {line_num}, {method_count} methods)")
            
            # Show functions with complexity
            for func_name, line_num, func_complexity, is_async in metadata.get('functions', []):
                async_indicator = "⚡" if is_async else "⚙️"
                func_complexity_indicator = "🔴" if func_complexity > 10 else "🟡" if func_complexity > 5 else "🟢"
                lines.append(f"{prefix}{'    ' if is_last else '│   '}└── {async_indicator} {func_name} "
                           f"{func_complexity_indicator} (line {line_num}, complexity: {func_complexity})")
        else:
            # It's a directory
            lines.append(f"{prefix}{connector}📁 {key}")
        
        # Recursion for subdirectories
        if any(k != '_metadata' for k in child.keys()):
            subtree_lines = generate_tree_visualization(child, prefix + ('    ' if is_last else '│   '))
            lines.extend(subtree_lines)
    
    return lines

def generate_comprehensive_markdown(tree_lines: List[str], data: Dict[str, FileInfo]) -> str:
    """Generate comprehensive AI-friendly Markdown report."""
    md = []
    
    # Header with comprehensive project overview
    md.append("# 🧠 AI-Friendly Code Structure Analysis\n")
    md.append("*Generated for AI model comprehension and code modification assistance*\n")
    
    # Project tree with complexity indicators
    md.append("## 🌲 Project Structure & Complexity Map\n")
    md.append("```text")
    md.append("📊 Legend:")
    md.append("🟢 Low Complexity (≤10)  🟡 Medium (11-20)  🔴 High (>20)")
    md.append("📃 Small (<100 lines)   📄 Medium (100-500)  📚 Large (>500)")
    md.append("🏛️ Class  ⚙️ Function  ⚡ Async  🔶 Abstract  📁 Directory")
    md.append("")
    md.append("PROJECT_ROOT/")
    md.extend(tree_lines)
    md.append("```\n")
    
    # Comprehensive statistics
    total_files = len(data)
    total_classes = sum(len(info.classes) for info in data.values())
    total_functions = sum(len(info.functions) for info in data.values())
    total_methods = sum(len(cls.methods) for info in data.values() for cls in info.classes)
    total_lines = sum(info.total_lines for info in data.values())
    avg_complexity = sum(info.complexity_score for info in data.values()) / len(data) if data else 0
    
    # Dependency analysis
    all_dependencies = set()
    for info in data.values():
        all_dependencies.update(info.dependencies)
    
    md.append("## 📊 Comprehensive Project Metrics\n")
    md.append(f"- **Python Files Analyzed:** {total_files}")
    md.append(f"- **Total Lines of Code:** {total_lines:,}")
    md.append(f"- **Classes Defined:** {total_classes}")
    md.append(f"- **Top-Level Functions:** {total_functions}")
    md.append(f"- **Class Methods:** {total_methods}")
    md.append(f"- **Average File Complexity:** {avg_complexity:.1f}")
    md.append(f"- **External Dependencies:** {len(all_dependencies)}")
    md.append(f"- **Most Complex Files:** {', '.join([f for f, info in sorted(data.items(), key=lambda x: x[1].complexity_score, reverse=True)[:3]])}")
    md.append("")
    
    # Dependency graph
    if all_dependencies:
        md.append("## 🔗 Dependency Overview\n")
        for dep in sorted(all_dependencies):
            using_files = [f for f, info in data.items() if dep in info.dependencies]
            md.append(f"- **{dep}** → Used in {len(using_files)} files")
        md.append("")

    # Detailed file analysis for AI modification assistance
    for file_path, info in sorted(data.items()):
        md.append(f"---\n\n## 📄 File Analysis: `{file_path}`\n")
        
        # File overview
        complexity_indicator = "🔴" if info.complexity_score > 20 else "🟡" if info.complexity_score > 10 else "🟢"
        md.append(f"**Overview:** {info.total_lines} lines, complexity: {info.complexity_score} {complexity_indicator}\n")
        
        if info.file_docstring:
            md.append(f"**File Purpose:** {info.file_docstring}\n")
        
        # Import analysis for dependency understanding
        if info.imports or info.from_imports:
            md.append("### 📦 Import Analysis\n")
            
            if info.imports:
                md.append("**Direct Imports:**")
                for imp in sorted(set(info.imports)):
                    md.append(f"- `{imp}`")
                md.append("")
            
            if info.from_imports:
                md.append("**From Imports:**")
                for module, names in sorted(info.from_imports.items()):
                    md.append(f"- `from {module} import {', '.join(names)}`")
                md.append("")
        
        # Global variables and constants
        if info.global_variables or info.constants:
            md.append("### 🌐 Global Scope Variables\n")
            
            if info.constants:
                md.append("**Constants:**")
                for const in info.constants:
                    md.append(f"- `{const.name}` = {const.assigned_values[0] if const.assigned_values else 'undefined'} (line {const.line_number})")
                md.append("")
            
            if info.global_variables:
                md.append("**Global Variables:**")
                for var in info.global_variables:
                    md.append(f"- `{var.name}` = {var.assigned_values[0] if var.assigned_values else 'undefined'} (line {var.line_number})")
                md.append("")
        
        # Class analysis with inheritance and method details
        if info.classes:
            md.append("### 🏛️ Class Definitions\n")
            for cls in info.classes:
                inheritance_info = f" extends {', '.join(cls.bases)}" if cls.bases else ""
                abstract_info = " (Abstract)" if cls.is_abstract else ""
                decorators_info = f" @{', @'.join(cls.decorators)}" if cls.decorators else ""
                
                md.append(f"#### `{cls.name}`{inheritance_info}{abstract_info} - lines {cls.line_number}-{cls.end_line_number}{decorators_info}")
                
                if cls.doc:
                    md.append(f"**Purpose:** {cls.doc[:150]}{'...' if len(cls.doc) > 150 else ''}\n")
                
                # Class variables
                if cls.class_variables:
                    md.append("**Class Variables:**")
                    for var in cls.class_variables:
                        md.append(f"- `{var.name}` = {var.assigned_values[0] if var.assigned_values else 'undefined'}")
                    md.append("")
                
                # Methods with detailed signatures
                if cls.methods:
                    md.append("**Methods:**")
                    for method in cls.methods:
                        params_str = f"({', '.join(method.params)})" if method.params else "()"
                        return_str = f" -> {method.return_type}" if method.return_type else ""
                        async_str = "async " if method.is_async else ""
                        yield_str = " (generator)" if method.yields else ""
                        complexity_ind = "🔴" if method.complexity_score > 10 else "🟡" if method.complexity_score > 5 else "🟢"
                        decorators_str = f" @{', @'.join(method.decorators)}" if method.decorators else ""
                        
                        md.append(f"- `{async_str}{method.name}{params_str}{return_str}` {complexity_ind} "
                                f"(lines {method.line_number}-{method.end_line_number}, complexity: {method.complexity_score}){yield_str}{decorators_str}")
                        
                        if method.doc:
                            md.append(f"  - 📝 {method.doc[:100]}{'...' if len(method.doc) > 100 else ''}")
                        
                        if method.calls:
                            calls_list = sorted(method.calls)[:5]
                            more_calls = f" (+{len(method.calls)-5} more)" if len(method.calls) > 5 else ""
                            md.append(f"  - 🔗 Calls: `{', '.join(calls_list)}`{more_calls}")
                        
                        if method.subfunctions:
                            md.append(f"  - 🔧 Nested functions: `{', '.join(method.subfunctions)}`")
                    md.append("")
        
# Top-level functions with comprehensive details
        if info.functions:
            md.append("### ⚙️ Top-Level Functions\n")
            for func in info.functions:
                params_str = f"({', '.join(func.params)})" if func.params else "()"
                return_str = f" -> {func.return_type}" if func.return_type else ""
                async_str = "async " if func.is_async else ""
                yield_str = " (generator)" if func.yields else ""
                complexity_ind = "🔴" if func.complexity_score > 10 else "🟡" if func.complexity_score > 5 else "🟢"
                decorators_str = f" @{', @'.join(func.decorators)}" if func.decorators else ""
                
                md.append(f"#### `{async_str}{func.name}{params_str}{return_str}` {complexity_ind} "
                        f"(lines {func.line_number}-{func.end_line_number}, complexity: {func.complexity_score}){yield_str}{decorators_str}")
                
                if func.doc:
                    md.append(f"**Purpose:** {func.doc[:150]}{'...' if len(func.doc) > 150 else ''}")
                
                if func.calls:
                    calls_list = sorted(func.calls)[:8]
                    more_calls = f" (+{len(func.calls)-8} more)" if len(func.calls) > 8 else ""
                    md.append(f"- 🔗 Function calls: `{', '.join(calls_list)}`{more_calls}")
                
                if func.subfunctions:
                    md.append(f"- 🔧 Nested functions: `{', '.join(func.subfunctions)}`")
                
                if func.variables:
                    var_names = [v.name for v in func.variables[:5]]
                    more_vars = f" (+{len(func.variables)-5} more)" if len(func.variables) > 5 else ""
                    md.append(f"- 📊 Local variables: `{', '.join(var_names)}`{more_vars}")
                
                if func.raises_exceptions:
                    md.append(f"- ⚠️ Raises: `{', '.join(func.raises_exceptions)}`")
                
                md.append("")
        
        # External references and API usage
        if info.external_references:
            md.append("### 🌐 External API Usage\n")
            # Group external references by module
            external_by_module = defaultdict(list)
            for ref in info.external_references:
                if '.' in ref:
                    module = ref.split('.')[0]
                    external_by_module[module].append(ref)
                else:
                    external_by_module['unknown'].append(ref)
            
            for module, refs in sorted(external_by_module.items()):
                if len(refs) <= 10:
                    md.append(f"- **{module}**: `{', '.join(sorted(refs))}`")
                else:
                    md.append(f"- **{module}**: `{', '.join(sorted(refs)[:10])}` (+{len(refs)-10} more)")
            md.append("")
        
        # Function call graph for AI understanding
        if info.all_calls:
            md.append("### 📞 Function Call Graph\n")
            md.append("*All function calls detected in this file (for AI dependency analysis)*\n")
            
            # Categorize calls
            internal_calls = []
            external_calls = []
            builtin_calls = []
            
            for call in sorted(info.all_calls):
                if '.' in call and not call.startswith('self.'):
                    external_calls.append(call)
                elif call in ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 'min', 'max', 'any', 'all', 'open', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr']:
                    builtin_calls.append(call)
                else:
                    internal_calls.append(call)
            
            if internal_calls:
                md.append(f"**Internal calls:** `{', '.join(internal_calls[:15])}`")
                if len(internal_calls) > 15:
                    md.append(f" (+{len(internal_calls)-15} more)")
                md.append("")
            
            if external_calls:
                md.append(f"**External API calls:** `{', '.join(external_calls[:15])}`")
                if len(external_calls) > 15:
                    md.append(f" (+{len(external_calls)-15} more)")
                md.append("")
            
            if builtin_calls:
                md.append(f"**Built-in functions:** `{', '.join(builtin_calls[:10])}`")
                if len(builtin_calls) > 10:
                    md.append(f" (+{len(builtin_calls)-10} more)")
                md.append("")
        
        # Modification suggestions for AI
        md.append("### 🤖 AI Modification Hints\n")
        modification_hints = []
        
        # High complexity functions
        high_complexity_funcs = [f for f in info.functions if f.complexity_score > 10]
        if high_complexity_funcs:
            func_names = [f.name for f in high_complexity_funcs]
            modification_hints.append(f"**Refactoring candidates:** Functions `{', '.join(func_names)}` have high complexity and could benefit from decomposition")
        
        # Functions without docstrings
        undocumented_funcs = [f for f in info.functions if not f.doc]
        if undocumented_funcs:
            func_names = [f.name for f in undocumented_funcs[:5]]
            more_str = f" (+{len(undocumented_funcs)-5} more)" if len(undocumented_funcs) > 5 else ""
            modification_hints.append(f"**Documentation needed:** Functions `{', '.join(func_names)}`{more_str} lack docstrings")
        
        # Classes without docstrings
        undocumented_classes = [c for c in info.classes if not c.doc]
        if undocumented_classes:
            class_names = [c.name for c in undocumented_classes]
            modification_hints.append(f"**Class documentation:** Classes `{', '.join(class_names)}` need docstrings")
        
        # Large files
        if info.total_lines > 500:
            modification_hints.append(f"**File size:** This file has {info.total_lines} lines, consider splitting into smaller modules")
        
        # Functions with many parameters
        complex_signatures = [f for f in info.functions if len(f.params) > 5]
        if complex_signatures:
            func_names = [f.name for f in complex_signatures]
            modification_hints.append(f"**Parameter complexity:** Functions `{', '.join(func_names)}` have many parameters, consider using dataclasses or configuration objects")
        
        if modification_hints:
            for hint in modification_hints:
                md.append(f"- {hint}")
        else:
            md.append("- ✅ Code structure appears well-organized for AI modifications")
        
        md.append("")
    
    return "\n".join(md)

def discover_python_files(root_path: Path) -> List[Tuple[Path, str]]:
    """Discover all Python files in the project, excluding ignored paths and self."""
    py_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_FOLDERS]
        
        for filename in filenames:
            if filename.endswith('.py') and filename not in IGNORE_FILES:
                # Skip self-awareness: don't analyze the current script
                if filename == CURRENT_SCRIPT_NAME:
                    logger.info(f"Skipping self-analysis of {filename}")
                    continue
                    
                full_path = Path(dirpath) / filename
                try:
                    relative_path = full_path.relative_to(root_path).as_posix()
                    py_files.append((full_path, relative_path))
                except ValueError:
                    continue
    
    return py_files

def generate_cross_reference_analysis(data: Dict[str, FileInfo]) -> str:
    """Generate cross-reference analysis for AI understanding."""
    md = []
    
    md.append("## 🔍 Cross-Reference Analysis\n")
    md.append("*For AI understanding of code relationships and dependencies*\n")
    
    # Function definitions vs calls analysis
    all_defined_functions = set()
    all_called_functions = set()
    
    for file_path, info in data.items():
        # Collect all defined functions
        for func in info.functions:
            all_defined_functions.add(func.name)
        for cls in info.classes:
            for method in cls.methods:
                all_defined_functions.add(f"{cls.name}.{method.name}")
        
        # Collect all called functions
        all_called_functions.update(info.all_calls)
    
    # Find potentially unused functions
    potentially_unused = all_defined_functions - all_called_functions
    if potentially_unused and len(potentially_unused) <= 20:
        md.append("### 🚫 Potentially Unused Functions\n")
        for func in sorted(potentially_unused):
            md.append(f"- `{func}`")
        md.append("")
    
    # Find external calls that might need attention
    external_calls = set()
    for info in data.values():
        external_calls.update(info.external_references)
    
    if external_calls:
        md.append("### 🌍 External Dependencies Summary\n")
        # Group by likely module
        by_module = defaultdict(list)
        for call in external_calls:
            if '.' in call:
                module = call.split('.')[0]
                by_module[module].append(call)
        
        for module, calls in sorted(by_module.items()):
            if len(calls) <= 5:
                md.append(f"- **{module}**: {len(calls)} calls - `{', '.join(sorted(calls))}`")
            else:
                md.append(f"- **{module}**: {len(calls)} calls - `{', '.join(sorted(calls)[:5])}` (+{len(calls)-5} more)")
        md.append("")
    
    # Class inheritance analysis
    inheritance_map = {}
    for file_path, info in data.items():
        for cls in info.classes:
            if cls.bases:
                inheritance_map[cls.name] = cls.bases
    
    if inheritance_map:
        md.append("### 🏗️ Class Inheritance Map\n")
        for cls, bases in sorted(inheritance_map.items()):
            md.append(f"- `{cls}` ← `{', '.join(bases)}`")
        md.append("")
    
    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive AI-friendly Markdown report of Python project structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_code_mapper.py --root ./my_project
  python ai_code_mapper.py --root /path/to/project --output custom_map.md
  python ai_code_mapper.py --root . --verbose
        """
    )
    parser.add_argument('--root', '-r', required=True, type=Path,
                        help="Root directory of the project to analyze")
    parser.add_argument('--output', '-o', default="AI_CODE_MAP.md", type=Path,
                        help="Output Markdown file (default: AI_CODE_MAP.md)")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Verbose mode with detailed logging")
    parser.add_argument('--include-private', action='store_true',
                        help="Include private methods and functions (starting with _)")
    parser.add_argument('--max-complexity', type=int, default=50,
                        help="Maximum complexity threshold for warnings (default: 50)")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    root_path = args.root.resolve()
    if not root_path.exists():
        logger.error(f"Directory not found: {root_path}")
        return 1
    
    if not root_path.is_dir():
        logger.error(f"Path is not a directory: {root_path}")
        return 1
    
    logger.info(f"Analyzing project at: {root_path}")
    logger.info(f"Current script: {CURRENT_SCRIPT_NAME} (will be skipped)")
    
    # Discover Python files
    py_files = discover_python_files(root_path)
    
    if not py_files:
        logger.warning("No Python files found for analysis!")
        return 1
    
    logger.info(f"Found {len(py_files)} Python files for analysis")
    
    # Analyze files
    analysis_data = {}
    errors = 0
    
    for full_path, relative_path in sorted(py_files, key=lambda x: x[1]):
        logger.debug(f"Analyzing: {relative_path}")
        file_info = analyze_python_file(full_path)
        
        if file_info is not None:
            analysis_data[relative_path] = file_info
        else:
            errors += 1
    
    if not analysis_data:
        logger.error("No files were successfully analyzed!")
        return 1
    
    logger.info(f"Successfully analyzed: {len(analysis_data)} files ({errors} errors)")
    
    # Generate project tree structure
    project_tree = build_project_tree(analysis_data)
    tree_visualization = generate_tree_visualization(project_tree)
    
    # Generate comprehensive report
    markdown_content = generate_comprehensive_markdown(tree_visualization, analysis_data)
    
    # Add cross-reference analysis
    cross_ref_analysis = generate_cross_reference_analysis(analysis_data)
    markdown_content += "\n" + cross_ref_analysis
    
    # Add generation metadata
    from datetime import datetime
    metadata = f"""
---

## 📋 Report Generation Metadata

- **Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Script version:** AI Code Mapper v2.0
- **Analysis root:** `{root_path}`
- **Files analyzed:** {len(analysis_data)}
- **Total errors:** {errors}
- **Self-awareness:** Skipped analysis of `{CURRENT_SCRIPT_NAME}`

*This report is optimized for AI model comprehension and code modification assistance.*
"""
    
    markdown_content += metadata
    
    # Write output file
    try:
        args.output.write_text(markdown_content, encoding='utf-8')
        logger.info(f"✅ AI-friendly code map generated successfully: {args.output}")
        logger.info(f"📊 Analysis summary: {len(analysis_data)} files, "
                   f"{sum(len(info.classes) for info in analysis_data.values())} classes, "
                   f"{sum(len(info.functions) for info in analysis_data.values())} functions")
        
        # Report high-complexity items
        high_complexity_files = [f for f, info in analysis_data.items() if info.complexity_score > args.max_complexity]
        if high_complexity_files:
            logger.warning(f"⚠️ High complexity files detected: {', '.join(high_complexity_files)}")
        
        return 0
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
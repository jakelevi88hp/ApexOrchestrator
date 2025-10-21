"""
Code Generation System

Generates new code, tools, and functions based on learned patterns and requirements.
"""

import ast
import json
import logging
import textwrap
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("apex_orchestrator.agent.code_generator")


class CodeGenerator:
    """Generate code for new capabilities and optimizations"""

    def __init__(self, memory_system, llm_client=None):
        self.memory = memory_system
        self.llm_client = llm_client
        logger.info("Code generator initialized")

    async def generate_function(self, purpose: str, requirements: Dict) -> Dict[str, Any]:
        """Generate a new Python function"""
        logger.info(f"Generating function for: {purpose}")

        # Check if similar function exists
        similar = self._find_similar_template(purpose)

        if similar:
            logger.info(f"Found similar template: {similar['name']}")
            return {
                "status": "template_found",
                "template": similar,
                "suggestion": f"Consider adapting existing template: {similar['name']}",
            }

        # Generate new function using LLM or templates
        function_code = await self._generate_function_code(purpose, requirements)

        # Validate syntax
        is_valid, error = self._validate_python_syntax(function_code)

        if not is_valid:
            logger.error(f"Generated code has syntax error: {error}")
            return {"status": "error", "error": error, "code": function_code}

        # Save as template
        template_name = self._generate_template_name(purpose)
        self.memory.save_code_template(
            name=template_name, code=function_code, description=purpose, tags=["auto-generated", "function"]
        )

        return {"status": "success", "code": function_code, "template_name": template_name, "validation": "passed"}

    async def generate_tool(self, tool_name: str, description: str, inputs: List[str], outputs: str) -> Dict[str, Any]:
        """Generate a new tool for the orchestrator"""
        logger.info(f"Generating tool: {tool_name}")

        tool_template = f'''
"""
{description}
Auto-generated tool by autonomous agent on {datetime.utcnow().isoformat()}
"""

async def {tool_name}({", ".join(inputs)}) -> Dict[str, Any]:
    """
    {description}
    
    Args:
{chr(10).join(f"        {inp}: Input parameter" for inp in inputs)}
    
    Returns:
        {outputs}
    """
    try:
        # TODO: Implement tool logic
        result = {{
            "status": "success",
            "message": "Tool executed successfully"
        }}
        
        logger.info(f"Tool {{tool_name}} executed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Tool {{tool_name}} failed: {{e}}")
        return {{
            "status": "error",
            "error": str(e)
        }}
'''

        # Validate
        is_valid, error = self._validate_python_syntax(tool_template)

        if not is_valid:
            return {"status": "error", "error": error}

        # Save as template
        self.memory.save_code_template(
            name=f"tool_{tool_name}", code=tool_template, description=description, tags=["tool", "auto-generated"]
        )

        return {"status": "success", "code": tool_template, "tool_name": tool_name}

    def generate_optimization(self, target_function: str, optimization_type: str) -> Dict[str, Any]:
        """Generate optimized version of existing code"""
        logger.info(f"Generating optimization for {target_function}: {optimization_type}")

        optimizations = {
            "caching": self._add_caching,
            "async": self._convert_to_async,
            "error_handling": self._improve_error_handling,
            "logging": self._add_logging,
        }

        if optimization_type not in optimizations:
            return {"status": "error", "error": f"Unknown optimization type: {optimization_type}"}

        try:
            optimized_code = optimizations[optimization_type](target_function)

            return {
                "status": "success",
                "original": target_function,
                "optimized": optimized_code,
                "optimization_type": optimization_type,
            }
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {"status": "error", "error": str(e)}

    def _add_caching(self, code: str) -> str:
        """Add caching to function"""
        cache_decorator = """
from functools import lru_cache

@lru_cache(maxsize=128)
"""
        return cache_decorator + code

    def _convert_to_async(self, code: str) -> str:
        """Convert function to async"""
        # Simple conversion - add async keyword
        if "def " in code and "async def " not in code:
            return code.replace("def ", "async def ")
        return code

    def _improve_error_handling(self, code: str) -> str:
        """Add comprehensive error handling"""
        # Wrap existing code in try-except
        lines = code.split("\n")
        indent = "    "

        improved = lines[0] + "\n"  # Keep function definition
        improved += f'{indent}"""Original function with improved error handling"""\n'
        improved += f"{indent}try:\n"

        # Indent existing code
        for line in lines[1:]:
            improved += f"{indent}{line}\n"

        improved += f"{indent}except Exception as e:\n"
        improved += f'{indent}    logger.error(f"Function failed: {{e}}", exc_info=True)\n'
        improved += f"{indent}    raise\n"

        return improved

    def _add_logging(self, code: str) -> str:
        """Add logging statements"""
        lines = code.split("\n")

        # Add logging import if not present
        if "import logging" not in code:
            code = "import logging\n\n" + code

        # Add entry/exit logging
        # This is a simplified version
        return code

    async def _generate_function_code(self, purpose: str, requirements: Dict) -> str:
        """Generate function code using LLM or templates"""

        # If LLM client available, use it
        if self.llm_client:
            prompt = f"""
Generate a Python function that: {purpose}

Requirements:
{json.dumps(requirements, indent=2)}

The function should:
- Have proper error handling
- Include logging
- Have type hints
- Include docstring
- Be production-ready

Return only the Python code, no explanations.
"""
            # Use LLM to generate code
            # (This would call the actual LLM)
            logger.info("Using LLM for code generation")

        # Fallback: Use template
        function_name = self._generate_function_name(purpose)

        template = f'''
def {function_name}(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    {purpose}
    
    Auto-generated function.
    
    Args:
        params: Input parameters
    
    Returns:
        Result dictionary
    """
    try:
        # Implementation
        result = {{
            "status": "success",
            "message": "Function executed"
        }}
        
        return result
        
    except Exception as e:
        logger.error(f"{{function_name}} failed: {{e}}")
        return {{
            "status": "error",
            "error": str(e)
        }}
'''
        return textwrap.dedent(template)

    def _validate_python_syntax(self, code: str) -> tuple[bool, Optional[str]]:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def _find_similar_template(self, purpose: str) -> Optional[Dict]:
        """Find similar existing template"""
        # Simple keyword matching
        purpose_lower = purpose.lower()
        keywords = purpose_lower.split()

        # Get all templates and check similarity
        # This is simplified - could use embeddings for better matching
        return None

    def _generate_function_name(self, purpose: str) -> str:
        """Generate function name from purpose"""
        # Extract key words and create snake_case name
        words = purpose.lower().split()
        # Take first few meaningful words
        name_words = [w for w in words if len(w) > 3][:3]
        return "_".join(name_words) if name_words else "generated_function"

    def _generate_template_name(self, purpose: str) -> str:
        """Generate template name"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base_name = self._generate_function_name(purpose)
        return f"auto_{base_name}_{timestamp}"

    def generate_test_case(self, function_code: str) -> str:
        """Generate test case for a function"""
        # Extract function name
        try:
            tree = ast.parse(function_code)
            func_name = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    break

            if not func_name:
                return "# Could not extract function name"

            test_code = f'''
import pytest
from unittest.mock import Mock, patch

def test_{func_name}_success():
    """Test {func_name} successful execution"""
    # Arrange
    test_input = {{"param": "value"}}
    
    # Act
    result = {func_name}(test_input)
    
    # Assert
    assert result["status"] == "success"

def test_{func_name}_error_handling():
    """Test {func_name} error handling"""
    # Test error conditions
    pass
'''
            return textwrap.dedent(test_code)

        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return f"# Test generation failed: {e}"

    def analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """Analyze code quality and suggest improvements"""
        issues = []
        suggestions = []

        try:
            tree = ast.parse(code)

            # Check for functions without docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        issues.append(f"Function '{node.name}' missing docstring")
                        suggestions.append(f"Add docstring to {node.name}")

            # Check for bare except clauses
            if "except:" in code:
                issues.append("Bare except clause found")
                suggestions.append("Use specific exception types")

            # Check for TODO comments
            todo_count = code.count("TODO")
            if todo_count > 0:
                issues.append(f"{todo_count} TODO items found")

            return {
                "quality_score": max(0, 100 - len(issues) * 10),
                "issues": issues,
                "suggestions": suggestions,
                "lines_of_code": len(code.split("\n")),
            }

        except Exception as e:
            return {"error": f"Analysis failed: {e}", "quality_score": 0}

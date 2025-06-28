"""
Safe Python code executor using RestrictedPython.
"""

import io
import sys
import time
import signal
import logging
from contextlib import redirect_stdout, redirect_stderr
import RestrictedPython
from RestrictedPython import compile_restricted
from security_config import ALLOWED_MODULES, RESTRICTED_NAMES

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception."""
    pass

class CodeExecutor:
    def __init__(self, timeout=10):
        """Initialize the code executor with timeout."""
        self.timeout = timeout
    
    def _timeout_handler(self, signum, frame):
        """Handle timeout signal."""
        raise TimeoutError("Code execution timed out")
    
    def execute(self, code: str) -> dict:
        """
        Execute Python code safely and return the result.
        
        Args:
            code (str): Python code to execute
            
        Returns:
            dict: Result containing success status, output, and error if any
        """
        result = {
            'success': False,
            'output': '',
            'error': ''
        }
        
        try:
            # Compile the code with restrictions
            compiled_code = compile_restricted(code, '<string>', 'exec')
            
            if compiled_code is None:
                result['error'] = "Code compilation failed - invalid or restricted syntax"
                return result
            
            # Check for compilation errors
            if hasattr(compiled_code, 'errors'):
                result['error'] = '\n'.join(compiled_code.errors)
                return result
            
            # Create safe execution environment
            safe_globals = self._create_safe_globals()
            safe_locals = {}
            
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Set up timeout
            old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(self.timeout)
            
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(compiled_code, safe_globals, safe_locals)
                
                # Get output
                stdout_value = stdout_capture.getvalue()
                stderr_value = stderr_capture.getvalue()
                
                if stderr_value:
                    result['error'] = stderr_value
                else:
                    result['success'] = True
                    result['output'] = stdout_value
                
            except TimeoutError:
                result['error'] = f"Code execution timed out after {self.timeout} seconds"
            except Exception as e:
                result['error'] = f"{type(e).__name__}: {str(e)}"
            finally:
                # Reset alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        except Exception as e:
            result['error'] = f"Compilation error: {str(e)}"
        
        return result
    
    def _create_safe_globals(self) -> dict:
        """Create a safe global environment for code execution."""
        safe_builtins = {
            # Safe built-in functions
            'abs': abs,
            'all': all,
            'any': any,
            'bin': bin,
            'bool': bool,
            'chr': chr,
            'dict': dict,
            'divmod': divmod,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'format': format,
            'hex': hex,
            'int': int,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'oct': oct,
            'ord': ord,
            'pow': pow,
            'print': print,
            'range': range,
            'reversed': reversed,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': type,
            'zip': zip,
        }
        
        # Add allowed modules
        safe_modules = {}
        for module_name in ALLOWED_MODULES:
            try:
                safe_modules[module_name] = __import__(module_name)
            except ImportError:
                logger.warning(f"Module {module_name} not available")
        
        return {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            **safe_modules
        }

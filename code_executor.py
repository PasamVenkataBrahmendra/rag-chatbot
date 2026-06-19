import subprocess
import sys
import tempfile
import os
import re

def extract_python_code(text):
    patterns = [
        r'```python\n(.*?)```',
        r'```py\n(.*?)```',
        r'```\n(.*?)```',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
    return None

def execute_python_code(code, timeout=10):
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        os.unlink(tmp_path)

        if result.returncode == 0:
            output = result.stdout
            if not output:
                output = "Code executed successfully with no output."
            return True, output
        else:
            error = result.stderr
            return False, error

    except subprocess.TimeoutExpired:
        return False, f"Code execution timed out after {timeout} seconds."
    except Exception as e:
        return False, str(e)

def is_safe_code(code):
    dangerous = [
        "os.system", "subprocess", "shutil.rmtree",
        "open('/etc", "open('C:\\\\Windows",
        "__import__('os')", "eval(", "exec(",
        "import socket", "urllib.request",
        "rm -rf", "del /f"
    ]
    code_lower = code.lower()
    for d in dangerous:
        if d.lower() in code_lower:
            return False, f"Blocked: contains potentially dangerous operation '{d}'"
    return True, "Safe"
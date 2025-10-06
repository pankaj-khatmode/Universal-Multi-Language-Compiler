"""
Compiler Manager - Backend for handling code compilation and execution
across multiple programming languages
"""

import subprocess
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional


class CompilerManager:
    """Manages compilation and execution of code in multiple languages"""

    def __init__(self):
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'compile_cmd': None,  # Python doesn't need compilation
                'run_cmd': [sys.executable, '{file}'],
                'temp_dir': True
            },
            'c': {
                'extension': '.c',
                'compile_cmd': ['gcc', '{file}', '-o', '{output}'],
                'run_cmd': ['{output}'],
                'temp_dir': True
            },
            'cpp': {
                'extension': '.cpp',
                'compile_cmd': ['g++', '{file}', '-o', '{output}'],
                'run_cmd': ['{output}'],
                'temp_dir': True
            },
            'java': {
                'extension': '.java',
                'compile_cmd': ['javac', '{file}'],
                'run_cmd': ['java', '{class_name}'],
                'temp_dir': False  # Java needs to be in a directory
            },
            'javascript': {
                'extension': '.js',
                'compile_cmd': None,  # Node.js doesn't need compilation
                'run_cmd': ['node', '{file}'],
                'temp_dir': True
            }
        }

        # Check if required compilers/interpreters are available
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required compilers and interpreters are available"""
        missing_deps = []

        # Check Python (should always be available)
        try:
            subprocess.run([sys.executable, '--version'],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_deps.append('python')

        # Check Node.js for JavaScript
        if not self._check_command(['node', '--version']):
            missing_deps.append('node.js')

        # Check GCC for C/C++
        if not self._check_command(['gcc', '--version']):
            missing_deps.append('gcc')

        # Check G++ for C++
        if not self._check_command(['g++', '--version']):
            missing_deps.append('g++')

        # Check Java compiler and runtime
        if not self._check_command(['javac', '-version']):
            missing_deps.append('javac')

        if not self._check_command(['java', '-version']):
            missing_deps.append('java')

        if missing_deps:
            print(f"Warning: Missing dependencies: {', '.join(missing_deps)}")
            print("Some language features may not work properly.")

    def _check_command(self, cmd):
        """Check if a command is available"""
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def compile_code(self, file_path: str, language: str, output_display) -> Dict[str, Any]:
        """Compile code for the specified language"""
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Unsupported language: {language}'
            }

        lang_config = self.supported_languages[language]

        try:
            # Handle Java specially (needs directory structure)
            if language == 'java':
                return self._compile_java(file_path, output_display)
            elif language in ['c', 'cpp']:
                return self._compile_compiled(file_path, language, output_display)
            else:
                # Interpreted languages don't need compilation
                return {
                    'success': True,
                    'message': 'No compilation needed for interpreted language'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Compilation failed: {str(e)}'
            }

    def run_code(self, file_path: str, language: str, output_display) -> Dict[str, Any]:
        """Run code for the specified language"""
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Unsupported language: {language}'
            }

        lang_config = self.supported_languages[language]

        try:
            # Handle different languages appropriately
            if language == 'java':
                return self._run_java(file_path, output_display)
            elif language in ['c', 'cpp']:
                return self._run_compiled(file_path, language, output_display)
            else:
                return self._run_interpreted(file_path, language, output_display)

        except Exception as e:
            return {
                'success': False,
                'error': f'Execution failed: {str(e)}'
            }

    def _compile_java(self, file_path: str, output_display) -> Dict[str, Any]:
        """Compile Java code"""
        file_path = Path(file_path)
        file_name = file_path.stem

        # Create a temporary directory for Java compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Copy the Java file to the temp directory
            import shutil
            java_file = temp_dir_path / file_path.name
            shutil.copy2(file_path, java_file)

            # Compile the Java file
            compile_cmd = ['javac', str(java_file)]
            result = self._execute_command(compile_cmd, temp_dir_path, output_display)

            if result['success']:
                output_display.show_info(f"Java compilation successful: {file_name}.class")
                return {
                    'success': True,
                    'compiled_files': [str(temp_dir_path / f"{file_name}.class")],
                    'temp_dir': str(temp_dir_path)
                }
            else:
                return result

    def _run_java(self, file_path: str, output_display) -> Dict[str, Any]:
        """Run Java code"""
        file_path = Path(file_path)
        file_name = file_path.stem

        # Create a temporary directory for Java execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Copy the Java file and compiled class files to the temp directory
            import shutil
            java_file = temp_dir_path / file_path.name
            shutil.copy2(file_path, java_file)

            # Compile first
            compile_result = self._compile_java(str(java_file), output_display)
            if not compile_result['success']:
                return compile_result

            # Run the compiled Java program
            run_cmd = ['java', file_name]
            return self._execute_command(run_cmd, temp_dir_path, output_display)

    def _compile_compiled(self, file_path: str, language: str, output_display) -> Dict[str, Any]:
        """Compile C/C++ code"""
        file_path = Path(file_path)
        output_name = file_path.stem

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Prepare compile command
            compile_cmd = self.supported_languages[language]['compile_cmd'].copy()
            for i, part in enumerate(compile_cmd):
                if '{file}' in part:
                    compile_cmd[i] = part.replace('{file}', str(file_path))
                elif '{output}' in part:
                    compile_cmd[i] = part.replace('{output}', str(temp_dir_path / output_name))

            result = self._execute_command(compile_cmd, temp_dir_path, output_display)

            if result['success']:
                output_display.show_info(f"{language.upper()} compilation successful: {output_name}")
                return {
                    'success': True,
                    'executable': str(temp_dir_path / output_name),
                    'temp_dir': str(temp_dir_path)
                }
            else:
                return result

    def _run_compiled(self, file_path: str, language: str, output_display) -> Dict[str, Any]:
        """Run compiled C/C++ code"""
        file_path = Path(file_path)

        # Compile first
        compile_result = self._compile_compiled(str(file_path), language, output_display)
        if not compile_result['success']:
            return compile_result

        # Run the compiled executable
        executable = compile_result['executable']
        run_cmd = [executable]
        return self._execute_command(run_cmd, Path(executable).parent, output_display)

    def _run_interpreted(self, file_path: str, language: str, output_display) -> Dict[str, Any]:
        """Run interpreted languages (Python, JavaScript)"""
        file_path = Path(file_path)

        # Special handling for Python input() functions
        if language == 'python':
            return self._run_python_interactive(file_path, output_display)

        # Prepare run command
        run_cmd = self.supported_languages[language]['run_cmd'].copy()
        for i, part in enumerate(run_cmd):
            if '{file}' in part:
                run_cmd[i] = part.replace('{file}', str(file_path))

        return self._execute_command(run_cmd, file_path.parent, output_display)

    def _run_python_interactive(self, file_path: str, output_display) -> Dict[str, Any]:
        """Run Python code with special handling for input() functions"""
        file_path = Path(file_path)

        # Read the file content to check for input() usage
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to read file: {str(e)}'
            }

        # Check if the code contains input() calls
        has_input = 'input(' in content

        if has_input:
            # For interactive programs, we'll run with a timeout and provide empty input
            if output_display:
                output_display.show_warning("Program contains input() - providing empty input for non-interactive execution")
            else:
                print("Warning: Program contains input() - providing empty input for non-interactive execution")

        # Prepare run command
        run_cmd = [sys.executable, '-u', str(file_path)]  # -u for unbuffered output

        try:
            # Start the process with stdin handling
            if has_input:
                # For programs with input(), we'll redirect stdin from a pipe
                # and close it immediately to simulate EOF after any initial output
                process = subprocess.Popen(
                    run_cmd,
                    cwd=str(file_path.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,  # Provide stdin pipe
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # Close stdin immediately to trigger EOF when input() is called
                process.stdin.close()

            else:
                # For non-interactive programs, use normal execution
                process = subprocess.Popen(
                    run_cmd,
                    cwd=str(file_path.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

            # Read output in real-time
            output_lines = []
            error_lines = []

            def read_output(stream, lines_list, is_error=False):
                for line in iter(stream.readline, ''):
                    line = line.strip()
                    if line:
                        lines_list.append(line)
                        if output_display:
                            if is_error:
                                output_display.show_error(line)
                            else:
                                output_display.show_output(line)

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_output,
                args=(process.stdout, output_lines, False)
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(process.stderr, error_lines, True)
            )

            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            # Wait for process to complete with timeout
            try:
                return_code = process.wait(timeout=10)  # 10 second timeout
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'success': False,
                    'error': 'Program execution timed out (10 seconds)'
                }

            # Wait for output threads to complete
            stdout_thread.join(timeout=1.0)
            stderr_thread.join(timeout=1.0)

            if return_code == 0:
                return {
                    'success': True,
                    'output': '\n'.join(output_lines),
                    'error_output': '\n'.join(error_lines)
                }
            else:
                error_msg = f"Command failed with return code {return_code}"
                if error_lines:
                    error_msg += f"\nError output: {' '.join(error_lines)}"
                return {
                    'success': False,
                    'error': error_msg,
                    'output': '\n'.join(output_lines),
                    'error_output': '\n'.join(error_lines)
                }

        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'Command not found: {e.filename}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Execution error: {str(e)}'
            }

    def _execute_command(self, cmd: list, working_dir: Path, output_display) -> Dict[str, Any]:
        """Execute a command and capture output"""
        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                cwd=str(working_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output in real-time
            output_lines = []
            error_lines = []

            def read_output(stream, lines_list, is_error=False):
                for line in iter(stream.readline, ''):
                    line = line.strip()
                    if line:
                        lines_list.append(line)
                        if output_display:
                            if is_error:
                                output_display.show_error(line)
                            else:
                                output_display.show_output(line)

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_output,
                args=(process.stdout, output_lines, False)
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(process.stderr, error_lines, True)
            )

            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            # Wait for process to complete
            return_code = process.wait()

            # Wait for output threads to complete
            stdout_thread.join(timeout=1.0)
            stderr_thread.join(timeout=1.0)

            if return_code == 0:
                return {
                    'success': True,
                    'output': '\n'.join(output_lines),
                    'error_output': '\n'.join(error_lines)
                }
            else:
                error_msg = f"Command failed with return code {return_code}"
                if error_lines:
                    error_msg += f"\nError output: {' '.join(error_lines)}"
                return {
                    'success': False,
                    'error': error_msg,
                    'output': '\n'.join(output_lines),
                    'error_output': '\n'.join(error_lines)
                }

        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'Command not found: {e.filename}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Execution error: {str(e)}'
            }

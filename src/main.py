"""
Main GUI application for Universal Multi-Language Compiler (UMLC)
Built with CustomTkinter for cross-platform compatibility
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent))

from backend.compiler_manager import CompilerManager
from gui.code_editor import CodeEditor
from gui.output_display import OutputDisplay
from gui.toolbar import Toolbar


class InputDialog(ctk.CTkToplevel):
    """Dialog for collecting user input for Python programs"""

    def __init__(self, parent, title, message):
        super().__init__(parent)

        self.title(title)
        self.geometry("500x300")
        self.resizable(True, True)

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        # Variables
        self.user_input = ""
        self.cancelled = False

        self._create_widgets(message)
        self._setup_layout()

        # Focus on text area
        self.text_area.focus()

    def _create_widgets(self, message):
        """Create dialog widgets"""
        # Message label
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            wraplength=450,
            justify="left"
        )

        # Text area for input
        self.text_area = ctk.CTkTextbox(
            self,
            height=150,
            wrap="word"
        )

        # Insert placeholder text
        self.text_area.insert("1.0", "Enter your input here...\nEach line will be used for one input() call.")

        # Buttons frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")

        # OK button
        self.ok_button = ctk.CTkButton(
            self.button_frame,
            text="Run Program",
            command=self._on_ok,
            width=120
        )

        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=120,
            fg_color="gray"
        )

    def _setup_layout(self):
        """Set up dialog layout"""
        # Message
        self.message_label.pack(padx=20, pady=(20, 10), anchor="w")

        # Text area
        self.text_area.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Buttons
        self.button_frame.pack(padx=20, pady=(0, 20), fill="x")
        self.ok_button.pack(side="right", padx=(10, 0))
        self.cancel_button.pack(side="right")

        # Bind events
        self.text_area.bind("<KeyRelease>", self._on_text_change)
        self.text_area.bind("<Button-1>", self._clear_placeholder)

    def _clear_placeholder(self, event=None):
        """Clear placeholder text when user clicks"""
        if self.text_area.get("1.0", "end-1c") == "Enter your input here...\nEach line will be used for one input() call.":
            self.text_area.delete("1.0", "end")
            self.text_area.configure(text_color="white")

    def _on_text_change(self, event=None):
        """Handle text changes"""
        self.user_input = self.text_area.get("1.0", "end-1c")

    def _on_ok(self):
        """Handle OK button click"""
        self.user_input = self.text_area.get("1.0", "end-1c")
        self.destroy()

    def _on_cancel(self):
        """Handle Cancel button click"""
        self.cancelled = True
        self.destroy()

    def get_input(self):
        """Get the user input"""
        return self.user_input
    """Main application window for UMLC"""

    def __init__(self):
        super().__init__()

        # Initialize core components
        self.compiler_manager = CompilerManager()
        self.current_file = None
        self.current_language = "python"

        # Configure window
        self.title("Universal Multi-Language Compiler (UMLC)")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Set up the GUI layout
        self._setup_layout()
        self._setup_menu()
        self._bind_events()

    def _setup_layout(self):
        """Set up the main layout of the application"""
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create toolbar
        self.toolbar = Toolbar(self.main_container, self)
        self.toolbar.pack(fill="x", padx=5, pady=5)

        # Create paned window for resizable sections
        self.paned_window = tk.PanedWindow(
            self.main_container,
            orient="vertical",
            sashwidth=5,
            sashrelief="raised"
        )
        self.paned_window.pack(fill="both", expand=True, padx=5, pady=5)

        # Create code editor (top section)
        self.code_editor = CodeEditor(
            self.paned_window,
            language=self.current_language
        )
        self.paned_window.add(self.code_editor, stretch="always")

        # Create output display (bottom section)
        self.output_display = OutputDisplay(self.paned_window)
        self.paned_window.add(self.output_display, stretch="always")

    def _setup_menu(self):
        """Set up the menu bar"""
        self.menu_bar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.code_editor.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.code_editor.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.code_editor.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.code_editor.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.code_editor.paste, accelerator="Ctrl+V")
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Language menu
        language_menu = tk.Menu(self.menu_bar, tearoff=0)
        language_menu.add_command(label="Python", command=lambda: self.set_language("python"))
        language_menu.add_command(label="C", command=lambda: self.set_language("c"))
        language_menu.add_command(label="C++", command=lambda: self.set_language("cpp"))
        language_menu.add_command(label="Java", command=lambda: self.set_language("java"))
        language_menu.add_command(label="JavaScript", command=lambda: self.set_language("javascript"))
        self.menu_bar.add_cascade(label="Language", menu=language_menu)

        # Run menu
        run_menu = tk.Menu(self.menu_bar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="Compile Only", command=self.compile_only, accelerator="F6")
        self.menu_bar.add_cascade(label="Run", menu=run_menu)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=self.menu_bar)

    def _bind_events(self):
        """Bind keyboard events"""
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind("<F5>", lambda e: self.run_code())
        self.bind("<F6>", lambda e: self.compile_only())

    def new_file(self):
        """Create a new file"""
        if self._check_save_changes():
            self.code_editor.clear()
            self.current_file = None
            self.title("Universal Multi-Language Compiler (UMLC) - Untitled")

    def open_file(self):
        """Open an existing file"""
        if not self._check_save_changes():
            return

        file_path = filedialog.askopenfilename(
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("C files", "*.c"),
                ("C++ files", "*.cpp *.cxx"),
                ("Java files", "*.java"),
                ("JavaScript files", "*.js"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self._load_file(file_path)

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the current file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("C files", "*.c"),
                ("C++ files", "*.cpp"),
                ("Java files", "*.java"),
                ("JavaScript files", "*.js"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self._save_to_file(file_path)

    def _check_save_changes(self):
        """Check if current file has unsaved changes"""
        # For now, always return True. In a full implementation,
        # this would check if the current content differs from the saved file
        return True

    def _load_file(self, file_path):
        """Load a file into the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.code_editor.set_content(content)
            self.current_file = file_path

            # Update window title
            file_name = os.path.basename(file_path)
            self.title(f"Universal Multi-Language Compiler (UMLC) - {file_name}")

            # Detect language from file extension
            ext = os.path.splitext(file_path)[1].lower()
            language_map = {
                '.py': 'python',
                '.c': 'c',
                '.cpp': 'cpp',
                '.cxx': 'cpp',
                '.java': 'java',
                '.js': 'javascript'
            }
            self.current_language = language_map.get(ext, 'python')
            self.set_language(self.current_language)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def _save_to_file(self, file_path):
        """Save content to a file"""
        try:
            content = self.code_editor.get_content()
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            self.current_file = file_path

            # Update window title
            file_name = os.path.basename(file_path)
            self.title(f"Universal Multi-Language Compiler (UMLC) - {file_name}")

            messagebox.showinfo("Success", "File saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def set_language(self, language):
        """Set the current programming language"""
        self.current_language = language
        self.code_editor.set_language(language)
        self.toolbar.update_language(language)

    def run_code(self):
        """Run the current code"""
        if not self.code_editor.get_content().strip():
            messagebox.showwarning("Warning", "No code to run!")
            return

        try:
            # Check if this is Python code with input()
            if self.current_language == 'python' and 'input(' in self.code_editor.get_content():
                # For Python code with input, show input dialog first
                self._run_python_with_input()
            else:
                # For other cases, use normal execution
                self._run_code_normal()

        except Exception as e:
            self.output_display.show_error(f"Runtime error: {str(e)}")

    def _run_python_with_input(self):
        """Run Python code that requires user input"""
        # Show input dialog
        dialog = InputDialog(self, "Program Input Required",
                           "Enter input for your Python program:\n(Separate multiple inputs with newlines)")
        self.wait_window(dialog)

        if dialog.cancelled:
            return

        user_input = dialog.get_input()

        # Save current content to a temporary file with input handling
        temp_file = self._create_temp_file_with_input(user_input)
        if not temp_file:
            return

        # Run the code using the compiler manager
        result = self.compiler_manager.run_code(
            temp_file,
            self.current_language,
            self.output_display
        )

        if not result["success"]:
            self.output_display.show_error(result["error"])

    def _run_code_normal(self):
        """Run code normally without special input handling"""
        # Save current content to a temporary file
        temp_file = self._create_temp_file()
        if not temp_file:
            return

        # Run the code using the compiler manager
        result = self.compiler_manager.run_code(
            temp_file,
            self.current_language,
            self.output_display
        )

        if not result["success"]:
            self.output_display.show_error(result["error"])

    def _create_temp_file_with_input(self, user_input):
        """Create a temporary file with user input for Python programs"""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = Path.home() / ".umlctemp"
            temp_dir.mkdir(exist_ok=True)

            # Create temp file with appropriate extension
            ext_map = {
                'python': '.py',
                'c': '.c',
                'cpp': '.cpp',
                'java': '.java',
                'javascript': '.js'
            }

            ext = ext_map.get(self.current_language, '.txt')
            temp_file = temp_dir / f"temp_{self.current_language}{ext}"

            # Write content to temp file
            content = self.code_editor.get_content()

            # For Python files with input, create a version that uses the provided input
            if self.current_language == 'python':
                content = self._create_input_version(content, user_input)

            with open(temp_file, 'w', encoding='utf-8') as file:
                file.write(content)

            return str(temp_file)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create temporary file: {str(e)}")
            return None

    def _create_input_version(self, content, user_input):
        """Create a version of Python code that uses provided input instead of input()"""
        lines = content.split('\n')
        modified_lines = []
        input_count = 0

        # Split user input by lines
        input_lines = user_input.split('\n') if user_input.strip() else ['']

        for line in lines:
            if 'input(' in line and not line.strip().startswith('#'):
                # Replace input() call with our predefined input
                input_count += 1
                if input_count <= len(input_lines):
                    # Use the corresponding input line
                    input_value = repr(input_lines[input_count - 1])
                    # Replace the input() call with the predefined value
                    modified_line = line.replace('input(', f'input({input_value}) # Original: ')
                    modified_lines.append(modified_line)
                else:
                    # No more input available, use empty string
                    modified_line = line.replace('input(', 'input("") # Original: ')
                    modified_lines.append(modified_line)
            else:
                modified_lines.append(line)

        return '\n'.join(modified_lines)

    def compile_only(self):
        """Compile the current code without running"""
        if not self.code_editor.get_content().strip():
            messagebox.showwarning("Warning", "No code to compile!")
            return

        try:
            # Save current content to a temporary file
            temp_file = self._create_temp_file()
            if not temp_file:
                return

            # Compile the code using the compiler manager
            result = self.compiler_manager.compile_code(
                temp_file,
                self.current_language,
                self.output_display
            )

            if not result["success"]:
                self.output_display.show_error(result["error"])

        except Exception as e:
            self.output_display.show_error(f"Compilation error: {str(e)}")

    def _wrap_python_input(self, content):
        """Wrap Python code containing input() calls with error handling"""
        lines = content.split('\n')
        wrapped_lines = []
        input_found = False

        for line in lines:
            wrapped_lines.append(line)
            if 'input(' in line and not line.strip().startswith('#'):
                input_found = True

        # If input() calls were found, add the wrapper
        if input_found:
            # Insert the try-except wrapper at the beginning
            wrapped_content = '''# Auto-generated wrapper for input() handling
import sys

# Store original stdin
_original_stdin = sys.stdin

try:
''' + '\n'.join('    ' + line for line in lines) + '''

except EOFError:
    print("Note: Program contains input() but is running in non-interactive mode.")
    print("Consider removing input() calls or running interactively.")

# Restore original stdin
sys.stdin = _original_stdin
'''
            return wrapped_content

        return content

    def show_about(self):
        """Show the about dialog"""
        messagebox.showinfo(
            "About UMLC",
            "Universal Multi-Language Compiler (UMLC)\n\n"
            "A cross-platform desktop compiler that supports:\n"
            "- Python\n"
            "- C\n"
            "- C++\n"
            "- Java\n"
            "- JavaScript\n\n"
            f"Version {__version__}\n"
            f"Built with CustomTkinter"
        )


def main():
    """Main entry point"""
    app = UMLCApp()
    app.mainloop()


if __name__ == "__main__":
    main()

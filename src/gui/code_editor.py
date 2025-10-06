"""
Code Editor component with syntax highlighting support
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.token import Token
from pygments.styles import get_style_by_name
import re


class CodeEditor(ctk.CTkFrame):
    """Enhanced code editor with syntax highlighting"""

    def __init__(self, parent, language="python", **kwargs):
        super().__init__(parent, **kwargs)

        self.language = language
        self.language_configs = {
            'python': {'lexer': 'python', 'extensions': ['.py']},
            'c': {'lexer': 'c', 'extensions': ['.c', '.h']},
            'cpp': {'lexer': 'cpp', 'extensions': ['.cpp', '.cxx', '.cc']},
            'java': {'lexer': 'java', 'extensions': ['.java']},
            'javascript': {'lexer': 'javascript', 'extensions': ['.js']}
        }

        self._setup_editor()
        self._setup_scrollbars()
        self._setup_bindings()

        # Initialize syntax highlighting
        self.update_syntax_highlighting()

    def _setup_editor(self):
        """Set up the text editor widget"""
        # Create text widget with syntax highlighting
        self.text = tk.Text(
            self,
            wrap="none",
            font=("Consolas", 11),
            bg="#1e1e1e",  # Dark theme background
            fg="#d4d4d4",  # Light text
            insertbackground="#ffffff",  # White cursor
            selectbackground="#264f78",  # Selection color
            undo=True,
            maxundo=50
        )

        # Configure tags for syntax highlighting
        self._setup_syntax_tags()

    def _setup_syntax_tags(self):
        """Set up text tags for syntax highlighting"""
        # Define color scheme for dark theme
        colors = {
            'keyword': '#569cd6',      # Blue
            'string': '#ce9178',       # Orange
            'comment': '#6a9955',      # Green
            'number': '#b5cea8',       # Light green
            'function': '#dcdcaa',     # Yellow
            'class': '#4ec9b0',        # Teal
            'operator': '#d4d4d4',     # Light gray
            'variable': '#9cdcfe',     # Light blue
        }

        # Create tags for each token type
        for token_type, color in colors.items():
            self.text.tag_configure(token_type, foreground=color)

    def _setup_scrollbars(self):
        """Set up scrollbars for the text widget"""
        # Vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.v_scrollbar.set)

        # Horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(xscrollcommand=self.h_scrollbar.set)

        # Grid layout
        self.text.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _setup_bindings(self):
        """Set up keyboard and mouse bindings"""
        # Bind syntax highlighting updates
        self.text.bind('<KeyRelease>', self._on_text_change)
        self.text.bind('<ButtonRelease>', self._on_text_change)

        # Bind for better interaction
        self.text.bind('<Control-a>', self._select_all)
        self.text.bind('<Control-l>', self._clear_selection)

    def _select_all(self, event=None):
        """Select all text"""
        self.text.tag_add("sel", "1.0", "end")
        return "break"

    def _clear_selection(self, event=None):
        """Clear current selection"""
        self.text.tag_remove("sel", "1.0", "end")
        return "break"

    def _on_text_change(self, event=None):
        """Handle text changes and update syntax highlighting"""
        # Debounce the syntax highlighting to avoid performance issues
        if hasattr(self, '_highlight_timer'):
            self.after_cancel(self._highlight_timer)

        self._highlight_timer = self.after(300, self.update_syntax_highlighting)

    def set_language(self, language):
        """Set the programming language for syntax highlighting"""
        if language in self.language_configs:
            self.language = language
            self.update_syntax_highlighting()

    def update_syntax_highlighting(self):
        """Update syntax highlighting for the current text"""
        if not self.language or self.language not in self.language_configs:
            return

        try:
            # Get the lexer for the current language
            lexer_name = self.language_configs[self.language]['lexer']
            lexer = get_lexer_by_name(lexer_name)

            # Get current text content
            content = self.text.get("1.0", "end")

            # Clear existing highlighting
            self._clear_highlighting()

            # Apply syntax highlighting
            self._apply_syntax_highlighting(content, lexer)

        except Exception as e:
            # If syntax highlighting fails, continue without it
            print(f"Syntax highlighting error: {e}")

    def _clear_highlighting(self):
        """Clear all syntax highlighting"""
        # Remove all token tags
        for tag in ['keyword', 'string', 'comment', 'number', 'function', 'class', 'operator', 'variable']:
            self.text.tag_remove(tag, "1.0", "end")

    def _apply_syntax_highlighting(self, content, lexer):
        """Apply syntax highlighting to the text"""
        try:
            # Tokenize the content
            tokens = list(lex(content, lexer))

            # Apply highlighting based on tokens
            current_pos = "1.0"
            for token_type, token_value in tokens:
                if token_value.strip():  # Skip empty tokens
                    # Map pygments token types to our tag names
                    tag = self._map_token_to_tag(token_type)
                    if tag:
                        # Find the end position
                        lines = token_value.split('\n')
                        if len(lines) == 1:
                            # Single line token
                            end_pos = self.text.index(f"{current_pos} + {len(token_value)} chars")
                            self.text.tag_add(tag, current_pos, end_pos)
                            current_pos = end_pos
                        else:
                            # Multi-line token
                            for i, line in enumerate(lines):
                                if i == 0:
                                    # First line
                                    end_pos = self.text.index(f"{current_pos} lineend")
                                    self.text.tag_add(tag, current_pos, end_pos)
                                    current_pos = self.text.index(f"{current_pos} + 1 line linestart")
                                elif i == len(lines) - 1:
                                    # Last line
                                    self.text.tag_add(tag, current_pos, f"{current_pos} + {len(line)} chars")
                                else:
                                    # Middle lines
                                    end_pos = self.text.index(f"{current_pos} lineend")
                                    self.text.tag_add(tag, current_pos, end_pos)
                                    current_pos = self.text.index(f"{current_pos} + 1 line linestart")

        except Exception as e:
            print(f"Error applying syntax highlighting: {e}")

    def _map_token_to_tag(self, token_type):
        """Map pygments token types to our tag names"""
        token_str = str(token_type)

        if 'Keyword' in token_str:
            return 'keyword'
        elif 'String' in token_str:
            return 'string'
        elif 'Comment' in token_str:
            return 'comment'
        elif 'Number' in token_str:
            return 'number'
        elif 'Name.Function' in token_str:
            return 'function'
        elif 'Name.Class' in token_str:
            return 'class'
        elif 'Operator' in token_str:
            return 'operator'
        elif 'Name' in token_str:
            return 'variable'

        return None

    def get_content(self):
        """Get the current text content"""
        return self.text.get("1.0", "end-1c")  # -1c removes trailing newline

    def set_content(self, content):
        """Set the text content"""
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.update_syntax_highlighting()

    def clear(self):
        """Clear the editor content"""
        self.text.delete("1.0", "end")

    def undo(self):
        """Undo the last action"""
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass  # No more undo actions

    def redo(self):
        """Redo the last undone action"""
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass  # No more redo actions

    def cut(self):
        """Cut selected text"""
        self.text.event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text"""
        self.text.event_generate("<<Copy>>")

    def paste(self):
        """Paste text from clipboard"""
        self.text.event_generate("<<Paste>>")

    def get_line_count(self):
        """Get the number of lines in the editor"""
        return int(self.text.index("end-1c").split(".")[0])

    def get_current_line(self):
        """Get the current line number"""
        return int(self.text.index("insert").split(".")[0])

    def get_current_column(self):
        """Get the current column number"""
        return int(self.text.index("insert").split(".")[1])

    def goto_line(self, line_number):
        """Go to a specific line"""
        try:
            self.text.mark_set("insert", f"{line_number}.0")
            self.text.see("insert")
            self.text.focus()
        except tk.TclError:
            pass  # Invalid line number

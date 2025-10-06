"""
Toolbar component for the UMLC application
"""

import customtkinter as ctk
import tkinter as tk


class Toolbar(ctk.CTkFrame):
    """Toolbar with language selection and execution controls"""

    def __init__(self, parent, main_app, **kwargs):
        super().__init__(parent, **kwargs)

        self.main_app = main_app
        self.current_language = "python"

        self._setup_toolbar()

    def _setup_toolbar(self):
        """Set up the toolbar layout"""
        # Language selection
        self.language_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.language_frame.pack(side="left", padx=(10, 20))

        self.language_label = ctk.CTkLabel(
            self.language_frame,
            text="Language:",
            font=("Arial", 12, "bold")
        )
        self.language_label.pack(side="left", padx=(0, 10))

        # Language dropdown
        self.language_var = tk.StringVar(value="Python")
        self.language_dropdown = ctk.CTkOptionMenu(
            self.language_frame,
            variable=self.language_var,
            values=["Python", "C", "C++", "Java", "JavaScript"],
            command=self._on_language_change,
            width=100
        )
        self.language_dropdown.pack(side="left")

        # Execution controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(side="left", padx=(0, 10))

        # Run button
        self.run_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶ Run (F5)",
            command=self._run_code,
            width=100,
            height=35,
            font=("Arial", 11)
        )
        self.run_btn.pack(side="left", padx=(0, 5))

        # Compile button
        self.compile_btn = ctk.CTkButton(
            self.controls_frame,
            text="⚙ Compile (F6)",
            command=self._compile_code,
            width=110,
            height=35,
            font=("Arial", 11)
        )
        self.compile_btn.pack(side="left", padx=(0, 5))

        # File operations
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_frame.pack(side="left", padx=(0, 10))

        # New file button
        self.new_btn = ctk.CTkButton(
            self.file_frame,
            text="📄 New",
            command=self._new_file,
            width=80,
            height=35,
            font=("Arial", 11)
        )
        self.new_btn.pack(side="left", padx=(0, 5))

        # Open file button
        self.open_btn = ctk.CTkButton(
            self.file_frame,
            text="📂 Open",
            command=self._open_file,
            width=80,
            height=35,
            font=("Arial", 11)
        )
        self.open_btn.pack(side="left", padx=(0, 5))

        # Save file button
        self.save_btn = ctk.CTkButton(
            self.file_frame,
            text="💾 Save",
            command=self._save_file,
            width=80,
            height=35,
            font=("Arial", 11)
        )
        self.save_btn.pack(side="left")

        # Status and info
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(side="right", padx=(10, 10))

        # Current file label
        self.file_label = ctk.CTkLabel(
            self.status_frame,
            text="No file open",
            font=("Arial", 10),
            text_color="gray"
        )
        self.file_label.pack(side="left")

        # Line/column info
        self.position_label = ctk.CTkLabel(
            self.status_frame,
            text="Ln 1, Col 1",
            font=("Arial", 10),
            text_color="gray"
        )
        self.position_label.pack(side="left", padx=(10, 0))

        # Language indicator
        self.lang_indicator = ctk.CTkLabel(
            self.status_frame,
            text="Python",
            font=("Arial", 10, "bold"),
            text_color="#4ec9b0"
        )
        self.lang_indicator.pack(side="left", padx=(10, 0))

    def _on_language_change(self, selected_language):
        """Handle language selection change"""
        language_map = {
            "Python": "python",
            "C": "c",
            "C++": "cpp",
            "Java": "java",
            "JavaScript": "javascript"
        }

        new_language = language_map.get(selected_language, "python")

        if new_language != self.current_language:
            self.current_language = new_language
            self.main_app.set_language(new_language)

            # Update language indicator
            self.lang_indicator.configure(text=selected_language)

    def update_language(self, language):
        """Update the current language display"""
        self.current_language = language

        language_map_reverse = {
            "python": "Python",
            "c": "C",
            "cpp": "C++",
            "java": "Java",
            "javascript": "JavaScript"
        }

        display_name = language_map_reverse.get(language, "Python")
        self.language_var.set(display_name)
        self.lang_indicator.configure(text=display_name)

    def update_file_info(self, file_path=None):
        """Update the current file information"""
        if file_path:
            import os
            file_name = os.path.basename(file_path)
            self.file_label.configure(text=f"File: {file_name}")
        else:
            self.file_label.configure(text="No file open")

    def update_position(self, line=1, column=1):
        """Update the cursor position display"""
        self.position_label.configure(text=f"Ln {line}, Col {column}")

    def _run_code(self):
        """Run the current code"""
        self.main_app.run_code()

    def _compile_code(self):
        """Compile the current code"""
        self.main_app.compile_only()

    def _new_file(self):
        """Create a new file"""
        self.main_app.new_file()

    def _open_file(self):
        """Open an existing file"""
        self.main_app.open_file()

    def _save_file(self):
        """Save the current file"""
        self.main_app.save_file()

    def set_run_button_state(self, enabled=True):
        """Enable or disable the run button"""
        state = "normal" if enabled else "disabled"
        self.run_btn.configure(state=state)

    def set_compile_button_state(self, enabled=True):
        """Enable or disable the compile button"""
        state = "normal" if enabled else "disabled"
        self.compile_btn.configure(state=state)

    def show_status_message(self, message, duration=3000):
        """Show a temporary status message"""
        # Create a temporary status label if it doesn't exist
        if not hasattr(self, '_status_label'):
            self._status_label = ctk.CTkLabel(
                self.status_frame,
                text="",
                font=("Arial", 9),
                text_color="#ffcc02"
            )
            self._status_label.pack(side="left", padx=(15, 0))

        self._status_label.configure(text=message)

        # Clear the message after the specified duration
        if hasattr(self, '_status_timer'):
            self.after_cancel(self._status_timer)

        self._status_timer = self.after(duration, lambda: self._status_label.configure(text=""))

    def get_current_language(self):
        """Get the currently selected language"""
        return self.current_language

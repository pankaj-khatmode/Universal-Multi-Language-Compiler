"""
Output Display component for showing compilation and execution results
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk


class OutputDisplay(ctk.CTkFrame):
    """Output display widget for showing compilation and execution results"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._setup_display()
        self._setup_scrollbars()
        self._setup_buttons()

    def _setup_display(self):
        """Set up the output text display"""
        # Create text widget for output
        self.text = tk.Text(
            self,
            wrap="word",
            font=("Consolas", 10),
            bg="#1e1e1e",  # Dark theme background
            fg="#d4d4d4",  # Light text
            state="disabled",
            height=8
        )

        # Configure tags for different types of output
        self.text.tag_configure("output", foreground="#d4d4d4")
        self.text.tag_configure("error", foreground="#f44747")  # Red for errors
        self.text.tag_configure("warning", foreground="#ffcc02")  # Yellow for warnings
        self.text.tag_configure("info", foreground="#4ec9b0")  # Teal for info
        self.text.tag_configure("success", foreground="#6a9955")  # Green for success

    def _setup_scrollbars(self):
        """Set up scrollbars for the output display"""
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

    def _setup_buttons(self):
        """Set up control buttons for the output display"""
        # Button frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Clear button
        self.clear_btn = ctk.CTkButton(
            self.button_frame,
            text="Clear Output",
            command=self.clear,
            width=100,
            height=28
        )
        self.clear_btn.pack(side="right", padx=(5, 0))

        # Copy button
        self.copy_btn = ctk.CTkButton(
            self.button_frame,
            text="Copy",
            command=self.copy_output,
            width=80,
            height=28
        )
        self.copy_btn.pack(side="right", padx=(5, 0))

        # Configure button frame grid weight
        self.button_frame.grid_columnconfigure(0, weight=1)

    def show_output(self, text, tag="output"):
        """Show regular output text"""
        self._append_text(text, tag)

    def show_error(self, text):
        """Show error text"""
        self._append_text(text, "error")

    def show_warning(self, text):
        """Show warning text"""
        self._append_text(text, "warning")

    def show_info(self, text):
        """Show info text"""
        self._append_text(text, "info")

    def show_success(self, text):
        """Show success text"""
        self._append_text(text, "success")

    def _append_text(self, text, tag="output"):
        """Append text to the output display"""
        # Enable text widget for editing
        self.text.configure(state="normal")

        # Add timestamp if this is the first text or after a clear
        if self.text.get("1.0", "end").strip() == "":
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.text.insert("end", f"[{timestamp}] ", "info")

        # Insert the text with appropriate tag
        self.text.insert("end", text + "\n", tag)

        # Scroll to the end
        self.text.see("end")

        # Disable text widget again
        self.text.configure(state="disabled")

    def clear(self):
        """Clear all output"""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def copy_output(self):
        """Copy output to clipboard"""
        try:
            # Enable text widget temporarily
            self.text.configure(state="normal")

            # Get selected text or all text if nothing is selected
            try:
                selected_text = self.text.get("sel.first", "sel.last")
            except tk.TclError:
                # No selection, get all text
                selected_text = self.text.get("1.0", "end-1c")

            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(selected_text)

            # Disable text widget again
            self.text.configure(state="disabled")

        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    def get_output_text(self):
        """Get all output text"""
        return self.text.get("1.0", "end-1c")

    def save_output(self, filename=None):
        """Save output to a file"""
        if filename is None:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.get_output_text())
                self.show_info(f"Output saved to {filename}")
            except Exception as e:
                self.show_error(f"Error saving output: {str(e)}")

    def set_max_lines(self, max_lines):
        """Set maximum number of lines to keep in the display"""
        self.text.configure(state="normal")

        # Count current lines
        current_lines = int(self.text.index("end-1c").split(".")[0])

        if current_lines > max_lines:
            # Remove lines from the beginning
            lines_to_remove = current_lines - max_lines
            self.text.delete("1.0", f"{lines_to_remove + 1}.0")

        self.text.configure(state="disabled")

    def auto_scroll(self, enabled=True):
        """Enable or disable auto-scrolling to bottom"""
        if enabled:
            self.text.see("end")
        # Note: This is called automatically when new text is added

    def highlight_line(self, line_number, tag="warning"):
        """Highlight a specific line"""
        try:
            start_idx = f"{line_number}.0"
            end_idx = f"{line_number}.end"

            self.text.configure(state="normal")
            self.text.tag_add(tag, start_idx, end_idx)
            self.text.configure(state="disabled")

            # Scroll to the highlighted line
            self.text.see(start_idx)

        except tk.TclError:
            pass  # Invalid line number

    def get_line_count(self):
        """Get the number of lines in the output"""
        return int(self.text.index("end-1c").split(".")[0])

    def search_output(self, search_term):
        """Search for text in the output"""
        self.text.configure(state="normal")

        # Clear previous search highlights
        self.text.tag_remove("search", "1.0", "end")

        # Configure search tag
        self.text.tag_configure("search", background="#264f78")

        # Search for the term
        count = 0
        start_pos = "1.0"

        while True:
            start_pos = self.text.search(search_term, start_pos, "end", nocase=True)
            if not start_pos:
                break

            end_pos = f"{start_pos} + {len(search_term)} chars"
            self.text.tag_add("search", start_pos, end_pos)

            start_pos = end_pos
            count += 1

        self.text.configure(state="disabled")
        return count

    def clear_search_highlights(self):
        """Clear search highlights"""
        self.text.configure(state="normal")
        self.text.tag_remove("search", "1.0", "end")
        self.text.configure(state="disabled")

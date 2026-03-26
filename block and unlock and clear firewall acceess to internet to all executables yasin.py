import os
import sys
import ctypes
import subprocess
import json
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- 1. Admin Privilege Check ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- 2. App Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Determine real directory (works even when compiled to .exe)
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "firewall_settings.json")
DEFAULT_EXTS = [".exe", ".dll", ".bat", ".cmd", ".vbs", ".ps1", ".jar", ".py"]

class FirewallApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Folder Firewall Lockdown")
        self.geometry("700x750")
        self.grid_columnconfigure(0, weight=1)

        self.target_folder = ctk.StringVar(value=APP_DIR)
        self.include_subfolders = ctk.BooleanVar(value=True)
        self.extensions = self.load_extensions()

        self.setup_ui()

    # --- 3. CRUD: Load and Save Settings ---
    def load_extensions(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_EXTS

    def save_extensions(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.extensions, f)

    # --- 4. UI Layout ---
    def setup_ui(self):
        # Folder Selection Frame
        folder_frame = ctk.CTkFrame(self)
        folder_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        folder_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(folder_frame, text="Target Folder:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.target_folder, state="disabled")
        self.folder_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(folder_frame, text="Browse", width=80, command=self.browse_folder).grid(row=0, column=2, padx=10, pady=10)
        
        # Subfolder Toggle
        ctk.CTkSwitch(folder_frame, text="Include Subfolders", variable=self.include_subfolders).grid(row=1, column=1, sticky="w", padx=10, pady=(0, 10))

        # Extensions CRUD Frame
        ext_frame = ctk.CTkFrame(self)
        ext_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ext_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(ext_frame, text="Target Extensions (Comma Separated)", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        
        self.ext_textbox = ctk.CTkTextbox(ext_frame, height=60)
        self.ext_textbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.refresh_ext_display()

        ctk.CTkButton(ext_frame, text="Save / Update Extensions", command=self.update_extensions).grid(row=2, column=0, padx=10, pady=(0, 10), sticky="e")
        ctk.CTkButton(ext_frame, text="Restore Defaults", fg_color="#555555", hover_color="#333333", command=self.restore_defaults).grid(row=2, column=1, padx=10, pady=(0, 10), sticky="w")

        # Actions Frame
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(action_frame, text="Block All", fg_color="#a32a2a", hover_color="#801f1f", command=lambda: self.execute_firewall("block")).grid(row=0, column=0, padx=5, pady=15)
        ctk.CTkButton(action_frame, text="Allow All", fg_color="#2a7a3a", hover_color="#1f5c2b", command=lambda: self.execute_firewall("allow")).grid(row=0, column=1, padx=5, pady=15)
        ctk.CTkButton(action_frame, text="Clear Rules", fg_color="#4a4a4a", hover_color="#333333", command=lambda: self.execute_firewall("clear")).grid(row=0, column=2, padx=5, pady=15)
        ctk.CTkButton(action_frame, text="View Active App Rules", fg_color="#1f5380", hover_color="#143652", command=self.view_active_rules).grid(row=0, column=3, padx=5, pady=15)

        # Log Output Frame
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.grid_rowconfigure(3, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="Activity Log", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(5, 0))
        self.log_box = ctk.CTkTextbox(log_frame, state="disabled")
        self.log_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # --- 5. Logic & Functionality ---
    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update()

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.target_folder.get())
        if folder:
            self.target_folder.set(folder)
            self.log(f"Selected folder: {folder}")

    def refresh_ext_display(self):
        self.ext_textbox.delete("1.0", "end")
        self.ext_textbox.insert("1.0", ", ".join(self.extensions))

    def update_extensions(self):
        raw_text = self.ext_textbox.get("1.0", "end").strip()
        new_exts = []
        for ext in raw_text.split(","):
            ext = ext.strip()
            if ext:
                if not ext.startswith("."):
                    ext = "." + ext
                new_exts.append(ext.lower())
        
        self.extensions = list(set(new_exts))
        self.save_extensions()
        self.refresh_ext_display()
        self.log(f"Extensions updated and saved: {self.extensions}")

    def restore_defaults(self):
        self.extensions = DEFAULT_EXTS.copy()
        self.save_extensions()
        self.refresh_ext_display()
        self.log("Extensions restored to default.")

    def run_cmd(self, command):
        return subprocess.run(command, capture_output=True, text=True, creationflags=0x08000000)

    def view_active_rules(self):
        self.log("\n--- Querying Firewall for App Rules ---")
        self.log("This may take a few seconds...")
        # Use powershell for a cleaner text output of rules starting with AppRule_
        cmd = ["powershell", "-Command", "Get-NetFirewallRule -DisplayName 'AppRule_*' | Select-Object DisplayName, Action, Direction | Format-Table -AutoSize"]
        result = self.run_cmd(cmd)
        
        if result.stdout.strip():
            self.log(result.stdout)
        else:
            self.log("No active rules found created by this application.")
        self.log("--- End of Query ---\n")

    def execute_firewall(self, action):
        folder = self.target_folder.get()
        recursive = self.include_subfolders.get()
        
        self.log(f"\n--- Starting {action.upper()} operation ---")
        self.log(f"Target: {folder} (Subfolders: {recursive})")

        target_path = Path(folder)
        files_to_process = []
        
        # Determine search depth
        for ext in self.extensions:
            if recursive:
                files_to_process.extend(target_path.rglob(f"*{ext}"))
            else:
                files_to_process.extend(target_path.glob(f"*{ext}"))

        if not files_to_process:
            self.log("No matching files found based on current filters.")
            return

        for filepath in files_to_process:
            filename = filepath.name
            full_path = str(filepath)
            rule_name = f"AppRule_{filename}"

            self.run_cmd(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}", f"program={full_path}"])

            if action == "block":
                self.run_cmd(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=out", f"program={full_path}", "action=block"])
                self.run_cmd(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", f"program={full_path}", "action=block"])
                self.log(f"Blocked: {filename}")
            elif action == "allow":
                self.run_cmd(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=out", f"program={full_path}", "action=allow"])
                self.run_cmd(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", f"program={full_path}", "action=allow"])
                self.log(f"Allowed: {filename}")
            elif action == "clear":
                self.log(f"Cleared rules for: {filename}")

        self.log("--- Operation Complete ---\n")

if __name__ == "__main__":
    app = FirewallApp()
    app.mainloop()
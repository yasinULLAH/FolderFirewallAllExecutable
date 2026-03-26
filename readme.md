# 🛡️ Folder Firewall Lockdown

A modern, minimalist desktop application built with Python and CustomTkinter that allows you to instantly block or allow internet access for all executable files and scripts within a specific folder and its subfolders.

Instead of manually adding rules to Windows Defender Firewall one by one, this tool automates the process, making it incredibly easy to prevent specific applications or entire directories from "phoning home."

## ✨ Features

* **Modern UI/UX:** Built with CustomTkinter for a sleek, dark-mode-by-default interface.
* **Context-Aware:** Automatically defaults to the directory it is run from.
* **Recursive Targeting:** Toggle whether to apply firewall rules to just the top folder or all subfolders.
* **Customizable Extensions:** Edit, add, or remove the exact file extensions you want to target (e.g., `.exe`, `.dll`, `.bat`, `.py`). Settings are automatically saved for your next session.
* **One-Click Actions:** * 🔴 **Block All:** Instantly cuts off inbound and outbound network access.
  * 🟢 **Allow All:** Restores inbound and outbound network access.
  * ⚪ **Clear Rules:** Cleans up the Windows Firewall by removing rules created by this app.
* **Rule Auditing:** Query the Windows Firewall directly from the app to see all active rules it has created.
* **Auto-Admin Escalation:** Automatically prompts for the necessary Administrator privileges required to modify firewall rules.
* **Portable:** Can be compiled into a single, standalone `.exe` file.


## ⚙️ Prerequisites

If you are running the app from the source code, you will need:
* **OS:** Windows 10 / 11
* **Python:** 3.8 or higher
* **Libraries:** CustomTkinter

Install the required library via pip:
```bash
pip install customtkinter
```

## 🚀 Usage

### Running from Source
Simply run the Python script. The app will automatically prompt you for Administrator rights via Windows UAC.
```bash
python block and unlock and clear firewall acceess to internet to all executables yasin.py
```

### Compiling to a Standalone Executable (.exe)
You can build a portable `.exe` so you don't need Python installed on the machine you are running it on.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Place your `logo.ico` in the same directory as the script.
3. Run the following build command:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --icon "logo.ico" --uac-admin --name "FolderFirewall" block and unlock and clear firewall acceess to internet to all executables yasin.py
   ```
4. Find your compiled `FolderFirewall.exe` inside the newly created `dist/` folder.

Or 

5. Simply Download and run the already compiled `FolderFirewall.exe` file

## 🧠 How it Works

This application acts as a graphical wrapper for the built-in Windows `netsh advfirewall` command-line tool. 
When you click "Block" or "Allow", the app scans your target directory for the file extensions you specified. For every match it finds, it executes a silent shell command to add strict Inbound and Outbound rules directly to your Windows Defender Firewall registry. 

To prevent clutter, the app dynamically names its rules (`AppRule_filename.exe`) and always deletes previous duplicate rules before adding new ones.

## ⚠️ Disclaimer

* **Requires Administrator Privileges:** Modifying firewall rules is a system-level action. This app will request elevated permissions on startup.
* **Use with Caution:** Blocking critical system executables or network drivers can cause unexpected behavior in Windows. Only block folders and software you understand.
* **Script Limitations:** While this app can add `.bat`, `.ps1`, or `.dll` files to the firewall, Windows Firewall primarily monitors the *host executables* (like `cmd.exe` or `rundll32.exe`) making the network requests. Blocking a script directly in the firewall may not always stop network traffic if the host program is still allowed.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
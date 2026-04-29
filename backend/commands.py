import subprocess
import psutil
import os
import pyautogui
import time
from datetime import datetime

def open_app(app_name):
    """Open any app or folder on Windows smartly"""
    
    app_name_lower = app_name.lower().strip()
    
    # Direct app map for common apps
    app_map = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "vs code": "code",
        "vscode": "code",
        "spotify": "spotify.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "terminal": "cmd.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "camera": "microsoft.windows.camera:",
        "gallery": "ms-photos:",
        "photos": "ms-photos:",
        "microsoft store": "ms-windows-store:",
        "store": "ms-windows-store:",
        "maps": "bingmaps:",
        "clock": "ms-clock:",
        "calendar": "outlookcal:",
        "mail": "outlookmail:",
        "whatsapp": "whatsapp:",
        "telegram": "telegram.exe",
        "vlc": "vlc.exe",
        "zoom": "zoom.exe",
        "discord": "discord.exe",
        "teams": "teams.exe",
        "outlook": "outlook.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "steam": "steam.exe",
        "obs": "obs64.exe",
        "postman": "postman.exe",
    }

    # Check direct map first
    if app_name_lower in app_map:
        executable = app_map[app_name_lower]
        try:
            if ":" in executable and not executable.endswith(".exe"):
                subprocess.Popen(f"start {executable}", shell=True)
            else:
                subprocess.Popen(executable, shell=True)
            return f"Opening {app_name} for you Abhishek."
        except:
            pass

    # Known folders map
    folder_map = {
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos"),
        "abhishek project": r"C:\Users\abhis\Abhishek Project",
        "project folder": r"C:\Users\abhis\Abhishek Project",
        "kairo": r"C:\Users\abhis\Abhishek Project\KAIRO",
        "kairo folder": r"C:\Users\abhis\Abhishek Project\KAIRO",
    }

    # Check known folders first
    for folder_key, folder_path in folder_map.items():
        if folder_key in app_name_lower:
            try:
                subprocess.Popen(f'explorer "{folder_path}"', shell=True)
                return f"Opening {folder_key} for you Abhishek."
            except Exception as e:
                return f"Could not open folder: {e}"

    # Smart folder search — searches entire PC for any folder name
    if any(w in app_name_lower for w in ["folder", "directory"]):
        search_name = app_name_lower.replace("folder", "").replace("directory", "") \
                                    .replace("open", "").replace("the", "").strip()
        try:
            search_paths = [
                r"C:\Users\abhis",
                r"C:\Users\abhis\Desktop",
                r"C:\Users\abhis\Documents",
                r"C:\Users\abhis\Abhishek Project",
            ]
            for search_path in search_paths:
                for root, dirs, files in os.walk(search_path):
                    for d in dirs:
                        if search_name.lower() in d.lower():
                            full_path = os.path.join(root, d)
                            subprocess.Popen(f'explorer "{full_path}"', shell=True)
                            return f"Found and opened {d} folder for you Abhishek."
            return f"Could not find any folder named {search_name} on your PC."
        except Exception as e:
            return f"Error searching for folder: {e}"

    # Final fallback — try PowerShell to find and open any installed app
    try:
        subprocess.Popen(
            f'powershell -Command "Start-Process \'{app_name_lower}\'"',
            shell=True
        )
        return f"Trying to open {app_name} for you Abhishek."
    except Exception as e:
        return f"Could not open {app_name}. Try saying the exact app name."

def close_app(app_name):
    """Close any running app by name"""
    app_process_map = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calculator.exe",
        "spotify": "spotify.exe",
        "whatsapp": "whatsapp.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
    }

    process_name = app_process_map.get(app_name.lower(), app_name.lower() + ".exe")

    killed = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
            proc.kill()
            killed = True

    if killed:
        return f"Closed {app_name} for you Abhishek."
    else:
        return f"Could not find {app_name} running."

def get_battery():
    """Get current battery status"""
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = "plugged in" if battery.power_plugged else "on battery"
        return f"Your battery is at {percent}% and {plugged} Abhishek."
    return "Could not get battery info."

def get_time():
    """Get current time and date"""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %d %B %Y")
    return f"It is {time_str} on {date_str} Abhishek."

def volume_up():
    """Increase system volume"""
    for _ in range(5):
        pyautogui.press('volumeup')
    return "Volume increased Abhishek."

def volume_down():
    """Decrease system volume"""
    for _ in range(5):
        pyautogui.press('volumedown')
    return "Volume decreased Abhishek."

def volume_mute():
    """Mute system volume"""
    pyautogui.press('volumemute')
    return "Volume muted Abhishek."

def take_screenshot():
    """Take a screenshot and save it"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop, f"kairo_screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    print(f"Screenshot saved at: {path}")
    
    # Show Windows notification
    subprocess.Popen([
        'powershell', '-Command',
        f'''Add-Type -AssemblyName System.Windows.Forms;
        $notify = New-Object System.Windows.Forms.NotifyIcon;
        $notify.Icon = [System.Drawing.SystemIcons]::Information;
        $notify.Visible = $true;
        $notify.ShowBalloonTip(3000, "KAIRO", "Screenshot saved to Desktop!", [System.Windows.Forms.ToolTipIcon]::Info);
        Start-Sleep -Seconds 3;
        $notify.Dispose()'''
    ])
    
    return f"Screenshot taken and saved to your Desktop Abhishek."

def get_system_info():
    """Get basic system info"""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_used = round(ram.used / (1024**3), 1)
    ram_total = round(ram.total / (1024**3), 1)
    return f"CPU is at {cpu}% usage. RAM is {ram_used}GB used out of {ram_total}GB Abhishek."

def lock_pc():
    """Lock the PC"""
    subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
    return "Locking your PC Abhishek."

def shutdown_pc():
    """Shutdown the PC"""
    subprocess.run("shutdown /s /t 10", shell=True)
    return "Shutting down your PC in 10 seconds Abhishek."

def restart_pc():
    """Restart the PC"""
    subprocess.run("shutdown /r /t 10", shell=True)
    return "Restarting your PC in 10 seconds Abhishek."

def cancel_shutdown():
    """Cancel shutdown or restart"""
    subprocess.run("shutdown /a", shell=True)
    return "Shutdown cancelled Abhishek."
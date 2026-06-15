import platform
import subprocess


class WindowMonitor:
    def active_window_title(self) -> str:
        system = platform.system().lower()
        if system == "windows":
            return self._windows_active_window()
        return self._linux_active_window() or self._windows_active_window_from_wsl()

    def _windows_active_window(self) -> str:
        script = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
  [DllImport("user32.dll")]
  public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")]
  public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@
$builder = New-Object System.Text.StringBuilder 1024
$handle = [Win32]::GetForegroundWindow()
[void][Win32]::GetWindowText($handle, $builder, $builder.Capacity)
$builder.ToString()
"""
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _windows_active_window_from_wsl(self) -> str:
        return self._windows_active_window()

    def _linux_active_window(self) -> str:
        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return ""

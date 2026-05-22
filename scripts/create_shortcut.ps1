# Create desktop shortcut - icon stays fixed (local ICO + optional DesktopPet.exe)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$iconSrc = Join-Path $root "assets\app_icon.ico"
$pyw = Join-Path $root ".venv\Scripts\pythonw.exe"
$main = Join-Path $root "main.py"
$exe = Join-Path $root "DesktopPet.exe"

if (-not (Test-Path $iconSrc)) {
    & (Join-Path $root ".venv\Scripts\python.exe") (Join-Path $root "scripts\build_app_icon.py")
}

if (-not (Test-Path $pyw)) {
    Write-Host "Run setup_env.bat first."
    exit 1
}

# Icon on local disk (OneDrive paths often revert to wrong icon)
$iconDir = Join-Path $env:LOCALAPPDATA "DesktopPet"
New-Item -ItemType Directory -Force -Path $iconDir | Out-Null
$icon = Join-Path $iconDir "app_icon.ico"
Copy-Item -Path $iconSrc -Destination $icon -Force
$icon = (Resolve-Path $icon).Path

$displayName = "Pet"
$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    foreach ($line in Get-Content $envFile -Encoding UTF8) {
        if ($line -match '^\s*CHARACTER_PACK\s*=\s*(.+)\s*$') {
            $displayName = $matches[1].Trim()
            break
        }
    }
}

$desktop = [Environment]::GetFolderPath("Desktop")
$lnk = Join-Path $desktop "DesktopPet.lnk"
$lnkLocal = Join-Path $root "DesktopPet.lnk"

function New-PetShortcut([string]$path) {
    $wsh = New-Object -ComObject WScript.Shell
    $sc = $wsh.CreateShortcut($path)
    if (Test-Path $exe) {
        $sc.TargetPath = $exe
        $sc.Arguments = ""
    } else {
        $sc.TargetPath = $pyw
        $sc.Arguments = "`"$main`""
    }
    $sc.WorkingDirectory = $root
    $sc.WindowStyle = 7
    $sc.Description = "AI Desktop Pet"
    $sc.IconLocation = "$icon,0"
    $sc.Save()
}

New-PetShortcut $lnk
New-PetShortcut $lnkLocal

# Refresh shell icon cache
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class IconCache {
  [DllImport("shell32.dll")]
  public static extern void SHChangeNotify(int e, int f, IntPtr i1, IntPtr i2);
}
"@
[IconCache]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null

Write-Host ""
Write-Host "OK"
Write-Host "  Desktop: $lnk"
Write-Host "  Project: $lnkLocal"
Write-Host "  Icon:    $icon"
if (Test-Path $exe) {
    Write-Host "  Launcher: $exe (best - icon built-in)"
} else {
    Write-Host ""
    Write-Host "Tip: run build_launcher.bat once for stable icon (DesktopPet.exe)"
}
Write-Host ""
Write-Host "Delete old shortcuts: run.vbs, StartDesktopPet.lnk"

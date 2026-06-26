$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppName = "PM Performance Manager"
$ExeName = "PMPerformanceManager"
$OutputDir = Join-Path $ProjectDir "dist"

Write-Host "=== Building $AppName Installer ===" -ForegroundColor Cyan

if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host "Cleaning old builds..." -ForegroundColor Yellow
Remove-Item -Path (Join-Path $ProjectDir "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $ProjectDir "*.spec") -Force -ErrorAction SilentlyContinue

Write-Host "Building executable..." -ForegroundColor Cyan
$iconPath = Join-Path $ProjectDir "assets\icon.ico"
$iconArg = ""
if (Test-Path $iconPath) {
    $iconArg = "--icon=`"$iconPath`""
}

pyinstaller --onefile --windowed `
    --name "$ExeName" `
    $iconArg `
    --add-data "app;app" `
    --hidden-import "customtkinter" `
    --hidden-import "psutil" `
    --hidden-import "wmi" `
    --hidden-import "win32api" `
    --hidden-import "win32com" `
    --hidden-import "GPUtil" `
    --hidden-import "PIL" `
    --hidden-import "PIL._tkinter_finder" `
    --hidden-import "requests" `
    --hidden-import "packaging" `
    --hidden-import "schedule" `
    --uac-admin `
    --clean `
    --noconfirm `
    --distpath "$OutputDir" `
    (Join-Path $ProjectDir "main.py")

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Output: $OutputDir\$ExeName.exe" -ForegroundColor Green
    Write-Host "`nCreating launcher script..." -ForegroundColor Cyan

    $launcherPath = Join-Path $ProjectDir "run.bat"
@"
@echo off
title PM Performance Manager
echo Starting PM Performance Manager...
echo.
echo NOTE: This application requires administrator privileges.
echo If prompted, click Yes to allow.
echo.
"%~dp0dist\$ExeName.exe"
pause
"@ | Set-Content -Path $launcherPath

    Write-Host "Launcher: $launcherPath" -ForegroundColor Green
    Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

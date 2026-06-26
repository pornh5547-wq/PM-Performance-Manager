$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppName = "PM Performance Manager"
$ExeName = "PMPerformanceManager"
$OutputDir = Join-Path $ProjectDir "dist"

Write-Host "=== Building $AppName Standalone Executable ===" -ForegroundColor Cyan

if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    & "C:\Program Files\Python312\python.exe" -m pip install pyinstaller
}

Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path (Join-Path $ProjectDir "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $ProjectDir "dist") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $ProjectDir "*.spec") -Force -ErrorAction SilentlyContinue

Write-Host "Creating executable (this takes a minute)..." -ForegroundColor Cyan

& "C:\Program Files\Python312\python.exe" -m PyInstaller `
    --onefile `
    --windowed `
    --name "$ExeName" `
    --add-data "app;app" `
    --hidden-import "customtkinter" `
    --hidden-import "psutil" `
    --hidden-import "wmi" `
    --hidden-import "win32api" `
    --hidden-import "win32com" `
    --hidden-import "win32com.client" `
    --hidden-import "win32com.shell" `
    --hidden-import "GPUtil" `
    --hidden-import "PIL" `
    --hidden-import "PIL._tkinter_finder" `
    --hidden-import "requests" `
    --hidden-import "packaging" `
    --hidden-import "schedule" `
    --hidden-import "ctypes" `
    --hidden-import "json" `
    --hidden-import "threading" `
    --hidden-import "datetime" `
    --hidden-import "math" `
    --hidden-import "platform" `
    --hidden-import "re" `
    --hidden-import "shutil" `
    --hidden-import "glob" `
    --hidden-import "tempfile" `
    --hidden-import "time" `
    --hidden-import "subprocess" `
    --collect-data "customtkinter" `
    --collect-data "PIL" `
    --uac-admin `
    --clean `
    --noconfirm `
    --distpath "$OutputDir" `
    "$ProjectDir\main.py"

if ($LASTEXITCODE -eq 0) {
    $exePath = Join-Path $OutputDir "$ExeName.exe"
    $size = (Get-Item $exePath).Length / 1MB

    Write-Host ""
    Write-Host "=== BUILD SUCCESSFUL ===" -ForegroundColor Green
    Write-Host "Output: $exePath" -ForegroundColor Green
    Write-Host "Size:   $("{0:N1}" -f $size) MB" -ForegroundColor Green
    Write-Host ""
    Write-Host "Users can download and run this single .exe file." -ForegroundColor Cyan
    Write-Host "It includes everything - no Python or dependencies needed." -ForegroundColor Cyan
    Write-Host "Windows may show a SmartScreen warning initially (normal for new apps)." -ForegroundColor Yellow
} else {
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    exit 1
}

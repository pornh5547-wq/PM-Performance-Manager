import json
from app.utils._pwsh import run, run_admin

BLOATWARE_LIST = [
    "Microsoft.3DBuilder", "Microsoft.BingWeather", "Microsoft.BingNews",
    "Microsoft.BingSports", "Microsoft.BingFinance", "Microsoft.GetHelp",
    "Microsoft.Getstarted", "Microsoft.Messaging", "Microsoft.Microsoft3DViewer",
    "Microsoft.MicrosoftOfficeHub", "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.MixedReality.Portal", "Microsoft.Office.OneNote",
    "Microsoft.OneConnect", "Microsoft.People", "Microsoft.Print3D",
    "Microsoft.SkypeApp", "Microsoft.Wallet", "Microsoft.WindowsAlarms",
    "Microsoft.WindowsCamera", "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps", "Microsoft.WindowsSoundRecorder",
    "Microsoft.XboxApp", "Microsoft.XboxGameCallableUI", "Microsoft.XboxGamingOverlay",
    "Microsoft.XboxIdentityProvider", "Microsoft.XboxSpeechToTextOverlay",
    "Microsoft.Xbox.TCUI", "Microsoft.YourPhone", "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo", "Microsoft.Advertising.Xaml",
    "Microsoft.MSPaint", "Microsoft.Todos", "Microsoft.PowerAutomateDesktop",
    "Microsoft.Windows.DevHome", "Microsoft.Whiteboard",
    "SpotifyAB.SpotifyMusic", "Disney.37853FC22B2CE", "Facebook.Facebook",
    "Instagram.Instagram", "TikTok.TikTok", "Netflix.Netflix",
]

def list_installed_bloatware():
    cmd = 'Get-AppxPackage | Select-Object Name, PackageFullName, InstallLocation | ConvertTo-Json'
    result = run(cmd)
    installed = []
    if result and result.stdout.strip():
        try:
            packages = json.loads(result.stdout)
            if isinstance(packages, dict):
                packages = [packages]
            for pkg in packages:
                name = pkg.get("Name", "")
                if name in BLOATWARE_LIST:
                    installed.append(pkg)
        except:
            pass
    return installed

def uninstall_package(full_name):
    r = run_admin(f'Get-AppxPackage "{full_name}" | Remove-AppxPackage')
    return r is not None and r.returncode == 0

def uninstall_all():
    results = []
    for pkg in list_installed_bloatware():
        name = pkg.get("Name", "Unknown")
        ok = uninstall_package(pkg.get("PackageFullName", ""))
        results.append({"name": name, "success": ok})
    return results

def reinstall_package(name):
    cmd = f'Get-AppxPackage -AllUsers | Where-Object {{$_.Name -eq "{name}"}} | Format-List PackageFullName'
    result = run(cmd)
    if result and result.stdout.strip():
        full_name = result.stdout.strip().split('\n')[0].split(':')[-1].strip()
        if full_name:
            r = run_admin(f'Add-AppxPackage -Register "$(Get-AppxPackage -AllUsers | Where-Object {{$_.Name -eq "{name}"}} | Select-Object -ExpandProperty InstallLocation)\\AppxManifest.xml" -DisableDevelopmentMode')
            return r is not None and r.returncode == 0
    return False

import platform
import subprocess
import json
import os

class SystemInfo:
    def get_all(self):
        return {
            "os": self.get_os_info(),
            "cpu": self.get_cpu_info(),
            "ram": self.get_ram_info(),
            "gpu": self.get_gpu_info(),
            "motherboard": self.get_motherboard_info(),
            "drives": self.get_drives_info(),
            "network": self.get_network_info(),
            "battery": self.get_battery_info(),
        }

    def get_os_info(self):
        uname = platform.uname()
        return {
            "name": f"{uname.system} {uname.release}",
            "version": uname.version,
            "build": uname.version.split('.')[-1] if '.' in uname.version else uname.version,
            "architecture": uname.machine,
            "install_date": self._get_wmi("Win32_OperatingSystem", "InstallDate"),
            "last_boot": self._get_wmi("Win32_OperatingSystem", "LastBootUpTime"),
            "username": os.environ.get("USERNAME", ""),
            "computername": uname.node,
        }

    def get_cpu_info(self):
        info = {}
        try:
            import wmi
            c = wmi.WMI()
            for cpu in c.Win32_Processor():
                info = {
                    "name": cpu.Name.strip() if cpu.Name else "Unknown",
                    "cores": cpu.NumberOfCores,
                    "logical_cores": cpu.NumberOfLogicalProcessors,
                    "max_clock": f"{float(cpu.MaxClockSpeed) / 1000:.2f} GHz" if cpu.MaxClockSpeed else "Unknown",
                    "l2_cache": f"{cpu.L2CacheSize} KB" if cpu.L2CacheSize else "Unknown",
                    "l3_cache": f"{cpu.L3CacheSize} KB" if cpu.L3CacheSize else "Unknown",
                    "architecture": cpu.Architecture,
                    "socket": cpu.SocketDesignation if hasattr(cpu, 'SocketDesignation') else "Unknown",
                }
        except:
            import psutil
            info = {
                "name": platform.processor() or "Unknown",
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_clock": f"{psutil.cpu_freq().max / 1000:.2f} GHz" if psutil.cpu_freq() else "Unknown",
            }
        return info

    def get_ram_info(self):
        modules = []
        total = 0
        try:
            import wmi
            c = wmi.WMI()
            for mem in c.Win32_PhysicalMemory():
                cap = int(mem.Capacity) if mem.Capacity else 0
                total += cap
                modules.append({
                    "capacity": self._format_bytes(cap),
                    "speed": f"{mem.Speed} MHz" if mem.Speed else "Unknown",
                    "type": self._get_ram_type(mem.SMBIOSMemoryType) if hasattr(mem, 'SMBIOSMemoryType') else "Unknown",
                    "manufacturer": mem.Manufacturer or "Unknown",
                    "part_number": mem.PartNumber.strip() if mem.PartNumber else "",
                })
        except:
            import psutil
            total = psutil.virtual_memory().total
        return {
            "total": self._format_bytes(total),
            "total_bytes": total,
            "modules": modules,
            "module_count": len(modules),
        }

    def get_gpu_info(self):
        gpus = []
        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                gpus.append({
                    "name": gpu.Name.strip() if gpu.Name else "Unknown",
                    "vram": self._format_bytes(int(gpu.AdapterRAM)) if gpu.AdapterRAM else "Unknown",
                    "driver": gpu.DriverVersion if hasattr(gpu, 'DriverVersion') else "Unknown",
                    "resolution": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if hasattr(gpu, 'CurrentHorizontalResolution') and gpu.CurrentHorizontalResolution else "Unknown",
                })
        except:
            pass
        return gpus

    def get_motherboard_info(self):
        try:
            import wmi
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                return {
                    "manufacturer": board.Manufacturer,
                    "product": board.Product,
                    "version": board.Version if hasattr(board, 'Version') else "Unknown",
                    "serial": board.SerialNumber if hasattr(board, 'SerialNumber') else "Unknown",
                }
        except:
            return {"manufacturer": "Unknown", "product": "Unknown"}

    def get_drives_info(self):
        drives = []
        try:
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                drives.append({
                    "model": disk.Model.strip() if disk.Model else "Unknown",
                    "size": self._format_bytes(int(disk.Size)) if disk.Size else "Unknown",
                    "interface": disk.InterfaceType if hasattr(disk, 'InterfaceType') else "Unknown",
                    "media_type": disk.MediaType if hasattr(disk, 'MediaType') else "Unknown",
                    "partitions": disk.Partitions if hasattr(disk, 'Partitions') else 0,
                })
        except:
            import psutil
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    drives.append({
                        "model": part.device,
                        "size": self._format_bytes(usage.total),
                        "mountpoint": part.mountpoint,
                    })
                except:
                    pass
        return drives

    def get_network_info(self):
        adapters = []
        try:
            import wmi
            c = wmi.WMI()
            for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                adapters.append({
                    "name": nic.Description if hasattr(nic, 'Description') else "Unknown",
                    "ip": nic.IPAddress[0] if hasattr(nic, 'IPAddress') and nic.IPAddress else "Unknown",
                    "mac": nic.MACAddress if hasattr(nic, 'MACAddress') else "Unknown",
                    "dhcp": nic.DHCPEnabled if hasattr(nic, 'DHCPEnabled') else False,
                })
        except:
            pass
        return adapters

    def get_battery_info(self):
        try:
            import wmi
            c = wmi.WMI()
            for battery in c.Win32_Battery():
                return {
                    "name": battery.Name.strip() if battery.Name else "Unknown",
                    "status": battery.BatteryStatus,
                    "charge": f"{battery.EstimatedChargeRemaining}%" if hasattr(battery, 'EstimatedChargeRemaining') else "Unknown",
                    "runtime": battery.EstimatedRunTime if hasattr(battery, 'EstimatedRunTime') else "Unknown",
                }
        except:
            return {}

    def _get_wmi(self, cls, prop):
        try:
            import wmi
            c = wmi.WMI()
            for item in c.Win32_OperatingSystem():
                return getattr(item, prop, "Unknown")
        except:
            return "Unknown"

    def _format_bytes(self, b):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def _get_ram_type(self, smbios_type):
        types = {20: "DDR", 21: "DDR2", 24: "DDR3", 26: "DDR4", 34: "DDR5", 0: "Unknown"}
        return types.get(smbios_type, f"Type {smbios_type}")

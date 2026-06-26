import psutil
import os
import subprocess
import re
import platform
import time

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

class SystemMonitor:
    def __init__(self):
        self._gpu_cache = None
        self._gpu_cache_time = 0
        self._gpu_cache_ttl = 10

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=0)

    def get_cpu_temperature(self):
        try:
            import wmi
            c = wmi.WMI()
            for sensor in c.Win32_TemperatureProbe():
                if sensor.CurrentReading is not None:
                    return sensor.CurrentReading / 10.0
        except:
            pass
        return None

    def get_cpu_info(self):
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        }

    def get_ram_usage(self):
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        }

    def get_ram_info(self):
        try:
            import wmi
            c = wmi.WMI()
            return [{
                "capacity": int(m.Capacity) if m.Capacity else 0,
                "speed": m.Speed,
                "manufacturer": m.Manufacturer,
            } for m in c.Win32_PhysicalMemory()]
        except:
            return []

    def get_disk_usage(self):
        disks = []
        for part in psutil.disk_partitions():
            if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
            except:
                pass
        return disks

    def get_disk_io(self):
        io = psutil.disk_io_counters()
        if io:
            return {
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes,
                "read_count": io.read_count,
                "write_count": io.write_count,
            }
        return {}

    def get_smart_status(self):
        try:
            import wmi
            c = wmi.WMI()
            return [{
                "model": d.Model if hasattr(d, 'Model') else "Unknown",
                "size_gb": round(int(d.Size) / (1024**3), 1) if d.Size else 0,
                "status": d.Status if hasattr(d, 'Status') else "Unknown",
                "interface": d.InterfaceType if hasattr(d, 'InterfaceType') else "Unknown",
            } for d in c.Win32_DiskDrive()]
        except:
            return []

    def get_gpu_usage(self):
        now = time.time()
        if self._gpu_cache and (now - self._gpu_cache_time) < self._gpu_cache_ttl:
            return self._gpu_cache

        gpus = []
        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                vram = int(gpu.AdapterRAM) if gpu.AdapterRAM else 0
                gpus.append({
                    "name": gpu.Name.strip() if gpu.Name else "Unknown",
                    "load": 0,
                    "memory_used": 0,
                    "memory_total": vram / (1024**3),
                    "memory_percent": 0,
                    "temperature": 0,
                })
        except:
            pass

        if not gpus:
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu', '--format=csv,noheader,nounits'],
                    capture_output=True, text=True, timeout=5,
                    startupinfo=SI, creationflags=NO_WINDOW
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 5:
                            gpus.append({
                                "name": parts[0],
                                "load": float(parts[1]),
                                "memory_used": float(parts[2]),
                                "memory_total": float(parts[3]),
                                "memory_percent": (float(parts[2]) / float(parts[3]) * 100) if float(parts[3]) > 0 else 0,
                                "temperature": float(parts[4]),
                            })
            except:
                pass

        self._gpu_cache = gpus if gpus else gpus
        self._gpu_cache_time = now
        return gpus

    def clear_gpu_cache(self):
        self._gpu_cache = None

    def get_network_stats(self):
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }

    def get_system_info(self):
        uname = platform.uname()
        import datetime
        return {
            "system": uname.system,
            "node_name": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor,
            "boot_time": psutil.boot_time(),
        }

    def get_process_list(self, sort_by='cpu'):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except:
                pass
        if sort_by == 'cpu':
            processes.sort(key=lambda p: p.get('cpu_percent', 0) or 0, reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda p: p.get('memory_percent', 0) or 0, reverse=True)
        return processes[:50]

    def get_top_processes(self, count=5):
        return self.get_process_list()[:count]

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_directory(path, min_size_mb=100, callback=None):
    results = []
    total = 0
    scanned = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for fname in filenames:
                try:
                    fp = os.path.join(dirpath, fname)
                    try:
                        size = os.path.getsize(fp)
                    except:
                        continue
                    if size >= min_size_mb * 1024 * 1024:
                        results.append({
                            "path": fp,
                            "size": size,
                            "name": fname,
                            "dir": dirpath,
                        })
                    scanned += 1
                    if callback and scanned % 50 == 0:
                        callback(scanned, len(results))
                except:
                    pass
    except:
        pass
    results.sort(key=lambda x: x["size"], reverse=True)
    return results

def scan_multiple(paths, min_size_mb=100, callback=None):
    all_results = []
    total_scanned = [0]
    lock = threading.Lock()

    def scan_single(path):
        results = scan_directory(path, min_size_mb, None)
        with lock:
            total_scanned[0] += 1
            if callback:
                callback(total_scanned[0], len(all_results) + len(results))
        return results

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(scan_single, p): p for p in paths}
        for future in as_completed(futures):
            try:
                all_results.extend(future.result())
            except:
                pass

    all_results.sort(key=lambda x: x["size"], reverse=True)
    return all_results

COMMON_SCAN_PATHS = [
    os.environ.get('USERPROFILE', 'C:\\Users\\Default'),
    os.environ.get('LOCALAPPDATA', ''),
    os.environ.get('TEMP', ''),
]

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"

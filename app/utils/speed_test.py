import subprocess
import time
import urllib.request
import urllib.error
import re
from app.config import log

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

TEST_FILE_URL = "http://speedtest.tele2.net/100MB.zip"
TEST_FILE_SIZE = 100 * 1024 * 1024

def test_download_speed():
    try:
        start = time.time()
        req = urllib.request.Request(TEST_FILE_URL)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(req, timeout=30)
        chunk_size = 8192
        total_read = 0
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            total_read += len(chunk)
        elapsed = time.time() - start
        speed_bps = (total_read * 8) / elapsed
        speed_mbps = speed_bps / (1024 * 1024)
        return {"download_mbps": round(speed_mbps, 2), "total_bytes": total_read, "elapsed_sec": round(elapsed, 2)}
    except Exception as e:
        return {"error": str(e)}

def test_latency():
    hosts = ["8.8.8.8", "1.1.1.1", "google.com"]
    results = []
    for host in hosts:
        try:
            start = time.time()
            subprocess.run(['ping', '-n', '1', host],
                          capture_output=True, timeout=10,
                          startupinfo=SI, creationflags=NO_WINDOW)
            elapsed = (time.time() - start) * 1000
            results.append({"host": host, "latency_ms": round(elapsed, 1)})
        except:
            results.append({"host": host, "latency_ms": None})
    return results

def test_speed_full():
    latency = test_latency()
    download = test_download_speed()
    return {"latency": latency, "download": download}

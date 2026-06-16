import json
import os
import ssl
import urllib.request
from version import VERSION

GITHUB_API = "https://api.github.com/repos/ZtaMDev/EasyHotCorners/releases/latest"
DOWNLOAD_BASE = "https://github.com/ZtaMDev/EasyHotCorners/releases/download/v{version}/EasyHotCorners_v{version}.exe"


def parse_version(v):
    return tuple(int(x) for x in str(v).lstrip("v").split("."))


def is_newer(latest, current):
    return parse_version(latest) > parse_version(current)


def get_download_url(version):
    return DOWNLOAD_BASE.format(version=version)


def get_latest_version():
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "EasyHotCorners"})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            tag = data.get("tag_name", "")
            return tag.lstrip("v")
    except Exception:
        return None


def check_update():
    latest = get_latest_version()
    if latest is None:
        return None
    if is_newer(latest, VERSION):
        return {"latest": latest, "download_url": get_download_url(latest)}
    return {}


def download_update(url, dest, progress_callback):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "EasyHotCorners"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 8192
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    progress_callback(downloaded, total)
    return dest

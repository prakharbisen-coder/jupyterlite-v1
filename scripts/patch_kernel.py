"""Patch the Pyodide kernel worker JS to auto-install piplite packages on startup."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE_DIR = ROOT / "_site"

AUTO_INSTALL_PACKAGES = ["openpyxl", "et-xmlfile"]


def get_worker_js():
    """Find the compiled worker JS file with initKernel."""
    static_dir = SITE_DIR / "extensions" / "@jupyterlite" / "pyodide-kernel-extension" / "static"
    candidates = []
    for js_file in static_dir.glob("*.js"):
        content = js_file.read_text(encoding="utf-8")
        if "initKernel" in content and "import pyodide_kernel" in content:
            candidates.append(js_file)
    candidates.sort(key=lambda x: x.stat().st_size, reverse=True)
    if candidates:
        return candidates[0]
    return None


def patch():
    js_file = get_worker_js()
    if js_file is None:
        print("[patch-kernel] Could not find worker JS file")
        return False

    patched_any = False

    # Search through JS files in the static dir
    static_dir = js_file.parent
    for f in static_dir.glob("*.js"):
        c = f.read_text(encoding="utf-8")
        match = re.search(r'(\w+)\.push\("import pyodide_kernel"\)', c)
        if not match:
            continue

        # Check if already patched
        if "openpyxl" in c:
            print(f"[patch-kernel] {f.name}: already patched")
            continue

        patched_any = True
        var_name = match.group(1)
        target = var_name + '.push("import pyodide_kernel")'

        # Add piplite.install calls for each package BEFORE "import pyodide_kernel"
        # Uses the exact same pattern as the existing kernel package installs
        install_calls = ""
        for pkg in AUTO_INSTALL_PACKAGES:
            install_calls += var_name + '.push("await piplite.install(\'' + pkg + '\', keep_going=True)");'

        replacement = install_calls + target

        c = c.replace(target, replacement)
        f.write_text(c, encoding="utf-8")
        print(f"[patch-kernel] Patched {f.name} (var={var_name}) - auto-install: {AUTO_INSTALL_PACKAGES}")

    return patched_any


if __name__ == "__main__":
    patch()

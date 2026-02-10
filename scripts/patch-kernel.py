#!/usr/bin/env python
"""Patch the Pyodide kernel worker JS to auto-install piplite packages on startup."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE_DIR = ROOT / "_site"
EXAMPLES_DIR = ROOT / "examples"

# Packages to auto-install on kernel startup (from requirements-piplite.txt)
# Only include packages users commonly import directly
AUTO_INSTALL_PACKAGES = [
    "openpyxl",
]


def get_worker_js():
    """Find the compiled worker JS file with initKernel."""
    static_dir = (
        SITE_DIR
        / "extensions"
        / "@jupyterlite"
        / "pyodide-kernel-extension"
        / "static"
    )
    # Find all matching files, return the largest one (the main bundle)
    candidates = []
    for js_file in static_dir.glob("*.js"):
        content = js_file.read_text(encoding="utf-8")
        if "initKernel" in content and 'import pyodide_kernel' in content:
            candidates.append((js_file, content))
    if candidates:
        # Sort by size descending - the main bundle is typically the largest
        candidates.sort(key=lambda x: len(x[1]), reverse=True)
        return candidates[0]
    return None, None


def patch():
    js_file, content = get_worker_js()
    if not js_file:
        print("[patch-kernel] Could not find worker JS file")
        return False

    # Patch ALL files that have the initKernel code (multiple chunks may exist)
    static_dir = js_file.parent
    patched_any = False
    for f in static_dir.glob("*.js"):
        c = f.read_text(encoding="utf-8")
        match = re.search(r'(\w+)\.push\("import pyodide_kernel"\)', c)
        if not match:
            continue
        if "openpyxl" in c:
            print(f"[patch-kernel] {f.name}: already patched")
            patched_any = True
            continue

        var_name = match.group(1)
        target = f'{var_name}.push("import pyodide_kernel")'
        replacement_parts = []
        for pkg in AUTO_INSTALL_PACKAGES:
            replacement_parts.append(
                f"""{var_name}.push("await piplite.install('{pkg}', keep_going=True)")"""
            )
        replacement_parts.append(target)
        replacement = ";".join(replacement_parts)

        c = c.replace(target, replacement, 1)
        f.write_text(c, encoding="utf-8")
        print(f"[patch-kernel] Patched {f.name} (var={var_name}) - auto-install: {AUTO_INSTALL_PACKAGES}")
        patched_any = True

    return patched_any


if __name__ == "__main__":
    patch()

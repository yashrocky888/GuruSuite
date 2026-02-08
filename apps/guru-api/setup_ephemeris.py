#!/usr/bin/env python3
"""
Setup Swiss Ephemeris data files.
Downloads ephemeris files if needed or points to system path.
"""

import os
import sys
import urllib.request
import tarfile
import shutil

def setup_ephemeris_path():
    """Setup Swiss Ephemeris data file path."""
    # Create ephe directory if it doesn't exist
    ephe_dir = os.path.abspath("ephe")
    
    if not os.path.exists(ephe_dir):
        os.makedirs(ephe_dir, exist_ok=True)
        print(f"Created ephemeris directory: {ephe_dir}")
    
    # Check if files already exist
    seplm_file = os.path.join(ephe_dir, "seplm48.se1")
    if os.path.exists(seplm_file):
        print(f"✅ Ephemeris files already exist in {ephe_dir}")
        return ephe_dir
    
    # Try to find system paths
    system_paths = [
        "/usr/share/swisseph",
        "/usr/local/share/swisseph",
        os.path.expanduser("~/swisseph/ephe"),
    ]
    
    for path in system_paths:
        if os.path.exists(path):
            seplm_check = os.path.join(path, "seplm48.se1")
            if os.path.exists(seplm_check):
                print(f"✅ Found ephemeris files in system path: {path}")
                return path
    
    # If not found, provide instructions
    print("⚠️  Ephemeris files not found.")
    print(f"   Please download Swiss Ephemeris data files from:")
    print(f"   https://www.astro.com/swisseph/swephinfo_e.htm")
    print(f"   Or install via package manager:")
    print(f"   - macOS: brew install swisseph")
    print(f"   - Linux: apt-get install swisseph-data")
    print(f"   - Or download and extract to: {ephe_dir}")
    print()
    print(f"   Required files: seplm*.se1 (planetary ephemeris)")
    print(f"   Place them in: {ephe_dir}")
    
    return ephe_dir

if __name__ == "__main__":
    path = setup_ephemeris_path()
    print(f"\nEphemeris path: {path}")
    print("\nTo use this path in Python:")
    print(f"  import swisseph as swe")
    print(f"  swe.set_ephe_path('{path}')")

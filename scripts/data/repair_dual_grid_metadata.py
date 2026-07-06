#!/usr/bin/env python3

from pathlib import Path
import pandas as pd

ROOT = Path("/root/autodl-tmp/trellis_character_data/trellis_dataset")
RESOLUTION = 256

metadata_path = ROOT / "metadata.csv"
backup_path = ROOT / "metadata.before_dual_grid_repair.csv"
dual_grid_dir = ROOT / f"dual_grid_{RESOLUTION}"

if not metadata_path.exists():
    raise FileNotFoundError(f"metadata.csv not found: {metadata_path}")

if not dual_grid_dir.exists():
    raise FileNotFoundError(f"dual grid directory not found: {dual_grid_dir}")

df = pd.read_csv(metadata_path)

if "sha256" not in df.columns:
    raise KeyError("metadata.csv must contain sha256 column")

df.to_csv(backup_path, index=False)

converted = []

for sha256 in df["sha256"].astype(str):
    vfile = dual_grid_dir / f"{sha256}.vxz"
    converted.append(vfile.exists())

df["dual_grid_converted"] = converted

df.to_csv(metadata_path, index=False)

print("========================================")
print("metadata.csv repaired")
print("========================================")
print(f"metadata: {metadata_path}")
print(f"backup:   {backup_path}")
print(f"dual dir: {dual_grid_dir}")
print("")
print(df["dual_grid_converted"].value_counts(dropna=False))

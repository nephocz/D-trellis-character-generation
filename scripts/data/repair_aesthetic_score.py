#!/usr/bin/env python3

from pathlib import Path
import pandas as pd

ROOT = Path("/root/autodl-tmp/trellis_character_data/trellis_dataset")

paths = [
    ROOT / "metadata.csv",
    ROOT / "renders_cond" / "metadata.csv",
    ROOT / "shape_latents" / "shape_enc_next_dc_f16c32_fp16_256" / "metadata.csv",
]

DEFAULT_SCORE = 5.0

for path in paths:
    print("=" * 80)
    print(path)

    if not path.exists():
        print("missing, skipped")
        continue

    backup = path.with_name(path.stem + ".before_aesthetic_score.csv")
    df = pd.read_csv(path)

    if not backup.exists():
        df.to_csv(backup, index=False)
        print("backup:", backup)

    if "aesthetic_score" not in df.columns:
        df["aesthetic_score"] = DEFAULT_SCORE
        print("added aesthetic_score")
    else:
        df["aesthetic_score"] = df["aesthetic_score"].fillna(DEFAULT_SCORE)
        print("filled missing aesthetic_score")

    df.to_csv(path, index=False)

    print("shape:", df.shape)
    print("columns:", df.columns.tolist())
    print(df["aesthetic_score"].value_counts(dropna=False).head())

#!/usr/bin/env python3

from pathlib import Path
import argparse
import csv
import hashlib
import shutil


def compute_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def find_glb_files(glb_dir: Path) -> list[Path]:
    if not glb_dir.exists():
        raise FileNotFoundError(f"GLB directory not found: {glb_dir}")

    glb_files = sorted(glb_dir.glob("*.glb"))

    if not glb_files:
        raise RuntimeError(f"No .glb files found in: {glb_dir}")

    return glb_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build minimal TRELLIS.2 metadata.csv for custom GLB assets."
    )

    parser.add_argument(
        "--glb_dir",
        type=str,
        default="/root/autodl-tmp/trellis_character_data/processed/glb",
    )

    parser.add_argument(
        "--root",
        type=str,
        default="/root/autodl-tmp/trellis_character_data/trellis_dataset",
    )

    parser.add_argument(
        "--copy_to_dataset",
        action="store_true",
        help="Copy GLB files into <root>/raw_assets and point metadata local_path to copied files.",
    )

    parser.add_argument(
        "--expected_count",
        type=int,
        default=50,
    )

    args = parser.parse_args()

    glb_dir = Path(args.glb_dir)
    root = Path(args.root)
    metadata_path = root / "metadata.csv"
    raw_assets_dir = root / "raw_assets"

    root.mkdir(parents=True, exist_ok=True)

    glb_files = find_glb_files(glb_dir)

    if len(glb_files) != args.expected_count:
        print(f"[WARN] Found {len(glb_files)} GLB files, expected {args.expected_count}.")

    rows = []
    seen_sha256 = set()

    if args.copy_to_dataset:
        raw_assets_dir.mkdir(parents=True, exist_ok=True)

    for glb_path in glb_files:
        sha256 = compute_sha256(glb_path)

        if sha256 in seen_sha256:
            print(f"[WARN] Duplicate sha256 detected: {glb_path}")

        seen_sha256.add(sha256)

        if args.copy_to_dataset:
            target_path = raw_assets_dir / f"{sha256}.glb"
            if not target_path.exists():
                shutil.copy2(glb_path, target_path)
            local_path = target_path
        else:
            local_path = glb_path

        rows.append({
            "sha256": sha256,
            "local_path": str(local_path.resolve()),
        })

    with metadata_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sha256", "local_path"])
        writer.writeheader()
        writer.writerows(rows)

    print("========================================")
    print("metadata.csv generated")
    print("========================================")
    print(f"Dataset root: {root}")
    print(f"Metadata path: {metadata_path}")
    print(f"Total assets: {len(rows)}")
    print("")
    print("Preview:")
    print("sha256,local_path")

    for row in rows[:5]:
        print(f"{row['sha256']},{row['local_path']}")


if __name__ == "__main__":
    main()
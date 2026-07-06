from pathlib import Path
import csv
import hashlib

GLB_DIR = Path("/root/autodl-tmp/trellis_character_data/processed/glb")

PROJECT_METADATA_DIR = Path("data/metadata")
TRELLIS_DATASET_DIR = Path("/root/autodl-tmp/trellis_character_data/trellis_dataset")

PROJECT_METADATA_DIR.mkdir(parents=True, exist_ok=True)
TRELLIS_DATASET_DIR.mkdir(parents=True, exist_ok=True)

asset_index_path = PROJECT_METADATA_DIR / "asset_index.csv"
license_path = PROJECT_METADATA_DIR / "license_registry.csv"
train_split_path = PROJECT_METADATA_DIR / "train_split.csv"
val_split_path = PROJECT_METADATA_DIR / "val_split.csv"
trellis_metadata_example_path = PROJECT_METADATA_DIR / "trellis_metadata_example.csv"

trellis_metadata_path = TRELLIS_DATASET_DIR / "metadata.csv"

EXPECTED_COUNT = 50
VAL_COUNT_FOR_50 = 5

AUTHOR = "Nepho"
CATEGORY = "human"
BODY_TYPE = "anime_character"
STYLE = "anime"
SURFACE = "smooth"
SOURCE_TYPE = "self_generated"
LICENSE = "self_owned"


def compute_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_split(index: int, total: int) -> str:
    if total == EXPECTED_COUNT:
        train_count = total - VAL_COUNT_FOR_50
    else:
        val_count = max(1, round(total * 0.1)) if total >= 2 else 0
        train_count = total - val_count

    return "train" if index <= train_count else "val"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def main() -> None:
    glb_files = sorted(GLB_DIR.glob("*.glb"))

    if len(glb_files) == 0:
        raise RuntimeError(f"No .glb files found in {GLB_DIR}")

    if len(glb_files) < EXPECTED_COUNT:
        print(f"[WARN] Found only {len(glb_files)} GLB files, expected {EXPECTED_COUNT}.")
    elif len(glb_files) > EXPECTED_COUNT:
        print(f"[WARN] Found {len(glb_files)} GLB files, expected {EXPECTED_COUNT}.")

    rows = []

    for index, glb_path in enumerate(glb_files, start=1):
        asset_id = glb_path.stem
        split = get_split(index=index, total=len(glb_files))

        file_size_bytes = glb_path.stat().st_size
        sha256 = compute_sha256(glb_path)

        rows.append({
            "id": asset_id,
            "glb_path": str(glb_path),
            "local_path": str(glb_path),
            "sha256": sha256,
            "file_size_bytes": file_size_bytes,
            "original_format": "glb",
            "category": CATEGORY,
            "body_type": BODY_TYPE,
            "style": STYLE,
            "surface": SURFACE,
            "source_type": SOURCE_TYPE,
            "status": "accepted",
            "quality_note": "good",
            "split": split,
        })

    asset_index_fields = [
        "id",
        "glb_path",
        "sha256",
        "file_size_bytes",
        "original_format",
        "category",
        "body_type",
        "style",
        "surface",
        "source_type",
        "status",
        "quality_note",
    ]

    write_csv(
        path=asset_index_path,
        fieldnames=asset_index_fields,
        rows=rows,
    )

    license_rows = []

    for row in rows:
        license_rows.append({
            "id": row["id"],
            "source": SOURCE_TYPE,
            "model_name": row["id"],
            "author": AUTHOR,
            "license": LICENSE,
            "original_url": "-",
            "download_allowed": "yes",
            "modify_allowed": "yes",
            "commercial_allowed": "yes",
            "redistribution_allowed": "yes",
            "ai_training_allowed": "yes",
            "status": "accepted",
            "note": "original self-made model",
        })

    license_fields = [
        "id",
        "source",
        "model_name",
        "author",
        "license",
        "original_url",
        "download_allowed",
        "modify_allowed",
        "commercial_allowed",
        "redistribution_allowed",
        "ai_training_allowed",
        "status",
        "note",
    ]

    write_csv(
        path=license_path,
        fieldnames=license_fields,
        rows=license_rows,
    )

    split_fields = ["id", "split"]

    train_rows = [
        {"id": row["id"], "split": row["split"]}
        for row in rows
        if row["split"] == "train"
    ]

    val_rows = [
        {"id": row["id"], "split": row["split"]}
        for row in rows
        if row["split"] == "val"
    ]

    write_csv(
        path=train_split_path,
        fieldnames=split_fields,
        rows=train_rows,
    )

    write_csv(
        path=val_split_path,
        fieldnames=split_fields,
        rows=val_rows,
    )

    trellis_rows = []

    for row in rows:
        trellis_rows.append({
            "id": row["id"],
            "sha256": row["sha256"],
            "split": row["split"],
            "local_path": row["local_path"],
            "category": row["category"],
            "style": row["style"],
            "status": row["status"],
        })

    trellis_fields = [
        "id",
        "sha256",
        "split",
        "local_path",
        "category",
        "style",
        "status",
    ]

    write_csv(
        path=trellis_metadata_path,
        fieldnames=trellis_fields,
        rows=trellis_rows,
    )

    write_csv(
        path=trellis_metadata_example_path,
        fieldnames=trellis_fields,
        rows=trellis_rows[: min(5, len(trellis_rows))],
    )

    print("========================================")
    print("Metadata generation finished.")
    print("========================================")
    print(f"Total GLB files: {len(rows)}")
    print(f"Train samples: {len(train_rows)}")
    print(f"Val samples: {len(val_rows)}")
    print("")
    print(f"Generated: {asset_index_path}")
    print(f"Generated: {license_path}")
    print(f"Generated: {train_split_path}")
    print(f"Generated: {val_split_path}")
    print(f"Generated: {trellis_metadata_example_path}")
    print(f"Generated: {trellis_metadata_path}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import argparse
import csv
import os
import shutil
import time
import traceback
from pathlib import Path

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import cv2
import imageio
import torch
import yaml
from PIL import Image

from trellis2.pipelines import Trellis2ImageTo3DPipeline
from trellis2.utils import render_utils
from trellis2.renderers import EnvMap
import o_voxel


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_envmap(path: Path):
    env = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

    if env is None:
        raise FileNotFoundError(f"Cannot read envmap: {path}")

    env = cv2.cvtColor(env, cv2.COLOR_BGR2RGB)

    return EnvMap(
        torch.tensor(
            env,
            dtype=torch.float32,
            device="cuda",
        )
    )


def find_images(input_dir: Path, extensions: list[str]) -> list[Path]:
    exts = {ext.lower() for ext in extensions}

    image_paths = [
        path
        for path in sorted(input_dir.iterdir())
        if path.is_file() and path.suffix.lower() in exts
    ]

    return image_paths


def copy_input_image(image_path: Path, sample_dir: Path) -> Path:
    copied_path = sample_dir / f"input{image_path.suffix.lower()}"
    shutil.copy2(image_path, copied_path)
    return copied_path


def export_preview_video(mesh, envmap, video_path: Path, fps: int) -> None:
    video = render_utils.make_pbr_vis_frames(
        render_utils.render_video(mesh, envmap=envmap)
    )

    imageio.mimsave(str(video_path), video, fps=fps)


def export_glb(mesh, glb_path: Path, mesh_cfg: dict, output_cfg: dict) -> None:
    simplify_faces = mesh_cfg.get("simplify_faces", None)

    if simplify_faces:
        mesh.simplify(simplify_faces)

    glb = o_voxel.postprocess.to_glb(
        vertices=mesh.vertices,
        faces=mesh.faces,
        attr_volume=mesh.attrs,
        coords=mesh.coords,
        attr_layout=mesh.layout,
        voxel_size=mesh.voxel_size,
        aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
        decimation_target=mesh_cfg.get("decimation_target", 1000000),
        texture_size=mesh_cfg.get("texture_size", 4096),
        remesh=mesh_cfg.get("remesh", True),
        remesh_band=mesh_cfg.get("remesh_band", 1),
        remesh_project=mesh_cfg.get("remesh_project", 0),
        verbose=True,
    )

    glb.export(
        str(glb_path),
        extension_webp=output_cfg.get("extension_webp", False),
    )


def write_manifest(manifest_path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "name",
        "input_path",
        "sample_dir",
        "glb_path",
        "video_path",
        "status",
        "error",
        "seconds",
    ]

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_one_image(
    pipeline,
    envmap,
    image_path: Path,
    experiment_output_dir: Path,
    cfg: dict,
) -> dict:
    name = image_path.stem
    sample_dir = experiment_output_dir / name
    sample_dir.mkdir(parents=True, exist_ok=True)

    glb_path = sample_dir / f"{name}.glb"
    video_path = sample_dir / f"{name}.mp4"
    error_path = sample_dir / "error.txt"

    output_cfg = cfg["output"]
    render_cfg = cfg["render"]
    mesh_cfg = cfg["mesh"]

    export_glb_enabled = output_cfg.get("export_glb", True)
    export_video_enabled = output_cfg.get("export_video", True)
    skip_existing = output_cfg.get("skip_existing", True)

    start_time = time.time()

    if skip_existing and export_glb_enabled and glb_path.exists():
        print(f"[SKIP] {name}: GLB already exists.")

        return {
            "name": name,
            "input_path": str(image_path),
            "sample_dir": str(sample_dir),
            "glb_path": str(glb_path),
            "video_path": str(video_path) if video_path.exists() else "",
            "status": "skipped_existing",
            "error": "",
            "seconds": "0.00",
        }

    try:
        print(f"\n========== Processing: {image_path} ==========")

        copy_input_image(image_path, sample_dir)

        image = Image.open(image_path).convert("RGBA")

        mesh = pipeline.run(image)[0]

        if export_video_enabled:
            if envmap is None:
                raise RuntimeError("export_video is true, but envmap is not loaded.")

            print(f"[{name}] Rendering preview video...")
            export_preview_video(
                mesh=mesh,
                envmap=envmap,
                video_path=video_path,
                fps=render_cfg.get("fps", 15),
            )
            print(f"[{name}] Video saved to: {video_path}")

        if export_glb_enabled:
            print(f"[{name}] Exporting GLB...")
            export_glb(
                mesh=mesh,
                glb_path=glb_path,
                mesh_cfg=mesh_cfg,
                output_cfg=output_cfg,
            )
            print(f"[{name}] GLB saved to: {glb_path}")

        seconds = time.time() - start_time

        if error_path.exists():
            error_path.unlink()

        return {
            "name": name,
            "input_path": str(image_path),
            "sample_dir": str(sample_dir),
            "glb_path": str(glb_path) if glb_path.exists() else "",
            "video_path": str(video_path) if video_path.exists() else "",
            "status": "ok",
            "error": "",
            "seconds": f"{seconds:.2f}",
        }

    except Exception as e:
        seconds = time.time() - start_time
        error_text = traceback.format_exc()

        with open(error_path, "w", encoding="utf-8") as f:
            f.write(error_text)

        print(f"[ERROR] Failed to process {image_path}: {e}")

        return {
            "name": name,
            "input_path": str(image_path),
            "sample_dir": str(sample_dir),
            "glb_path": str(glb_path) if glb_path.exists() else "",
            "video_path": str(video_path) if video_path.exists() else "",
            "status": "error",
            "error": repr(e),
            "seconds": f"{seconds:.2f}",
        }

    finally:
        if "mesh" in locals():
            del mesh

        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baseline image-to-3D inference for TRELLIS.2"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="configs/inference/baseline_autodl.yaml",
        help="Path to inference YAML config.",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = load_config(config_path)

    experiment_name = cfg["experiment_name"]

    input_dir = Path(cfg["paths"]["input_dir"])
    base_output_dir = Path(cfg["paths"]["output_dir"])
    experiment_output_dir = base_output_dir / experiment_name

    experiment_output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    image_paths = find_images(
        input_dir=input_dir,
        extensions=cfg["input"]["extensions"],
    )

    if not image_paths:
        raise FileNotFoundError(f"No images found in: {input_dir}")

    export_video_enabled = cfg["output"].get("export_video", True)

    envmap = None
    if export_video_enabled:
        envmap_path = Path(cfg["paths"]["envmap"])
        print(f"[INFO] Loading environment map: {envmap_path}")
        envmap = load_envmap(envmap_path)

    model_name = cfg["model"]["name"]
    device = cfg["model"].get("device", "cuda")

    print(f"[INFO] Loading TRELLIS.2 pipeline: {model_name}")
    pipeline = Trellis2ImageTo3DPipeline.from_pretrained(model_name)

    if device == "cuda":
        pipeline.cuda()
    else:
        raise ValueError(f"Unsupported device: {device}")

    print(f"[INFO] Found {len(image_paths)} image(s).")
    print(f"[INFO] Output directory: {experiment_output_dir}")

    manifest_rows = []
    manifest_path = experiment_output_dir / "manifest.csv"

    for image_path in image_paths:
        row = process_one_image(
            pipeline=pipeline,
            envmap=envmap,
            image_path=image_path,
            experiment_output_dir=experiment_output_dir,
            cfg=cfg,
        )

        manifest_rows.append(row)
        write_manifest(manifest_path, manifest_rows)

    print("\nAll tasks finished.")
    print(f"Manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()
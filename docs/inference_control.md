# 推理实验记录

## Exp001：Baseline 单图推理实验

### 1. 实验目的

本实验用于验证原版 TRELLIS.2 模型在人物风格图片上的基础图生 3D 能力，并搭建一个可以复现的 AutoDL 推理流程。

本阶段重点不是提升生成质量，而是先确认以下流程能够稳定运行：

* 从指定输入目录读取图片
* 调用 TRELLIS.2 进行图生 3D 推理
* 导出 GLB 模型文件
* 渲染 MP4 预览视频
* 记录每个样本的运行状态
* 支持跳过已经生成过的结果

### 2. 实验配置

* 配置文件：`configs/inference/baseline_autodl.yaml`
* 实验名称：`exp001_baseline_single_image`
* 模型：`microsoft/TRELLIS.2-4B`
* 运行设备：CUDA
* 输入目录：`/root/autodl-tmp/input`
* 输出目录：`/root/autodl-tmp/output`
* 环境贴图：`/root/TRELLIS.2/assets/hdri/forest.exr`

### 3. 输入设置

支持的输入图片格式包括：

* `.png`
* `.jpg`
* `.jpeg`
* `.webp`
* `.bmp`

当前推理流程会在程序启动时扫描输入目录，并按文件名顺序逐张处理图片。由于显存限制，当前不进行并发推理，而是采用单张图片顺序生成的方式。

### 4. 输出设置

* 导出 GLB：开启
* 导出 MP4 预览视频：开启
* 已存在结果跳过：开启
* WebP 贴图扩展：关闭

输出结果会按照实验名和样本名组织，例如：

```text
/root/autodl-tmp/output/exp001_baseline_single_image/
├── manifest.csv
├── sample_001/
│   ├── input.png
│   ├── sample_001.glb
│   └── sample_001.mp4
└── sample_002/
    ├── input.png
    ├── sample_002.glb
    └── sample_002.mp4
```

### 5. Mesh 导出参数

本次实验使用较高质量的导出参数：

* `simplify_faces: 16777216`
* `decimation_target: 1000000`
* `texture_size: 4096`
* `remesh: true`
* `remesh_band: 1`
* `remesh_project: 0`

这些参数有利于获得较高质量的模型与贴图，但会增加 GLB 导出阶段的耗时。

### 6. 初步观察

本次实验已经验证以下内容：

* TRELLIS.2 推理流程可以正常调用。
* 输入图片可以被批量顺序处理。
* GLB 模型可以成功导出。
* MP4 预览视频可以成功生成。
* 已经生成过的 `.glb` 文件可以被跳过，便于中断后继续运行。
* GLB 导出阶段中的 `xatlas: Computing charts` 可能耗时较长。




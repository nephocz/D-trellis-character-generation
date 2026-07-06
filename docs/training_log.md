# Training Log

本文档记录 TRELLIS.2 动漫人物生成与训练实验的主要进展和问题。

## 2026-06-18：环境准备

### 完成内容

* 配置 Conda / Python 环境
* 安装 PyTorch、CUDA 相关依赖
* 安装 TRELLIS.2 所需扩展组件

涉及组件：

```text
flash-attn
nvdiffrast
nvdiffrec
cumesh
o-voxel
flexgemm
```

### 遇到的问题

* CUDA / PyTorch 版本匹配复杂
* 部分 CUDA 扩展需要本地编译
* 网络和环境变量容易导致安装失败

### 结果

TRELLIS.2 基础环境基本跑通，可以继续进行推理和数据集准备。

---

## 2026-06-28：Baseline 推理流程整理

### 完成内容

* 编写 baseline 推理配置
* 编写批量推理脚本
* 支持输入图片生成 GLB
* 支持导出预览视频
* 记录 `manifest.csv` 和错误日志

### 结果

原版 TRELLIS.2 推理流程可用，可作为后续人物训练和可控化输出实验的基准。

---

## 2026-07-02：动漫人物数据集构建

### 完成内容

* 整理 50 个 3D 动漫人物资产
* 统一整理为 GLB 格式
* 生成资产索引
* 记录数据来源与许可信息
* 生成 train / val split
* 生成 TRELLIS.2 训练所需 `metadata.csv`

数据集信息：

```text
Dataset: AnimeCharacterSelf50
Assets: 50
Format: GLB
Path: /root/autodl-tmp/trellis_character_data/trellis_dataset
```

数据转换流程：

```text
GLB
→ asset_index.csv
→ license_registry.csv
→ train_split.csv / val_split.csv
→ TRELLIS metadata.csv
→ mesh dump
→ dual grid / voxel 表示
→ TRELLIS.2 训练读取
```

### 结果

数据集构建完成，已经打通从 GLB 资产到 TRELLIS.2 训练数据结构的基本流程。

---

## 2026-07-02：数据预处理接口问题

### 遇到的问题

运行 dual grid 预处理时出现错误：

```text
TypeError: foreach_instance() got an unexpected keyword argument 'no_file'
```

### 原因

`dual_grid.py` 调用的参数和当前 TRELLIS.2 代码中的 `foreach_instance()` 接口不一致。

### 结果

需要修改预处理脚本，使其和当前 TRELLIS.2 代码版本兼容。

---

## 2026-07-02：文件句柄问题

### 遇到的问题

训练或数据加载阶段出现：

```text
Error: [Errno 24] Too many open files
```

### 原因

DataLoader 同时读取文件较多，系统默认文件句柄数量不足。

### 结果

通过降低 `num_workers`、提高 `ulimit` 等方式缓解该问题。

---

## 2026-07-02：小规模人物训练尝试

### 实验配置

```text
Experiment: exp001_self50_character_finetune
Dataset: AnimeCharacterSelf50
Base model: microsoft/TRELLIS.2-4B
Target: shape
Assets: 50
```

训练参数：

```text
batch_size: 1
gradient_accumulation_steps: 4
learning_rate: 1e-5
max_steps: 500
num_workers: 2
precision: bf16
```

### 遇到的问题

训练过程中出现 CUDA 显存不足：

```text
CUDA out of memory
Cuda error: 2[cudaMalloc(&m_gpuPtr, bytes);]
Retrying (3/3)
```

### 结果

训练可以启动，但无法稳定完成 fine-tuning，暂未得到有效 checkpoint。

---

## 2026-07-06：24GB 显存瓶颈确认

### 完成内容

* 复查当前训练配置
* 确认当前 GPU 显存为 24GB
* 评估 24GB 显存是否足够完成 TRELLIS.2-4B 训练

### 遇到的问题

即使已经使用较保守配置，训练仍然受显存限制：

```text
batch_size: 1
gradient_accumulation_steps: 4
precision: bf16
num_workers: 2
```

主要错误仍然集中在 CUDA 显存分配失败：

```text
Cuda error: 2[cudaMalloc(&m_gpuPtr, bytes);]
CUDA out of memory
```

### 原因

TRELLIS.2-4B 模型规模较大，训练时需要保存大量中间激活。3D 生成中的 shape、voxel、sparse structure 等计算进一步增加显存压力。当前 24GB 显存不足以稳定完成完整 fine-tuning。

### 结果

确认当前训练瓶颈是显存不足。当前阶段记录为：

```text
数据集构建完成
训练数据结构完成
训练配置完成
训练启动成功
完整 fine-tuning 受 24GB 显存限制阻塞
暂未得到有效 fine-tuned checkpoint
```

---

## 当前阶段结果

```text
TRELLIS.2 环境基本跑通
baseline 推理流程完成
50 个 3D 动漫人物数据集构建完成
TRELLIS.2 metadata 构建完成
训练配置和启动脚本完成
训练阶段最终卡在 24GB 显存不足
```

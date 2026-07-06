# Dataset

本项目的数据集用于 **TRELLIS.2 的 3D 动漫人物生成、训练适配与可控化输出实验**。

当前数据集：

```text
Dataset name: AnimeCharacterSelf50
Asset type: 3D anime character
Format: GLB
Asset count: 50
Usage: TRELLIS.2 character fine-tuning experiment
```

本地数据集路径：

```text
/root/autodl-tmp/trellis_character_data/trellis_dataset
```

## 数据构建目标

TRELLIS.2 训练时不能只直接读取一堆 `.glb` 文件。

需要先把原始 3D 资产整理成 TRELLIS.2 能识别的数据结构，包括：

```text
GLB 文件
→ 资产索引 CSV
→ 训练 / 验证集划分
→ TRELLIS metadata.csv
→ mesh dump
→ dual grid / voxel 表示
→ 训练流程可读取的数据
```

也就是说，`.glb` 是原始资产，`metadata.csv` 和预处理结果才是 TRELLIS.2 训练时真正依赖的数据入口。

## 构建流程

### 1. 准备原始 GLB 资产

首先准备 50 个动漫人物 GLB 文件。

示例目录：

```text
/root/autodl-tmp/trellis_character_data/processed/glb/
```

每个文件对应一个 3D 人物资产。

要求：

* 文件能被正常读取
* 模型格式为 `.glb`
* 尽量保持统一朝向和尺度
* 尽量避免破面、空模型、严重材质缺失
* 只使用许可明确的数据

## 2. 生成资产索引

扫描 GLB 文件，生成资产索引：

```text
data/metadata/asset_index.csv
```

它记录每个资产的基本信息，例如：

```text
id
raw_path
converted_glb_path
original_format
category
style
status
quality_note
```

作用：

* 记录每个模型在哪里
* 记录它是否已经转换为 GLB
* 标记它是否可以进入训练集
* 方便后续复现数据集

## 3. 记录许可信息

生成或维护许可记录：

```text
data/metadata/license_registry.csv
```

它记录：

```text
id
source
model_name
author
license
original_url
ai_training_allowed
status
note
```

作用：

* 防止版权不清楚的模型进入训练
* 区分 self-generated、CC0、CC-BY 等来源
* 记录是否允许 AI training

当前原则：

```text
只有 status = accepted 且 ai_training_allowed = yes 的资产才进入训练集。
```

## 4. 生成 train / val 划分

生成训练集和验证集划分：

```text
data/metadata/train_split.csv
data/metadata/val_split.csv
```

示例：

```csv
id,split
000001,train
000002,train
```

作用：

* 固定实验划分
* 避免每次训练随机分配数据
* 保证后续实验可以复现

## 5. 生成 TRELLIS metadata.csv

然后把项目自己的资产记录转换成 TRELLIS.2 使用的 metadata：

```text
/root/autodl-tmp/trellis_character_data/trellis_dataset/metadata.csv
```

这个文件是 TRELLIS.2 数据集读取的入口。

它的作用不是保存模型本身，而是告诉 TRELLIS：

```text
有哪些样本
每个样本的 sha256 是什么
每个样本属于 train 还是 val
哪些预处理步骤已经完成
对应的 mesh / voxel / latent 文件在哪里
```

仓库中只保留示例文件：

```text
data/metadata/trellis_metadata_example.csv
```

真正训练用的完整 `metadata.csv` 保存在 AutoDL 本地目录，不上传 GitHub。

## 6. 生成 mesh dump

TRELLIS.2 不能直接把 GLB 当作最终训练数据使用。

需要先把 GLB 解析成统一的 mesh 表示，通常会生成到类似目录：

```text
/root/autodl-tmp/trellis_character_data/trellis_dataset/mesh_dumps/
```

这一步会把 GLB 中的几何信息整理出来，例如：

```text
vertices
faces
materials
mesh status
```

同时会生成处理记录，例如：

```text
mesh_dumps/new_records/part_0.csv
```

其中会记录类似：

```text
sha256,mesh_dumped
xxxx,true
```

作用：

* 确认每个 GLB 是否成功解析
* 把原始模型转成 TRELLIS 后续工具能继续处理的 mesh 数据

## 7. 生成 dual grid / voxel 表示

完成 mesh dump 后，需要进一步生成 TRELLIS.2 训练所需的空间结构表示。

当前使用过的命令形式类似：

```bash
python data_toolkit/dual_grid.py Custom \
  --root /root/autodl-tmp/trellis_character_data/trellis_dataset \
  --resolution 256
```

这一步的作用是把 mesh 转换成更适合 3D 生成模型学习的结构，例如：

```text
mesh
→ dual grid
→ voxel / sparse structure
→ shape representation
```

可以理解为：

```text
GLB 是给人和建模软件看的格式；
dual grid / voxel 是给 TRELLIS 训练流程看的格式。
```

## 8. 进入训练流程

当数据集目录中已经具备：

```text
metadata.csv
mesh_dumps/
dual grid / voxel 相关预处理结果
train / val 标记
```

训练脚本就可以通过配置文件读取数据集。

当前训练配置使用的数据集路径是：

```text
/root/autodl-tmp/trellis_character_data/trellis_dataset
```

训练配置：

```text
configs/training/train_character_50.yaml
```

启动脚本：

```text
scripts/training/launch_train_character_50.sh
```

当前训练实验：

```text
exp001_self50_character_finetune
```

## 当前状态

当前已经完成：

```text
GLB 资产整理
资产索引构建
许可记录整理
train / val 划分
TRELLIS metadata 构建
mesh dump 处理
训练配置编写
训练启动测试
```

当前卡点：

```text
24GB 显存环境下训练受 CUDA memory limitation 阻塞
暂未得到有效 fine-tuned checkpoint
```

## 不上传到 GitHub 的内容

以下内容不上传：

```text
完整 GLB / VRM / FBX 模型
mesh_dumps/
dual grid / voxel 预处理文件
latent 文件
训练 checkpoint
版权不明确的角色资产
```

仓库只保留：

```text
数据说明
metadata 示例
数据处理脚本
实验配置
少量展示样例
```

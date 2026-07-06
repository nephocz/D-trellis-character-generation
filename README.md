# trellis-character-generation

面向 **3D 动漫人物生成、训练适配与可控化输出** 的 TRELLIS.2 实验项目。

本项目围绕 TRELLIS.2 搭建一套角色生成实验流程，重点探索：

* 3D 动漫人物数据集构建
* TRELLIS.2 人物方向训练 / 微调
* 单图、多视角、seed、背景等可控化输出
* 生成结果在游戏开发中的可用性验证

## 当前进度

当前阶段已完成：

* 构建 50 个 3D 动漫人物资产的小规模数据集
* 整理 GLB 数据路径
* 生成 TRELLIS.2 训练所需 metadata
* 准备 train / val split
* 编写 baseline 推理配置与脚本
* 编写人物训练配置与启动脚本

当前问题：

* 已尝试在 24GB 显存环境下训练
* 训练阶段受 CUDA 显存限制阻塞
* 暂未得到有效 fine-tuned checkpoint

## 项目流程

```text
3D 人物资产整理
→ 数据集 metadata 构建
→ TRELLIS.2 baseline 推理
→ 人物方向训练 / 微调
→ 可控化推理实验
→ 结果评估与游戏引擎验证
```

## 仓库结构

```text
configs/        实验配置
scripts/        数据处理、推理、训练脚本
data/           数据说明、metadata、split，不存完整大数据
assets/         输入图、输出结果、对比图
docs/           数据集、训练日志、评估与失败案例
engine_demo/    Unity / Godot 导入验证
```

## 当前实验

### Baseline 推理

使用原版 TRELLIS.2-4B 进行 image-to-3D 生成测试。

输出内容包括：

* GLB 模型
* 预览视频
* manifest 记录
* 错误日志

### 人物训练实验

当前训练实验：

```text
exp001_self50_character_finetune
```

数据集：

```text
AnimeCharacterSelf50
```

训练目标：

```text
验证 TRELLIS.2 在小规模动漫人物数据上的训练适配流程
```

当前状态：

```text
数据集构建完成，训练启动完成，但 24GB 显存不足，训练暂未完成。
```

## 数据说明

完整 3D 数据集、预处理文件和 checkpoint 不上传到 GitHub。

仓库只保留：

* 数据说明
* metadata 示例
* 数据来源记录
* 数据处理脚本
* 实验配置
* 少量展示结果

## 后续计划

* 解决训练显存问题
* 尝试更轻量的 fine-tuning 方案
* 补充 baseline / finetuned / controlled output 对比
* 增加多视角和 seed 控制实验
* 验证生成 GLB 在 Unity / Godot 中的使用效果

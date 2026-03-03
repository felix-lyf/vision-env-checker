# Vision Env Checker - 工业视觉运行环境检测工具

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A cross-platform environment checker for industrial machine vision systems.
基于 C# WPF 项目重构的 Python 跨平台版本。

![Screenshot](docs/screenshot.png)

## ✨ 功能特性

### 基础检测（源自原 C# 项目）
- ✅ **VisionPlus 软件安装检查** - 检测视觉软件是否安装
- ✅ **系统配置要求检查** - 内存/磁盘/CPU 检查（内存≥4GB，磁盘≥10GB）
- ✅ **网卡 IP 配置检查** - 检测 IP 地址冲突
- ✅ **网卡驱动检查** - 检测网卡驱动状态
- ✅ **网卡参数配置检查** - 检测网卡速度和参数
- ✅ **防火墙检查** - 检测系统防火墙状态
- ✅ **杀毒软件检查** - 检测第三方杀毒软件

### 新增检测项
- 🎥 **相机驱动检查** - Basler/海康/大华/FLIR 等 SDK
- 🖥️ **GPU 检查** - 检测独立显卡
- 🔥 **CUDA 环境检查** - 检测 CUDA 版本

### 其他功能
- 📊 可视化检测结果表格
- 📈 实时进度条显示
- 📄 导出检测报告（TXT/HTML）
- 🎨 彩色状态标识（绿/黄/红）
- 🖥️ 跨平台支持（Windows/Linux/macOS）

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python src/main.py
```

### 打包为可执行文件（可选）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

## 📋 系统要求

- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.10 或更高版本
- **内存**: 建议 4GB 以上
- **磁盘**: 建议 10GB 可用空间

## 🛠️ 开发环境

- Python 3.12
- PyQt6 6.6.0+
- psutil 5.9.0+

## 📁 项目结构

```
vision-env-checker/
├── src/
│   ├── main.py                    # 主入口，GUI界面
│   └── services/
│       └── checker_service.py     # 检测服务核心
├── assets/                        # 资源文件
├── docs/                          # 文档
├── tests/                         # 测试代码
├── requirements.txt               # 依赖列表
└── README.md                      # 项目说明
```

## 🔧 检测项说明

| 检测项 | 描述 | 状态 |
|--------|------|------|
| VisionPlus 安装 | 检查视觉软件安装状态 | ✅/❌ |
| 系统配置 | 内存/磁盘/CPU检查 | ✅/⚠️ |
| GPU | 检测独立显卡 | ✅/⚠️ |
| CUDA | 检测 CUDA 环境 | ✅/⚠️ |
| 相机驱动 | 检测相机 SDK | ✅/⚠️ |
| 网卡 IP | IP 配置和冲突检测 | ✅/❌ |
| 网卡驱动 | 网卡驱动状态 | ✅/⚠️ |
| 网卡参数 | 网卡速度和配置 | ✅/⚠️ |
| 防火墙 | 系统防火墙状态 | ✅/⚠️ |
| 杀毒软件 | 第三方杀毒软件 | ✅/⚠️ |

## 📝 历史

- **v1.0** (2026-03-03) - 初始版本，基于 C# WPF 项目重构
  - 保留原项目所有检测功能
  - 新增 GPU/CUDA/相机驱动检测
  - 跨平台支持

## 👥 开发团队

苏州德创测控科技有限公司

## 📄 许可证

MIT License

# Mirror Switch - 镜像源切换工具

一个交互式命令行工具，用于快速切换 uv、pip、npm 和 cargo 的国内镜像源。

## ✨ 特性

- 🎯 **交互式操作**：支持方向键选择，用户友好
- 🔍 **状态显示**：实时查看当前使用的源
- 🛡️ **安全可靠**：支持恢复官方源
- ⚡ **多工具支持**：支持 uv、pip、npm、cargo

## 📦 安装

### 使用 uv 安装（推荐）

```bash
# 在项目目录下
uv sync

# 或者全局安装
cd mirror-switch
uv pip install -e .
```

### 或使用 pip 安装

```bash
pip install .
```

## 🚀 使用方法

直接运行命令即可进入交互式模式：

```bash
mirror-switch
```

或者：

```bash
python -m mirror_switch.main
```

### 操作流程

1. 选择要配置的工具（uv、pip、npm、cargo 或查看当前状态）
2. 选择镜像源（支持多个国内镜像源）
3. 确认切换

## 🌐 支持的包管理器和镜像源

### 支持的包管理器

- **uv**: Python 包管理器（uv）
- **pip**: Python 包管理器（pip）
- **npm**: Node.js 包管理器（npm）
- **cargo**: Rust 包管理器（cargo）

### uv (Python 包管理器)

| 代码 | 名称 | 说明 |
|------|------|------|
| `default` | 官方源 | PyPI 官方源 |
| `aliyun` | 阿里云 | 阿里云镜像 |
| `tsinghua` | 清华源 | 清华大学镜像（推荐） |
| `tencent` | 腾讯云 | 腾讯云镜像 |
| `netease` | 网易 | 网易镜像 |

### pip (Python 包管理器)

| 代码 | 名称 | 说明 |
|------|------|------|
| `default` | 官方源 | PyPI 官方源 |
| `aliyun` | 阿里云 | 阿里云镜像 |
| `tsinghua` | 清华源 | 清华大学镜像（推荐） |
| `tencent` | 腾讯云 | 腾讯云镜像 |
| `netease` | 网易 | 网易镜像 |

### npm (Node.js 包管理器)

| 代码 | 名称 | 说明 |
|------|------|------|
| `default` | 官方源 | NPM 官方源 |
| `taobao` | 淘宝镜像 | 淘宝 NPM 镜像（推荐） |
| `huawei` | 华为云 | 华为云 NPM 镜像 |
| `tencent` | 腾讯云 | 腾讯云 NPM 镜像 |
| `uniapp` | UniApp | UniApp 镜像 |

### cargo (Rust 包管理器)

| 代码 | 名称 | 说明 |
|------|------|------|
| `default` | 官方源 | Cargo 官方源 |
| `tuna` | 清华源 | 清华大学镜像（推荐） |
| `ustc` | 中科大 | 中国科学技术大学镜像 |
| `rustcc` | rustcc | rustcc 社区镜像 |

## 💡 使用示例

### 示例：交互式切换镜像源

```bash
$ mirror-switch

┌─────────────────────────────────┐
│ Mirror Switch - 镜像源切换工具  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 选择要配置的工具                │
├─────────────────────────────────┤
│ ❯ uv (Python 包管理器)         │
│   pip (Python 包管理器)        │
│   npm (Node.js 包管理器)       │
│   cargo (Rust 包管理器)        │
│   查看当前状态                  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 选择 uv 的镜像源                │
├─────────────────────────────────┤
│ ❯ 清华源 (tsinghua) ← 推荐     │
│   阿里云 (aliyun)               │
│   官方源 (default)              │
│   腾讯云 (tencent)              │
└─────────────────────────────────┘

准备切换镜像源：
  工具: uv
  源: 清华源 (tsinghua)
  URL: https://pypi.tuna.tsinghua.edu.cn/simple

确认执行切换？ [是/否]: 是

✓ 已切换到 清华源
```

### 查看当前状态

```bash
$ mirror-switch

选择要配置的工具: 查看当前状态

当前源状态:
------------------------------------------------------------
  uv: 清华源 (tsinghua)
    https://pypi.tuna.tsinghua.edu.cn/simple
  pip: 阿里云 (aliyun)
    https://mirrors.aliyun.com/pypi/simple
  npm: 淘宝镜像 (taobao)
    https://registry.npmmirror.com/
  cargo: 清华源 (tuna)
    https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git
------------------------------------------------------------
```

## 🔧 依赖说明

需要安装的 Python 包：
- `inquirerpy>=0.3.4` - 交互式命令行
- `colorama>=0.4.6` - 彩色输出

系统要求：
- `uv` - 用于 uv 源切换
- `pip` - 用于 pip 源切换
- `npm` - 用于 npm 源切换（如需要）
- `cargo` - 用于 cargo 源切换（如需要）

## 📝 配置说明

### uv 配置原理

配置文件位置：`~/.config/uv/uv.toml`

使用 `uv config` 命令管理：
- 设置源：`uv config index-url <url>`
- 移除配置：`uv config --remove index-url`

### pip 配置原理

配置文件位置：`~/.config/pip/pip.conf`

使用 `pip config` 命令管理：
- 设置源：`pip config set global.index-url <url>`

### npm 配置原理

使用 `npm config` 命令管理：
- 设置源：`npm config set registry <url>`

### cargo 配置原理

配置文件位置：`~/.cargo/config.toml`

修改 `[source.crates-io]` 配置段落：

```toml
[source.crates-io]
replace-with = "mirror"

[mirror]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"
```

## 🐛 常见问题

### Q: 未检测到 uv、npm 或其他工具？

A: 请确保相应的工具已安装并添加到 PATH 环境变量中。

### Q: 如何查看当前配置？

A: 在交互模式中选择"查看当前状态"，或者使用以下命令查看：

```bash
uv config list | grep index-url
npm config get registry
pip config list
```

### Q: 如何添加自定义源？

A: 编辑 `mirror_switch/config.py` 文件，在相应的工具配置中添加新的源配置。

## 🤝 贡献

欢迎提出 Issue 或 Pull Request！

## 📄 许可证

MIT License

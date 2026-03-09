#!/bin/bash
set -e

# 如果你部署在 Cloudflare Pages 上，可以将这里的 ProjectUrl 换成你托管的 ZIP 包链接
# 例如: "https://your-cf-pages.dev/mirror-switch.zip"
# 默认推测的 Cloudflare Pages 域名，如果你的项目名不同，请稍后自行修改
PROJECT_URL="https://tool.vanzor.com/mirror-switch.zip"

TEMP_ZIP="/tmp/mirror-switch.zip"
EXTRACT_DIR="/tmp/mirror-switch-extracted"

echo -e "\033[1;36m>>> 开始下载 Mirror Switch...\033[0m"
curl -fsSL "$PROJECT_URL" -o "$TEMP_ZIP"

if [ -d "$EXTRACT_DIR" ]; then
    rm -rf "$EXTRACT_DIR"
fi
mkdir -p "$EXTRACT_DIR"

echo -e "\033[1;36m>>> 解压中...\033[0m"
if command -v unzip &> /dev/null; then
    unzip -q "$TEMP_ZIP" -d "$EXTRACT_DIR"
elif command -v python3 &> /dev/null; then
    python3 -c "import zipfile; zipfile.ZipFile('$TEMP_ZIP', 'r').extractall('$EXTRACT_DIR')"
elif command -v python &> /dev/null; then
    python -c "import zipfile; zipfile.ZipFile('$TEMP_ZIP', 'r').extractall('$EXTRACT_DIR')"
else
    echo -e "\033[1;31m>>> 错误：未检测到 unzip 或 python，无法完成解压。\033[0m"
    exit 1
fi

# 因为我们打包的 ZIP 没有外层目录，文件直接在根目录
ACTUAL_DIR="$EXTRACT_DIR"

echo -e "\033[1;36m>>> 准备运行环境（使用 阿里源 加速）...\033[0m"

# 根据用户喜好，如果有 uv 则使用 uv
# 根据用户喜好，如果有 uv 则使用自带 uv，否则下载基于 Cloudflare 的独立版
if command -v uv &> /dev/null; then
    echo -e "\033[1;32m>>> 检测到 uv，正在通过当前环境 uv 运行...\033[0m"
    UV_BIN="uv"
else
    echo -e "\033[1;33m>>> 未检测到 uv，正在极速拉取免安装运行环境 (${OS}-${ARCH})...\033[0m"
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then ARCH_NAME="x86_64";
    elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then ARCH_NAME="aarch64";
    else
        echo -e "\033[1;31m>>> 暂不支持当前架构: $ARCH，请先安装 uv。\033[0m"
        exit 1
    fi

    if [ "$OS" = "linux" ]; then PLAT_NAME="unknown-linux-gnu"
    elif [ "$OS" = "darwin" ]; then PLAT_NAME="apple-darwin"
    fi
    
    UV_FILE="uv-${ARCH_NAME}-${PLAT_NAME}.tar.gz"
    UV_URL="https://tool.vanzor.com/bin/${UV_FILE}"
    
    curl -sSL "$UV_URL" -o "/tmp/$UV_FILE"
    tar -xzf "/tmp/$UV_FILE" -C "/tmp"
    UV_BIN="/tmp/uv-${ARCH_NAME}-${PLAT_NAME}/uv"
    chmod +x "$UV_BIN"
fi

cd "$ACTUAL_DIR"
# 注意：因为用户是通过 | bash 执行的脚本，此时 stdin 是未连接到终端的，必须加上 < /dev/tty 获取交互输入
"$UV_BIN" run --python 3.12 --index-url https://mirrors.aliyun.com/pypi/simple/ python -m mirror_switch.main < /dev/tty

echo -e "\033[1;36m>>> 运行结束，清理临时文件...\033[0m"
rm -rf "$EXTRACT_DIR" "$TEMP_ZIP"
echo -e "\033[1;32m>>> 完成\033[0m"

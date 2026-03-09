#!/bin/bash
# 这个脚本供 Cloudflare Pages 构建时使用，本地无需运行。
# 作用是让 Cloudflare 帮你从 GitHub 拉取构建好的 `uv` 独立程序，从而让你的工具脱离本地环境依赖。

echo "========== 开始构建 Mirror Switch =========="

# 创建存放二进制文件的目录
mkdir -p dist_site/bin

echo "> 开始从 GitHub 极速同步 uv 免安装版..."

# 需要同步的 uv 包列表（覆盖主流系统和架构）
FILES=(
    "uv-x86_64-unknown-linux-gnu.tar.gz"
    "uv-aarch64-unknown-linux-gnu.tar.gz"
    "uv-x86_64-apple-darwin.tar.gz"
    "uv-aarch64-apple-darwin.tar.gz"
    "uv-x86_64-pc-windows-msvc.zip"
)

BASE_URL="https://github.com/astral-sh/uv/releases/latest/download"

# 对于每一个文件，让 Cloudflare 下载它放入 dist_site/bin 文件夹中
for file in "${FILES[@]}"; do
    echo "正在同步: $file"
    curl -sSL -H "Cache-Control: no-cache" "$BASE_URL/$file" -o "dist_site/bin/$file"
done

echo "> 同步完成！所有文件已准备发布。"
echo "========== 构建结束 =========="

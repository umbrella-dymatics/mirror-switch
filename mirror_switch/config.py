"""配置管理模块 - 加载各种工具的镜像源配置"""
import json
import os
from pathlib import Path

# 获取模块所在目录，定位默认的 mirrors.json
_current_dir = Path(__file__).parent
_default_mirrors_path = _current_dir / "mirrors.json"

# 获取用户自定义配置路径
_user_mirrors_path = Path.home() / ".mirror-switch.json"

# 初始化 TOOLS 字典
TOOLS = {}

def _load_mirrors():
    """加载镜像源配置，支持与用户自定义配置合并"""
    global TOOLS
    
    # 1. 加载默认配置
    try:
        if _default_mirrors_path.exists():
            with open(_default_mirrors_path, "r", encoding="utf-8") as f:
                TOOLS = json.load(f)
    except Exception as e:
        print(f"警告: 无法加载默认的 mirrors.json 配置 ({e})")
        # 提供一个极简的后备配置
        TOOLS = {
            "uv": {"name": "uv", "description": "Python 包管理器（uv）", "sources": {"default": {"name": "官方源", "url": "default", "description": "PyPI 官方源"}}},
            "pip": {"name": "pip", "description": "Python 包管理器（pip）", "sources": {"default": {"name": "官方源", "url": "default", "description": "PyPI 官方源"}}},
            "npm": {"name": "npm", "description": "Node.js 包管理器（npm）", "sources": {"default": {"name": "官方源", "url": "https://registry.npmjs.org/", "description": "NPM 官方源"}}},
            "cargo": {"name": "cargo", "description": "Rust 包管理器（cargo）", "sources": {"default": {"name": "官方源", "url": "https://crates.io", "description": "Cargo 官方源"}}}
        }

    # 2. 尝试加载用户自定义配置并合并
    if _user_mirrors_path.exists():
        try:
            with open(_user_mirrors_path, "r", encoding="utf-8") as f:
                user_tools = json.load(f)
                
            # 深合并用户配置 (允许覆盖或添加新的工具/镜像源)
            for tool_key, tool_config in user_tools.items():
                if tool_key not in TOOLS:
                    TOOLS[tool_key] = tool_config
                else:
                    # 如果工具存在，合并 sources
                    if "sources" in tool_config:
                        for source_key, source_config in tool_config["sources"].items():
                            TOOLS[tool_key]["sources"][source_key] = source_config
                    # 合并其他属性
                    for k, v in tool_config.items():
                        if k != "sources":
                            TOOLS[tool_key][k] = v
        except Exception as e:
            print(f"提示: 用户自定义配置 ~/.mirror-switch.json 解析失败，将被忽略 ({e})")

# 在模块导入时执行加载
_load_mirrors()

# 兼容导出以往的独立变量（避免外部使用时报错，尽管主要通过 TOOLS 访问）
UV_SOURCES = TOOLS.get("uv", {}).get("sources", {})
PIP_SOURCES = TOOLS.get("pip", {}).get("sources", {})
NPM_SOURCES = TOOLS.get("npm", {}).get("sources", {})
CARGO_SOURCES = TOOLS.get("cargo", {}).get("sources", {})

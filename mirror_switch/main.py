"""主程序 - 交互式镜像源切换工具"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional, Literal, Tuple

from colorama import Fore, Style, init
from InquirerPy import prompt

from .config import TOOLS

# 初始化 colorama
init(autoreset=True)

ScopeType = Literal["global", "project"]

# --- 跨平台配置文件路径定义 ---

def get_uv_global_config_path() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.environ.get("APPDATA", "~")) / "uv" / "uv.toml"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "uv" / "uv.toml"
    else:
        return Path.home() / ".config" / "uv" / "uv.toml"

def get_pip_global_config_path() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.environ.get("APPDATA", "~")) / "pip" / "pip.ini"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "pip" / "pip.conf"
    else:
        return Path.home() / ".config" / "pip" / "pip.conf"

def get_go_global_config_path() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.environ.get("APPDATA", "~")) / "go" / "env"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "go" / "env"
    else:
        return Path.home() / ".config" / "go" / "env"

def get_conda_global_config_path() -> Path:
    return Path.home() / ".condarc"

# 用户全局 (Global)
UV_CONFIG_FILE_GLOBAL = get_uv_global_config_path()
PIP_CONFIG_FILE_GLOBAL = get_pip_global_config_path()
CARGO_CONFIG_FILE_GLOBAL = Path.home() / ".cargo" / "config.toml"
NPM_CONFIG_FILE_GLOBAL = Path.home() / ".npmrc"
GO_CONFIG_FILE_GLOBAL = get_go_global_config_path()
CONDA_CONFIG_FILE_GLOBAL = get_conda_global_config_path()

# 工作区/项目级 (Project) - 使用当前工作目录
CURRENT_DIR = Path.cwd()
UV_CONFIG_FILE_PROJECT = CURRENT_DIR / "uv.toml"
PIP_CONFIG_FILE_PROJECT = CURRENT_DIR / "pip.conf"
CARGO_CONFIG_FILE_PROJECT = CURRENT_DIR / ".cargo" / "config.toml"
NPM_CONFIG_FILE_PROJECT = CURRENT_DIR / ".npmrc"
GO_CONFIG_FILE_PROJECT = CURRENT_DIR / "go.env"
CONDA_CONFIG_FILE_PROJECT = CURRENT_DIR / ".condarc"


class MirrorSwitch:
    """镜像源切换器"""

    def __init__(self):
        self.tools = TOOLS

    def print_header(self):
        """打印程序头"""
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{' Mirror Switch - 镜像源切换工具 ':^60}")
        print(f"{'=' * 60}\n")

    def print_success(self, message: str):
        """打印成功信息"""
        print(f"{Fore.GREEN}✓ {message}")

    def print_error(self, message: str):
        """打印错误信息"""
        print(f"{Fore.RED}✗ {message}")

    # --- 配置读取辅助方法 (匹配并返回源的 key) ---

    def _match_url_to_source_key(self, tool_name: str, url: str) -> str:
        if not url:
            return None
        url = url.strip().strip("'\"")
        if not url:
            return None
            
        for key, info in self.tools[tool_name]["sources"].items():
            if info["url"] == url or (info["url"].rstrip("/") == url.rstrip("/")):
                return key
        return "custom"

    def _get_uv_source_from_file(self, config_file: Path) -> Optional[str]:
        try:
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                in_index_section = False
                for line in content.split("\n"):
                    line = line.strip()
                    if line == "[[index]]":
                        in_index_section = True
                    elif in_index_section and line.startswith("url ="):
                        url_part = line.split("=", 1)[1]
                        return self._match_url_to_source_key("uv", url_part)
                    elif in_index_section and (line == "" or (line.startswith("[") and line != "[[index]]")):
                        in_index_section = False
        except Exception:
            pass
        return None

    def _get_pip_source_from_file(self, config_file: Path) -> Optional[str]:
        try:
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("index-url =") or line.startswith("index-url="):
                        url_part = line.split("=", 1)[1]
                        return self._match_url_to_source_key("pip", url_part)
        except Exception:
            pass
        return None

    def _get_npm_source_from_file(self, config_file: Path) -> Optional[str]:
        try:
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("registry="):
                        url_part = line.split("=", 1)[1]
                        return self._match_url_to_source_key("npm", url_part)
        except Exception:
            pass
        return None

    def _get_cargo_source_from_file(self, config_file: Path) -> Optional[str]:
        try:
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                in_mirror_section = False
                for line in content.split("\n"):
                    line = line.strip()
                    if line == "[mirror]" or line == "[source.crates-io]":
                        in_mirror_section = True
                    elif in_mirror_section and line.startswith("registry ="):
                        url_part = line.split("=", 1)[1]
                        return self._match_url_to_source_key("cargo", url_part)
                    elif in_mirror_section and line.startswith("["):
                        in_mirror_section = False
        except Exception:
            pass
        return None

    def _get_go_source_from_file(self, config_file: Path) -> Optional[str]:
        try:
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("GOPROXY="):
                        url_part = line.split("=", 1)[1]
                        return self._match_url_to_source_key("go", url_part)
        except Exception:
            pass
        return None

    def _get_conda_source_from_file(self, config_file: Path) -> Optional[str]:
        try:
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    line = line.strip()
                    if "- https://mirrors." in line or "- http://mirrors." in line:
                        url_part = line.replace("- ", "").strip()
                        return self._match_url_to_source_key("conda", url_part)
        except Exception:
            pass
        return None

    # --- 获取三层状态配置 ---

    def get_source_env(self, tool_name: str) -> Optional[Tuple[str, str]]:
        """检查环境变量。返回 (匹配的key, 原始URL)"""
        url = None
        if tool_name == "uv":
            url = os.environ.get("UV_INDEX_URL") or os.environ.get("UV_DEFAULT_INDEX")
        elif tool_name == "pip":
            url = os.environ.get("PIP_INDEX_URL")
        elif tool_name == "npm":
            url = os.environ.get("npm_config_registry")
        elif tool_name == "go":
            url = os.environ.get("GOPROXY")
            
        if url:
            key = self._match_url_to_source_key(tool_name, url)
            return (key, url)
        return None

    def get_source_file(self, tool_name: str, scope: ScopeType) -> Optional[str]:
        if tool_name == "uv":
            path = UV_CONFIG_FILE_GLOBAL if scope == "global" else UV_CONFIG_FILE_PROJECT
            return self._get_uv_source_from_file(path)
        elif tool_name == "pip":
            path = PIP_CONFIG_FILE_GLOBAL if scope == "global" else PIP_CONFIG_FILE_PROJECT
            return self._get_pip_source_from_file(path)
        elif tool_name == "npm":
            path = NPM_CONFIG_FILE_GLOBAL if scope == "global" else NPM_CONFIG_FILE_PROJECT
            return self._get_npm_source_from_file(path)
        elif tool_name == "cargo":
            path = CARGO_CONFIG_FILE_GLOBAL if scope == "global" else CARGO_CONFIG_FILE_PROJECT
            return self._get_cargo_source_from_file(path)
        elif tool_name == "go":
            path = GO_CONFIG_FILE_GLOBAL if scope == "global" else GO_CONFIG_FILE_PROJECT
            return self._get_go_source_from_file(path)
        elif tool_name == "conda":
            path = CONDA_CONFIG_FILE_GLOBAL if scope == "global" else CONDA_CONFIG_FILE_PROJECT
            return self._get_conda_source_from_file(path)
        return None

    # --- 状态显示 ---

    def _format_active_indicator(self, is_active: bool) -> str:
        return f"{Fore.GREEN}[生效]{Style.RESET_ALL}" if is_active else ""

    def show_status(self):
        """显示当前所有工具的三层源状态 (环境/项目/全局)"""
        print(f"\n{Fore.CYAN}=== 当前镜像源三层检查结果 ==={Style.RESET_ALL}")
        
        for tool_name in ["uv", "pip", "npm", "cargo", "go", "conda"]:
            print(f"\n{Fore.CYAN}📍 {tool_name}{Style.RESET_ALL} (最终优先级: 环境变量 > 项目级 > 全局级)")
            print("-" * 50)
            
            # 最高优先级：环境变量
            env_res = self.get_source_env(tool_name)
            env_active = env_res is not None
            
            # 第二优先级：项目级
            proj_key = self.get_source_file(tool_name, "project")
            proj_active = proj_key is not None and not env_active
            
            # 第三优先级：全局级
            global_key = self.get_source_file(tool_name, "global")
            global_active = global_key is not None and not env_active and not proj_active
            
            # 环境变量打印
            if env_res:
                key, url = env_res
                name = self.tools[tool_name]["sources"].get(key, {}).get("name", "自定义")
                print(f"  {Fore.MAGENTA}1. 环境变量{Style.RESET_ALL} {self._format_active_indicator(True)}")
                print(f"     -> {name} ({key})\n     URL: {url}")
            else:
                print(f"  {Fore.LIGHTBLACK_EX}1. 环境变量  -> 未设置{Style.RESET_ALL}")

            # 项目级打印
            if proj_key:
                info = self.tools[tool_name]["sources"].get(proj_key, {"name": "自定义", "url": "Unknown"})
                print(f"  {Fore.YELLOW}2. 项目配置{Style.RESET_ALL} {self._format_active_indicator(proj_active)}")
                print(f"     -> {info['name']} ({proj_key})")
            else:
                print(f"  {Fore.LIGHTBLACK_EX}2. 项目配置  -> 未设置{Style.RESET_ALL}")

            # 全局级打印
            if global_key:
                info = self.tools[tool_name]["sources"].get(global_key, {"name": "自定义", "url": "Unknown"})
                print(f"  {Fore.CYAN}3. 全局配置{Style.RESET_ALL} {self._format_active_indicator(global_active)}")
                print(f"     -> {info['name']} ({global_key})")
            else:
                print(f"  {Fore.LIGHTBLACK_EX}3. 全局配置  -> 未设置 (默认官方源){Style.RESET_ALL}")

        print("\n" + "=" * 50 + "\n")

    # --- 切换逻辑实现 ---

    def _write_config_file(self, file_path: Path, content: str, delete_on_empty: bool = False):
        try:
            if delete_on_empty and not content:
                if file_path.exists():
                    file_path.unlink()
                return True

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            self.print_error(f"写入配置失败 {file_path}: {e}")
            return False

    def switch_uv(self, source_key: str, scope: ScopeType):
        source_info = self.tools["uv"]["sources"][source_key]
        config_file = UV_CONFIG_FILE_GLOBAL if scope == "global" else UV_CONFIG_FILE_PROJECT
        
        if source_key == "default":
            self._write_config_file(config_file, "", delete_on_empty=True)
            self.print_success("已清除 uv 的镜像源配置 (恢复官方源)")
            return True
            
        content = f'''# uv 镜像源配置 ({scope})
# Generated by mirror-switch

[[index]]
url = "{source_info["url"]}"
default = true
'''
        if self._write_config_file(config_file, content):
            self.print_success(f"已成功设置 uv 源为: {source_info['name']}")
            print(f"配置文件位置: {config_file}")
            return True
        return False

    def switch_pip(self, source_key: str, scope: ScopeType):
        source_info = self.tools["pip"]["sources"][source_key]
        config_file = PIP_CONFIG_FILE_GLOBAL if scope == "global" else PIP_CONFIG_FILE_PROJECT

        if source_key == "default":
            self._write_config_file(config_file, "", delete_on_empty=True)
            self.print_success("已清除 pip 的镜像源配置 (恢复官方源)")
            return True

        content = f"""[global]
index-url = {source_info["url"]}
"""
        if self._write_config_file(config_file, content):
            self.print_success(f"已成功设置 pip 源为: {source_info['name']}")
            print(f"配置文件位置: {config_file}")
            return True
        return False

    def switch_npm(self, source_key: str, scope: ScopeType):
        source_info = self.tools["npm"]["sources"][source_key]
        config_file = NPM_CONFIG_FILE_GLOBAL if scope == "global" else NPM_CONFIG_FILE_PROJECT
        
        if source_key == "default":
            if config_file.exists():
                content = config_file.read_text(encoding="utf-8")
                lines = [line for line in content.splitlines() if not line.startswith("registry=")]
                if lines:
                    config_file.write_text("\n".join(lines), encoding="utf-8")
                else:
                    config_file.unlink()
            self.print_success("已清除 npm 的镜像源配置 (恢复官方源)")
            return True
        
        existing_content = ""
        if config_file.exists():
            content = config_file.read_text(encoding="utf-8")
            existing_content = "\n".join(line for line in content.splitlines() if not line.startswith("registry="))
            if existing_content:
                existing_content += "\n"
        
        final_content = existing_content + f"registry={source_info['url']}\n"
        if self._write_config_file(config_file, final_content):
            self.print_success(f"已成功设置 npm 源为: {source_info['name']}")
            print(f"配置文件位置: {config_file}")
            return True
        return False

    def switch_cargo(self, source_key: str, scope: ScopeType):
        source_info = self.tools["cargo"]["sources"][source_key]
        config_file = CARGO_CONFIG_FILE_GLOBAL if scope == "global" else CARGO_CONFIG_FILE_PROJECT

        existing_content = ""
        if config_file.exists():
            existing_content = config_file.read_text(encoding="utf-8")
            
            clean_lines = []
            skip_mode = False
            for line in existing_content.splitlines():
                if line.strip() in ("[source.crates-io]", "[mirror]"):
                    skip_mode = True
                elif skip_mode and line.startswith("["):
                    skip_mode = False
                
                if not skip_mode:
                    clean_lines.append(line)
                    
            existing_content = "\n".join(clean_lines).strip()
            if existing_content:
                existing_content += "\n\n"

        if source_key == "default":
            self._write_config_file(config_file, existing_content, delete_on_empty=True)
            self.print_success("已清除 cargo 的镜像源配置 (恢复官方源)")
            return True
        else:
            new_config = f'''[source.crates-io]
replace-with = "mirror"

[mirror]
registry = "{source_info["url"]}"
'''
            final_content = existing_content + new_config
            if self._write_config_file(config_file, final_content):
                 self.print_success(f"已成功设置 cargo 源为: {source_info['name']}")
                 print(f"配置文件位置: {config_file}")
                 return True
        return False

    def switch_go(self, source_key: str, scope: ScopeType):
        source_info = self.tools["go"]["sources"][source_key]
        config_file = GO_CONFIG_FILE_GLOBAL if scope == "global" else GO_CONFIG_FILE_PROJECT

        if source_key == "default":
            self._write_config_file(config_file, "", delete_on_empty=True)
            self.print_success("已清除 go 的镜像源配置 (恢复官方源)")
            return True

        content = f"GOPROXY={source_info['url']}\n"
        if self._write_config_file(config_file, content):
            self.print_success(f"已成功设置 go 源为: {source_info['name']}")
            print(f"配置文件位置: {config_file}")
            return True
        return False

    def switch_conda(self, source_key: str, scope: ScopeType):
        source_info = self.tools["conda"]["sources"][source_key]
        config_file = CONDA_CONFIG_FILE_GLOBAL if scope == "global" else CONDA_CONFIG_FILE_PROJECT

        if source_key == "default":
            self._write_config_file(config_file, "", delete_on_empty=True)
            self.print_success("已清除 conda 的镜像源配置 (恢复官方源)")
            return True

        content = f"""channels:
  - defaults
show_channel_urls: true
default_channels:
  - {source_info["url"]}
custom_channels:
  conda-forge: {source_info["url"]}
"""
        if self._write_config_file(config_file, content):
            self.print_success(f"已成功设置 conda 源为: {source_info['name']}")
            print(f"配置文件位置: {config_file}")
            return True
        return False

    # --- 交互步骤 ---

    def create_source_choices(self, tool_name: str, scope: ScopeType) -> list:
        choices = []
        current = self.get_source_file(tool_name, scope)

        sources = self.tools[tool_name]["sources"]
        for key, info in sources.items():
            label = f"{info['name']} ({key})"
            if key == current:
                label = f"{label} [当前]"
            if "推荐" in info.get("description", ""):
                label = f"{label} ← 推荐"

            choices.append({"name": label, "value": key})

        return choices

    def select_tool(self) -> Optional[str]:
        questions = [
            {
                "type": "list",
                "name": "tool",
                "message": "1. 选择要配置的包管理器",
                "choices": [
                    {"name": "查看所有当前状态 (三层检查)", "value": "status"},
                    {"name": "uv (Python 现代包管理器)", "value": "uv"},
                    {"name": "pip (Python 基础包管理器)", "value": "pip"},
                    {"name": "npm (Node.js 包管理器)", "value": "npm"},
                    {"name": "cargo (Rust 包管理器)", "value": "cargo"},
                    {"name": "go (Go 包管理器)", "value": "go"},
                    {"name": "conda (Conda 环境管理器)", "value": "conda"},
                    {"name": "退出", "value": "exit"},
                ],
            }
        ]
        result = prompt(questions)
        return result.get("tool") if result else None

    def select_scope(self) -> Optional[ScopeType]:
        questions = [
            {
                "type": "list",
                "name": "scope",
                "message": "2. 选择目标作用域",
                "choices": [
                    {"name": f"项目级 (Local) -> 仅针对当前文件夹生效", "value": "project"},
                    {"name": f"用户级 (Global) -> 针对当前用户的全局环境生效", "value": "global"},
                ],
            }
        ]
        result = prompt(questions)
        return result.get("scope") if result else None

    def select_source(self, tool_name: str, scope: ScopeType) -> Optional[str]:
        choices = self.create_source_choices(tool_name, scope)
        questions = [
            {
                "type": "list",
                "name": "source",
                "message": f"3. 选择 {tool_name} 的镜像源 ({'项目级' if scope == 'project' else '用户级'})",
                "choices": choices,
            }
        ]
        result = prompt(questions)
        return result.get("source") if result else None

    def confirm_switch(self, tool_name: str, source_key: str, scope: ScopeType) -> bool:
        source_info = self.tools[tool_name]["sources"][source_key]
        scope_str = "项目级 (Project/Local)" if scope == "project" else "用户级全局 (Global)"
        
        print(f"\n{Fore.CYAN}=== 准备切换 ==={Style.RESET_ALL}")
        print(f"[{Fore.YELLOW}作用范围{Style.RESET_ALL}] {scope_str}")
        print(f"[{Fore.MAGENTA}目标工具{Style.RESET_ALL}] {tool_name}")
        print(f"[{Fore.GREEN}选中镜像{Style.RESET_ALL}] {source_info['name']} ({source_key})")
        print(f"[{Fore.CYAN}配置 URL{Style.RESET_ALL}] {source_info['url']}\n")

        questions = [
            {
                "type": "confirm",
                "name": "confirm",
                "message": "确认执行切换？",
                "default": True,
            }
        ]
        result = prompt(questions)
        return result.get("confirm") if result else False

    def run_interactive(self):
        self.print_header()

        while True:
            # 步骤 1: 选择工具 (或查看状态)
            tool = self.select_tool()
            if not tool or tool == "exit":
                print(f"\n{Fore.GREEN}感谢使用 Mirror Switch，再见！{Style.RESET_ALL}\n")
                return

            if tool == "status":
                self.show_status()
                continue

            # 步骤 2: 选择全局还是项目级
            scope = self.select_scope()
            if not scope:
                continue

            # 步骤 3: 选择具体源
            source = self.select_source(tool, scope)
            if not source:
                continue

            # 步骤 4: 确认切换
            if self.confirm_switch(tool, source, scope):
                if tool == "uv":
                    self.switch_uv(source, scope)
                elif tool == "pip":
                    self.switch_pip(source, scope)
                elif tool == "npm":
                    self.switch_npm(source, scope)
                elif tool == "cargo":
                    self.switch_cargo(source, scope)
                elif tool == "go":
                    self.switch_go(source, scope)
                elif tool == "conda":
                    self.switch_conda(source, scope)
                
                print()

            # 是否继续配置其他
            questions = [
                {
                    "type": "confirm",
                    "name": "continue",
                    "message": "是否继续配置其他源？",
                    "default": False,
                }
            ]
            result = prompt(questions)
            if not result or not result.get("continue"):
                print(f"\n{Fore.GREEN}配置完成，享受极速下载吧！{Style.RESET_ALL}\n")
                break

def main():
    switcher = MirrorSwitch()
    args = sys.argv[1:]

    # 处理帮助/查看参数
    if len(args) > 0 and args[0] in ["-h", "--help", "help", "status"]:
        if args[0] == "status":
            switcher.show_status()
            return
            
        print(f"\n{Style.BRIGHT}Mirror Switch - 镜像源切换工具{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}使用方法:{Style.RESET_ALL}")
        print("  mirror-switch          # 进入交互式配置模式")
        print("  mirror-switch status   # 直接查看当前各工具的配置状态 (三层检查)")
        return

    switcher.run_interactive()

if __name__ == "__main__":
    main()

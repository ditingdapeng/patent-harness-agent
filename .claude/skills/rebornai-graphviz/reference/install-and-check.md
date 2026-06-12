# Graphviz 安装与检测

## 1. 目标

本文件解决三个问题：

- **[安装]**：如何在 Windows、Linux、macOS 安装 Graphviz
- **[检测]**：如何确认 `dot` 已经可用
- **[执行]**：如何把 `.dot` 文件转为 `png`，并保证 `dpi >= 300`

## 2. Windows

### 2.1 推荐安装方式

任选一种即可：

- **[winget]**：`winget install Graphviz.Graphviz`
- **[Chocolatey]**：`choco install graphviz`
- **[Scoop]**：`scoop install graphviz`
- **[官网安装包]**：从 Graphviz 官方发布页下载安装包，安装后确认 `dot` 已进入 `PATH`

### 2.2 检测命令

- **[PowerShell 命令发现]**：`Get-Command dot`
- **[Windows 路径检测]**：`where dot`
- **[版本检测]**：`dot -V`

## 3. macOS

### 3.1 推荐安装方式

- **[Homebrew]**：`brew install graphviz`

### 3.2 检测命令

- **[路径检测]**：`which dot`
- **[版本检测]**：`dot -V`

## 4. Linux

### 4.1 Debian / Ubuntu

- **[apt]**：`sudo apt-get update && sudo apt-get install -y graphviz`

### 4.2 Fedora / RHEL / Rocky / AlmaLinux / CentOS Stream

- **[dnf]**：`sudo dnf install -y graphviz`
- **[yum]**：`sudo yum install -y graphviz`

### 4.3 Arch Linux

- **[pacman]**：`sudo pacman -S graphviz`

### 4.4 openSUSE

- **[zypper]**：`sudo zypper install graphviz`

### 4.5 检测命令

- **[路径检测]**：`command -v dot`
- **[版本检测]**：`dot -V`

## 5. 推荐检测流程

1. **[先跑脚本]**：`python .claude/skills/rebornai-graphviz/scripts/check_graphviz.py`
2. **[缺失则安装]**：根据当前操作系统执行对应安装命令
3. **[刷新终端环境]**：必要时重新打开终端或 shell，确保 `PATH` 生效
4. **[再次验证]**：重新执行 `dot -V`

## 6. 最小可用转换命令

### 6.1 原生命令

```bash
dot -Tpng -Gdpi=300 input.dot -o output.png
```

### 6.2 项目内推荐脚本

```bash
python .claude/skills/rebornai-graphviz/scripts/render_dot.py --input ai_think/20260307/dot/example.dot --output ai_think/20260307/images/example.png --dpi 300
```

## 7. 常见问题

- **[找不到 dot]**
  - 原因通常是 Graphviz 未安装，或安装后 `PATH` 未刷新
  - 先执行 `dot -V`，再检查 `where dot`、`which dot`、`command -v dot`

- **[图片分辨率太低]**
  - 必须显式设置 `-Gdpi=300` 或更高
  - 如果输出用于文档沉淀，禁止低于 `300`

- **[Markdown 引用了 dot]**
  - Markdown 中应引用 `png`
  - `.dot` 作为源文件保留，不直接作为渲染图片嵌入

- **[中文字体显示不稳定]**
  - 在 `.dot` 中显式指定字体更稳妥，例如 `fontname="Microsoft YaHei"`
  - 在不同平台渲染时，若字体不同，图形布局可能轻微变化

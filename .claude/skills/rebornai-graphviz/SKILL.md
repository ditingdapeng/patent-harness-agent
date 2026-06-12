---
name: rebornai-graphviz
description: Creates and maintains Graphviz .dot source files and high-resolution PNG diagrams for Markdown documentation. Use when a task needs flowcharts, architecture diagrams, ER diagrams, class diagrams, sequence diagrams, state diagrams, or when .dot files must be rendered to png with dpi >= 300 in ai_think/YYYYMMDD.
argument-hint: "[target-md-or-topic] [date-or-output-root]"
---

# Graphviz Diagramming

This skill standardizes how diagrams are created, rendered, and referenced in this project.

## Core objectives
- Create a `.dot` source file first.
- Render a `png` from the `.dot` with `dpi >= 300`.
- Keep the `.dot` and `.png` files on the same basename.
- Make Markdown reference the rendered `png`, not the `.dot`.
- Prefer a higher-level output convention if the task, surrounding documents, or existing artifact set already defines one.

## Output convention
1. If the user, the target document set, or an existing folder convention already defines output directories, follow that convention first.
2. Otherwise use the default project convention:
   - `ai_think/YYYYMMDD/dot/<name>.dot`
   - `ai_think/YYYYMMDD/images/<name>.png`
3. If an existing artifact set already uses `png/` instead of `images/`, stay consistent within that artifact set rather than mixing directory names.
4. The `.dot` and `.png` files must share the same basename.

## Required workflow
1. Determine the target Markdown file and the governing output convention.
2. Choose the diagram type: architecture, flow, sequence, ER, class, state, or data flow.
3. Write or update the `.dot` file first.
4. Check whether Graphviz is installed:
   - Read [reference/install-and-check.md](reference/install-and-check.md)
   - Or run `python .claude/skills/rebornai-graphviz/scripts/check_graphviz.py`
5. Render the `.png` with `dpi >= 300`:
   - Run `python .claude/skills/rebornai-graphviz/scripts/render_dot.py --input <dot-file> --output <png-file> --dpi 300`
6. Confirm the render succeeded and the Markdown references the `.png`.
7. If the task edits Markdown, insert the image link and keep the `.dot` file in place for future edits.

## Markdown rule
- Good: `![流程图](./images/backend-overview.png)`
- Good: `![流程图](../images/backend-overview.png)` when the Markdown file is in a child directory such as `backend/`
- Avoid using the `.dot` file directly in the image tag
- If helpful, mention the source `.dot` in plain text near the image

## HTML-like label 排版参考

当使用 `subgraph cluster_*` 无法满足等宽对齐等需求时，改用 HTML TABLE label（`shape=plaintext, label=<TABLE ...>`）。以下是关键属性速查：

### 文字对齐
| 属性 | 作用域 | 说明 |
|------|--------|------|
| `ALIGN="CENTER"` | TABLE / TD | 居中**文本块整体**在单元格中的位置（默认值） |
| `BALIGN="CENTER"` | TD only | 居中**多行文本每一行**（`<BR/>` 分隔的行默认左对齐，必须用 BALIGN 修正） |
| `VALIGN="MIDDLE"` | TABLE / TD | 垂直居中（默认值） |

### 常见陷阱
- **多行文字不居中**：只写 `ALIGN="CENTER"` 不够，多行文本（含 `<BR/>`）的每行仍左对齐 → 必须加 `BALIGN="CENTER"`
- **cluster 不等宽**：Graphviz cluster 宽度由内容撑开，无法跨 cluster 强制等宽 → 改用单个 HTML TABLE 节点，用 `COLSPAN` 控制列宽
- **中文字体**：`.dot` 中显式指定 `fontname="PingFang SC,Helvetica Neue,Arial,sans-serif"`

### 参考文档
- 属性完整列表：https://graphviz.org/doc/info/shapes.html#html
- 节点/边/图属性：https://graphviz.org/doc/info/attrs.html

## When to load more detail
- Installation and detection: [reference/install-and-check.md](reference/install-and-check.md)
- Directory layout, rendering rules, compatibility handling, and Markdown integration: [reference/workflow-and-paths.md](reference/workflow-and-paths.md)

## Available utility scripts
- `scripts/check_graphviz.py`
- `scripts/render_dot.py`

Use these scripts instead of re-creating ad hoc conversion logic unless the task explicitly requires a different implementation.

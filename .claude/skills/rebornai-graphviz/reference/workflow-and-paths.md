# Graphviz 工作流与路径约定

## 1. 总原则

- **[上层约定优先]**：如果用户、父级任务、现有文档集已经明确约定输出目录，优先遵守现有约定。
- **[默认约定]**：如果没有更高优先级约定，使用：
  - `ai_think/YYYYMMDD/dot`
  - `ai_think/YYYYMMDD/images`
- **[命名一致]**：`.dot` 与 `.png` 必须同名，仅后缀不同。
- **[引用一致]**：Markdown 引用 `png`，不要直接把 `.dot` 放进图片链接。
- **[不混用目录]**：同一组产物里不要同时混用 `images/` 和 `png/`。

## 2. 标准工作流

1. **[锁定目标文档]**：明确要生成或更新的 Markdown 文件位置。
2. **[确定日期目录]**：通常是 `ai_think/YYYYMMDD`，例如 `ai_think/20260307`。
3. **[确定图名]**：选择稳定、语义化的 basename，例如 `backend-overview`、`document-pipeline`。
4. **[先写 dot]**：先生成 `.dot` 源文件。
5. **[再转 png]**：使用 Graphviz 渲染，并显式设置 `dpi >= 300`。
6. **[回写 Markdown]**：在 Markdown 中插入 `png` 图片引用。
7. **[保留源文件]**：后续所有图修改都以 `.dot` 为准，不直接手改图片。

## 3. 默认路径映射示例

- **[日期目录根文档]**
  - Markdown：`ai_think/20260307/summary.md`
  - Dot：`ai_think/20260307/dot/backend-overview.dot`
  - PNG：`ai_think/20260307/images/backend-overview.png`
  - Markdown 引用：`![后端架构图](./images/backend-overview.png)`

- **[日期目录子文档]**
  - Markdown：`ai_think/20260307/backend/overview.md`
  - Dot：`ai_think/20260307/dot/backend-overview.dot`
  - PNG：`ai_think/20260307/images/backend-overview.png`
  - Markdown 引用：`![后端架构图](../images/backend-overview.png)`

## 4. 与历史产物兼容

当前仓库中已经存在 `ai_think/20260306/dot` 与 `ai_think/20260306/png` 的历史实践。

因此需要遵守下面的兼容规则：

- **[维护旧文档]**：如果你是在维护已存在的 `png/` 产物集，就继续沿用 `png/`，不要半路改成 `images/`
- **[新文档新约定]**：如果没有历史约束，优先使用本 skill 的默认新约定 `images/`
- **[同一文档集一致]**：一个日期目录或一组交付物内部必须统一

## 5. 推荐命令

### 5.1 原生命令

```bash
dot -Tpng -Gdpi=300 ai_think/20260307/dot/backend-overview.dot -o ai_think/20260307/images/backend-overview.png
```

### 5.2 项目内脚本

```bash
python .claude/skills/rebornai-graphviz/scripts/render_dot.py --input ai_think/20260307/dot/backend-overview.dot --output ai_think/20260307/images/backend-overview.png --dpi 300
```

## 6. 质量门禁

在结束前至少确认以下事项：

- **[源文件存在]**：`.dot` 文件已生成并保存
- **[图片存在]**：`.png` 文件已成功渲染
- **[分辨率合规]**：`dpi >= 300`
- **[命名合规]**：`.dot` 与 `.png` 同 basename
- **[引用合规]**：Markdown 引用的是 `png`
- **[路径合规]**：相对路径与 Markdown 实际所在位置一致
- **[更新闭环]**：图修改后已经重新渲染图片

## 7. 与 Johari 文档联动

当 Johari 类文档中出现以下任一图形需求时，都应先走本工作流：

- **[流程图]**
- **[架构图]**
- **[时序图]**
- **[类图]**
- **[状态图]**
- **[ER 图]**
- **[数据流图]**

先生成 `.dot`，再转为 `png`，最后在 Markdown 中引用 `png`。

# 专利交底书生成 Harness

## 0. 项目目标

从三个输入源生成一份符合专利局要求的专利技术方案交底书：

- `doc/`：已有成型交底书（风格和写法参考，只读）
- `model/专利技术方案交底书模板.docx`：章节结构和模板约束（只读）
- `content/`：本次专利的技术内容素材（只读）

最终输出：`res/专利交底书.docx`

本 Harness 的目标是通过可追踪、可验证、可回滚的多 Agent DAG Workflow 生成专利，而不是一次性提示词生成。

---

## 1. 绝对禁止事项

1. 禁止修改 `doc/`、`model/`、`content/` 下的任何文件
2. 禁止残留任何 `【...】` 占位符进入最终文档
3. 禁止跳过 Review 直接输出 `res/专利交底书.docx`
4. 禁止 Revision 后不回到 Review
5. 禁止 Agent 自写 `completion_signal=true` 作为完成证据
6. 禁止未经人工确认将外部专利/论文/竞品写成确定性事实
7. 禁止擅自修正模板中的重复章节编号（如 `2.3` 重复出现属正常）
8. 禁止直接覆盖最终文件，必须先写 `.tmp_` 临时文件并验证后发布

---

## 2. 路径白名单

**只读（不得修改）：**
- `doc/*.docx`
- `model/*.docx`
- `content/**`
- `.claude/skills/**`

**可写：**
- `AGENTS.md`（活文档，失败后追加防错条目）
- `feature_list.json`
- `progress.md`
- `session-handoff.md`
- `workflow/**`
- `intermediate/**`
- `scripts/**`
- `ai_think/**`
- `res/.tmp_专利交底书.docx`
- `res/专利交底书.docx`（仅 Release 节点写入）

---

## 3. 模板硬约束

模板章节结构（以实际抽取结果为准）：

| 章节 | 内容 |
|------|------|
| 基本信息 | 发明名称、所属产品、提交部门、提交人、联系方式（人工填写） |
| 一、发明目的 | |
| 1.1 | 解决的技术问题以及应用产品、应用场景 |
| 1.2 | 现有技术或产品的实现方案（三种以上） |
| 1.3 | 现有技术或产品的缺点（与 1.2 一一对应） |
| 二、发明内容 | |
| 2.1 | 完整技术实现方案（后台为主，三级子节展开） |
| 2.2 | 产品使用或交互方案（前端为主） |
| 2.3 | 附图说明 |
| 2.3 或 2.4 | 产品帮助（模板编号以实际为准，可能与上一个 2.3 编号相同） |
| 2.4 | 替代方案 |
| 三、业界检索 | |
| 3.1 | 竞争对手或相关产品 |
| 3.2 | 现有专利及科技论文 + 区别点 |

**重要**：章节编号以模板实际抽取结果为准，不得自行修正。

---

## 4. 专利逻辑依赖

```
1.1 技术问题  →  1.2 现有技术  →  1.3 缺点
                                       ↓
                              2.1 后台技术方案  ←─ 必须逐项回应 1.3
                                       ↓
                              2.2 前端交互方案  ←─ 必须回应 1.3 + 与 2.1 闭环
                                       ↓
                              2.3 附图说明  ←─ 必须覆盖 2.1/2.2 关键步骤
                                       ↓
                              2.4 替代方案  ←─ 基于 2.1/2.2 提出变体
                                       ↓
                              3.2 区别点  ←─ 基于 2.1/2.2 + 检索结果
```

强制规则：
- `1.3` 每个缺点必须有对应 `1.2` 方案
- `2.1` 必须逐项回应 `1.3` 所有缺点
- `2.2` 每个关键步骤必须关联 `2.1` 模块和 `1.3` 缺点
- `3.2` 区别点必须引用 `2.1`/`2.2` 具体技术手段

---

## 5. Workflow DAG

```
START
  ↓
feat-001: ManifestAgent（抽取模板约束和输入清单）
  ↓
feat-002: SkeletonAgent（章节骨架 + 术语表 + traceability_seed）
  ↓
feat-003: D0PriorArtBaselineAgent（1.2/1.3 基线，固定 defect_id）
  ↓──────────────────────────────────────
  ├── feat-004A: PurposeAgent（1.1）
  ├── feat-004B: BackendSolutionAgent（2.1）
  ├── feat-004C: FrontendInteractionAgent（2.2）
  └── feat-004D: ResearchAgent（3.1/3.2 深度检索）
  ↓（等待 B/C 完成）
  ├── feat-005E: FigureAgent（2.3 附图）
  ↓（等待 B/C/D 完成）
  └── feat-005F: AlternativeAgent（2.4 + 3.2 区别点）
  ↓
feat-006: ReviewAgent（对抗审查）
  ├── pass ──────────────────────────────→ feat-008: Release
  ├── fix_required → feat-007: RevisionAgent → feat-006
  ├── human_required → 人工确认 → feat-006
  └── fail → FailExit
```

关键约束：
- D0 必须在 B/C 之前完成，提供 `defect_id` 供其引用
- D（深度检索）与 A/B/C 并行，但不得修改 D0 已固定的 `1.3` 编号
- Revision 后必须回到 Review，不能直接发布

---

## 6. Agent 职责摘要

| Agent | 职责 | 只读输入 | 可写输出 |
|-------|------|---------|---------|
| ManifestAgent | 解析模板结构和参考文档风格 | doc/, model/ | intermediate/00_manifest/ |
| SkeletonAgent | 发明主题、核心 claim、术语、边界 | manifest, content/ | intermediate/01_skeleton/ |
| D0PriorArtBaselineAgent | 1.2/1.3 基线，固定 defect_id | skeleton, content/ | intermediate/02_prior_art_baseline/ |
| PurposeAgent (A) | 1.1 技术问题+应用场景 | skeleton, D0 baseline | intermediate/03_parallel/A_purpose/ |
| BackendSolutionAgent (B) | 2.1 后台技术方案（三级子节） | skeleton, D0 baseline, content/ | intermediate/03_parallel/B_backend/ |
| FrontendInteractionAgent (C) | 2.2 前端交互方案 | skeleton, D0 baseline, B outputs | intermediate/03_parallel/C_frontend/ |
| ResearchAgent (D) | 3.1 竞品 + 3.2 深度检索 | skeleton, D0 baseline | intermediate/03_parallel/D_research/ |
| FigureAgent (E) | 2.3 附图说明 + Graphviz | B, C outputs | intermediate/04_derived/E_figures/, ai_think/ |
| AlternativeAgent (F) | 2.4 替代方案 + 3.2 区别点精修 | B, C, D outputs | intermediate/04_derived/F_alternatives/ |
| ReviewAgent | 对抗审查，生成 revision_tasks | A-F 全部产物 | intermediate/05_review/ |
| RevisionAgent | 逐项修订，组装 final_payload | Review 报告, A-F | intermediate/06_revision/, res/.tmp_*.docx |
| ReleaseAgent | 验证通过后原子发布 | final_payload, tmp docx | res/专利交底书.docx, intermediate/07_release/ |

---

## 7. 质量门禁

| 级别 | 说明 | 处理 |
|------|------|------|
| P0 阻断 | 模板章节缺失/占位符残留/1.2-1.3 错位/2.1 未回应 1.3/修改只读目录/未重新 Review | 不得 Release |
| P1 人工确认 | 实体附图缺失/外部专利论文竞品未确认/封面人工字段缺失 | 进入 human_confirmation.md |
| P2 优化 | 表达不够专利化/篇幅不足/术语轻微重复 | 作为建议，不阻断 |

---

## 8. 节点完成判定

节点不能自我声明完成。完成由验证脚本写入：

```json
{
  "verified_done": true,
  "verified_by": "scripts/verify_xxx.py",
  "artifact_hash": "...",
  "verification_log": "..."
}
```

---

## 9. 会话生命周期

**每次会话开始：**
1. 读 `AGENTS.md`
2. 读 `session-handoff.md`
3. 读 `feature_list.json`，选第一个 `status=pending` 的可运行节点
4. 运行验证命令确认基线

**每次会话结束：**
1. 运行该节点验证命令
2. 更新 `feature_list.json` 状态和 evidence
3. 追加 `progress.md`
4. 更新 `session-handoff.md`

**失败处理：**
- 同一类错误出现后，立即将防错规则追加到本文件底部

---

## 10. 完成定义

当前阶段（Harness 设计）完成：

- [x] `AGENTS.md` 存在
- [x] `feature_list.json` 存在
- [x] `workflow/patent-disclosure-workflow.md` 存在
- [x] `workflow/agent-contracts.md` 存在
- [x] `workflow/quality-gates.md` 存在
- [x] `session-handoff.md` 存在
- [x] `progress.md` 存在
- [x] `scripts/` 目录存在，各验证脚本职责已定义

下一阶段（专利生成执行）：

- 按 `feature_list.json` DAG 顺序执行
- 每个节点验证通过后才推进
- 最终通过 Release 节点生成 `res/专利交底书.docx`

---

## 附录：防错记录（活文档，失败后追加）

### ERR-001: python-docx 图片插入 API 变更（2026-06-12）

**现象**：FigureAgent/ReleaseAgent 使用 `doc.part.get_or_add_image_part()` 或手动拼 `wp:inline` XML 插入图片失败。

**根因**：python-docx 1.2.0 移除了 `get_or_add_image_part` 旧内部 API，手动拼 DrawingML XML 依赖过时接口。

**正确做法**：
```python
# 先用官方 API 追加图片到文档末尾（自动处理关系和嵌入）
doc.add_picture(img_path, width=Inches(5.5))
# 再用 lxml 移动到目标段落之后
last_p = doc.element.body[-1]
target_paragraph._element.addnext(last_p)
```

**规则**：插入图片到 docx 时，禁止使用 `get_or_add_image_part`、禁止手动拼 `wp:inline` XML。必须使用 `doc.add_picture()` + 元素位置移动的两步法。

---

### ERR-002: [待人工确认] 标记必须在 Release 前解决，不得带入最终文档（2026-06-12）

**现象**：ReleaseAgent 将含 `[待人工确认]` 标记的内容直接写入最终 docx，用户需要事后手动清理。

**根因**：AGENTS.md 允许 `human_required` 出口生成临时文件，但未禁止带标记发布。导致"先生成再清理"的错误流程。

**正确做法**：
1. `[待人工确认]` 内容属于 P1 门禁，有两种合规处理方式：
   - **方式 A（人工确认）**：暂停流程，等用户提供真实信息后替换标记，再继续 Release
   - **方式 B（删除）**：用户明确指示"不需要该内容"时，从正文中彻底删除该段落/单元格
2. 两种方式必须在 `res/.tmp_专利交底书.docx` 阶段完成，不得带入 `res/专利交底书.docx`

**规则**：
- ReleaseAgent 发布前必须扫描 docx 全文（段落+表格），确认 0 处 `[待人工确认]` / `[待人工]` / `[待填写]` 标记
- 若扫描到标记 → 阻断 Release，输出标记清单，请求用户选择方式 A 或方式 B
- 禁止自动静默删除人工确认标记（必须有用户明确指令）
- 禁止自动填充虚假信息替代人工确认标记

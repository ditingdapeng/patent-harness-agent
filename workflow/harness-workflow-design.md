# 专利交底书生成 Harness — Workflow 与出口系统设计

> **目标**：将 `content/reborn-harness` 的 Harness Engineering 技术内容，基于 `model/专利技术方案交底书模板.docx` 模板，参考 `doc/` 已有专利风格，生成 `res/专利交底书.docx`。

---

## 1. Workflow 全景架构

![专利Harness Workflow全景](../ai_think/20260612/images/patent_harness_workflow.png)

> 源文件：`ai_think/20260612/dot/patent_harness_workflow.dot`

---

## 2. 四阶段 DAG 编排

### 阶段零：串行·骨架（Phase 0）

| 节点 | Agent | 输入 | 输出 | 出口条件 |
|------|-------|------|------|---------|
| feat-001 | ManifestAgent | `doc/*.docx` `model/*.docx` | `intermediate/00_manifest/` | 模板章节全抽取，占位符全记录 |
| feat-002 | SkeletonAgent | manifest + `content/` | `intermediate/01_skeleton/` | 骨架覆盖全章节，前后端边界明确 |
| feat-003 | D0PriorArtBaseline | skeleton + `content/` | `intermediate/02_prior_art_baseline/` | defect_id 固定，1.2/1.3 一一对应 |

**设计原因**：模板要求 2.1(后台) 和 2.2(前端) 分开写，必须先划清边界；1.3 缺点编号是后续所有方案引用的锚点，必须冻结。

---

### 阶段一：半并行·生成（Phase 1）

```
feat-003 完成
    ├── feat-004A: PurposeAgent (1.1)          ─┐
    ├── feat-004B: BackendSolutionAgent (2.1)   │ 并行启动
    ├── feat-004C: FrontendInteractionAgent (2.2)│ C 弱依赖 B 的边界
    └── feat-004D: ResearchAgent (3.1/3.2)     ─┘
              │
              │ 等待 B/C 完成
              ├── feat-005E: FigureAgent (2.3)
              │
              │ 等待 B/C/D 完成
              └── feat-005F: AlternativeAgent (2.4 + 3.2区别点)
```

**调度规则**：
- A/B/C/D 由 `parallel()` 并发派发，写隔离目录互不干扰
- C 可读 B 的 `backend_solution.json` 作为边界参考（弱依赖，B 未完成时 C 仍可用 skeleton）
- E 和 F 用 `pipeline()` 在前置依赖完成后立即触发

---

### 阶段二：Adversarial 审查（Phase 2）

| 节点 | Agent | 检查项 |
|------|-------|--------|
| feat-006 | ReviewAgent | ① 1.3缺点→2.1方案覆盖 ② 2.1↔2.2数据流闭环 ③ 附图覆盖率 ④ 区别点成立性 ⑤ 术语一致性 ⑥ 保护范围过度限定 ⑦ 占位符残留 ⑧ 外部事实确认 |
| feat-007 | RevisionAgent | 逐项处理 revision_tasks → 生成 `res/.tmp_专利交底书.docx` |

**Review↔Revision 闭环**：最多 3 轮；超出强制进入人工确认出口。

---

### 阶段三：发布（Phase 3）

| 节点 | Agent | 触发条件 |
|------|-------|---------|
| feat-008 | ReleaseAgent | review pass + 全部验证脚本通过 + 输入目录哈希不变 |

---

## 3. 出口设计（Exit Design）

### 3.1 四种出口

```
                    ┌─────────────────────────┐
                    │      ReviewAgent        │
                    │   (feat-006 审查)       │
                    └─────────┬───────────────┘
                              │
          ┌───────────────────┼───────────────────┬──────────────────┐
          ▼                   ▼                   ▼                  ▼
   ┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌───────────┐
   │ 成功出口     │   │ 修订出口     │   │ 人工确认出口   │   │ 失败出口  │
   │ pass ✓      │   │ fix_required │   │ human_required │   │ fail ✗   │
   └──────┬──────┘   └──────┬───────┘   └───────┬───────┘   └─────┬─────┘
          │                  │                   │                  │
          ▼                  ▼                   ▼                  ▼
   ReleaseAgent        RevisionAgent      human_confirmation   failure.json
   res/专利交底书.docx   → 重回 Review        .md 等人工        不生成 res/
```

### 3.2 出口触发条件

| 出口 | 触发条件 | 后续动作 |
|------|---------|---------|
| **成功** (`pass`) | P0 全pass + P1 全pass/human_confirmed | ReleaseAgent 原子发布 |
| **修订** (`fix_required`) | P0 有 fail | RevisionAgent 修订后重新 Review |
| **人工** (`human_required`) | P1 未确认 或 修订超 3 轮 | 写 `human_confirmation.md`，等人工 |
| **失败** (`fail`) | 结构性错误不可自动修复 | 写 `failure.json`，终止 |

### 3.3 每节点微观出口

每个 Agent 节点产物必须携带标准出口信号：

```json
{
  "node_id": "feat-004B",
  "claimed_done": true,
  "verified_done": false,    // 只能由验证脚本写入
  "verified_by": null,
  "artifact_hash": null,
  "warnings": []
}
```

节点失败时写入 `failure.json`：
```json
{
  "status": "failed",
  "blocking": true,
  "retry_count": 1,
  "max_retries": 2,
  "recover_suggestion": "..."
}
```

---

## 4. Workflow Script 设计（Claude Code 实现）

```javascript
export const meta = {
  name: 'patent-disclosure-gen',
  description: '专利交底书生成 — 四阶段DAG编排+对抗审查闭环',
  phases: [
    { title: '骨架', detail: 'ManifestAgent → SkeletonAgent → D0Baseline' },
    { title: '并行生成', detail: 'Purpose/Backend/Frontend/Research 并行' },
    { title: '衍生', detail: 'FigureAgent + AlternativeAgent' },
    { title: '审查', detail: 'ReviewAgent 对抗检查' },
    { title: '修订', detail: 'RevisionAgent 逐项修订' },
    { title: '发布', detail: 'ReleaseAgent 原子发布' },
  ],
}

// ── Phase 0: 串行骨架 ──
phase('骨架')
const manifest = await agent('ManifestAgent: 解析模板约束和参考风格', {
  schema: MANIFEST_SCHEMA
})
const skeleton = await agent('SkeletonAgent: 生成骨架+术语+边界', {
  schema: SKELETON_SCHEMA
})
const d0baseline = await agent('D0PriorArtBaseline: 固定1.2/1.3基线', {
  schema: D0_SCHEMA
})

// ── Phase 1: 半并行生成 ──
phase('并行生成')
const [purposeResult, backendResult, frontendResult, researchResult] = await parallel([
  () => agent('PurposeAgent: 1.1技术问题+应用场景', { schema: PURPOSE_SCHEMA }),
  () => agent('BackendSolutionAgent: 2.1后台三级子节方案', { schema: BACKEND_SCHEMA }),
  () => agent('FrontendInteractionAgent: 2.2前端交互方案', { schema: FRONTEND_SCHEMA }),
  () => agent('ResearchAgent: 3.1竞品+3.2专利论文检索', { schema: RESEARCH_SCHEMA }),
])

// ── Phase 1.5: 衍生节点 ──
phase('衍生')
const [figureResult, altResult] = await parallel([
  () => agent('FigureAgent: 2.3附图说明+Graphviz', { schema: FIGURE_SCHEMA }),
  () => agent('AlternativeAgent: 2.4替代方案+3.2区别点', { schema: ALT_SCHEMA }),
])

// ── Phase 2: 审查闭环 ──
phase('审查')
let reviewResult = await agent('ReviewAgent: 对抗审查6项检查', { schema: REVIEW_SCHEMA })
let rounds = 0

while (reviewResult.status === 'fix_required' && rounds < 3) {
  phase('修订')
  await agent('RevisionAgent: 处理revision_tasks', { schema: REVISION_SCHEMA })
  rounds++
  phase('审查')
  reviewResult = await agent('ReviewAgent: 第' + (rounds+1) + '轮重审', { schema: REVIEW_SCHEMA })
}

if (reviewResult.status === 'pass') {
  phase('发布')
  await agent('ReleaseAgent: 验证+原子发布res/专利交底书.docx', { schema: RELEASE_SCHEMA })
  log('✓ 专利交底书已发布至 res/专利交底书.docx')
} else if (reviewResult.status === 'human_required' || rounds >= 3) {
  log('⚠ 需人工确认，详见 intermediate/07_release/human_confirmation.md')
} else {
  log('✗ 生成失败，详见 intermediate/05_review/review_report.json')
}
```

---

## 5. 质量门禁与 Workflow 的绑定

| 门禁级别 | 检查时机 | 对 Workflow 出口的影响 |
|---------|---------|---------------------|
| **P0 阻断** | ReviewAgent 执行时 | 任一 P0 fail → `fix_required` 出口 |
| **P1 人工** | ReviewAgent 执行时 | 任一 P1 未确认 → `human_required` 出口 |
| **P2 建议** | ReviewAgent 执行时 | 不影响出口，记入 `review_report.md` |

验证脚本在 Review 中被调用：
- `verify_scope.py` → 确认输入只读
- `verify_structure.py` → 章节完整性
- `verify_fields.py` → 无占位符残留
- `verify_traceability.py` → 逻辑闭环
- `verify_graphviz.py` → 附图可渲染
- `verify_output.py` → docx 可打开

---

## 6. Skill 集成

| Skill | 在 Workflow 中的角色 |
|-------|-------------------|
| `reborn-harness` | 提供五大子系统框架、AGENTS.md 设计、feature_list DAG 管理、验证命令生成 |
| `rebornai-graphviz` | FigureAgent (feat-005E) 生成系统架构图、流程图、状态机图 |
| `docx` | RevisionAgent/ReleaseAgent 生成和操作 .docx 最终文件 |

---

## 7. 数据流概览

```
content/reborn-harness/ ──读──→ SkeletonAgent → 骨架
                                    ↓
doc/*.docx ──风格参考──→ ManifestAgent → 模板约束
                                    ↓
model/*.docx ──结构约束──→ ManifestAgent ─┘
                                    ↓
                          D0Baseline → defect_id 锚点
                                    ↓
                    ┌───────────────────────────────┐
                    │  B(后台) / C(前端) / D(检索)   │
                    └───────────────────────────────┘
                                    ↓
                    ┌───────────────────────────────┐
                    │  E(附图) / F(替代方案+区别点)  │
                    └───────────────────────────────┘
                                    ↓
                          ReviewAgent → 审查报告
                                    ↓
                          RevisionAgent → .tmp_docx
                                    ↓
                          ReleaseAgent → res/专利交底书.docx
```

---

## 8. 与 feature_list.json 的映射

Workflow 的每个 `phase()` / `agent()` 调用与 `feature_list.json` 中的 feat-ID 一一对应。Workflow 执行过程中：

1. 进入节点前：`feature_list.json` 中该节点 `status` 设为 `in_progress`
2. Agent 产物生成后：`claimed_done: true`
3. 验证脚本通过后：`verified_done: true` + `evidence` 写入
4. 失败时：`status` 保持 `in_progress`，写 `failure.json`

这保证了 Workflow 中断后可从 `feature_list.json` 中恢复执行位置。

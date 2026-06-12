# Agent 输入输出契约

## ManifestAgent (feat-001)

**输入：**
- `doc/*.docx` — 提取章节结构、写作风格（只读）
- `model/专利技术方案交底书模板.docx` — 提取模板章节、字段、占位符（只读）

**输出：**
```
intermediate/00_manifest/
├── manifest.json              # 输入路径清单、文件哈希
├── template_constraints.json  # 章节编号、必须字段、禁止事项
└── reference_style.json       # 参考文档的写作风格摘要
```

**完成条件：**
- 模板所有章节已抽取
- 所有占位符已识别并记录
- 参考文档风格（1.1/1.2/1.3/2.1/2.2 段落数量、表达方式）已记录

---

## SkeletonAgent (feat-002)

**输入：**
- `intermediate/00_manifest/`
- `content/reborn-harness/`（技术素材）

**输出：**
```
intermediate/01_skeleton/
├── skeleton.json          # 章节骨架（section_id → 内容方向）
├── section_plan.md        # 人类可读的章节规划
├── terminology.md         # 统一术语表
└── traceability_seed.json # 初始问题-方案-区别点映射种子
```

**完成条件：**
- 覆盖模板所有章节
- 明确 2.1（后台）与 2.2（前端）边界
- 技术问题 ≥ 3 个
- 现有技术方向 ≥ 3 个
- 术语表已建立

**约束：**
- Skeleton 产物一旦并行阶段启动，不得修改

---

## D0PriorArtBaselineAgent (feat-003)

**输入：**
- `intermediate/01_skeleton/`
- `content/reborn-harness/`

**输出：**
```
intermediate/02_prior_art_baseline/
├── prior_art_baseline.json   # defect_id → {prior_art, defect, pa_id} 映射
└── prior_art_baseline.md
```

**完成条件：**
- 现有技术方案 ≥ 3 种，每种有名称和实现原理
- 每种现有技术对应至少 1 个缺点
- 1.2/1.3 编号一一对应，固定 defect_id
- 包含"上述所有现有技术的共同缺点"总结段

**约束：**
- D0 产物一旦 B/C 开始引用，不得修改 defect_id 编号

---

## PurposeAgent (feat-004A)

**输入：**
- `intermediate/01_skeleton/`
- `intermediate/02_prior_art_baseline/`
- `intermediate/00_manifest/reference_style.json`

**输出：**
```
intermediate/03_parallel/A_purpose/
├── purpose.json   # 技术问题列表（problem_id → description）
└── purpose.md     # 1.1 正文草稿
```

**完成条件：**
- 包含"应用产品："段落
- 技术问题 ≥ 3 个，已编号
- 包含"应用场景："段落
- 每个 problem_id 可映射到 defect_id

---

## BackendSolutionAgent (feat-004B)

**输入：**
- `intermediate/01_skeleton/`
- `intermediate/02_prior_art_baseline/prior_art_baseline.json`（defect_id 清单）
- `content/reborn-harness/`（Harness 技术素材）

**输出：**
```
intermediate/03_parallel/B_backend/
├── backend_solution.json  # solution_module_id → {name, tech_means, role, effect, resolves_defect_ids}
└── backend_solution.md    # 2.1 正文草稿（含三级子节）
```

**完成条件：**
- 三级子节 ≥ 3 个（建议 2.1.1/2.1.2/2.1.3 等）
- 每个子节包含：技术手段、执行模块、作用、有益效果
- 每个 defect_id 至少被一个子节的 `resolves_defect_ids` 覆盖
- 字数建议 ≥ 800 字

---

## FrontendInteractionAgent (feat-004C)

**输入：**
- `intermediate/01_skeleton/`
- `intermediate/02_prior_art_baseline/prior_art_baseline.json`
- `intermediate/03_parallel/B_backend/backend_solution.json`（后台边界）

**输出：**
```
intermediate/03_parallel/C_frontend/
├── frontend_solution.json  # interaction_step_id → {step, backend_module, defect_id}
└── frontend_solution.md    # 2.2 正文草稿
```

**完成条件：**
- 每个关键交互步骤引用 ≥ 1 个后台模块 (`solution_module_id`)
- 每个关键交互步骤标注支撑的 defect_id 或有益效果
- 与 B 的数据流形成闭环（前端提交→后台处理→前端展示）

---

## ResearchAgent (feat-004D)

**输入：**
- `intermediate/01_skeleton/`
- `intermediate/02_prior_art_baseline/`

**输出：**
```
intermediate/03_parallel/D_research/
├── research.json   # 竞品列表、专利/论文候选（含可信度字段）、关键词
└── research.md     # 3.1 + 3.2 草稿
```

**完成条件：**
- 竞品 ≥ 2 个（含名称和相关性说明）
- 中文关键词和英文关键词均存在
- 每条专利/论文标注可信度：`confirmed` / `needs_human_confirmation` / `internal_reference_only`

**约束：**
- `needs_human_confirmation` 的条目不得进入最终确定性结论
- 竞品名称若未确认，写入 `human_confirmation.md` 等待人工核实

---

## FigureAgent (feat-005E)

**输入：**
- `intermediate/03_parallel/B_backend/`
- `intermediate/03_parallel/C_frontend/`

**输出：**
```
intermediate/04_derived/E_figures/
├── figures.json     # figure_id → {type, title, covers_modules, covers_steps}
└── figures.md       # 2.3 附图说明正文
ai_think/20260612/dot/*.dot   # Graphviz 源文件（使用 rebornai-graphviz skill）
ai_think/20260612/images/*.png # 渲染图（dpi ≥ 300）
```

**建议附图：**
- 图1：系统总体架构图
- 图2：五大子系统交互图（I/S/V/Sc/L）
- 图3：Workflow DAG 图（含出口）
- 图4：feature_list 状态转移图
- 图5：会话生命周期状态机

**完成条件：**
- 每个图有图号、类型、说明
- 每个图标注覆盖的 `solution_module_id` 或 `interaction_step_id`
- 无实体图片时，在 figures.json 中标注 `"status": "pending_human"`

---

## AlternativeAgent (feat-005F)

**输入：**
- `intermediate/03_parallel/B_backend/`
- `intermediate/03_parallel/C_frontend/`
- `intermediate/03_parallel/D_research/`

**输出：**
```
intermediate/04_derived/F_alternatives/
├── alternatives.json  # alternative_id → {desc, vs_main_approach}
│                      # distinction_id → {existing_tech, this_application, evidence_module}
└── alternatives.md    # 2.4 替代方案 + 3.2 区别点精修
```

**完成条件：**
- 替代方案 ≥ 1 个，且与主方案有明确差异
- 区别点采用"现有技术采用……本申请采用……"对比表达
- 不引用 `needs_human_confirmation` 来源作为强区别点

---

## ReviewAgent (feat-006)

**输入：**
- `intermediate/03_parallel/` （A/B/C/D 全部产物）
- `intermediate/04_derived/` （E/F 全部产物）
- `intermediate/01_skeleton/traceability_seed.json`
- `intermediate/00_manifest/template_constraints.json`

**输出：**
```
intermediate/05_review/
├── review_report.json    # 含 status, p0_gates, p1_gates, p2_suggestions
├── review_report.md
└── revision_tasks.json   # [{task_id, section, issue, severity, fix_suggestion}]
```

**检查项：**
1. 1.3 每个 defect_id 是否在 2.1 有对应方案
2. 1.3 每个 defect_id 是否在 2.2 有对应交互步骤
3. 2.1 和 2.2 是否数据流闭环
4. 2.3 附图是否覆盖关键模块和步骤
5. 3.2 区别点是否成立，是否引用了确认来源
6. 是否存在未确认外部事实
7. 是否残留模板占位符
8. 术语是否统一
9. 是否修改了只读输入目录

---

## RevisionAgent (feat-007)

**输入：**
- `intermediate/05_review/revision_tasks.json`
- `intermediate/03_parallel/` + `intermediate/04_derived/`
- `model/专利技术方案交底书模板.docx`

**输出：**
```
intermediate/06_revision/
├── final_markdown.md    # 全文 Markdown 稿
└── final_payload.json   # 章节 → 内容 + 来源节点 + task_id 映射
res/.tmp_专利交底书.docx
```

**完成条件：**
- 每个 `revision_task_id` 有处理记录
- 临时 docx 通过 `verify_fields.py` 和 `verify_output.py --tmp`
- 完成后回到 ReviewAgent（必须，不能跳过）

---

## ReleaseAgent (feat-008)

**输入：**
- `intermediate/06_revision/final_payload.json`
- `res/.tmp_专利交底书.docx`
- `intermediate/07_release/human_confirmation.md`（如有 P1 项）

**输出：**
```
res/专利交底书.docx
intermediate/07_release/release_manifest.json
```

**Release 条件（全部满足才执行）：**
1. `review_report.status == "pass"`
2. `res/.tmp_专利交底书.docx` 存在且可打开
3. 全部验证脚本通过
4. P0 门禁全部 pass
5. P1 门禁均 pass 或已写入 `human_confirmation.md`
6. 输入目录哈希未变化（`doc/`、`model/`、`content/` 未被修改）
7. `release_manifest.json` 已生成

# Workflow：专利交底书生成

## 概览

本 Workflow 基于 DAG（有向无环图）编排，将专利生成拆分为 12 个节点。每个节点独立输出结构化产物，下游节点只读上游产物。

## DAG 结构

```
START
  ↓
[feat-001] ManifestAgent
  解析 model/ 模板和 doc/ 参考文档的结构、字段、风格约束
  输出：intermediate/00_manifest/
  ↓
[feat-002] SkeletonAgent
  确定发明主题、核心 claim、关键术语、前后端边界
  输出：intermediate/01_skeleton/
  ↓
[feat-003] D0PriorArtBaselineAgent
  生成 1.2 现有技术方案基线 + 1.3 缺点基线，固定 defect_id
  输出：intermediate/02_prior_art_baseline/
  ↓
  ┌───────────────────────────────────────────────────┐
  │  并行阶段（A/B/C/D 可同时启动，均依赖 feat-003）  │
  ├──────────┬──────────┬──────────┬──────────────────┤
  │ feat-004A│ feat-004B│ feat-004C│ feat-004D        │
  │ Purpose  │ Backend  │ Frontend │ Research         │
  │ (1.1)    │ (2.1)    │ (2.2)    │ (3.1 / 3.2 原始) │
  └──────────┴──────────┴──────────┴──────────────────┘
       依赖 B/C          依赖 B/C/D
          ↓                 ↓
  [feat-005E]         [feat-005F]
  FigureAgent         AlternativeAgent
  (2.3 附图)          (2.4 + 3.2 区别点)
  ↓
  ↓（等待 A/B/C/D/E/F 全部完成）
[feat-006] ReviewAgent（对抗审查）
  ├─ pass ─────────────────────→ [feat-008] ReleaseAgent
  ├─ fix_required → [feat-007] RevisionAgent → [feat-006]
  ├─ human_required → human_confirmation.md → [feat-006]
  └─ fail → FailExit（写 failure.json，不生成 res）
```

## 并行调度说明

- A/B/C/D 可以由调度器同时派发，互相隔离只写自己的输出目录
- C 可以等 B 完成后立即启动（B 输出作为 C 的前后端边界参考）
- E 等 B/C 完成即可启动，不必等 D
- F 需等 B/C/D 全部完成

## Review/Revision 闭环

```
ReviewAgent 输出 review_report.json：
  {
    "status": "fix_required | pass | human_required | fail",
    "p0_gates": [...],   // 全 pass 才能 Release
    "p1_gates": [...],   // pass 或 human_confirmed 才能 Release
    "p2_suggestions": [...],
    "revision_tasks": [
      {"task_id": "rt-001", "section": "2.1", "issue": "...", "fix": "..."}
    ]
  }

RevisionAgent 必须：
  1. 逐个处理 revision_tasks，每条引用 task_id
  2. 完成后回到 ReviewAgent，不得直接发布
  3. 最多循环 3 次，超出强制进入 human_required 出口

ReleaseAgent 只在以下条件全满足时执行：
  1. review_report.status == "pass"
  2. res/.tmp_专利交底书.docx 存在
  3. 所有验证脚本通过
  4. 原始输入目录未被修改
```

## 中间产物目录

```
intermediate/
├── 00_manifest/           manifest.json, template_constraints.json, reference_style.json
├── 01_skeleton/           skeleton.json, section_plan.md, terminology.md, traceability_seed.json
├── 02_prior_art_baseline/ prior_art_baseline.json, prior_art_baseline.md
├── 03_parallel/
│   ├── A_purpose/         purpose.json, purpose.md
│   ├── B_backend/         backend_solution.json, backend_solution.md
│   ├── C_frontend/        frontend_solution.json, frontend_solution.md
│   └── D_research/        research.json, research.md
├── 04_derived/
│   ├── E_figures/         figures.json, figures.md
│   └── F_alternatives/    alternatives.json, alternatives.md
├── 05_review/             review_report.json, review_report.md, revision_tasks.json
├── 06_revision/           final_markdown.md, final_payload.json
└── 07_release/            release_manifest.json, human_confirmation.md
```

## 每个产物的必须字段

所有 JSON 产物必须包含：

```json
{
  "node_id": "feat-004B",
  "agent": "BackendSolutionAgent",
  "generated_at": "2026-06-12T...",
  "schema_version": "0.1",
  "claimed_done": true,
  "verified_done": false,
  "verification_log": null,
  "artifact_hash": null,
  "warnings": []
}
```

`verified_done` 由验证脚本而非 Agent 写入。

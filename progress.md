# Progress Log

## 2026-06-12

- 完成：feat-000（建立 Harness 控制面）
- 创建文件：
  - AGENTS.md（Harness 指令、禁止事项、路径白名单、模板约束、DAG、质量门禁、出口设计）
  - feature_list.json（12 个节点，feat-000 到 feat-008，DAG 依赖关系已定义）
  - workflow/patent-disclosure-workflow.md（Workflow 总体设计）
  - workflow/agent-contracts.md（各 Agent 输入输出契约）
  - workflow/quality-gates.md（P0/P1/P2 门禁 + 出口状态机）
  - workflow/traceability-matrix.md（专利逻辑闭环 Matrix 设计）
  - workflow/harness-workflow-design.md（Workflow 全景 + 出口系统设计）
  - session-handoff.md
  - progress.md（本文件）
- 防错记录追加：
  - ERR-001: python-docx 图片插入必须用 add_picture() + 元素移动两步法
  - ERR-002: [待人工确认] 标记必须在 Release 前解决，不得带入最终文档
- 下一步：feat-001（ManifestAgent）

# Session Handoff

## 上次会话

- 日期：2026-06-12
- 完成节点：feat-000（Harness 控制面搭建）
- 执行过一次全量 Workflow 生成，已清空产物并还原状态

## 当前状态

feat-000 已完成，feat-001~feat-008 均为 pending。
intermediate/ 和 res/ 目录已清空。

**下一个待执行节点：feat-001（ManifestAgent）**

## 防错经验（来自上次执行）

1. python-docx 插入图片必须用 `doc.add_picture()` + 元素位置移动，不得用旧 API
2. `[待人工确认]` 标记必须在 Release 前解决（人工提供或明确删除），不得带入最终 docx
3. 封面人工字段（部门/联系人等）要在 Release 前向用户收集或由用户明确跳过

## 下次会话启动步骤

```bash
# 1. 读 AGENTS.md
# 2. 读本文件
# 3. 读 feature_list.json，确认 feat-001 状态为 pending
# 4. 开始执行 ManifestAgent
```

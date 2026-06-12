# Traceability Matrix：专利逻辑闭环

## 目的

Traceability Matrix 用于证明专利交底书不是各章节孤立生成，而是形成如下闭环：

```text
1.1 技术问题
  → 1.2 现有技术
  → 1.3 现有技术缺点
  → 2.1 后台技术方案
  → 2.2 前端交互方案
  → 2.3 附图说明
  → 2.4 替代方案
  → 3.2 区别点分析
```

## 核心结构

```json
{
  "problem_id": "P1",
  "problem_text": "长周期 AI Agent 执行过程中缺少可验证完成机制",

  "prior_art_id": "PA1",
  "prior_art_text": "传统提示词工程方案依赖单次对话输出",

  "defect_id": "D1",
  "defect_text": "无法跨会话持久追踪状态，也无法证明任务已完成",

  "backend_solution_id": "B1",
  "backend_solution_text": "通过 feature_list 状态机和 verification 字段控制完成状态转移",

  "frontend_step_id": "C1",
  "frontend_step_text": "前端展示任务状态、验证结果和 evidence 证据",

  "figure_id": "FIG1",
  "figure_text": "图1 系统总体架构图，展示状态模块与验证模块的关系",

  "alternative_id": "ALT1",
  "alternative_text": "也可以使用数据库表代替 feature_list.json 作为状态持久化介质",

  "distinction_id": "DIST1",
  "distinction_text": "现有技术采用一次性提示词输出，本申请采用状态机+验证证据驱动的闭环执行"
}
```

## 必须检查的关系

### 1.1 → 1.2

每个 `problem_id` 至少对应一个 `prior_art_id`。

### 1.2 → 1.3

每个 `prior_art_id` 必须对应至少一个 `defect_id`。

### 1.3 → 2.1

每个 `defect_id` 必须至少被一个 `backend_solution_id` 覆盖。

### 2.1 → 2.2

每个关键 `backend_solution_id` 必须至少被一个 `frontend_step_id` 呈现或触发。

### 2.1 / 2.2 → 2.3

每个核心后台模块或前端流程必须至少被一个 `figure_id` 覆盖，若无实体图，标记为 `pending_human`。

### 2.1 / 2.2 → 2.4

替代方案必须说明与主方案的差异，不能简单重复主方案。

### 2.1 / 2.2 / D_research → 3.2

每个区别点必须引用：
- 一个现有技术或竞品依据
- 一个本申请技术模块
- 一个可信度字段

## 阻断规则

以下情况属于 P0：

- 存在未被 2.1 覆盖的 `defect_id`
- 存在未被 2.2 支撑的关键后台模块
- `3.2` 区别点引用了 `needs_human_confirmation` 的外部来源但写成确定性事实
- `1.2` 和 `1.3` 编号数量不一致

## 人工确认规则

以下情况属于 P1：

- `figure_id.status == "pending_human"`
- 外部来源可信度为 `needs_human_confirmation`
- 竞品名称或专利号无法自动确认

P1 允许生成 `human_confirmation.md`，但不得伪造确认结果。

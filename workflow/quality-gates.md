# 质量门禁与出口设计

## 三级门禁

### P0 阻断项（任一失败，不得 Release）

| 编号 | 检查内容 | 验证方式 |
|------|---------|---------|
| P0-01 | 模板章节缺失（任意必须章节不存在） | `verify_structure.py` |
| P0-02 | 存在 `【` 或 `】` 占位符 | `verify_fields.py` |
| P0-03 | `1.2` 与 `1.3` 编号不一一对应 | `verify_traceability.py --check 1.2-1.3` |
| P0-04 | `2.1` 未回应全部 `1.3` 缺点 | `verify_traceability.py --check 2.1-defects` |
| P0-05 | `2.2` 与 `2.1` 数据流不闭环 | `verify_traceability.py --check 2.2-2.1` |
| P0-06 | Revision 后未重新经过 ReviewAgent | `review_report.json` 中 revision_round 字段 |
| P0-07 | 修改了 `doc/`、`model/`、`content/` 目录 | `verify_scope.py`（比较哈希） |
| P0-08 | 未确认外部事实（专利/论文/竞品）被写成确定性结论 | `verify_traceability.py --check research` |
| P0-09 | docx 文件损坏或无法打开 | `verify_output.py` |

---

### P1 人工确认项（不可静默通过，进入 human_confirmation.md）

| 编号 | 检查内容 | 处理方式 |
|------|---------|---------|
| P1-01 | 实体附图缺失 | 在正文中标注"图X：待人工补充"，写入 human_confirmation.md |
| P1-02 | 专利/论文来源未确认（`needs_human_confirmation`） | 不得写入 3.2 确定性结论，写入 human_confirmation.md |
| P1-03 | 竞品名称未确认 | 3.1 写"[待确认：竞品名称]"，写入 human_confirmation.md |
| P1-04 | 发明名称未最终确认 | 封面字段空置或标注"待确认"，写入 human_confirmation.md |
| P1-05 | 部门、提交人、联系方式等封面字段未填写 | 封面字段空置，写入 human_confirmation.md，不得臆造 |

---

### P2 优化建议（不阻断 Release，进入 review_report 建议区）

| 编号 | 检查内容 |
|------|---------|
| P2-01 | 某章节表达不够专利化 |
| P2-02 | 2.1 字数不足 800 字 |
| P2-03 | 术语使用轻微不统一 |
| P2-04 | 替代方案数量偏少（≥1 即可，建议 ≥2） |
| P2-05 | 附图说明不够细 |

---

## 出口设计

### 1. 阶段出口（每个节点）

每个节点产物必须包含以下标准字段才能被下游读取：

```json
{
  "node_id": "feat-004B",
  "claimed_done": true,
  "verified_done": false,
  "verified_by": null,
  "verification_log": null,
  "artifact_hash": null
}
```

`verified_done` 只能由验证脚本写入，Agent 不得自写。

---

### 2. 失败出口

任何验证失败写入：

```
intermediate/<stage>/failure.json
```

格式：

```json
{
  "node_id": "feat-004B",
  "status": "failed",
  "reason": "未回应 defect_id D3",
  "blocking": true,
  "retry_count": 1,
  "max_retries": 2,
  "recover_suggestion": "检查 backend_solution.json 的 resolves_defect_ids 字段",
  "failed_at": "2026-06-12T10:00:00"
}
```

规则：
- 失败出口不得生成 `res/专利交底书.docx`
- `retry_count >= max_retries` 时强制进入人工确认出口

---

### 3. 人工确认出口

```
intermediate/07_release/human_confirmation.md
```

格式：

```markdown
# 人工确认清单

## P1-01 实体附图
- 图1：系统总体架构图 → 待补充
- 图2：五大子系统交互图 → 已有 Graphviz 源文件，可直接使用

## P1-02 检索来源确认
- 《...》（论文名）：需确认真实性

## P1-05 封面字段
- 发明名称：[待确认]
- 提交部门：[待填写]
- 提交人：[待填写]
- 联系方式：[待填写]
```

规则：
- 可标注为"待人工补充"的项目允许进入最终文档
- 未确认的外部事实不得以确定语气写入

---

### 4. Review 条件出口状态机

```
ReviewAgent 完成
    │
    ├─[p0_gates 全 pass + p1 全 pass/human_confirmed]─→ "pass" → ReleaseAgent
    │
    ├─[p0_gates 有 fail]─→ "fix_required" → RevisionAgent → ReviewAgent
    │                        (最多循环 3 次，超出 → "human_required")
    │
    ├─[p1_gates 有 needs_human_confirmation]─→ "human_required"
    │   → 写 human_confirmation.md
    │   → 等待人工确认
    │   → ReviewAgent（再次）
    │
    └─[结构性失败，不可自动修复]─→ "fail" → FailExit
```

---

### 5. Release 出口（最终）

触发条件（全部满足）：

1. `review_report.status == "pass"`
2. `res/.tmp_专利交底书.docx` 存在
3. 以下脚本全部通过：
   - `verify_scope.py`
   - `verify_structure.py`
   - `verify_fields.py`
   - `verify_traceability.py`
   - `verify_output.py`
4. 输入目录哈希未变化
5. `release_manifest.json` 已生成

执行动作：

```
rename(res/.tmp_专利交底书.docx, res/专利交底书.docx)
write(intermediate/07_release/release_manifest.json)
update(feature_list.json, feat-008, status=completed)
update(session-handoff.md)
```

---

## 验证脚本职责

| 脚本 | 职责 |
|------|------|
| `verify_scope.py` | 检查原始输入目录哈希未变化；检查各节点写入路径在白名单内 |
| `verify_structure.py` | 检查章节标题与模板一致；保留模板中重复编号；无跳号 |
| `verify_fields.py` | 全文无 `【` 或 `】`；封面表格结构完整 |
| `verify_traceability.py` | 检查 1.2/1.3 编号对应；1.3→2.1 覆盖；2.2→2.1 闭环；3.2 来源可信度 |
| `verify_graphviz.py` | .dot 可解析；.png 存在；dpi ≥ 300；图中含 Review/Fail 出口节点 |
| `verify_output.py` | docx 可打开；字数 ≥ 2000；章节数量正确 |

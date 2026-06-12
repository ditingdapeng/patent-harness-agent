# patent-harness-agent

基于 Harness 工程方法论的多 Agent DAG Workflow 专利交底书自动生成系统。

A multi-agent DAG workflow system that automatically generates patent disclosure documents using Harness Engineering methodology (I+S+V+Sc+L five-subsystem constraint model).

## 项目结构

```
├── AGENTS.md                  # Harness 宪法（指令、禁止事项、DAG、质量门禁）
├── feature_list.json          # DAG 状态机（节点依赖、状态、验证命令）
├── workflow/                   # 编排设计文档
│   ├── patent-disclosure-workflow.md   # Workflow DAG 结构
│   ├── agent-contracts.md              # Agent 输入输出契约
│   ├── quality-gates.md                # P0/P1/P2 门禁 + 出口设计
│   ├── traceability-matrix.md          # 专利逻辑闭环矩阵
│   └── harness-workflow-design.md      # Workflow 全景设计
├── content/reborn-harness/    # 技术素材（只读输入）
├── doc/                       # 参考专利交底书（只读输入）
├── model/                     # 模板文件（只读输入）
├── intermediate/              # 中间产物（执行时生成）
├── res/                       # 最终输出（专利交底书.docx）
├── scripts/                   # 验证脚本
├── session-handoff.md         # 会话断点续接
└── progress.md                # 执行日志
```

## 核心设计

### 五大子系统 (I+S+V+Sc+L)

| 子系统 | 核心文件 | 职责 |
|--------|---------|------|
| Instruction | AGENTS.md | 告诉 Agent 做什么、禁什么 |
| State | feature_list.json | 跨会话状态持久化 |
| Validation | scripts/verify_*.py | 外部验证，Agent 不能自证完成 |
| Scope | feature_list 单条目 | 一次只做一件事 |
| Lifecycle | session-handoff.md | 会话有标准的开始和结束 |

### DAG Workflow

```
ManifestAgent → SkeletonAgent → D0Baseline
                                    ↓
                    ┌───────────────────────────────┐
                    │  A(1.1) / B(2.1) / C(2.2) / D(3.1)  │  并行
                    └───────────────────────────────┘
                                    ↓
                    ┌───────────────────────────────┐
                    │  E(附图) / F(替代方案+区别点)    │  并行
                    └───────────────────────────────┘
                                    ↓
                    ReviewAgent ↔ RevisionAgent（最多3轮）
                                    ↓
                              ReleaseAgent → res/专利交底书.docx
```

### 四种出口

- **pass** → Release 发布
- **fix_required** → Revision 修订后重审
- **human_required** → 人工确认后继续
- **fail** → 终止，不生成文件

## 使用方式

本项目设计为 Claude Code Workflow 驱动。在项目目录下启动 Claude Code，Workflow 脚本会按 DAG 顺序自动编排 11 个 Agent 完成专利生成。

## License

MIT

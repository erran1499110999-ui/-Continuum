/**
 * Continuity 体检 — 内存态体检纯函数（P2 实现，本文件为占位）
 *
 * P2 将在此实现 H1–H6 检查纯函数（输入为 context 快照，输出结构化发现列表）：
 * - H1 当前聊天 chat_metadata.integrity 缺失
 * - H2 疑似被重置的聊天（消息数 ≤ 2 且末条为角色 first_mes）
 * - H3 同名角色卡（不同内容）提示
 * - H4 当前卡关键字段完整性
 * - H5 当前聊天消息结构异常
 * - H6 服务器可唤起性（P3 定）
 *
 * 原则：只读输入、纯函数、无副作用；话术保守（「提示/疑似/建议」），
 * 绝不产出 R 级修复判定（R 级结论只由 Python 引擎给出，规则 4/9）。
 * 单元测试：extensions/sillytavern/tests/checks.test.mjs（node:test，P2）。
 */
"use strict";

/* P2 TODO: export check functions here */

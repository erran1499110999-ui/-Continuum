/**
 * checks.js 纯函数单元测试（node:test，零 npm 依赖）
 *
 * 运行方式（两种）：
 * 1. 官方方式：node --test extensions/sillytavern/tests/checks.test.mjs
 *    （受限沙箱内不可用：--test runner 需 spawn 子进程，被沙箱以 EPERM 拒绝）；
 * 2. 沙箱替代：node extensions/sillytavern/tests/checks.test.mjs
 *    ——直接执行本文件入口，在单进程内运行同一套 node:test 用例
 *    （Node v24.15.0 实测 24/24 通过）。
 *
 * 全部样本为程序化构造的假 context，不含任何真实用户数据；
 * 覆盖 H1–H5 判定分支、边界反例、话术保守性与只读性。
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  buildSnapshot,
  checkIntegrity,
  checkResetChat,
  checkDuplicateNames,
  checkCardFields,
  checkMessageStructure,
  runChecks,
} from "../continuity-st/checks.js";

// —— 假 context 构造器（默认：两条消息、健康聊天、有 integrity） ——
function makeContext(overrides = {}) {
  const card = { name: "测试角色", first_mes: "你好。", description: "测试描述" };
  return Object.assign(
    {
      chat: [
        { name: "测试角色", is_user: false, mes: "你好。" },
        { name: "用户", is_user: true, mes: "在吗？" },
      ],
      characters: { c1: { data: card } },
      characterId: "c1",
      chatMetadata: { integrity: "abc123" },
    },
    overrides
  );
}

// —— buildSnapshot ——

test("buildSnapshot 映射 chat/characters/characterId/metadata", () => {
  const ctx = makeContext();
  const snap = buildSnapshot(ctx);
  assert.equal(snap.chat.length, 2);
  assert.ok(snap.characters.c1);
  assert.equal(snap.characterId, "c1");
  assert.equal(snap.metadata.integrity, "abc123");
});

test("buildSnapshot 兼容旧字段名 chat_metadata", () => {
  const ctx = makeContext({ chatMetadata: undefined, chat_metadata: { integrity: "legacy" } });
  const snap = buildSnapshot(ctx);
  assert.equal(snap.metadata.integrity, "legacy");
});

test("buildSnapshot 复制当前卡数据（快照与源对象隔离）", () => {
  const ctx = makeContext();
  const snap = buildSnapshot(ctx);
  ctx.characters.c1.data.name = "改名后";
  assert.equal(snap.currentCard.name, "测试角色");
});

// —— H1 integrity ——

test("H1：integrity 存在时无提示", () => {
  assert.equal(checkIntegrity(buildSnapshot(makeContext())), null);
});

test("H1：integrity 缺失时报提示", () => {
  const ctx = makeContext({ chatMetadata: { integrity: "" } });
  const f = checkIntegrity(buildSnapshot(ctx));
  assert.equal(f.id, "H1");
  assert.equal(f.level, "hint");
  assert.ok(f.detail.includes("旧格式"));
});

test("H1：整体无 metadata 时报提示（旧格式不当作损坏）", () => {
  const ctx = makeContext({ chatMetadata: undefined });
  const f = checkIntegrity(buildSnapshot(ctx));
  assert.equal(f.id, "H1");
  assert.ok(f.detail.includes("不一定是损坏"));
});

// —— H2 疑似被重置的聊天 ——

test("H2：正常聊天（末条为用户消息）无提示", () => {
  assert.equal(checkResetChat(buildSnapshot(makeContext())), null);
});

test("H2：只剩开场白（1 条角色消息）报疑似重置", () => {
  const ctx = makeContext({ chat: [{ name: "测试角色", is_user: false, mes: "你好。" }] });
  const f = checkResetChat(buildSnapshot(ctx));
  assert.equal(f.id, "H2");
  assert.ok(f.detail.includes("疑似"));
});

test("H2 边界：2 条消息且末条为 first_mes 报提示", () => {
  const ctx = makeContext({
    chat: [
      { name: "用户", is_user: true, mes: "你好" },
      { name: "测试角色", is_user: false, mes: "你好。" },
    ],
  });
  const f = checkResetChat(buildSnapshot(ctx));
  assert.equal(f.id, "H2");
});

test("H2 边界：末条不是 first_mes 不误报", () => {
  const ctx = makeContext({
    chat: [{ name: "测试角色", is_user: false, mes: "不是开场白的其他话" }],
  });
  assert.equal(checkResetChat(buildSnapshot(ctx)), null);
});

test("H2：超过 2 条消息不触发（非重置形态）", () => {
  const ctx = makeContext({
    chat: [
      { name: "测试角色", is_user: false, mes: "你好。" },
      { name: "用户", is_user: true, mes: "在吗？" },
      { name: "测试角色", is_user: false, mes: "你好。" },
    ],
  });
  assert.equal(checkResetChat(buildSnapshot(ctx)), null);
});

// —— H3 同名角色卡 ——

test("H3：同名且内容不同报提示", () => {
  const ctx = makeContext({
    characters: {
      c1: { data: { name: "雷电将军", first_mes: "A", description: "甲" } },
      c2: { data: { name: "雷电将军", first_mes: "A", description: "乙" } },
    },
  });
  const f = checkDuplicateNames(buildSnapshot(ctx));
  assert.equal(f.id, "H3");
  assert.ok(f.detail.includes("雷电将军"));
});

test("H3：同名且内容相同不报", () => {
  const ctx = makeContext({
    characters: {
      c1: { data: { name: "雷电将军", first_mes: "A" } },
      c2: { data: { name: "雷电将军", first_mes: "A" } },
    },
  });
  assert.equal(checkDuplicateNames(buildSnapshot(ctx)), null);
});

test("H3：不同名不报", () => {
  assert.equal(checkDuplicateNames(buildSnapshot(makeContext())), null);
});

// —— H4 卡字段完整性 ——

test("H4：关键字段齐全无提示", () => {
  assert.equal(checkCardFields(buildSnapshot(makeContext())), null);
});

test("H4：缺少 first_mes 报字段名（不列内容）", () => {
  const ctx = makeContext({
    characters: { c1: { data: { name: "测试角色", description: "x" } } },
  });
  const f = checkCardFields(buildSnapshot(ctx));
  assert.equal(f.id, "H4");
  assert.ok(f.detail.includes("first_mes"));
  assert.ok(!f.detail.includes("测试角色")); // 隐私：只报字段名
});

test("H4：无当前卡不报", () => {
  const ctx = makeContext({ characterId: null });
  assert.equal(checkCardFields(buildSnapshot(ctx)), null);
});

// —— H5 消息结构 ——

test("H5：结构正常无提示", () => {
  assert.equal(checkMessageStructure(buildSnapshot(makeContext())), null);
});

test("H5：缺 mes 与 is_user 非布尔被计数", () => {
  const ctx = makeContext({
    chat: [
      { name: "用户", is_user: true }, // 缺 mes
      { name: "测试角色", is_user: "yes", mes: "x" }, // is_user 非布尔
    ],
  });
  const f = checkMessageStructure(buildSnapshot(ctx));
  assert.equal(f.id, "H5");
  assert.ok(f.detail.includes("2"));
});

test("H5：非对象消息被计数且不崩溃", () => {
  const ctx = makeContext({ chat: [null, { is_user: true, mes: "ok" }] });
  const f = checkMessageStructure(buildSnapshot(ctx));
  assert.equal(f.id, "H5");
  assert.ok(f.detail.includes("1"));
});

// —— runChecks 组合 ——

test("runChecks：无问题返回空发现列表", () => {
  const result = runChecks(makeContext());
  assert.deepEqual(result.findings, []);
});

test("runChecks：多重问题返回对应 id 集合", () => {
  const ctx = makeContext({
    chatMetadata: undefined, // H1：无 integrity
    chat: [{ name: "雷电将军", is_user: false, mes: "你好。" }], // H2：只剩开场白（与当前卡 first_mes 一致）
    characters: {
      c1: { data: { name: "雷电将军", first_mes: "你好。" } }, // 缺 description → H4
      c2: { data: { name: "雷电将军", first_mes: "A", description: "乙" } }, // 同名不同内容 → H3
    },
    characterId: "c1",
  });
  const result = runChecks(ctx);
  const ids = result.findings.map((f) => f.id).sort();
  assert.deepEqual(ids, ["H1", "H2", "H3", "H4"]);
});

// —— 话术保守性与只读性 ——

test("话术保守：所有发现 level 恒为 hint，且不含 R 级判定字样", () => {
  const ctx = makeContext({ chatMetadata: undefined });
  const result = runChecks(ctx);
  assert.ok(result.findings.length > 0);
  for (const f of result.findings) {
    assert.equal(f.level, "hint");
    for (const r of ["R0", "R1", "R2", "R3"]) {
      assert.ok(!(f.title + f.detail).includes(r), `发现 ${f.id} 出现 R 级字样`);
    }
  }
});

test("只读性：runChecks 前后 context 内容不变", () => {
  const ctx = makeContext({ chatMetadata: undefined });
  const before = JSON.stringify(ctx);
  runChecks(ctx);
  assert.equal(JSON.stringify(ctx), before);
});

/**
 * Continuity 体检 — 内存态体检纯函数（P2）
 *
 * 原则（AGENTS.md 规则 1/2/3/4/9）：
 * - 只读：所有函数只读取入参快照，绝不写文件、写设置、发网络请求；
 * - 纯函数：同一输入必然同一输出，无 DOM、无副作用，可独立单测（node:test）；
 * - 话术保守：每条结论只陈述结构事实（「提示/疑似/建议」），
 *   绝不产出 R 级修复判定——R 级结论只由 Python 引擎给出；
 * - 格式不确定不猜测：字段缺失只报缺失，不推断原因。
 *
 * 加载方式：浏览器中由 index.js 以 ES Module 导入（import ... from "./checks.js"）；
 * Node 单测：本扩展根目录 package.json 声明 "type":"module"。
 *
 * 运行单测的两种方式：
 * 1. 官方方式：node --test extensions/sillytavern/tests/checks.test.mjs
 *    （受限沙箱内不可用：--test runner 需 spawn 子进程，被沙箱以 EPERM 拒绝）；
 * 2. 沙箱替代：node extensions/sillytavern/tests/checks.test.mjs
 *    ——直接执行测试文件入口，在单进程内运行同一套 node:test 用例
 *    （Node v24.15.0 实测 24/24 通过）。
 */
"use strict";

/** 关键字段检查表（保守最小集：只查存在性，不评内容质量）。 */
const REQUIRED_CARD_FIELDS = ["name", "first_mes", "description"];

/**
 * 从 SillyTavern context 构建只读快照（纯数据，不持有 DOM/ST 内部引用）。
 * 所有检查函数都以本快照为唯一输入，保证可测试性与零副作用。
 */
export function buildSnapshot(context) {
  // 当前聊天消息数组（ST 内存中的 chat[]）
  const chat = context && Array.isArray(context.chat) ? context.chat : [];
  // 已载入角色卡表（id → {data:{...}}）
  const characters =
    context && context.characters && typeof context.characters === "object"
      ? context.characters
      : {};
  const characterId =
    context && typeof context.characterId === "string" ? context.characterId : null;
  // 兼容两种字段名：ST 内存对象为 chatMetadata，聊天文件落盘字段为 chat_metadata
  const metadata = (context && (context.chatMetadata || context.chat_metadata)) || null;
  // 当前角色卡数据做浅拷贝（H 系列检查只读顶层标量字段，浅拷贝即足够）：
  // 检查结果不受后续 ST 内存变化影响（纯函数语义）
  let currentCard = null;
  if (characterId && characters[characterId] && characters[characterId].data) {
    currentCard = Object.assign({}, characters[characterId].data);
  }
  return { chat, characters, metadata, characterId, currentCard };
}

/**
 * H1：当前聊天缺少完整性标识（integrity）。
 * 依据失败案例库 CASE-02/13/16：旧格式聊天没有该字段——只提示，不当作损坏。
 */
export function checkIntegrity(snapshot) {
  const meta = snapshot.metadata;
  if (meta && typeof meta.integrity === "string" && meta.integrity.length > 0) {
    return null; // 标识存在，无需提示
  }
  return {
    id: "H1",
    level: "hint",
    title: "当前聊天缺少完整性标识（integrity）",
    detail:
      "可能是旧格式或保存异常。旧格式不一定是损坏——建议先打开本地 Web UI 深度体检，不要立刻覆盖保存。",
  };
}

/**
 * H2：疑似被重置的聊天。
 * 依据 CASE-01/03：消息数 ≤2 且结尾是角色开场白时，疑似只剩「header+开场白」。
 * 只做「疑似」提示，绝不判定为已损坏（规则 4/9）。
 */
export function checkResetChat(snapshot) {
  const msgs = snapshot.chat;
  const card = snapshot.currentCard;
  if (!Array.isArray(msgs) || msgs.length === 0 || msgs.length > 2) return null;
  if (!card || typeof card.first_mes !== "string" || card.first_mes.length === 0) return null;
  const last = msgs[msgs.length - 1];
  const looksLikeGreeting =
    last &&
    typeof last === "object" &&
    last.is_user === false &&
    typeof last.mes === "string" &&
    last.mes === card.first_mes;
  if (!looksLikeGreeting) return null;
  return {
    id: "H2",
    level: "hint",
    title: "疑似被重置的聊天",
    detail:
      "当前聊天只剩很少的消息且结尾是开场白，疑似曾发生重置。请用本地 Web UI 深度体检，并从备份核对历史。",
  };
}

/**
 * H3：同名但内容不同的角色卡。
 * 依据 CASE-07：按名字键控的存储存在同名导入互相覆盖风险。
 * 内容签名用整卡 JSON 串（内存中卡体积小，同步处理即可；不猜字段语义）。
 */
export function checkDuplicateNames(snapshot) {
  const chars = snapshot.characters || {};
  const byName = new Map(); // 名字 → 该名下不同内容签名的集合
  for (const id of Object.keys(chars)) {
    const data = chars[id] && chars[id].data;
    if (!data || typeof data.name !== "string" || data.name.length === 0) continue;
    const signature = JSON.stringify(data);
    if (!byName.has(data.name)) byName.set(data.name, new Set());
    byName.get(data.name).add(signature);
  }
  const names = [];
  for (const [name, sigs] of byName) {
    if (sigs.size > 1) names.push(name); // 同名且内容不同才是风险
  }
  if (names.length === 0) return null;
  const shown = names.slice(0, 5).join("、") + (names.length > 5 ? " 等" : "");
  return {
    id: "H3",
    level: "hint",
    title: "发现同名但内容不同的角色卡",
    detail:
      "同名角色：" + shown + "。批量导入可能互相覆盖——建议先备份再导入（本地 Web UI）。",
  };
}

/**
 * H4：当前角色卡关键字段缺失。
 * 依据 CASE-18/21：只报缺失的字段名，绝不展示字段内容（隐私与克制）。
 */
export function checkCardFields(snapshot) {
  const card = snapshot.currentCard;
  if (!card) return null; // 无当前卡：不做无谓告警
  const missing = REQUIRED_CARD_FIELDS.filter(
    (f) => !(f in card) || card[f] === "" || card[f] === null || card[f] === undefined
  );
  if (missing.length === 0) return null;
  return {
    id: "H4",
    level: "hint",
    title: "当前角色卡缺少关键字段",
    detail:
      "缺少字段：" + missing.join("、") + "。可能影响导入与显示；深度检查请打开本地 Web UI。",
  };
}

/**
 * H5：当前聊天消息结构异常。
 * 依据 CASE-11：缺文本（mes）或角色标记（is_user）非布尔的条目只计数提示，不猜原因。
 */
export function checkMessageStructure(snapshot) {
  const msgs = snapshot.chat;
  if (!Array.isArray(msgs)) return null;
  let bad = 0;
  for (const m of msgs) {
    if (!m || typeof m !== "object") {
      bad += 1;
      continue;
    }
    if (typeof m.mes !== "string" || m.mes.length === 0) bad += 1;
    if (typeof m.is_user !== "boolean") bad += 1;
  }
  if (bad === 0) return null;
  return {
    id: "H5",
    level: "hint",
    title: "消息结构异常",
    detail:
      "当前聊天存在 " + bad + " 处结构异常（缺少文本或角色标记异常）。内存态只能提示——完整诊断请用本地 Web UI。",
  };
}

/**
 * 一键体检：按 H1–H5 顺序执行全部检查，返回快照与发现列表（无发现时为空数组）。
 * 每条发现 level 恒为 "hint"（提示），绝不携带修复等级判定。
 */
export function runChecks(context) {
  const snapshot = buildSnapshot(context);
  const checks = [
    checkIntegrity,
    checkResetChat,
    checkDuplicateNames,
    checkCardFields,
    checkMessageStructure,
  ];
  const findings = [];
  for (const fn of checks) {
    const finding = fn(snapshot);
    if (finding) findings.push(finding);
  }
  return { snapshot, findings };
}

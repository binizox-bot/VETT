import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const here = path.dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(await fs.readFile(path.join(here, "workbook_data.json"), "utf8"));
const workbook = Workbook.create();

const navy = "#17324D";
const blue = "#DCEAF7";
const pale = "#F4F7FA";
const green = "#E2F0D9";
const amber = "#FFF2CC";
const red = "#FCE4D6";

function scalar(value) {
  if (value === undefined) return null;
  if (value === null || ["string", "number", "boolean"].includes(typeof value)) return value;
  return JSON.stringify(value);
}

function addDataSheet(name, rows, columns, tableName, widths = {}) {
  const sheet = workbook.worksheets.add(name);
  const matrix = [columns.map((c) => c.label)];
  for (const row of rows) matrix.push(columns.map((c) => scalar(row[c.key])));
  sheet.getRangeByIndexes(0, 0, matrix.length, columns.length).values = matrix;
  const header = sheet.getRangeByIndexes(0, 0, 1, columns.length);
  header.format.fill = navy;
  header.format.font = { bold: true, color: "#FFFFFF" };
  header.format.wrapText = true;
  header.format.rowHeight = 34;
  const body = sheet.getRangeByIndexes(1, 0, Math.max(rows.length, 1), columns.length);
  body.format.verticalAlignment = "top";
  body.format.wrapText = true;
  const used = sheet.getRangeByIndexes(0, 0, matrix.length, columns.length);
  used.format.borders = { preset: "all", style: "thin", color: "#D9E1E8" };
  if (rows.length) {
    const table = sheet.tables.add(`A1:${columnLetter(columns.length)}${matrix.length}`, true, tableName);
    table.style = "TableStyleMedium2";
  }
  columns.forEach((c, i) => {
    sheet.getRangeByIndexes(0, i, matrix.length, 1).format.columnWidth = widths[c.key] || 16;
  });
  sheet.freezePanes.freezeRows(1);
  return sheet;
}

function columnLetter(count) {
  let n = count;
  let out = "";
  while (n > 0) {
    n -= 1;
    out = String.fromCharCode(65 + (n % 26)) + out;
    n = Math.floor(n / 26);
  }
  return out;
}

const summary = workbook.worksheets.add("Summary");
summary.mergeCells("A1:D1");
summary.getRange("A1").values = [["VETT 独立离线评分 v3"]];
summary.getRange("A1:D1").format.fill = navy;
summary.getRange("A1:D1").format.font = { bold: true, color: "#FFFFFF", size: 18 };
summary.getRange("A1:D1").format.rowHeight = 34;
summary.getRange("A3:C3").values = [["指标", "结果", "解释"]];
summary.getRange("A3:C3").format.fill = blue;
summary.getRange("A3:C3").format.font = { bold: true, color: navy };
summary.getRange("A4:A14").values = [
  ["N1 重评行数"], ["N1 旧正确格"], ["N1 新正确格"], ["N1 净变化"],
  ["N2 排名修订场次"], ["其中成员退出"], ["畸形 JSON 行数"], ["严格格式通过"],
  ["恢复后身份数值正确"], ["评分回归通过"], ["恢复器测试通过"],
];
summary.getRange("B4:B14").formulas = [
  ["=ROWS('N1 Diff'!A2:A25)"], ["=SUM('N1 Diff'!E2:E25)"], ["=SUM('N1 Diff'!F2:F25)"],
  ["=SUM('N1 Diff'!G2:G25)"], ["=ROWS('N2 Rank'!A2:A6)"], [`=${data.summary.n2_membership_revisions}`],
  ["=ROWS(Malformed!A2:A17)"], ["=SUM(Malformed!E2:E17)"], ["=COUNTIF(Malformed!O2:O17,\"correct\")"],
  [`=${data.summary.regression_cases_passed}`], [`=${data.summary.parser_tests_passed}`],
];
summary.getRange("C4:C14").values = [
  ["当前冻结金标，43 字段/条"], ["原 JSONL 内嵌 score"], ["本版本逐格复算"], ["新减旧"],
  ["另表记录，不改 manifest"], ["match_0008 / match_0010"], ["严格与恢复双分"], ["目标必须为仅含 fields 的合法 JSON"],
  ["按姓名映射 wickets/runs"], ["错人、两场退出、精确同分"], ["含重复同值与冲突重复"],
];
summary.getRange("A3:C14").format.borders = { preset: "all", style: "thin", color: "#C9D3DC" };
summary.getRange("A4:C14").format.wrapText = true;
summary.getRange("A4:C14").format.verticalAlignment = "top";
summary.getRange("A4:A14").format.fill = pale;
summary.getRange("B4:B14").format.font = { bold: true, color: navy };
summary.getRange("A16:D16").values = [["最小诊断 /72", "全文", "窗口", "通知分布见 Diagnostics"]];
summary.getRange("A16:D16").format.fill = blue;
summary.getRange("A16:D16").format.font = { bold: true, color: navy };
summary.getRange("A17:D18").values = [
  ["q1 batter", "11/72", "36/72", "全文 N2=11；窗口 N0/N1/N2=6/8/22"],
  ["q4 old", "44/72", "56/72", "全文 N0/N1/N2=22/22/0；窗口=23/23/10"],
];
summary.getRange("A16:D18").format.borders = { preset: "all", style: "thin", color: "#C9D3DC" };
summary.getRange("A20:D22").values = [
  ["判分边界", "成员集合", "行序", "数值"],
  ["按人物身份", "先判断合法 top-2", "wickets↓ / runs↑", "映射到该人物后再比较"],
  ["精确同分", "任一合法同分候选集合可接受", "入选二人完全同分则未定", "不使用隐藏源顺序"],
];
summary.getRange("A20:D20").format.fill = navy;
summary.getRange("A20:D20").format.font = { bold: true, color: "#FFFFFF" };
summary.getRange("A20:D22").format.borders = { preset: "all", style: "thin", color: "#C9D3DC" };
summary.getRange("A1:D22").format.wrapText = true;
summary.getRange("A1:A22").format.columnWidth = 24;
summary.getRange("B1:B22").format.columnWidth = 16;
summary.getRange("C1:C22").format.columnWidth = 31;
summary.getRange("D1:D22").format.columnWidth = 42;
summary.freezePanes.freezeRows(3);

addDataSheet("N1 Diff", data.n1_diff, [
  { key: "match", label: "比赛" }, { key: "innings", label: "局" }, { key: "model", label: "模型" },
  { key: "event", label: "事件" }, { key: "old_embedded_correct", label: "旧正确格" },
  { key: "new_fixed_correct", label: "新正确格" }, { key: "new_minus_old_correct", label: "差值" },
  { key: "strict_format_pass", label: "严格格式" }, { key: "recovery_source", label: "恢复来源" },
  { key: "manifest_rows", label: "冻结金标两行" }, { key: "observed_rows", label: "模型两行" },
  { key: "member_set_status", label: "成员集合" }, { key: "row_order_status", label: "行序" },
  { key: "identity_value_status", label: "身份数值" }, { key: "total_status", label: "全队总数" },
  { key: "changed_gold_fields", label: "变更金标字段" },
], "N1DiffTable", { model: 28, manifest_rows: 30, observed_rows: 34, changed_gold_fields: 30, member_set_status: 24, row_order_status: 23 });

addDataSheet("N2 Rank", data.n2_rank, [
  { key: "match", label: "比赛" }, { key: "innings", label: "局" }, { key: "event", label: "事件" },
  { key: "action", label: "处理" }, { key: "membership_changed", label: "成员变化" }, { key: "order_changed", label: "顺序变化" },
  { key: "current_manifest_rows", label: "当前 manifest" }, { key: "revised_semantic_rows", label: "语义修订" },
  { key: "post_notice_rank3", label: "通知后 top-3" }, { key: "cutoff_tie", label: "截止同分" },
  { key: "top_order_tie", label: "前二同分" }, { key: "note", label: "说明" },
], "N2RankTable", { action: 30, current_manifest_rows: 34, revised_semantic_rows: 34, post_notice_rank3: 48, note: 34 });

addDataSheet("Malformed", data.malformed, [
  { key: "match", label: "比赛" }, { key: "innings", label: "局" }, { key: "model", label: "模型" }, { key: "arm", label: "通知" },
  { key: "strict_format_score", label: "严格格式分" }, { key: "strict_reason", label: "严格失败原因" },
  { key: "recovery_source", label: "恢复来源" }, { key: "recovered_field_count", label: "恢复字段数" },
  { key: "recoverable_correct", label: "恢复正确" }, { key: "recoverable_wrong", label: "恢复错误" },
  { key: "recoverable_missing", label: "恢复缺失" }, { key: "recoverable_undetermined", label: "恢复未定" },
  { key: "member_set_status", label: "成员集合" }, { key: "row_order_status", label: "行序" },
  { key: "identity_value_status", label: "身份数值" }, { key: "total_status", label: "全队总数" },
], "MalformedTable", { model: 20, strict_reason: 20, recovery_source: 20, member_set_status: 24, row_order_status: 22 });

addDataSheet("Diagnostics", data.diag_distribution, [
  { key: "input_mode", label: "输入" }, { key: "notice", label: "通知" }, { key: "question", label: "问题" },
  { key: "correct", label: "正确" }, { key: "total", label: "总数" }, { key: "undetermined", label: "未定" },
  { key: "qwen2.5_correct", label: "Qwen 正确" }, { key: "qwen2.5_total", label: "Qwen 总数" },
  { key: "llama3.1_correct", label: "Llama 正确" }, { key: "llama3.1_total", label: "Llama 总数" },
  { key: "gemma2_correct", label: "Gemma 正确" }, { key: "gemma2_total", label: "Gemma 总数" },
], "DiagnosticsTable");

const regressionRows = data.regression.map((r) => ({
  case_id: r.case_id, kind: r.kind, fixture: r.fixture || r.task_key || "", expected: r.expected,
  actual: r.actual, pass: r.pass,
}));
addDataSheet("Regression", regressionRows, [
  { key: "case_id", label: "案例" }, { key: "kind", label: "类型" }, { key: "fixture", label: "夹具/任务" },
  { key: "expected", label: "预期" }, { key: "actual", label: "实际" }, { key: "pass", label: "通过" },
], "RegressionTable", { case_id: 34, kind: 45, fixture: 44, expected: 60, actual: 75 });

addDataSheet("Sources", data.source_inventory, [
  { key: "source_id", label: "来源 ID" }, { key: "role", label: "角色" }, { key: "path", label: "绝对路径" },
  { key: "sha256", label: "SHA-256" }, { key: "bytes", label: "字节" }, { key: "read_only_in_this_version", label: "本版本只读" },
], "SourcesTable", { role: 34, path: 90, sha256: 68, read_only_in_this_version: 18 });

workbook.worksheets.getItem("N1 Diff").getRange("G2:G25").conditionalFormats.add("colorScale", {
  colors: [red, amber, green], thresholds: ["min", { type: "num", value: 0 }, "max"],
});
workbook.worksheets.getItem("Malformed").getRange("E2:E17").conditionalFormats.add("cellIs", {
  operator: "equal", formula: 0, format: { fill: red, font: { color: "#9C0006" } },
});

const summaryEvidence = await workbook.inspect({ kind: "region", sheetId: "Summary", range: "A1:D22", maxChars: 9000 });
const formulaEvidence = await workbook.inspect({ kind: "formula", sheetId: "Summary", range: "A1:D22", maxChars: 5000 });
const verificationText = `${summaryEvidence.ndjson || summaryEvidence}\n${formulaEvidence.ndjson || formulaEvidence}`;
const errorTokens = ["#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A"];
const foundErrors = errorTokens.filter((token) => verificationText.includes(token));
if (foundErrors.length) throw new Error(`formula errors: ${foundErrors.join(", ")}`);

const previewDir = path.join(here, "_previews");
await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of ["Summary", "N1 Diff", "N2 Rank", "Malformed", "Diagnostics", "Regression", "Sources"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 0.8, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName.replaceAll(" ", "_")}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
const outputPath = path.join(here, "SCORING_V3_REVIEW.xlsx");
await output.save(outputPath);
const exportedBytes = await fs.readFile(outputPath);
const exportedArrayBuffer = exportedBytes.buffer.slice(exportedBytes.byteOffset, exportedBytes.byteOffset + exportedBytes.byteLength);
const reopened = await SpreadsheetFile.importXlsx(exportedArrayBuffer);
const reopenedEvidence = await reopened.inspect({ kind: "region", sheetId: "Summary", range: "A1:D22", maxChars: 9000 });
const reopenedText = reopenedEvidence.ndjson || String(reopenedEvidence);
const reopenedErrors = errorTokens.filter((token) => reopenedText.includes(token));
if (reopenedErrors.length) throw new Error(`reopened workbook errors: ${reopenedErrors.join(", ")}`);
const reopenedPreview = await reopened.render({ sheetName: "Summary", autoCrop: "all", scale: 0.8, format: "png" });
await fs.writeFile(path.join(previewDir, "Summary_reopened.png"), new Uint8Array(await reopenedPreview.arrayBuffer()));
await fs.writeFile(
  path.join(here, "workbook_verification.txt"),
  `${verificationText}\n--- REOPENED XLSX ---\n${reopenedText}`,
  "utf8",
);
const deliverables = [
  "SCORING_CONTRACT.md", "RESCORE_SUMMARY.md", "SCORING_V3_REVIEW.xlsx",
  "fulltable_rescore_rows.csv", "n1_old_to_new_diff.csv", "n2_rank_revision.csv",
  "malformed_json_rescore.csv", "minimal_diag_q1_q4_rows.csv",
  "minimal_diag_q1_q4_distribution.csv", "rescored_lines.jsonl",
  "regression_cases.json", "parser_regression_tests.json", "summary.json",
  "SOURCE_INVENTORY.csv", "SOURCE_HASHES.json", "workbook_verification.txt",
];
const deliverableHashes = {};
for (const name of deliverables) {
  const bytes = await fs.readFile(path.join(here, name));
  deliverableHashes[name] = { bytes: bytes.byteLength, sha256: createHash("sha256").update(bytes).digest("hex") };
}
await fs.writeFile(
  path.join(here, "VERSION_MANIFEST.json"),
  JSON.stringify({
    scoring_version: data.summary.scoring_version,
    original_runs_mutated: false,
    frozen_inputs: "SOURCE_HASHES.json",
    deliverables: deliverableHashes,
  }, null, 2),
  "utf8",
);
console.log(JSON.stringify({ sheets: 7, foundErrors, reopenedErrors, output: outputPath }, null, 2));

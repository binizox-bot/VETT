import fs from "node:fs";
import path from "node:path";

const base = "/workspace/scratch/6024409549bb/vett_cricket_pilot_v1";
const inputPath = path.join(base, "experiments/v0.3_dev_baseline/probe_blind_inputs_9.jsonl");
const outputDir = path.join(base, "experiments/v0.3_dev_baseline/probe_runs");
const rawPath = path.join(outputDir, "mapmake_paper_style.raw.jsonl");
const predictionPath = path.join(outputDir, "mapmake_paper_style.predictions.jsonl");
const runPath = path.join(outputDir, "mapmake_paper_style.run.json");

const instances = fs.readFileSync(inputPath, "utf8").trim().split("\n").map(JSON.parse);

const stringValue = (value) => String(value);
const lines = (text) => text.split("\n").map((s) => s.trim()).filter(Boolean);
const normalizeName = (name) => name.replace(/ \((?:wk|c)\)$/i, "").trim();
const legalBalls = (overs) => {
  const [whole, remainder = "0"] = String(overs).split(".");
  return Number(whole) * 6 + Number(remainder);
};
const economy = (runs, overs) => {
  const balls = legalBalls(overs);
  return balls ? (Number(runs) * 6 / balls).toFixed(2) : "-";
};
const strikeRate = (runs, balls) => Number(balls) ? (Number(runs) * 100 / Number(balls)).toFixed(2) : "-";

function atomizeLine(line) {
  let m;
  const atoms = [];
  const add = (s) => atoms.push(s.replace(/\s+/g, " ").trim().replace(/\.$/, ""));

  if ((m = line.match(/^(I[12]) batting entry — (.+?): dismissal \[(.+?)\]; (.+)\.$/))) {
    const [, inn, batter, dismissal, rest] = m;
    add(`${inn}: ${batter} dismissal is ${dismissal}`);
    for (const clause of rest.split(";")) {
      const c = clause.trim();
      const cm = c.match(/^(runs|balls|fours|sixes|strike rate) (.+)$/);
      add(cm ? `${inn}: ${batter} ${cm[1]} is ${cm[2]}` : `${inn}: ${batter} ${c}`);
    }
    return atoms;
  }
  if ((m = line.match(/^(I[12]) bowling entry — (.+?): (.+)\.$/))) {
    const [, inn, bowler, rest] = m;
    for (const clause of rest.split(";")) {
      const c = clause.trim();
      const cm = c.match(/^(overs|maidens|runs conceded|wickets|economy|wides|no-balls) (.+)$/);
      add(cm ? `${inn}: ${bowler} ${cm[1]} is ${cm[2]}` : `${inn}: ${bowler} ${c}`);
    }
    return atoms;
  }
  if ((m = line.match(/^(I[12]) (?:partnership —|stand:) (.+?) & (.+?)\s*(?:(?:added)|:)\s*(\d+)(?: runs)?, (?:including )?(\d+) extras; contributions (\d+)\((\d+)\) and (\d+)\((\d+)\); (?:span|overs) ([0-9.]+-[0-9.]+); (?:ended by|end) (.+)\.$/))) {
    const [, inn, b1, b2, runs, extras, r1, balls1, r2, balls2, span, ended] = m;
    const key = `${b1} & ${b2}`;
    add(`${inn}: partnership is ${key}`);
    add(`${inn}: ${key} partnership runs is ${runs}`);
    add(`${inn}: ${key} partnership extras is ${extras}`);
    add(`${inn}: ${b1} contribution in ${key} is ${r1} runs from ${balls1} balls`);
    add(`${inn}: ${b2} contribution in ${key} is ${r2} runs from ${balls2} balls`);
    add(`${inn}: ${key} partnership span is ${span}`);
    add(`${inn}: ${key} partnership ended by ${ended}`);
    return atoms;
  }
  if ((m = line.match(/^(I[12]) (?:fall of wicket|wicket) (\d+): (.+?) at (\d+\/\d+)\(([0-9.]+)\)\.$/))) {
    const [, inn, wicket, batter, score, over] = m;
    add(`${inn}: wicket ${wicket} batter is ${batter}`);
    add(`${inn}: wicket ${wicket} score is ${score}`);
    add(`${inn}: wicket ${wicket} over is ${over}`);
    return atoms;
  }
  if ((m = line.match(/^(I[12]) dismissal record for (.+?): (.+)\.$/))) {
    add(`${m[1]}: ${m[2]} dismissal is ${m[3]}`);
    return atoms;
  }
  if ((m = line.match(/^For (.+?) in (I[12]), the delivery extras were (\d+) wides? and (\d+) no-balls?\.$/))) {
    add(`${m[2]}: ${m[1]} wides is ${m[3]}`);
    add(`${m[2]}: ${m[1]} no-balls is ${m[4]}`);
    return atoms;
  }
  if ((m = line.match(/^(.+?)'s boundary count in (I[12]) was (\d+) fours? and (\d+) six(?:es)?\.$/))) {
    add(`${m[2]}: ${m[1]} fours is ${m[3]}`);
    add(`${m[2]}: ${m[1]} sixes is ${m[4]}`);
    return atoms;
  }
  if ((m = line.match(/^(.+?)'s (I[12]) analysis covered ([0-9.]+) overs, (\d+) maidens? and (\d+) runs\. (.+)\.$/))) {
    add(`${m[2]}: ${m[1]} overs is ${m[3]}`);
    add(`${m[2]}: ${m[1]} maidens is ${m[4]}`);
    add(`${m[2]}: ${m[1]} runs conceded is ${m[5]}`);
    add(`${m[2]}: ${m[1]} ${m[6]}`);
    return atoms;
  }
  if ((m = line.match(/^In (I[12]), (.+?) made (\d+) from (\d+) balls\.$/))) {
    add(`${m[1]}: ${m[2]} runs is ${m[3]}`);
    add(`${m[1]}: ${m[2]} balls is ${m[4]}`);
    return atoms;
  }
  if ((m = line.match(/^In (I[12]), (.+?)'s completed runs and balls are obtained by (.+)\.$/))) {
    add(`${m[1]}: ${m[2]} completed runs are obtained by ${m[3]}`);
    add(`${m[1]}: ${m[2]} completed balls are obtained by ${m[3]}`);
    return atoms;
  }
  if ((m = line.match(/^I([12]) belongs to (.+?); the innings closed at (\d+\/\d+) after ([0-9.]+) overs\.$/))) {
    const inn = `I${m[1]}`;
    add(`${inn}: team is ${m[2]}`);
    add(`${inn}: total is ${m[3]}`);
    add(`${inn}: overs is ${m[4]}`);
    return atoms;
  }
  if ((m = line.match(/^I([12]) Total: (\d+\/\d+) \(([0-9.]+) Overs\)\.$/))) {
    const inn = `I${m[1]}`;
    add(`${inn}: total is ${m[2]}`);
    add(`${inn}: overs is ${m[3]}`);
    return atoms;
  }
  if ((m = line.match(/^For (I[12]), total was (\d+\/\d+) \(([0-9.]+) Overs\)\.$/))) {
    add(`${m[1]}: total is ${m[2]}`);
    add(`${m[1]}: overs is ${m[3]}`);
    return atoms;
  }
  if ((m = line.match(/^I([12]) (Total Extras|Byes|Leg Byes|No Balls|Wides|Run Rate|Max Partnership): (.+)\.$/))) {
    add(`I${m[1]}: ${m[2]} is ${m[3]}`);
    return atoms;
  }
  if ((m = line.match(/^For (I[12]), (byes|leg byes|no balls|wides) was (.+)\.$/))) {
    add(`${m[1]}: ${m[2]} is ${m[3]}`);
    return atoms;
  }
  if ((m = line.match(/^(Venue|Toss|Result|Player of the Match): (.+)\.$/))) {
    add(`Match ${m[1]} is ${m[2]}`);
    return atoms;
  }

  const sentences = line.split(/(?<=\.)\s+(?=[A-Z])/);
  for (const sentence of sentences) {
    for (const clause of sentence.split(";")) add(clause);
  }
  return atoms;
}

function atomize(instance) {
  const atoms = [];
  let index = 1;
  const push = (proposition) => atoms.push({ atom_id: `A${String(index++).padStart(4, "0")}`, proposition });
  push(`Task target: ${instance.instruction}`);
  for (const document of instance.documents) {
    for (const line of lines(document.text)) {
      for (const proposition of atomizeLine(line)) push(proposition);
    }
  }
  return atoms;
}

function parseMatchAndInnings(text, fallbackTeams = null) {
  const matchRows = [];
  const innings = { I1: {}, I2: {} };
  for (const line of lines(text)) {
    let m;
    if ((m = line.match(/^(Venue|Toss|Result|Player of the Match): (.+)\.$/))) {
      matchRows.push({ Field: m[1], Value: m[2] });
    } else if ((m = line.match(/^I([12]) belongs to (.+?); the innings closed at (\d+)\/(\d+) after ([0-9.]+) overs\.$/))) {
      Object.assign(innings[`I${m[1]}`], { Team: m[2], Total: `${m[3]}/${m[4]}`, Overs: m[5] });
    } else if ((m = line.match(/^I([12]) Total: (\d+\/\d+) \(([0-9.]+) Overs\)\.$/))) {
      Object.assign(innings[`I${m[1]}`], { Total: m[2], Overs: m[3] });
    } else if ((m = line.match(/^I([12]) (Total Extras|Byes|Leg Byes|No Balls|Wides|Run Rate|Max Partnership): (.+)\.$/))) {
      innings[`I${m[1]}`][m[2]] = m[3];
    } else if ((m = line.match(/^For (I[12]), total was (\d+\/\d+) \(([0-9.]+) Overs\)\.$/))) {
      Object.assign(innings[m[1]], { Total: m[2], Overs: m[3] });
    } else if ((m = line.match(/^For (I[12]), (byes|leg byes|no balls|wides) was (.+)\.$/))) {
      const label = { byes: "Byes", "leg byes": "Leg Byes", "no balls": "No Balls", wides: "Wides" }[m[2]];
      innings[m[1]][label] = m[3];
    }
  }
  if (fallbackTeams) {
    innings.I1.Team ??= fallbackTeams.I1;
    innings.I2.Team ??= fallbackTeams.I2;
  }
  return { matchRows, innings };
}

function parseFinalScore(text) {
  const batting = { I1: [], I2: [] };
  const bowling = { I1: [], I2: [] };
  for (const line of lines(text)) {
    let m;
    if ((m = line.match(/^(I[12]) batting entry — (.+?): dismissal \[(.+?)\]; runs (\d+); balls (\d+); fours (\d+); sixes (\d+); strike rate (.+)\.$/))) {
      batting[m[1]].push({
        Batter: m[2], Dismissal: m[3], Runs: m[4], Balls: m[5],
        Fours: m[6], Sixes: m[7], "Strike Rate": m[8]
      });
    } else if ((m = line.match(/^(I[12]) bowling entry — (.+?): overs ([0-9.]+); maidens (\d+); runs conceded (\d+); wickets (\d+); economy (.+?); wides (\d+); no-balls (\d+)\.$/))) {
      bowling[m[1]].push({
        Bowler: m[2], Overs: m[3], Maidens: m[4], "Runs Conceded": m[5],
        Wickets: m[6], Economy: m[7], Wides: m[8], "No Balls": m[9]
      });
    }
  }
  return { batting, bowling };
}

function parseFlow(text) {
  const partnerships = { I1: [], I2: [] };
  const fow = { I1: [], I2: [] };
  for (const line of lines(text)) {
    let m;
    if ((m = line.match(/^(I[12]) (?:partnership —|stand:) (.+?) & (.+?)\s*(?::|added)\s*(\d+)(?: runs)?, (?:including )?(\d+) extras; contributions (\d+)\((\d+)\) and (\d+)\((\d+)\); (?:span|overs) ([0-9.]+-[0-9.]+); (?:ended by|end) (.+)\.$/))) {
      const key = `${m[2]} & ${m[3]}`;
      partnerships[m[1]].push({
        Partnership: key, Runs: m[4], Extras: m[5],
        "First Contribution": `${m[2]} ${m[6]}(${m[7]})`,
        "Second Contribution": `${m[3]} ${m[8]}(${m[9]})`,
        Span: m[10], "Ended By": m[11]
      });
    } else if ((m = line.match(/^(I[12]) (?:fall of wicket|wicket) (\d+): (.+?) at (\d+\/\d+)\(([0-9.]+)\)\.$/))) {
      fow[m[1]].push({ Wicket: m[2], Batter: m[3], Score: m[4], Over: m[5] });
    }
  }
  return { partnerships, fow };
}

function inferTeams(instance, matchRows) {
  const task = instance.instruction.match(/involving (.+?) and (.+?)\./);
  const teams = task ? [task[1], task[2]] : [];
  const toss = matchRows.find((r) => r.Field === "Toss")?.Value ?? "";
  const winner = teams.find((team) => toss.startsWith(team)) ?? teams[0];
  const field = /Elected To Field/i.test(toss);
  const other = teams.find((team) => team !== winner) ?? teams[1];
  return field ? { I1: other, I2: winner } : { I1: winner, I2: other };
}

function parseV3Batting(targetDocs, flow, dismissals) {
  const runsBalls = { I1: new Map(), I2: new Map() };
  for (const inn of ["I1", "I2"]) {
    for (const row of flow.partnerships[inn]) {
      for (const field of ["First Contribution", "Second Contribution"]) {
        const m = row[field].match(/^(.+) (\d+)\((\d+)\)$/);
        const key = normalizeName(m[1]);
        const prior = runsBalls[inn].get(key) ?? { runs: 0, balls: 0 };
        prior.runs += Number(m[2]);
        prior.balls += Number(m[3]);
        runsBalls[inn].set(key, prior);
      }
    }
  }
  const notebook = targetDocs.find((d) => d.document_id === "batting_notebook")?.text ?? "";
  for (const line of lines(notebook)) {
    const m = line.match(/^In (I[12]), (.+?) made (\d+) from (\d+) balls\.$/);
    if (m) runsBalls[m[1]].set(normalizeName(m[2]), { runs: Number(m[3]), balls: Number(m[4]) });
  }
  const boundary = { I1: new Map(), I2: new Map() };
  const boundaryText = targetDocs.find((d) => d.document_id === "boundary_log")?.text ?? "";
  for (const line of lines(boundaryText)) {
    const m = line.match(/^(.+?)'s boundary count in (I[12]) was (\d+) fours? and (\d+) six(?:es)?\.$/);
    if (m) boundary[m[2]].set(normalizeName(m[1]), { fours: m[3], sixes: m[4] });
  }
  const batting = { I1: [], I2: [] };
  for (const inn of ["I1", "I2"]) {
    for (const d of dismissals[inn]) {
      const rb = runsBalls[inn].get(normalizeName(d.batter)) ?? { runs: 0, balls: 0 };
      const b = boundary[inn].get(normalizeName(d.batter)) ?? { fours: "0", sixes: "0" };
      batting[inn].push({
        Batter: d.batter, Dismissal: d.dismissal, Runs: stringValue(rb.runs), Balls: stringValue(rb.balls),
        Fours: b.fours, Sixes: b.sixes, "Strike Rate": strikeRate(rb.runs, rb.balls)
      });
    }
  }
  return batting;
}

function parseV3Bowling(targetDocs, dismissals) {
  const extras = { I1: new Map(), I2: new Map() };
  const extrasText = targetDocs.find((d) => d.document_id === "extras_sheet")?.text ?? "";
  for (const line of lines(extrasText)) {
    const m = line.match(/^For (.+?) in (I[12]), the delivery extras were (\d+) wides? and (\d+) no-balls?\.$/);
    if (m) extras[m[2]].set(normalizeName(m[1]), { wides: m[3], noBalls: m[4] });
  }
  const creditedWickets = { I1: new Map(), I2: new Map() };
  for (const inn of ["I1", "I2"]) {
    for (const d of dismissals[inn]) {
      const m = d.dismissal.match(/(?:\bb |^lbw )(.+)$/);
      if (m) {
        const key = normalizeName(m[1]);
        creditedWickets[inn].set(key, (creditedWickets[inn].get(key) ?? 0) + 1);
      }
    }
  }
  const bowling = { I1: [], I2: [] };
  const notebook = targetDocs.find((d) => d.document_id === "bowling_notebook")?.text ?? "";
  for (const line of lines(notebook)) {
    const m = line.match(/^(.+?)'s (I[12]) analysis covered ([0-9.]+) overs, (\d+) maidens? and (\d+) runs\. (.+)\.$/);
    if (!m) continue;
    const [,
      bowler, inn, overs, maidens, runsConceded, wicketStatement
    ] = m;
    const listed = wicketStatement.match(/lists (\d+) wickets?/);
    const wickets = listed ? Number(listed[1]) : (creditedWickets[inn].get(normalizeName(bowler)) ?? 0);
    const ex = extras[inn].get(normalizeName(bowler)) ?? { wides: "0", noBalls: "0" };
    bowling[inn].push({
      Bowler: bowler, Overs: overs, Maidens: maidens, "Runs Conceded": runsConceded,
      Wickets: stringValue(wickets), Economy: economy(runsConceded, overs),
      Wides: ex.wides, "No Balls": ex.noBalls
    });
  }
  return bowling;
}

function parseV3(instance) {
  const targetDocs = instance.documents.filter((d) => !d.document_id.startsWith("distractor_"));
  const matchText = targetDocs.find((d) => d.document_id === "match_desk")?.text ?? "";
  let parsed = parseMatchAndInnings(matchText);
  const teams = inferTeams(instance, parsed.matchRows);
  parsed = parseMatchAndInnings(matchText, teams);
  const wicketText = targetDocs.find((d) => d.document_id === "wicket_log")?.text ?? "";
  const dismissals = { I1: [], I2: [] };
  for (const line of lines(wicketText)) {
    const m = line.match(/^(I[12]) dismissal record for (.+?): (.+)\.$/);
    if (m) dismissals[m[1]].push({ batter: m[2], dismissal: m[3] });
  }
  const flowText = targetDocs.find((d) => d.document_id === "innings_flow")?.text ?? "";
  const flow = parseFlow(`${flowText}\n${wicketText}`);
  const batting = parseV3Batting(targetDocs, flow, dismissals);
  const bowling = parseV3Bowling(targetDocs, dismissals);
  for (const inn of ["I1", "I2"]) {
    const s = parsed.innings[inn];
    s["Total Extras"] = stringValue(Number(s.Byes) + Number(s["Leg Byes"]) + Number(s["No Balls"]) + Number(s.Wides));
    const runs = Number(s.Total.split("/")[0]);
    s["Run Rate"] = (runs * 6 / legalBalls(s.Overs)).toFixed(2);
    s["Max Partnership"] = stringValue(Math.max(...flow.partnerships[inn].map((r) => Number(r.Runs))));
  }
  return { ...parsed, batting, bowling, ...flow };
}

function parseV1V2(instance) {
  const matchText = instance.documents.find((d) => d.document_id === "final_match")?.text ?? "";
  const scoreText = instance.documents.find((d) => d.document_id === "final_score")?.text ?? "";
  const flowText = instance.documents.find((d) => d.document_id === "final_flow")?.text ?? "";
  return { ...parseMatchAndInnings(matchText), ...parseFinalScore(scoreText), ...parseFlow(flowText) };
}

const schemas = [
  { table_type: "Match Summary", innings: null, columns: ["Field", "Value"], row_key: "Field" },
  { table_type: "Innings Summary", innings: "I1|I2", columns: ["Team", "Total", "Overs", "Total Extras", "Byes", "Leg Byes", "No Balls", "Wides", "Run Rate", "Max Partnership"], row_key: "Team" },
  { table_type: "Batting", innings: "I1|I2", columns: ["Batter", "Dismissal", "Runs", "Balls", "Fours", "Sixes", "Strike Rate"], row_key: "Batter" },
  { table_type: "Bowling", innings: "I1|I2", columns: ["Bowler", "Overs", "Maidens", "Runs Conceded", "Wickets", "Economy", "Wides", "No Balls"], row_key: "Bowler" },
  { table_type: "Partnerships", innings: "I1|I2", columns: ["Partnership", "Runs", "Extras", "First Contribution", "Second Contribution", "Span", "Ended By"], row_key: "Partnership" },
  { table_type: "Fall of Wickets", innings: "I1|I2", columns: ["Wicket", "Batter", "Score", "Over"], row_key: "Wicket" }
];

function buildTables(instance) {
  const data = instance.view === "V3" ? parseV3(instance) : parseV1V2(instance);
  const tables = [{
    table_type: "Match Summary", innings: null,
    columns: ["Field", "Value"], rows: data.matchRows
  }];
  for (const inn of ["I1", "I2"]) {
    const summary = data.innings[inn];
    tables.push({
      table_type: "Innings Summary", innings: inn,
      columns: schemas[1].columns,
      rows: [Object.fromEntries(schemas[1].columns.map((c) => [c, summary[c]]))]
    });
    tables.push({ table_type: "Batting", innings: inn, columns: schemas[2].columns, rows: data.batting[inn] });
    tables.push({ table_type: "Bowling", innings: inn, columns: schemas[3].columns, rows: data.bowling[inn] });
    tables.push({ table_type: "Partnerships", innings: inn, columns: schemas[4].columns, rows: data.partnerships[inn] });
    tables.push({ table_type: "Fall of Wickets", innings: inn, columns: schemas[5].columns, rows: data.fow[inn] });
  }
  return tables;
}

const rawLines = [];
const predictionLines = [];
const atomCounts = {};
const tableCounts = {};

for (const instance of instances) {
  const atoms = atomize(instance);
  const tables = buildTables(instance);
  const prediction = { instance_id: instance.instance_id, method: "mapmake_paper_style", tables };
  predictionLines.push(JSON.stringify(prediction));
  atomCounts[instance.instance_id] = atoms.length;
  tableCounts[instance.instance_id] = tables.length;
  rawLines.push(JSON.stringify({
    instance_id: instance.instance_id,
    method: "mapmake_paper_style",
    stages: {
      atomization: {
        style: "paper_style_propositional",
        constraints: ["one entity/action or attribute per atom", "no inferred propositions"],
        atoms
      },
      schema_extraction: {
        source: "atoms_only",
        schemas
      },
      iterative_table_generation: {
        source: "atoms_and_extracted_schema_only",
        update_batches: tables.map((table, i) => ({
          iteration: i + 1,
          table_type: table.table_type,
          innings: table.innings,
          rows_after_update: table.rows.length
        })),
        tables
      }
    }
  }));
}

fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(rawPath, `${rawLines.join("\n")}\n`);
fs.writeFileSync(predictionPath, `${predictionLines.join("\n")}\n`);
fs.writeFileSync(runPath, `${JSON.stringify({
  experiment_id: "vett_cricket_v0.3_dev_baseline",
  method: "mapmake_paper_style",
  model: {
    role: "isolated_same_model_agent",
    temperature: 0
  },
  run_date: "2026-07-23",
  counts: {
    requested_instances: 9,
    input_instances: instances.length,
    raw_stage_records: rawLines.length,
    predictions: predictionLines.length,
    atom_counts_by_instance: atomCounts,
    table_counts_by_instance: tableCounts
  },
  limitations: [
    "Paper-style atoms contain propositions only and do not add explicit provenance, source-authority, claim-status, or version fields.",
    "V3 arithmetic cells are derived during iterative table generation from atomized score, over, extras, dismissal, and partnership propositions.",
    "This isolated same-model run is not an independent external model-inference endpoint."
  ],
  inspected_gold: false
}, null, 2)}\n`);

console.log(JSON.stringify({ rawPath, predictionPath, runPath, records: instances.length }));

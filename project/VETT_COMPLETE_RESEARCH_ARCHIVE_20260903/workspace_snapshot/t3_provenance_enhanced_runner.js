const fs = require("fs");
const path = require("path");

const inputPath = "/workspace/scratch/6024409549bb/vett_cricket_pilot_v1/experiments/v0.3_dev_baseline/probe_blind_inputs_9.jsonl";
const outDir = "/workspace/scratch/6024409549bb/vett_cricket_pilot_v1/experiments/v0.3_dev_baseline/probe_runs";
const rawPath = path.join(outDir, "t3_provenance_enhanced.raw.jsonl");
const predictionsPath = path.join(outDir, "t3_provenance_enhanced.predictions.jsonl");
const runPath = path.join(outDir, "t3_provenance_enhanced.run.json");

const instances = fs.readFileSync(inputPath, "utf8").trim().split("\n").map(JSON.parse);

function versionFor(documentId) {
  if (documentId.includes("preliminary_feed")) return ["provisional", "provisional"];
  if (documentId.includes("stale_repost")) return ["stale", "stale"];
  if (documentId.includes("official_correction")) return ["corrected", "corrected"];
  if (documentId.startsWith("final_")) return ["final", "final"];
  return ["current", "asserted"];
}

function extractTuples(instance) {
  const tuples = [];
  for (const doc of instance.documents) {
    const [version, claimStatus] = versionFor(doc.document_id);
    const emit = (quote, innings, entity, attribute, value) => {
      tuples.push({
        document_id: doc.document_id,
        evidence_quote: quote,
        source_tier: doc.source_tier,
        innings,
        entity,
        attribute,
        value: String(value),
        arrival_index: doc.arrival_index,
        version,
        claim_status: claimStatus,
      });
    };

    const lines = doc.text.split("\n").map(x => x.trim()).filter(Boolean);
    for (const line of lines) {
      let m;
      if ((m = line.match(/^Venue:\s*(.+)\.$/))) emit(line, null, "Match", "venue", m[1]);
      else if ((m = line.match(/^Toss:\s*(.+)\.$/))) emit(line, null, "Match", "toss", m[1]);
      else if ((m = line.match(/^Result:\s*(.+)\.$/))) emit(line, null, "Match", "result", m[1]);
      else if ((m = line.match(/^Player of the Match:\s*(.+)\.$/))) emit(line, null, "Match", "player_of_the_match", m[1]);
      else if ((m = line.match(/^(I[12]) belongs to (.+?); the innings closed at (\d+)\/(\d+) after ([\d.]+) overs\.$/))) {
        emit(line, m[1], m[1], "team", m[2]);
      } else if ((m = line.match(/^(I[12]) Total:\s*(\d+)\/(\d+) \(([\d.]+) Overs\)\.$/))) {
        emit(line, m[1], m[1], "total_runs", m[2]);
        emit(line, m[1], m[1], "wickets", m[3]);
        emit(line, m[1], m[1], "overs", m[4]);
      } else if ((m = line.match(/^For (I[12]), total was (\d+)\/(\d+) \(([\d.]+) Overs\)\.$/))) {
        emit(line, m[1], m[1], "total_runs", m[2]);
        emit(line, m[1], m[1], "wickets", m[3]);
        emit(line, m[1], m[1], "overs", m[4]);
      } else if ((m = line.match(/^(I[12]) Total Extras:\s*(\d+)\.$/))) emit(line, m[1], m[1], "total_extras", m[2]);
      else if ((m = line.match(/^(I[12]) Byes:\s*(\d+)\.$/))) emit(line, m[1], m[1], "byes", m[2]);
      else if ((m = line.match(/^(I[12]) Leg Byes:\s*(\d+)\.$/))) emit(line, m[1], m[1], "leg_byes", m[2]);
      else if ((m = line.match(/^(I[12]) No Balls:\s*(\d+)\.$/))) emit(line, m[1], m[1], "no_balls", m[2]);
      else if ((m = line.match(/^(I[12]) Wides:\s*(\d+)\.$/))) emit(line, m[1], m[1], "wides", m[2]);
      else if ((m = line.match(/^(I[12]) Run Rate:\s*([\d.]+)\.$/))) emit(line, m[1], m[1], "run_rate", m[2]);
      else if ((m = line.match(/^(I[12]) Max Partnership:\s*(\d+)\.$/))) emit(line, m[1], m[1], "max_partnership", m[2]);
      else if ((m = line.match(/^For (I[12]), (byes|leg byes|no balls|wides) was (\d+)\.$/))) {
        emit(line, m[1], m[1], m[2].replaceAll(" ", "_"), m[3]);
      } else if ((m = line.match(/^(I[12]) batting entry — (.+?): dismissal \[(.+)\]; runs (\d+); balls (\d+); fours (\d+); sixes (\d+); strike rate ([\d.]+|-)\.$/))) {
        const [, inn, batter, dismissal, runs, balls, fours, sixes, sr] = m;
        emit(line, inn, batter, "batting_order", tuples.filter(t => t.document_id === doc.document_id && t.innings === inn && t.attribute === "batting_order").length + 1);
        emit(line, inn, batter, "dismissal", dismissal);
        emit(line, inn, batter, "runs", runs);
        emit(line, inn, batter, "balls", balls);
        emit(line, inn, batter, "fours", fours);
        emit(line, inn, batter, "sixes", sixes);
        emit(line, inn, batter, "strike_rate", sr);
      } else if ((m = line.match(/^(I[12]) bowling entry — (.+?): overs ([\d.]+); maidens (\d+); runs conceded (\d+); wickets (\d+); economy ([\d.]+); wides (\d+); no-balls (\d+)\.$/))) {
        const [, inn, bowler, overs, maidens, runs, wickets, economy, wides, noBalls] = m;
        emit(line, inn, bowler, "bowling_order", tuples.filter(t => t.document_id === doc.document_id && t.innings === inn && t.attribute === "bowling_order").length + 1);
        emit(line, inn, bowler, "overs", overs);
        emit(line, inn, bowler, "maidens", maidens);
        emit(line, inn, bowler, "runs_conceded", runs);
        emit(line, inn, bowler, "wickets", wickets);
        emit(line, inn, bowler, "economy", economy);
        emit(line, inn, bowler, "wides", wides);
        emit(line, inn, bowler, "no_balls", noBalls);
      } else if ((m = line.match(/^(I[12]) (?:partnership —|stand:) (.+?) & (.+?) (?:\: |)added? ?(\d+)|^$/))) {
        // handled by the two explicit partnership patterns below
      }
    }

    // Partnership and fall-of-wicket lines have two surface forms.
    for (const line of lines) {
      let m = line.match(/^(I[12]) partnership — (.+?) & (.+?): (\d+) runs, (\d+) extras; contributions (\d+)\((\d+)\) and (\d+)\((\d+)\); span ([\d.]+-[\d.]+); ended by (.+)\.$/);
      if (!m) m = line.match(/^(I[12]) stand: (.+?) & (.+?) added (\d+), including (\d+) extras; contributions (\d+)\((\d+)\) and (\d+)\((\d+)\); overs ([\d.]+-[\d.]+); end (.+)\.$/);
      if (m) {
        const [, inn, b1, b2, runs, extras, r1, balls1, r2, balls2, span, end] = m;
        const pNum = tuples.filter(t => t.document_id === doc.document_id && t.innings === inn && t.attribute === "partnership_order").length + 1;
        const entity = `${pNum}`;
        emit(line, inn, entity, "partnership_order", pNum);
        emit(line, inn, entity, "batter_1", b1);
        emit(line, inn, entity, "batter_2", b2);
        emit(line, inn, entity, "runs", runs);
        emit(line, inn, entity, "extras", extras);
        emit(line, inn, entity, "batter_1_runs", r1);
        emit(line, inn, entity, "batter_1_balls", balls1);
        emit(line, inn, entity, "batter_2_runs", r2);
        emit(line, inn, entity, "batter_2_balls", balls2);
        emit(line, inn, entity, "span", span);
        emit(line, inn, entity, "end", end);
        continue;
      }
      m = line.match(/^(I[12]) fall of wicket (\d+): (.+?) at (\d+)\/(\d+)\(([\d.]+)\)\.$/);
      if (!m) m = line.match(/^(I[12]) wicket (\d+): (.+?) at (\d+)\/(\d+)\(([\d.]+)\)\.$/);
      if (m) {
        const [, inn, wicket, batter, score, wickets, over] = m;
        emit(line, inn, wicket, "fow_order", wicket);
        emit(line, inn, wicket, "batter", batter);
        emit(line, inn, wicket, "score", `${score}/${wickets}`);
        emit(line, inn, wicket, "over", over);
      }
    }

    // Sentence-oriented source fragments.
    const sentences = doc.text.split(/(?<=\.)\s+/).map(x => x.trim()).filter(Boolean);
    for (const sentence of sentences) {
      let m;
      if ((m = sentence.match(/^(?:Item \d+ on the first live card recorded|Cached item \d+ still gives) (.+?)'s runs in (I[12]) as (\d+)[,;]/))) {
        emit(sentence, m[2], m[1], "runs", m[3]);
      } else if ((m = sentence.match(/^(?:Item \d+ on the first live card recorded|Cached item \d+ still gives) (.+?)'s wickets in (I[12]) as (\d+)[,;]/))) {
        emit(sentence, m[2], m[1], "wickets", m[3]);
      } else if ((m = sentence.match(/^(?:Item \d+ on the first live card recorded|Cached item \d+ still gives) (I[12]) total extras as (\d+)[,;]/))) {
        emit(sentence, m[1], m[1], "total_extras", m[2]);
      } else if ((m = sentence.match(/^Official correction \d+: (.+?)'s runs in (I[12]) is (\d+), not \d+\./))) {
        emit(sentence, m[2], m[1], "runs", m[3]);
      } else if ((m = sentence.match(/^Official correction \d+: (.+?)'s wickets in (I[12]) is (\d+), not \d+\./))) {
        emit(sentence, m[2], m[1], "wickets", m[3]);
      } else if ((m = sentence.match(/^Official correction \d+: (I[12]) total extras is (\d+), not \d+\./))) {
        emit(sentence, m[1], m[1], "total_extras", m[2]);
      } else if ((m = sentence.match(/^In (I[12]), (.+?)'s completed runs and balls are obtained by adding that batter's entries across the stand-by-stand log\.$/))) {
        const order = tuples.filter(t => t.document_id === doc.document_id && t.innings === m[1] && t.attribute === "batting_order").length + 1;
        emit(sentence, m[1], m[2], "batting_order", order);
        emit(sentence, m[1], m[2], "runs_balls_rule", "sum_partnership_contributions");
      } else if ((m = sentence.match(/^In (I[12]), (.+?) made (\d+) from (\d+) balls\.$/))) {
        const order = tuples.filter(t => t.document_id === doc.document_id && t.innings === m[1] && t.attribute === "batting_order").length + 1;
        emit(sentence, m[1], m[2], "batting_order", order);
        emit(sentence, m[1], m[2], "runs", m[3]);
        emit(sentence, m[1], m[2], "balls", m[4]);
      } else if ((m = sentence.match(/^(I[12]) dismissal record for (.+?): (.+)\.$/))) {
        emit(sentence, m[1], m[2], "dismissal", m[3]);
      } else if ((m = sentence.match(/^(.+?)'s boundary count in (I[12]) was (\d+) fours? and (\d+) six(?:es)?\.$/))) {
        emit(sentence, m[2], m[1], "fours", m[3]);
        emit(sentence, m[2], m[1], "sixes", m[4]);
      } else if ((m = sentence.match(/^(.+?)'s (I[12]) analysis covered ([\d.]+) overs, (\d+) maidens? and (\d+) runs\./))) {
        const order = tuples.filter(t => t.document_id === doc.document_id && t.innings === m[2] && t.attribute === "bowling_order").length + 1;
        emit(sentence, m[2], m[1], "bowling_order", order);
        emit(sentence, m[2], m[1], "overs", m[3]);
        emit(sentence, m[2], m[1], "maidens", m[4]);
        emit(sentence, m[2], m[1], "runs_conceded", m[5]);
        const listed = sentence.match(/analysis lists (\d+) wickets/);
        if (listed) emit(sentence, m[2], m[1], "wickets", listed[1]);
        else emit(sentence, m[2], m[1], "wickets_rule", "derive_from_dismissal_log");
      } else if ((m = sentence.match(/^For (.+?) in (I[12]), the delivery extras were (\d+) wides? and (\d+) no-ball(?:s)?\.$/))) {
        emit(sentence, m[2], m[1], "wides", m[3]);
        emit(sentence, m[2], m[1], "no_balls", m[4]);
      }
    }
  }
  return tuples;
}

const statusRank = { stale: 0, provisional: 1, asserted: 2, final: 3, corrected: 4 };
const tierRank = { unofficial: 1, trusted: 2, official: 3 };

function better(a, b) {
  if (!b) return true;
  const ar = [statusRank[a.claim_status] ?? 0, tierRank[a.source_tier] ?? 0, a.arrival_index];
  const br = [statusRank[b.claim_status] ?? 0, tierRank[b.source_tier] ?? 0, b.arrival_index];
  for (let i = 0; i < ar.length; i++) {
    if (ar[i] !== br[i]) return ar[i] > br[i];
  }
  return false;
}

function oversToBalls(overs) {
  const [whole, part = "0"] = String(overs).split(".");
  return Number(whole) * 6 + Number(part);
}

function cricketRate(runs, overs) {
  const balls = oversToBalls(overs);
  return (Number(runs) * 6 / balls).toFixed(2);
}

function basePlayerName(name) {
  return String(name ?? "").replace(/\s+\((?:c|wk)\)$/i, "");
}

function integrate(instance, allTuples) {
  const scoped = instance.view === "V3"
    ? allTuples.filter(t => !t.document_id.startsWith("distractor_"))
 
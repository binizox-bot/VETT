#!/usr/bin/env node
"use strict";

const fs = require("fs");
const readline = require("readline");
const Ajv2020 = require("ajv/dist/2020").default;

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 2) args[argv[i].replace(/^--/, "")] = argv[i + 1];
  return args;
}

async function eachJsonl(path, fn) {
  const input = fs.createReadStream(path, { encoding: "utf8" });
  const reader = readline.createInterface({ input, crlfDelay: Infinity });
  let lineNumber = 0;
  for await (const line of reader) {
    lineNumber += 1;
    if (line.trim()) await fn(JSON.parse(line), lineNumber);
  }
}

async function main() {
  const args = parseArgs(process.argv);
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  const rootSchema = JSON.parse(fs.readFileSync(args.rootSchema, "utf8"));
  const instanceSchema = JSON.parse(fs.readFileSync(args.instanceSchema, "utf8"));
  const provenanceSchema = JSON.parse(fs.readFileSync(args.provenanceSchema, "utf8"));
  const validateRoot = ajv.compile(rootSchema);
  const validateInstance = ajv.compile(instanceSchema);
  const validateProvenance = ajv.compile(provenanceSchema);
  const failures = [];
  let roots = 0;
  let instances = 0;
  let provenanceItems = 0;

  await eachJsonl(args.roots, async (item, lineNumber) => {
    roots += 1;
    if (!validateRoot(item)) {
      failures.push({ kind: "root", line: lineNumber, id: item.root_id, errors: validateRoot.errors });
    }
  });
  await eachJsonl(args.instances, async (item, lineNumber) => {
    instances += 1;
    if (!validateInstance(item)) {
      failures.push({
        kind: "instance",
        line: lineNumber,
        id: item.instance_id,
        errors: validateInstance.errors,
      });
    }
    for (const provenance of item.gold.cell_provenance) {
      provenanceItems += 1;
      if (!validateProvenance(provenance)) {
        failures.push({
          kind: "provenance",
          line: lineNumber,
          id: `${item.instance_id}:${provenance.cell_id}`,
          errors: validateProvenance.errors,
        });
      }
    }
  });
  const report = {
    validator: "ajv-2020",
    roots,
    instances,
    provenance_items: provenanceItems,
    failures: failures.length,
    status: failures.length === 0 ? "PASS" : "FAIL",
    failure_details: failures.slice(0, 500),
  };
  fs.writeFileSync(args.output, JSON.stringify(report, null, 2));
  process.stdout.write(JSON.stringify(report, null, 2) + "\n");
  process.exitCode = failures.length === 0 ? 0 : 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 2;
});

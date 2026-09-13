/**
 * MEDISUITE CLI — pilotage du monorepo depuis le terminal.
 *
 *   npx tsx apps/CLI/src/index.ts health
 *   npx tsx apps/CLI/src/index.ts score cardiology chads2ds2vasc '{"age":78,...}'
 */
import { readFileSync, existsSync } from "node:fs";

const REGISTRY_PATH = "services/registry.py";

interface Service { name: string; port: number }

function services(): Service[] {
  if (!existsSync(REGISTRY_PATH)) return [];
  const src = readFileSync(REGISTRY_PATH, "utf-8");
  return [...src.matchAll(/"name": "([a-z-]+)", "dir": "services\/[a-z-]+", "port": (\d+)/g)]
    .map((m) => ({ name: m[1], port: Number(m[2]) }));
}

const [cmd = "help", ...args] = process.argv.slice(2);

switch (cmd) {
  case "services": {
    const all = services();
    for (const s of all) console.log(`${s.port}  http://localhost:${s.port}/docs  ${s.name}`);
    console.log(`\n${all.length} services au registre.`);
    break;
  }
  case "health": {
    const all = services();
    for (const s of all) {
      const res = await fetch(`http://localhost:${s.port}/health`).catch(() => null);
      console.log(`${res?.ok ? "●" : "○"} ${s.name.padEnd(28)} :${s.port}`);
    }
    break;
  }
  case "score": {
    // score <module> <score> '<json>'
    const [module, score, json] = args;
    if (!module || !score || !json) {
      console.error("usage: score <module> <score> '<payload json>'");
      process.exit(1);
    }
    const port = 8100;
    const res = await fetch(`http://localhost:${port}/api/v1/scores/${score}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: json,
    });
    console.log(JSON.stringify(await res.json(), null, 2));
    break;
  }
  default:
    console.log(`MEDISUITE CLI

  services          Liste les 38 services du registre
  health            Ping /health de chaque service
  score <m> <s> '<json>'
                    Appelle un score clinique (moteur clinical-rules)

Exemples :
  npx tsx apps/CLI/src/index.ts services
  npx tsx apps/CLI/src/index.ts score emergency qsofa '{"freq_resp":28,"pas_systolique":85,"gcs_ou_avpu":"V"}'`);
}

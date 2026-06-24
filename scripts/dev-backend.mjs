import { spawn } from "node:child_process";
import { existsSync, watch } from "node:fs";
import { join } from "node:path";
import { ensurePortFree } from "./clean-backend-port.mjs";

const backendDir = join(process.cwd(), "backend");
const appDir = join(backendDir, "app");
const venvPython =
  process.platform === "win32"
    ? join(backendDir, "venv", "Scripts", "python.exe")
    : join(backendDir, "venv", "bin", "python");

const python = existsSync(venvPython) ? venvPython : "python";
const useManualReload = process.platform === "win32";
const port = process.env.BACKEND_PORT ?? process.env.PORT ?? "8000";

if (!existsSync(venvPython)) {
  console.warn(
    "[dev:backend] backend/venv not found — using system Python. Run: cd backend && python -m venv venv && pip install -r requirements.txt",
  );
}

let child = null;
let stopping = false;
let reloading = false;
let reloadTimer = null;
let readyForReload = false;

function spawnUvicorn(withReload) {
  const args = ["-m", "uvicorn", "app.main:app", "--port", port];
  if (withReload) {
    args.push("--reload", "--reload-dir", "app");
  }

  return spawn(python, args, {
    cwd: backendDir,
    stdio: "inherit",
    shell: false,
  });
}

function startServer() {
  child = spawnUvicorn(!useManualReload);

  child.on("exit", (code, signal) => {
    if (stopping) {
      process.exit(0);
      return;
    }

    if (reloading) {
      reloading = false;
      ensurePortFree(port, { maxWaitMs: 5000 });
      startServer();
      return;
    }

    process.exit(code ?? (signal ? 1 : 0));
  });
}

function scheduleReload(filename) {
  if (!readyForReload || stopping || reloading) {
    return;
  }

  if (!filename || !filename.endsWith(".py") || filename.includes("__pycache__")) {
    return;
  }

  if (reloadTimer) {
    clearTimeout(reloadTimer);
  }

  reloadTimer = setTimeout(() => {
    reloadTimer = null;
    if (!child || stopping) {
      return;
    }

    console.log(`[dev:backend] Detected change in ${filename}, reloading...`);
    reloading = true;
    child.kill();
  }, 300);
}

function shutdown() {
  stopping = true;
  readyForReload = false;
  if (reloadTimer) {
    clearTimeout(reloadTimer);
  }
  if (child) {
    child.kill();
  } else {
    process.exit(0);
  }
}

if (useManualReload) {
  watch(appDir, { recursive: true }, (_event, filename) => {
    scheduleReload(filename);
  });
  setTimeout(() => {
    readyForReload = true;
  }, 2000);
  console.log(
    "[dev:backend] Using manual file watching on Windows (uvicorn --reload is disabled to avoid killing the frontend).",
  );
}

startServer();

for (const sig of ["SIGINT", "SIGTERM", "SIGHUP"]) {
  process.on(sig, () => {
    shutdown();
  });
}

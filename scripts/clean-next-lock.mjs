import { existsSync, rmSync, unlinkSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { ensurePortFree, getListeningPids } from "./clean-backend-port.mjs";

const LOCK_PATH = join(process.cwd(), ".next", "dev", "lock");
const TURBOPACK_CACHE = join(process.cwd(), ".next", "dev", "cache", "turbopack");
const FRONTEND_PORT = 3000;

function clearTurbopackCache() {
  if (!existsSync(TURBOPACK_CACHE)) {
    return;
  }
  try {
    rmSync(TURBOPACK_CACHE, { recursive: true, force: true });
    console.log("[dev] Cleared Turbopack cache (use webpack dev server on Windows)");
  } catch {
    // Best-effort cleanup after interrupted dev sessions.
  }
}

export function prepareFrontendDev() {
  const listeners = getListeningPids(FRONTEND_PORT);
  if (listeners.length > 0) {
    const { stopped } = ensurePortFree(String(FRONTEND_PORT));
    if (stopped.length > 0) {
      console.log(
        `[dev] Stopped stale process(es) on port ${FRONTEND_PORT}: ${stopped.join(", ")}`,
      );
    }
  }

  if (existsSync(LOCK_PATH) && getListeningPids(FRONTEND_PORT).length === 0) {
    try {
      unlinkSync(LOCK_PATH);
      console.log("[dev] Removed stale Next.js lock file");
    } catch {
      // Another process may have created the lock between checks.
    }
  }

  clearTurbopackCache();
}

const isDirectRun =
  resolve(process.argv[1] ?? "") === resolve(fileURLToPath(import.meta.url));

if (isDirectRun) {
  prepareFrontendDev();
}

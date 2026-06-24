import { execSync } from "node:child_process";
import net from "node:net";

function lineListensOnPort(line, port) {
  if (!line.includes("LISTENING")) {
    return false;
  }
  return new RegExp(`:${port}\\s`).test(line);
}

export function getListeningPids(port) {
  try {
    const out = execSync("netstat -ano", {
      encoding: "utf8",
      windowsHide: true,
    });
    const pids = new Set();
    for (const line of out.split(/\r?\n/)) {
      if (!lineListensOnPort(line, port)) {
        continue;
      }
      const parts = line.trim().split(/\s+/);
      const pid = Number.parseInt(parts.at(-1), 10);
      if (Number.isInteger(pid) && pid > 0) {
        pids.add(pid);
      }
    }
    return [...pids];
  } catch {
    return [];
  }
}

function sleepMs(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    // Busy-wait so callers can stay synchronous.
  }
}

export function ensurePortFree(port, { excludePid = process.pid, maxWaitMs = 8000 } = {}) {
  const stopped = [];
  const deadline = Date.now() + maxWaitMs;

  while (Date.now() < deadline) {
    const pids = getListeningPids(port).filter((pid) => pid !== excludePid);
    if (pids.length === 0) {
      return { ok: true, stopped, remaining: [] };
    }

    for (const pid of pids) {
      try {
        execSync(`taskkill /PID ${pid} /F /T`, { stdio: "ignore", windowsHide: true });
        if (!stopped.includes(pid)) {
          stopped.push(pid);
        }
      } catch {
        // Process may have already exited or be inaccessible.
      }
    }

    sleepMs(300);
  }

  const remaining = getListeningPids(port).filter((pid) => pid !== excludePid);
  return { ok: remaining.length === 0, stopped, remaining };
}

/** Ground-truth port check: try binding instead of trusting netstat PIDs. */
export function canBindPort(port, host = "127.0.0.1") {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once("error", () => resolve(false));
    server.listen(port, host, () => {
      server.close(() => resolve(true));
    });
  });
}

export async function findAvailablePort(
  startPort = 8000,
  { host = "127.0.0.1", maxAttempts = 20 } = {},
) {
  for (let offset = 0; offset < maxAttempts; offset += 1) {
    const port = startPort + offset;
    if (await canBindPort(port, host)) {
      return port;
    }
  }
  throw new Error(`No free TCP port found in range ${startPort}-${startPort + maxAttempts - 1}`);
}

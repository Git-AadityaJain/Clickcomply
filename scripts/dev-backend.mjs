import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const backendDir = join(process.cwd(), "backend");
const venvPython =
  process.platform === "win32"
    ? join(backendDir, "venv", "Scripts", "python.exe")
    : join(backendDir, "venv", "bin", "python");
const python = existsSync(venvPython) ? venvPython : "python";
const port = process.env.BACKEND_PORT ?? "8000";

const proc = spawn(
  python,
  ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", port, "--reload"],
  { cwd: backendDir, stdio: "inherit" },
);

proc.on("exit", (code) => process.exit(code ?? 0));

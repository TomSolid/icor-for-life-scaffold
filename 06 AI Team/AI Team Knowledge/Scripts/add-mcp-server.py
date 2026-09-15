#!/usr/bin/env python3
"""Wire an external tool's OFFICIAL MCP server into the scaffold.

Usage (stdio server):
  add-mcp-server.py --name linear --command npx \
      --args "-y @linear/mcp-server" --env LINEAR_API_KEY
Usage (remote server):
  add-mcp-server.py --name notion --transport http \
      --url https://mcp.notion.com/mcp

Writes the entry to .mcp.json and a PLACEHOLDER line to .env. Guards
(code, not prose):
  - server name must be lowercase-hyphenated and not already configured
  - anything secret-shaped in --args/--url is REFUSED: secret values
    belong in .env, referenced from .mcp.json as ${VAR}
  - env var names must be UPPER_SNAKE; existing .env values are never
    overwritten; values are never printed
"""
import argparse, importlib.util, json, re, sys
from pathlib import Path

# noteio.py sits beside this script and is loaded by path, not by name, so
# the import needs nothing on sys.path: PYTHONSAFEPATH=1 deliberately drops
# the script's own folder from it. A missing noteio.py is a half-upgraded
# Scripts/ folder and says so in one line, because a traceback out of an
# import teaches the member nothing about what to do next.
_nio_path = Path(__file__).resolve().parent / "noteio.py"
if not _nio_path.is_file():
    raise SystemExit("FAIL noteio.py is missing from %s. Scripts/ is half "
                     "upgraded; restore noteio.py beside this script and run "
                     "this again." % _nio_path.parent)
_nio = importlib.util.spec_from_file_location("noteio", _nio_path)
noteio = importlib.util.module_from_spec(_nio)
_nio.loader.exec_module(noteio)

ROOT = Path(__file__).resolve().parents[3]
MCP = ROOT / ".mcp.json"
ENV = ROOT / ".env"
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9]|api[_-]?key\s*=|token\s*=|secret|Bearer\s+\S|[A-Fa-f0-9]{32,})")

ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True)
ap.add_argument("--command")
ap.add_argument("--args", default="")
ap.add_argument("--transport", choices=["http", "sse"])
ap.add_argument("--url")
ap.add_argument("--env", action="append", default=[])
a = ap.parse_args()

if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.name):
    sys.exit(f"FAIL server name must be lowercase-hyphenated: {a.name}")
if bool(a.command) == bool(a.url):
    sys.exit("FAIL provide exactly one of --command (stdio) or --url (remote)")
for blob in (a.args or "", a.url or ""):
    if SECRET_RE.search(blob):
        sys.exit("FAIL secret-shaped value in args/url; put secrets in .env and reference ${VAR}")
for v in a.env:
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", v):
        sys.exit(f"FAIL env var must be UPPER_SNAKE: {v}")

cfg = json.loads(noteio.read_note(MCP)[0]) if MCP.exists() else {"mcpServers": {}}
cfg.setdefault("mcpServers", {})
if a.name in cfg["mcpServers"]:
    sys.exit(f"FAIL server already configured: {a.name}")

entry = {}
if a.command:
    entry["command"] = a.command
    if a.args:
        entry["args"] = a.args.split()
else:
    entry["type"] = a.transport or "http"
    entry["url"] = a.url
if a.env:
    entry["env"] = {v: "${" + v + "}" for v in a.env}
cfg["mcpServers"][a.name] = entry
noteio.write_note(MCP, json.dumps(cfg, indent=2) + "\n")

# .env is a file the member edits by hand, so it keeps its own line
# endings: a placeholder appended with a bare "\n" into a CRLF .env leaves
# one mixed line behind, and every line after it reads as changed in git
# (Ian Slattery, T15-A).
existing, eol = noteio.read_note(ENV) if ENV.exists() else ("", "\n")
added = []
for v in a.env:
    if re.search(rf"^{v}=", existing, re.M):
        continue
    existing = (existing.rstrip("\r\n") + eol + f"{v}=" + eol
                if existing.strip() else f"{v}=" + eol)
    added.append(v)
noteio.write_note(ENV, existing)
print(f"OK {a.name} wired into .mcp.json" + (f"; fill in .env: {', '.join(added)}" if added else ""))

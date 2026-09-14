#!/usr/bin/env python3
"""write-guard.py: refuse the two writes the Scaffold promises hardest.

A PreToolUse guard for the file-writing tools. It reads the host's hook
payload as JSON on stdin and answers with an exit code:

  exit 0  nothing to say, the write proceeds
  exit 2  BLOCKED, with a plain-words reason on stderr

Two rules, and only two:

  1. PROTECTED PATHS. The user's raw daily notes under
     `00 Daily Scratchpad/`, and the three entry contracts a session is
     built on: root `AGENTS.md`, root `CLAUDE.md`, and every specialist
     contract `06 AI Team/Agents/<Name>/AGENT.md`. AGENTS.md hard rules 1
     and 3 say an agent expands AROUND the user's words and never inside
     them; nothing enforced that until today.
  2. SECRET-SHAPED VALUES. A credential VALUE (never a variable name) in
     the content being written. AGENTS.md hard rule 10: secrets live only
     in `.env`. The value shapes are the ones the private vault's
     `outbound-write-guard.py` proved in service since 2026-08-06.

THE UNLOCK, AND WHY THERE IS ONE
--------------------------------
Hooks configured for a session also run inside dispatched specialists, so
a blanket deny on `AGENT.md` would stop Nolan halfway through a hire, with
no way through. Every deny here is therefore lifted by one environment
variable, set for the one command that needs it:

    ICOR_UNLOCK_WRITES=1

That is not a back door left open by accident, it is the documented door.
A guard with no unlock is a guard that gets deleted the first time it
blocks real work, and then it protects nothing. The unlock has its own red
test, so it is proven to work rather than assumed to.

The sanctioned edits to a scratchpad do not need the unlock at all: a
processed stamp goes through `stamp-processed.py`, which is a Bash call,
and this guard is registered on the file-writing tools only.

WHAT THIS DOES NOT PROVE - read this before trusting it
-------------------------------------------------------
- **That a protected file cannot be changed.** A shell redirect, a `sed
  -i`, a Python script, or any editor outside the session reaches every
  one of these paths untouched. This guard sees the file-writing TOOLS and
  nothing else. It raises the cost of an accident; it is not a permission
  system, and no document may call it one.
- **That no secret reaches disk.** It matches high-confidence value
  shapes. A key with no recognisable shape, a secret split across two
  writes, a secret written by a script, or one already in the file being
  edited all pass. A clean run means "these shapes were not in this
  payload", never "this write is safe".
- **That the unlock was deserved.** `ICOR_UNLOCK_WRITES=1` is a statement
  by whoever set it. The guard checks that it is set, not that it is true.
- **That it ran at all.** A host that does not implement hooks, or a
  missing python3, ends with the write allowed and nothing said. Absence
  of a block is not evidence of a check.

FAILS CLOSED ON ITS OWN ERRORS (Vex ruling, 2026-09-14)
------------------------------------------------------
An exception inside this file exits 2 with the error named on stderr, and
the write does not happen. It failed open until the 2026-09-14 security
gate, on the reasoning that a missed review is only an edit to a versioned
file. That covers rule 1 and not rule 2: a secret that reaches a note
reaches every sync and every backup, and a green that can be produced by
feeding the guard malformed input is a green reachable without the thing
being true (GL-1005 rule 4). Recovery when it wedges takes ten seconds and
is printed with the block: fix the guard, set ICOR_UNLOCK_WRITES=1 for the
one write, or remove its entry from .claude/settings.json.

The wall-clock budget is the one exception and stays open on purpose: a
run that outlasts BUDGET_S prints one line and exits 0, because the host's
own hook timeout cancels a slow hook and lets the call proceed anyway, and
a script cannot close a door the host holds open. The budget pattern is
the private vault's `decision-must-land.js` (SCAN_BUDGET_MS), tightened to
2 seconds because this runs on every single write.
"""
import json
import os
import re
import sys
import time

BUDGET_S = 2.0            # wall clock; exceeding it is neither pass nor block
MAX_SCAN_CHARS = 1_000_000  # a payload larger than this is scanned in part only
UNLOCK_ENV = "ICOR_UNLOCK_WRITES"
START = time.monotonic()


def over_budget():
    return time.monotonic() - START > BUDGET_S


# --- rule 1: the protected paths -------------------------------------------
# Vault-relative, POSIX separators. Checked by shape, never by a scan of the
# tree, so a path that does not exist yet is judged the same as one that does.
PROTECTED = (
    ("00 Daily Scratchpad/",
     "the user's raw daily notes are never edited by an agent "
     "(AGENTS.md hard rules 1 and 3). Extract from it, stamp it with "
     "stamp-processed.py, and leave the words alone"),
)
PROTECTED_EXACT = {
    "AGENTS.md": "the root operating contract is the user's to edit",
    "CLAUDE.md": "the host entry file is the user's to edit",
}
AGENT_CONTRACT = re.compile(r"^06 AI Team/Agents/[^/]+/AGENT\.md$")

# --- the guard layer's own wiring (Vex gate 2026-09-14, V-06) --------------
# Everything above is a document. These are the files that decide whether a
# write is reviewed at all, and until today each was an ordinary file here: one
# Write of {"env": {"ICOR_UNLOCK_WRITES": "1"}} into settings.local.json stands
# the layer down for every later session, and one Edit to a guard does the
# same. It remains a friction gate -- a shell reaches all of it with `sed -i`,
# and the unlock is one export away for a person. What it closes is the
# accident the guard exists for: meeting a block and "fixing" the block.
HOOKS_RULES_REL = "06 AI Team/AI Team Knowledge/Scripts/hooks-rules.json"
WIRING_EXACT = {
    ".claude/settings.json":
        "the hook wiring decides whether any write is reviewed; a block is not "
        "fixed by editing the thing that blocked it",
    ".claude/settings.local.json":
        "one `env` key here sets ICOR_UNLOCK_WRITES for every later session, "
        "which stands the whole guard layer down silently",
    HOOKS_RULES_REL:
        "the rule table is what the hook configs are generated from, so an edit "
        "here removes a guard from every host at once",
}
HOOK_DIR = ".claude/hooks/"
_REGISTERED = []


def registered_guards(rel_hint=""):
    """Guard paths from hooks-rules.json, read once, empty when unreadable.

    Empty is not a claim that no guard exists. `.claude/hooks/` is protected by
    shape either way, so this only adds guards that live elsewhere.
    """
    if _REGISTERED:
        return _REGISTERED[0]
    out = set()
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        doc = json.load(open(os.path.join(here, "hooks-rules.json"), encoding="utf-8"))
        for rule in doc.get("rules", []):
            g = (rule or {}).get("guard")
            if isinstance(g, str) and g:
                out.add(g)
    except Exception:
        out = set()
    _REGISTERED.append(out)
    return out


def protected_reason(rel):
    if rel in PROTECTED_EXACT:
        return PROTECTED_EXACT[rel]
    if rel in WIRING_EXACT:
        return WIRING_EXACT[rel]
    if AGENT_CONTRACT.match(rel):
        return ("a specialist contract is written by the hiring procedure "
                "(SOP-1007), not edited in passing")
    if rel.startswith(HOOK_DIR) and rel != HOOK_DIR:
        return ("a hook script is the guard layer itself; edit it deliberately "
                "with the unlock set, never in passing")
    if rel in registered_guards():
        return ("hooks-rules.json registers this file as a guard, so editing it "
                "changes what every host enforces")
    for prefix, why in PROTECTED:
        if rel.startswith(prefix):
            return why
    return None


# --- rule 2: the secret value shapes ---------------------------------------
# Every pattern matches a VALUE, never a name. Naming a secret is normal
# practice and must not fire. Ported from the private vault's
# outbound-write-guard.py, which has carried them since 2026-08-06.
SECRET_PATTERNS = [
    ("a JSON web token", r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ("a Supabase secret key", r"\bsb_secret_[A-Za-z0-9_-]{16,}"),
    ("a Resend API key", r"\bre_[A-Za-z0-9]{4,32}_[A-Za-z0-9]{16,}"),
    ("an OpenAI API key", r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}"),
    ("an Anthropic API key", r"\bsk-ant-[A-Za-z0-9_-]{24,}"),
    ("a GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    ("a Slack token", r"\bxox[baprs]-[A-Za-z0-9-]{12,}"),
    ("a Stripe key", r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{20,}"),
    ("a Telegram bot token", r"\b\d{8,10}:[A-Za-z0-9_-]{33,}"),
    ("a Google refresh token", r"\b1//[A-Za-z0-9_-]{25,}"),
    ("a Postgres connection string carrying a password",
     r"\bpostgres(?:ql)?://[^\s:/@]+:[^\s@'\"]{6,}@"),
    ("a private key block",
     r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    # The long tail no list of vendors can enumerate.
    ("a key assigned to a NAME_KEY style variable",
     r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_"
     r"(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|PWD|DSN|CREDENTIALS|APIKEY)"
     r"\s*[=:]\s*[\"']?([A-Za-z0-9_\-./+]{16,})"),
]

# A value carrying one of these is a worked example, not a credential. Without
# this list the guideline that documents a key shape could not be written.
PLACEHOLDERS = (
    "example", "placeholder", "redacted", "masked", "changeme", "change_me",
    "dummy", "your", "yourkey", "xxxx", "abcdef", "<", ">", "${", "$(",
    "insert_here", "todo", "notreal", "sample", "test_key",
)


def looks_placeholder(value):
    low = value.lower()
    return low.startswith("$") or any(t in low for t in PLACEHOLDERS)


def secret_reason(text):
    for label, pat in SECRET_PATTERNS:
        if over_budget():
            return None
        m = re.search(pat, text)
        if m and not looks_placeholder(m.group(1) if m.groups() else m.group(0)):
            return label
    return None


# --- payload reading --------------------------------------------------------
def strings(node, out, depth=0):
    """Every string in the tool input, whatever shape the host wraps it in.
    Read by walking rather than by naming fields, so a host that renames
    `content` or nests an edit list differently still gets scanned."""
    if depth > 12 or len(out) > 5000:
        return out
    if isinstance(node, dict):
        for v in node.values():
            strings(v, out, depth + 1)
    elif isinstance(node, list):
        for v in node:
            strings(v, out, depth + 1)
    elif isinstance(node, str):
        out.append(node)
    return out


def relative(path, payload):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ""
    if not path:
        return None
    try:
        ap = os.path.abspath(path)
        if root:
            rel = os.path.relpath(ap, os.path.abspath(root))
            if not rel.startswith(".."):
                return rel.replace(os.sep, "/")
    except (ValueError, OSError):
        return None
    return None


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    payload = json.loads(raw)
    tool_input = payload.get("tool_input") or {}

    unlocked = os.environ.get(UNLOCK_ENV) == "1"

    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    rel = relative(path, payload)
    if rel:
        why = protected_reason(rel)
        if why and not unlocked:
            print("BLOCKED write to %s: %s.\nIf this write is the sanctioned one, "
                  "re-run the command with %s=1 set for that one call."
                  % (rel, why, UNLOCK_ENV), file=sys.stderr)
            return 2

    if not unlocked:
        text = "\n".join(strings(tool_input, []))[:MAX_SCAN_CHARS]
        label = secret_reason(text)
        if label:
            print("BLOCKED write to %s: the content carries %s. Secrets live only "
                  "in .env (AGENTS.md hard rule 10); write the variable NAME here "
                  "and the value there. If this is a worked example, make it "
                  "obviously fake (EXAMPLE, your-key-here) or set %s=1 for this "
                  "one call." % (rel or path or "this file", label, UNLOCK_ENV),
                  file=sys.stderr)
            return 2

    if over_budget():
        print("write-guard: budget of %.0fs exceeded; the write was NOT checked"
              % BUDGET_S, file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail CLOSED, loudly. See the docstring.
        print("BLOCKED by write-guard: it failed closed on its own error (%s: %s); "
              "this write was NOT checked. Fix the guard, or set %s=1 for this one "
              "write, or remove the write-guard.py entry from .claude/settings.json."
              % (type(exc).__name__, exc, UNLOCK_ENV), file=sys.stderr)
        sys.exit(2)

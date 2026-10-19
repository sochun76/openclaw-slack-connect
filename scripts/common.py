"""Shared helpers for the openclaw-slack-connect scripts. Never prints token values.

Works on macOS, Linux and Windows (WSL) as long as the `openclaw` CLI runs for the
same OS user as the gateway. Paths are discovered, not hard-coded:
- CLI: PATH, then common install folders (npm global, ~/.local/bin, Homebrew, nvm).
- State dir: $OPENCLAW_STATE_DIR, else ~/.openclaw  (the gateway reads <state>/.env).
- Config: `openclaw config file`, else $OPENCLAW_CONFIG_PATH, else <state>/openclaw.json.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")


def _add_cli_to_path():
    if shutil.which("openclaw"):
        return
    candidates = [os.path.join(HOME, p) for p in (
        ".local/bin", ".npm-global/bin", ".local/node24/bin", ".local/share/pnpm", ".bun/bin", ".volta/bin")]
    candidates += ["/opt/homebrew/bin", "/usr/local/bin"]
    candidates += sorted(glob.glob(os.path.join(HOME, ".nvm/versions/node/*/bin")), reverse=True)
    candidates += sorted(glob.glob(os.path.join(HOME, ".local/node*/bin")), reverse=True)
    for c in candidates:
        if os.path.exists(os.path.join(c, "openclaw")):
            os.environ["PATH"] = c + os.pathsep + os.environ.get("PATH", "")
            return


_add_cli_to_path()

STATE_DIR = os.environ.get("OPENCLAW_STATE_DIR") or os.path.join(HOME, ".openclaw")
ENV_FILE = os.path.join(STATE_DIR, ".env")


def die(msg):
    print("✗ " + msg)
    sys.exit(1)


def run(cmd, timeout=120, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except FileNotFoundError:
        die("openclaw 명령을 찾지 못했다. 게이트웨이와 같은 사용자 계정의 터미널에서 실행하고, `which openclaw`로 확인한다.")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def config_path():
    code, out = run(["openclaw", "config", "file"], timeout=60)
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.endswith(".json") or line.endswith(".json5"):
            return os.path.expanduser(line)
    return os.environ.get("OPENCLAW_CONFIG_PATH") or os.path.join(STATE_DIR, "openclaw.json")


def env_names(account):
    up = re.sub(r"[^A-Za-z0-9]", "_", account).upper()
    return f"SLACK_{up}_BOT_TOKEN", f"SLACK_{up}_APP_TOKEN"


def read_env():
    env = {}
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE, encoding="utf-8"):
            k, sep, v = line.strip().partition("=")
            if sep and k and not k.startswith("#"):
                env[k] = v.strip().strip('"').strip("'")
    return env


def write_env(updates):
    """Replace or append KEY=VALUE lines, keep everything else, chmod 600."""
    lines = open(ENV_FILE, encoding="utf-8").read().splitlines() if os.path.exists(ENV_FILE) else []
    lines = [l for l in lines if l.partition("=")[0] not in updates]
    lines += [f"{k}={v}" for k, v in updates.items()]
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    try:
        os.chmod(ENV_FILE, 0o600)
    except OSError:
        pass


def slack(method, token, params=None, get=False):
    """Call the Slack Web API. Returns (json, scopes:set)."""
    url = f"https://slack.com/api/{method}"
    data = None
    if get and params:
        url += "?" + urllib.parse.urlencode(params)
    elif not get:
        data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": "Bearer " + token})
    resp = urllib.request.urlopen(req, timeout=20)
    scopes = set(filter(None, resp.headers.get("x-oauth-scopes", "").split(",")))
    return json.loads(resp.read()), scopes


def load_config():
    path = config_path()
    try:
        return json.load(open(path, encoding="utf-8"))
    except ValueError:
        die(f"{path} 가 순수 JSON이 아니다(JSON5 주석 등). `openclaw config set`으로 직접 넣거나 주석을 정리한 뒤 다시 실행.")


def save_config_validated(cfg, tag):
    """Write to a temp file, validate it with the OpenClaw CLI, then swap it in (with backup)."""
    path = config_path()
    tmp = path + ".new"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    code, out = run(["openclaw", "config", "validate"], env=dict(os.environ, OPENCLAW_CONFIG_PATH=tmp))
    if code != 0:
        os.remove(tmp)
        die("설정 검사 실패, 아무것도 바꾸지 않았다:\n" + out.strip()[-800:])
    backup = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}-{tag}"
    shutil.copy2(path, backup)
    os.replace(tmp, path)
    return backup

#!/usr/bin/env python3
"""에이전트 확인·생성·모델 선택.

  python3 agent.py list                                   에이전트 목록(작업 폴더, 모델)
  python3 agent.py models                                 고를 수 있는 모델과 실행 방식
  python3 agent.py check                                  Claude Code·Codex 설치/버전 확인
  python3 agent.py create --id tori [--model anthropic/claude-sonnet-5-5] [--workspace 경로]
  python3 agent.py model --agent tori --set anthropic/claude-opus-5-5 [--runtime cli|api]

실행 방식(runtime)
  cli : 이 컴퓨터에 로그인된 Claude Code(구독)로 실행. API 요금 없음, 구독 한도 사용.
  api : OpenClaw에 등록된 API 키로 실행(사용량 과금). 키가 없으면 실행이 실패한다.
"""
import argparse
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import die, load_config, run, save_config_validated  # noqa: E402

# Claude CLI version needed for a model to run through the CLI runtime (observed).
MIN_CLI_FOR = {"claude-opus-5-5": (2, 1, 280)}


def agents():
    code, out = run(["openclaw", "agents", "list", "--json"])
    i = min([x for x in (out.find("["), out.find("{")) if x >= 0] or [0])
    try:
        d = json.loads(out[i:])
    except ValueError:
        die("openclaw agents list --json 을 읽지 못했다:\n" + out[-300:])
    return d if isinstance(d, list) else d.get("agents", [])


def cli_version():
    if not shutil.which("claude"):
        return None
    code, out = run(["claude", "--version"], timeout=30)
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
    return tuple(int(x) for x in m.groups()) if m else None


a = argparse.ArgumentParser()
sub = a.add_subparsers(dest="cmd", required=True)
sub.add_parser("list")
sub.add_parser("models")
sub.add_parser("check")
c = sub.add_parser("create")
c.add_argument("--id", required=True)
c.add_argument("--model")
c.add_argument("--workspace")
m = sub.add_parser("model")
m.add_argument("--agent", required=True)
m.add_argument("--set", required=True)
m.add_argument("--runtime", choices=["cli", "api"], default="cli")
o = a.parse_args()

if o.cmd == "list":
    for x in agents():
        print(f"- {x.get('id')} ({x.get('name') or ''}) 모델={x.get('model')} 작업폴더={x.get('workspace')}")

elif o.cmd == "check":
    v = cli_version()
    print(f"Claude Code: {'.'.join(map(str, v)) if v else '없음'}")
    print(f"Codex: {'있음' if shutil.which('codex') else '없음'}")
    code, out = run(["openclaw", "--version"])
    print("OpenClaw: " + out.strip().splitlines()[-1] if out.strip() else "OpenClaw: ?")

elif o.cmd == "models":
    cfg = load_config()
    runtimes = {k: (v.get("agentRuntime") or {}).get("id") for k, v in
                cfg.get("agents", {}).get("defaults", {}).get("models", {}).items()}
    code, out = run(["openclaw", "models", "list"])
    print("모델 | 실행 방식(설정됨)")
    for line in out.splitlines():
        ref = line.split()[0] if line.strip() else ""
        if "/" in ref and not ref.startswith("claude-cli/"):
            print(f"- {ref} | {runtimes.get(ref) or '-'}")
    print("※ 'claude-cli' = Claude Code 구독으로 실행. '-' = API 키 방식이거나 아직 설정 안 됨.")

elif o.cmd == "create":
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,40}", o.id):
        die("--id 는 영문 소문자로 시작하는 짧은 아이디(예: tori)")
    if any(x.get("id") == o.id for x in agents()):
        die(f"이미 있는 에이전트: {o.id}")
    ws = o.workspace or os.path.join(os.path.dirname(load_config().get("agents", {}).get("defaults", {})
                                                     .get("workspace", os.path.expanduser("~/.openclaw/workspace"))),
                                     f"workspace-{o.id}")
    cmd = ["openclaw", "agents", "add", o.id, "--non-interactive", "--workspace", ws, "--json"]
    if o.model:
        cmd += ["--model", o.model]
    code, out = run(cmd)
    if code != 0:
        die("에이전트 생성 실패:\n" + out[-500:])
    print(f"✓ 에이전트 {o.id} 생성, 작업 폴더 {ws}")
    print("  다음: persona.py 로 페르소나 적용(기본 템플릿과 BOOTSTRAP.md 가 들어 있다)")

elif o.cmd == "model":
    if not any(x.get("id") == o.agent for x in agents()):
        die(f"없는 에이전트: {o.agent}")
    cfg = load_config()
    entry = cfg["agents"]["entries"].setdefault(o.agent, {})
    entry["model"] = o.set
    models = cfg["agents"].setdefault("defaults", {}).setdefault("models", {})
    if o.runtime == "cli":
        v = cli_version()
        if not v:
            die("Claude Code(claude)가 없다. 구독 방식(cli)을 쓰려면 Claude Code를 설치하고 `claude auth login`.")
        need = MIN_CLI_FOR.get(o.set.split("/")[-1])
        if need and v < need:
            die(f"이 모델은 Claude Code {'.'.join(map(str, need))} 이상이 필요하다(현재 {'.'.join(map(str, v))}). `claude update` 후 다시.")
        models.setdefault(o.set, {})["agentRuntime"] = {"id": "claude-cli"}
    backup = save_config_validated(cfg, f"model-{o.agent}")
    print(f"✓ {o.agent} 모델 = {o.set} (실행 방식 {o.runtime}). 백업 {backup}")
    print("  새 대화부터 적용된다. 바로 확인: openclaw agent --agent " + o.agent + " --message '어떤 모델로 동작해?'")

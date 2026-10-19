#!/usr/bin/env python3
"""페르소나 파일 백업·보기·적용. 작업 폴더를 git으로 백업하고 나서 바꾼다.

  python3 persona.py show   --agent tori                   현재 IDENTITY/SOUL/USER/AGENTS/MEMORY 요약
  python3 persona.py backup --agent tori [--msg "설명"]     현재 상태를 git 커밋
  python3 persona.py apply  --agent tori --from <폴더 또는 파일...> [--msg "설명"]

apply 는 표준 파일 이름(IDENTITY.md, SOUL.md, USER.md, AGENTS.md, MEMORY.md, HEARTBEAT.md, TOOLS.md)만 복사한다.
채용설계서처럼 한 문서에 다 들어 있으면, 에이전트(Claude/Codex)가 references/persona-mapping.md 대로
먼저 표준 파일로 나눠 임시 폴더에 쓰고 사람 확인을 받은 뒤 apply 한다.
적용 후: BOOTSTRAP.md(첫 대화 의식)를 지우고, IDENTITY.md 의 이름을 OpenClaw 설정에 동기화하고, 커밋한다.
"""
import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import die, run  # noqa: E402
import json  # noqa: E402

STANDARD = ["IDENTITY.md", "SOUL.md", "USER.md", "AGENTS.md", "MEMORY.md", "HEARTBEAT.md", "TOOLS.md"]


def workspace(agent):
    code, out = run(["openclaw", "agents", "list", "--json"])
    i = min([x for x in (out.find("["), out.find("{")) if x >= 0] or [0])
    d = json.loads(out[i:])
    for x in (d if isinstance(d, list) else d.get("agents", [])):
        if x.get("id") == agent:
            return x.get("workspace")
    die(f"없는 에이전트: {agent}")


def git(ws, *args):
    return subprocess.run(["git", "-C", ws, *args], capture_output=True, text=True)


def commit(ws, msg):
    if git(ws, "rev-parse", "--git-dir").returncode != 0:
        git(ws, "init", "-q")
    git(ws, "add", "-A")
    r = git(ws, "-c", "user.name=openclaw-slack-connect", "-c", "user.email=agent@localhost", "commit", "-q", "-m", msg)
    return "변경 없음" if r.returncode != 0 else git(ws, "log", "--oneline", "-1").stdout.strip()


a = argparse.ArgumentParser()
a.add_argument("cmd", choices=["show", "backup", "apply"])
a.add_argument("--agent", required=True)
a.add_argument("--from", dest="src", nargs="*")
a.add_argument("--msg")
o = a.parse_args()
ws = workspace(o.agent)

if o.cmd == "show":
    for name in STANDARD + ["BOOTSTRAP.md"]:
        p = os.path.join(ws, name)
        if os.path.exists(p):
            text = open(p, encoding="utf-8").read()
            first = next((l for l in text.splitlines() if l.strip() and not l.startswith("#")), "")[:80]
            markers = ("Fill this in", "_(pick something", "You're not a chatbot", "Replace the example below",
                       "Keep workspace conventions here")
            template = any(mk in text for mk in markers)
            print(f"- {name} ({len(text)}자){' [기본 템플릿]' if template else ''}: {first}")
    print(f"작업 폴더: {ws}")

elif o.cmd == "backup":
    print("✓ 백업:", commit(ws, o.msg or "페르소나 변경 전 백업"))

elif o.cmd == "apply":
    if not o.src:
        die("--from 에 폴더나 파일을 준다")
    files = []
    for s in o.src:
        s = os.path.expanduser(s)
        if os.path.isdir(s):
            files += [os.path.join(s, n) for n in STANDARD if os.path.exists(os.path.join(s, n))]
        elif os.path.basename(s) in STANDARD:
            files.append(s)
        else:
            die(f"표준 파일 이름이 아니다: {s} (채용설계서는 먼저 references/persona-mapping.md 대로 나눈다)")
    if not files:
        die("적용할 표준 파일이 없다")
    print("✓ 백업:", commit(ws, "페르소나 적용 전 백업"))
    for f in files:
        shutil.copyfile(f, os.path.join(ws, os.path.basename(f)))
        print(f"  적용: {os.path.basename(f)}")
    boot = os.path.join(ws, "BOOTSTRAP.md")
    if os.path.exists(boot) and any(os.path.basename(f) in ("IDENTITY.md", "SOUL.md") for f in files):
        os.remove(boot)
        print("  BOOTSTRAP.md 삭제(정체성이 정해졌으므로 첫 대화 의식 생략)")
    if any(os.path.basename(f) == "IDENTITY.md" for f in files):
        code, out = run(["openclaw", "agents", "set-identity", "--agent", o.agent, "--from-identity"])
        print("  이름 동기화:", "완료" if code == 0 else out.strip()[-200:])
    os.makedirs(os.path.join(ws, "memory"), exist_ok=True)
    print("✓ 커밋:", commit(ws, o.msg or "페르소나 적용"))
    print("  새 대화부터 적용된다. 슬랙에서는 /new 를 보내 새 대화를 시작하면 확실하다.")

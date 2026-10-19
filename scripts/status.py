#!/usr/bin/env python3
"""어디까지 됐나. 에이전트, 슬랙 계정, 바인딩, 연결 상태, 토큰 유무를 보여 준다(값은 출력 안 함).

  python3 status.py [--account <계정>]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import env_names, load_config, read_env, run  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument("--account")
o = a.parse_args()

code, out = run(["openclaw", "agents", "list"])
print("== 에이전트")
print("\n".join(l for l in out.splitlines() if l.startswith("- ")) or out.strip()[-400:])

cfg = load_config()
accounts = cfg.get("channels", {}).get("slack", {}).get("accounts", {})
env = read_env()
print("\n== 슬랙 계정")
for name, acc in accounts.items():
    b, ap = env_names(name)
    owner = acc.get("allowFrom")
    print(f"- {name} ({acc.get('name', '')}): dm={acc.get('dmPolicy')} group={acc.get('groupPolicy')} "
          f"allowFrom={owner} tokens={'있음' if env.get(b) and env.get(ap) else '없음'}")

print("\n== 바인딩")
for x in cfg.get("bindings", []):
    m = x.get("match", {})
    scope = (x.get("session") or {}).get("dmScope", "기본")
    print(f"- {x.get('agentId')} <- {m.get('channel')} account={m.get('accountId', '(전체)')} dmScope={scope}")

code, out = run(["openclaw", "channels", "status"], timeout=90)
print("\n== 연결 상태")
for l in out.splitlines():
    if l.startswith("- ") and (not o.account or o.account in l or "slack" not in l.lower()):
        print(l[:160])

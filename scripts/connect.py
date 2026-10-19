#!/usr/bin/env python3
"""슬랙 계정을 OpenClaw에 추가하고 에이전트에 연결한다. 설정은 검사 후에만 바꾼다(백업 남김).

  python3 connect.py --account company --agent main --name "우리 회사" --slash tori

처음 연결은 항상 잠긴 상태로 시작한다: DM은 페어링(승인 필요), 채널 응답 꺼짐.
주인 승인 뒤의 공개 범위는 approve_owner.py --preset 으로 정한다.

넣는 기본 규칙(노닥 입주 규칙 + 서버 실측):
  allowBots=mentions, botLoopProtection 5분 8회 → 15분 쉼, replyToMode=all, joinIntro=false,
  mentionPatterns deny(@멘션으로만 깸), 바인딩 dmScope=per-account-channel-peer(사람별 대화 분리)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import die, env_names, load_config, read_env, save_config_validated  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument("--account", required=True, help="계정 이름(영문, 예: company, workshop)")
a.add_argument("--agent", required=True, help="연결할 agentId")
a.add_argument("--name", help="워크스페이스 이름(표시용)")
a.add_argument("--slash", help="슬래시 명령 이름")
o = a.parse_args()

b, ap = env_names(o.account)
env = read_env()
if not env.get(b) or not env.get(ap):
    die(f"열쇠가 없다: {b}, {ap} → save_tokens.py 먼저")

cfg = load_config()
agents = cfg.get("agents", {}).get("entries", {})
if o.agent not in agents:
    die(f"에이전트 '{o.agent}' 가 없다. 있는 것: {', '.join(agents)}")

slack_cfg = cfg.setdefault("channels", {}).setdefault("slack", {})
accounts = slack_cfg.setdefault("accounts", {})
existing = accounts.get(o.account)
acc = dict(existing or {})
acc.update({
    "enabled": True, "mode": "socket",
    "botToken": {"source": "env", "provider": "default", "id": b},
    "appToken": {"source": "env", "provider": "default", "id": ap},
})
if o.name:
    acc["name"] = o.name
if not existing:  # 새 계정은 잠긴 상태로 시작
    acc.update({"dmPolicy": "pairing", "groupPolicy": "disabled"})
for k, v in {"allowBots": "mentions",
             "botLoopProtection": {"enabled": True, "maxEventsPerWindow": 8, "windowSeconds": 300, "cooldownSeconds": 900},
             "replyToMode": "all", "joinIntro": False, "mentionPatterns": {"mode": "deny"}}.items():
    acc.setdefault(k, v)
if o.slash:
    acc["slashCommand"] = {"enabled": True, "name": o.slash.lstrip("/")}
accounts[o.account] = acc

bindings = cfg.setdefault("bindings", [])
mine = [x for x in bindings if x.get("match", {}).get("channel") == "slack"
        and x.get("match", {}).get("accountId") == o.account]
if mine and any(x.get("agentId") != o.agent for x in mine):
    die(f"계정 {o.account} 은 이미 {mine[0].get('agentId')} 에 연결돼 있다. 바꾸려면 사람에게 먼저 확인.")
if not mine:
    bindings.append({"type": "route", "agentId": o.agent,
                     "match": {"channel": "slack", "accountId": o.account},
                     "session": {"dmScope": "per-account-channel-peer"}})

backup = save_config_validated(cfg, f"slack-{o.account}")
print(f"✓ 계정 {o.account} → {o.agent} ({'갱신' if existing else '새로 추가, DM 승인 필요·채널 꺼짐'})")
print(f"  백업: {backup}")
print("  다음: restart_wait.py 로 게이트웨이 재시작(새 열쇠는 재시작해야 읽힌다)")

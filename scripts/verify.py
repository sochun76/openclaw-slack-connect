#!/usr/bin/env python3
"""저장된 열쇠가 진짜인지, 봇 이름이 한글로 반영됐는지, 메시지 이름 권한이 있는지 확인한다.

  python3 verify.py --account company [--expect-name 토리]

출력: 워크스페이스·팀 ID·봇 유저 ID·봇 이름(real_name)·chat:write.customize·Socket Mode 가능 여부
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import die, env_names, read_env, slack  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument("--account", required=True)
a.add_argument("--expect-name")
o = a.parse_args()

b, ap = env_names(o.account)
env = read_env()
if not env.get(b) or not env.get(ap):
    die(f"{b} 또는 {ap} 가 ~/.openclaw/.env 에 없다 → save_tokens.py")

auth, scopes = slack("auth.test", env[b])
if not auth.get("ok"):
    die(f"봇 열쇠 실패: {auth.get('error')}")
user, _ = slack("users.info", env[b], {"user": auth["user_id"]}, get=True)
real = user.get("user", {}).get("real_name")
print(f"✓ 봇 열쇠: {auth['team']} ({auth['team_id']}) 봇 {auth['user_id']} 아이디 {auth['user']} 이름 「{real}」")
ok = True
if o.expect_name and real != o.expect_name:
    ok = False
    print(f"✗ 봇 이름이 「{real}」 이다. 「{o.expect_name}」 이 아니면 App Home > Edit > Display Name 저장 후 다시 설치."
          " 그래도 영문이면 assistant_view 설계도로 앱을 다시 만든다(references/gotchas.md).")
if "chat:write.customize" in scopes:
    print("✓ chat:write.customize 있음 (메시지에 에이전트 이름 표시)")
else:
    print("! chat:write.customize 없음 → OAuth & Permissions 에 추가하고 다시 설치 권장")
conn, _ = slack("apps.connections.open", env[ap])
print("✓ 앱 열쇠: Socket Mode 연결 가능" if conn.get("ok") else f"✗ 앱 열쇠 실패: {conn.get('error')}")
ok = ok and conn.get("ok")
print(f"TEAM_ID={auth['team_id']} BOT_USER_ID={auth['user_id']}")
sys.exit(0 if ok else 1)

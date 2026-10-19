#!/usr/bin/env python3
"""열쇠 두 개를 ~/.openclaw/.env 에 저장한다(권한 600). 값은 화면에 찍지 않는다.

  사람이 터미널에서:   python3 save_tokens.py --account company
                       (입력이 화면에 안 보이는 상태로 xoxb-, xapp- 를 차례로 붙여 넣음)
  Claude가 대신(사용자가 채팅에 붙여 준 경우):
                       printf '%s\\n%s\\n' "$BOT" "$APP" | python3 save_tokens.py --account company --stdin

변수 이름: SLACK_<계정>_BOT_TOKEN / SLACK_<계정>_APP_TOKEN
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import ENV_FILE, die, env_names, write_env  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument("--account", required=True)
a.add_argument("--stdin", action="store_true")
o = a.parse_args()

if o.stdin:
    vals = [l.strip() for l in sys.stdin.read().split() if l.strip()]
else:
    vals = [getpass.getpass("봇 열쇠(xoxb-...) 붙여 넣고 Enter: ").strip(),
            getpass.getpass("앱 열쇠(xapp-...) 붙여 넣고 Enter: ").strip()]
bot = next((v for v in vals if v.startswith("xoxb-")), None)
app = next((v for v in vals if v.startswith("xapp-")), None)
if not bot:
    die("xoxb- 로 시작하는 봇 열쇠가 없다 (OAuth & Permissions > Bot User OAuth Token)")
if not app:
    die("xapp- 로 시작하는 앱 열쇠가 없다 (Basic Information > App-Level Tokens, scope connections:write)")
b, ap = env_names(o.account)
write_env({b: bot, ap: app})
print(f"✓ 저장: {b} (길이 {len(bot)}), {ap} (길이 {len(app)}) → {ENV_FILE}")

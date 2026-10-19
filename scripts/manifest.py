#!/usr/bin/env python3
"""슬랙 앱 설계도(매니페스트) 만들기. 한글 이름이 실제로 반영되는 assistant_view 형식.

  python3 manifest.py --name 토리 --id tori [--slash tori] [--desc "설명"] [--lang ko|en] [--out 파일]

- display_information.name 은 한글 가능. bot_user.display_name 은 영문 소문자만(슬랙 제한).
- agent_view 형식(OpenClaw 문서 기본)으로 만들면 봇 이름이 영문으로 고정된다(2026-10-19 실측).
- chat:write.customize 를 넣어 OpenClaw가 메시지에 에이전트 이름을 붙일 수 있게 한다.
"""
import argparse
import json
import re
import sys

a = argparse.ArgumentParser()
a.add_argument("--name", required=True, help="한글 표시 이름")
a.add_argument("--id", required=True, help="영문 소문자 아이디")
a.add_argument("--slash", help="슬래시 명령(없으면 --id)")
a.add_argument("--desc", help="앱 설명")
a.add_argument("--out", help="저장할 파일(없으면 출력만)")
a.add_argument("--lang", choices=["ko", "en"], default="ko", help="앱 설명·추천 질문 언어")
o = a.parse_args()
if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,79}", o.id):
    sys.exit("--id 는 영문 소문자·숫자·.-_ 만")
slash = (o.slash or o.id).lstrip("/")
EN = o.lang == "en"
desc = o.desc or (f"OpenClaw agent {o.name}" if EN else f"OpenClaw 에이전트 {o.name}")
prompt = "What can you help me with?" if EN else "무엇을 도와줄 수 있어?"
talk = f"Talk to {o.name}" if EN else f"{o.name}에게 말 걸기"
hint = "[what you want to say]" if EN else "[하고 싶은 말]"
m = {
    "display_information": {"name": o.name, "description": desc},
    "features": {
        "bot_user": {"display_name": o.id, "always_online": True},
        "app_home": {"home_tab_enabled": True, "messages_tab_enabled": True, "messages_tab_read_only_enabled": False},
        "assistant_view": {"assistant_description": desc,
                           "suggested_prompts": [{"title": prompt, "message": prompt}]},
        "slash_commands": [{"command": "/" + slash, "description": talk,
                            "usage_hint": hint, "should_escape": False}],
    },
    "oauth_config": {"scopes": {"bot": [
        "app_mentions:read", "assistant:write", "channels:history", "channels:read", "chat:write",
        "chat:write.customize", "commands", "emoji:read", "files:read", "files:write", "groups:history",
        "groups:read", "im:history", "im:read", "im:write", "mpim:history", "mpim:read", "mpim:write",
        "pins:read", "pins:write", "reactions:read", "reactions:write", "usergroups:read", "users:read"]}},
    "settings": {"socket_mode_enabled": True, "event_subscriptions": {"bot_events": [
        "app_home_opened", "app_mention", "assistant_thread_context_changed", "assistant_thread_started",
        "channel_rename", "member_joined_channel", "member_left_channel", "message.channels", "message.groups",
        "message.im", "message.mpim", "pin_added", "pin_removed", "reaction_added", "reaction_removed"]}},
}
one_line = json.dumps(m, ensure_ascii=False, separators=(",", ":"))
if o.out:
    with open(o.out, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
print(one_line)

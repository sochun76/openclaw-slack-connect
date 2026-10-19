#!/usr/bin/env python3
"""주인 승인과 공개 범위 설정. 사람이 봇에게 DM을 보낸 뒤 돌린다.

  python3 approve_owner.py --account company --preset owner
  python3 approve_owner.py --account company --preset staff

1) openclaw pairing list 에서 대기 요청을 찾는다. 딱 1건일 때만 승인(0건·2건 이상이면 멈춤).
   --expect-user U... 를 주면 그 ID일 때만 승인.
2) 프리셋 적용
   owner : DM 주인만, 채널은 주인이 @멘션할 때만 (외부 슬랙·기본값)
   staff : DM 누구나, 채널은 누구든 @멘션하면 (사내 슬랙 직원 개방. 에이전트 차단 장치가 있을 때만)
3) commands.ownerAllowFrom 에 slack:<주인 ID> 추가. 승인 코드는 출력하지 않는다.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import die, load_config, run, save_config_validated  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument("--account", required=True)
a.add_argument("--preset", choices=["owner", "staff"], default="owner")
a.add_argument("--expect-user")
a.add_argument("--owner", help="이미 아는 주인 ID(승인 없이 프리셋만 적용)")
o = a.parse_args()

owner = o.owner
if not owner:
    code, out = run(["openclaw", "pairing", "list", "slack", "--account", o.account, "--json"])
    idx = [i for i in (out.find("{"), out.find("[")) if i >= 0]
    reqs = json.loads(out[min(idx):]).get("requests", []) if idx else []
    if len(reqs) != 1:
        die(f"대기 요청 {len(reqs)}건 — 1건일 때만 승인한다: "
            + ", ".join(f"{r.get('meta', {}).get('name')}({r.get('id')})" for r in reqs))
    r = reqs[0]
    if o.expect_user and r["id"] != o.expect_user:
        die(f"요청자 {r['id']} 가 기대한 {o.expect_user} 와 다르다")
    code, out = run(["openclaw", "pairing", "approve", "slack", r["code"], "--account", o.account])
    if code != 0:
        die("승인 실패: " + out.strip()[-300:])
    owner = r["id"]
    print(f"✓ 승인: {r.get('meta', {}).get('name')} {owner}")

cfg = load_config()
acc = cfg["channels"]["slack"]["accounts"].get(o.account) or die(f"계정 {o.account} 없음")
if o.preset == "owner":
    acc.update({"allowFrom": [owner], "dmPolicy": "allowlist", "groupPolicy": "open",
                "channels": {"*": {"requireMention": True, "users": [owner]}}})
else:
    acc.update({"allowFrom": ["*"], "dmPolicy": "open", "groupPolicy": "open",
                "channels": {"*": {"requireMention": True}}})
oa = cfg.setdefault("commands", {}).setdefault("ownerAllowFrom", [])
if f"slack:{owner}" not in oa:
    oa.append(f"slack:{owner}")
backup = save_config_validated(cfg, f"slack-{o.account}-{o.preset}")
print(f"✓ 프리셋 {o.preset} 적용 (주인 {owner}). 백업 {backup}")
print("  다음: restart_wait.py (설정이 'accepted' 만 되고 반영 안 되는 경우가 있어 재시작으로 확실히)")
print(f"OWNER_ID={owner}")

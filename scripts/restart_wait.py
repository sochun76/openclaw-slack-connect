#!/usr/bin/env python3
"""게이트웨이를 재시작하고, 지정한 슬랙 계정이 connected 될 때까지 기다린다(기본 최대 12분).

  python3 restart_wait.py [<계정>] [--max 720]

`openclaw gateway restart`는 launchd(macOS)·systemd(Linux)·schtasks(Windows)를 알아서 다룬다.
재시작 완료는 게이트웨이 프로세스 번호(pid)가 바뀌고 RPC가 응답하는 것으로 판단한다.
재시작 동안 모든 채널이 멈춘다. 몇 초에서 몇 분까지 걸린다(미전송 메시지 정리 때문).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from common import run  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument("account", nargs="?")
a.add_argument("--max", type=int, default=720)
o = a.parse_args()


def gateway():
    code, out = run(["openclaw", "gateway", "status", "--json"], timeout=60)
    try:
        d = json.loads(out[out.index("{"):])
    except ValueError:
        return None, False
    return (d.get("service") or {}).get("runtime", {}).get("pid"), bool((d.get("rpc") or {}).get("ok"))


def connected(account):
    code, out = run(["openclaw", "channels", "status"], timeout=90)
    return any(f"slack {account}".lower() in l.lower() and "connected" in l and "disconnected" not in l
               for l in out.splitlines())


old_pid, _ = gateway()
start = time.time()
print(f"재시작 요청 {time.strftime('%H:%M:%S')} (이전 pid {old_pid})")
run(["openclaw", "gateway", "restart"], timeout=o.max)
while True:
    pid, ok = gateway()
    restarted = ok and (old_pid is None or (pid is not None and pid != old_pid) or time.time() - start > 20)
    if restarted and (not o.account or connected(o.account)):
        break
    if time.time() - start > o.max:
        print(f"✗ {o.max}초 안에 끝나지 않음. `openclaw gateway status`와 `openclaw logs`로 확인.")
        break
    time.sleep(10)
print(f"걸린 시간 {int(time.time() - start)}초 (pid {old_pid} → {gateway()[0]})")
code, out = run(["openclaw", "channels", "status", "--probe"], timeout=120)
print("\n".join(l[:150] for l in out.splitlines() if l.startswith("- ")))

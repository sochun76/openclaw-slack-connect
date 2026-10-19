---
name: openclaw-slack-connect
description: 이미 만들어 둔 OpenClaw 에이전트를 슬랙 워크스페이스에 연결하는 스킬(어사이드 같은 브라우저 자동화 없이). "내 봇을 슬랙에 연결해줘", "에이전트를 회사 슬랙에 넣어줘", "다른 워크스페이스에도 등록해줘", "슬랙 봇 이름이 영어로 나와", "슬랙 열쇠 바꿔줘", "openclaw slack connect" 같은 요청에서 사용. 슬랙 앱 설계도 생성, 열쇠 저장·검증, 한글 봇 이름 확인, 계정·바인딩·보안 규칙, 게이트웨이 재시작, 주인 승인, 공개 범위까지 안내한다. 새 에이전트 만들기, 페르소나 작성, OpenClaw 설치는 범위가 아니다.
---

# openclaw-slack-connect — 만들어진 OpenClaw 에이전트를 슬랙에 연결

OpenClaw 에이전트(페르소나, 기억이 이미 있는 봇)를 슬랙 워크스페이스에 붙인다. **브라우저 화면 클릭은 사람이, 그 컴퓨터 안의 일은 에이전트(Claude Code·Codex)가** 맡는다. 맥, 리눅스, 윈도우(WSL)에서 쓸 수 있다. 단, 이 스킬을 실행하는 터미널은 OpenClaw 게이트웨이와 **같은 컴퓨터, 같은 사용자 계정**이어야 한다.

스크립트: `<스킬>/scripts/` (`<스킬>` = 이 파일이 있는 폴더). 모든 스크립트는 열쇠 값을 출력하지 않는다. 필요한 것: Python 3, 인터넷, `openclaw` CLI.

## 진행 원칙

- 시작할 때 `python3 <스킬>/scripts/status.py`로 에이전트, 슬랙 계정, 바인딩, 연결 상태를 본다. 이미 된 단계는 건너뛴다.
- **한 번에 하나만 묻는다.** 사용자가 비개발자일 수 있다. "accountId", "binding" 대신 "연결 이름", "누가 말을 걸 수 있는지"처럼 말한다.
- 사람 차례(슬랙 웹 화면, 열쇠 복사)에서는 멈추고 할 일을 번호로 준다. 사용자가 화면 캡처를 보내면 그 화면 기준으로 다음 버튼을 짚는다.
- 게이트웨이 재시작 전에는 "몇 초~몇 분 동안 모든 메신저가 멈춘다"고 먼저 알린다.
- 에이전트의 작업 폴더로 `cd` 하지 않는다. 전체 경로를 쓴다(그 폴더를 기준으로 동작하는 보안 훅이 있을 수 있다).

## 0. 정할 것 (한 칸씩)

| 항목 | 물어볼 말 | 예 |
|---|---|---|
| 에이전트 | "어느 에이전트를 연결할까요?" + `openclaw agents list` 결과 | main, tori |
| 워크스페이스 | "어느 슬랙에 넣을까요? 사내 전용인가요, 외부 사람도 있는 곳인가요?" | 회사 슬랙, 교육 슬랙 |
| 한글 이름 / 영문 아이디 | "슬랙에 보일 이름은요? 영문 아이디도 하나(소문자)" | 토리 / tori |
| 연결 이름 | 묻지 말고 제안: 워크스페이스 약칭. 같은 곳에 봇이 둘이면 `약칭-아이디` | company, workshop, company-tori |
| 공개 범위 | "누가 말을 걸 수 있게 할까요? 나만 / 우리 직원 모두" | owner / staff |

**보안 판단 (반드시 사용자에게 설명)**
- 같은 에이전트는 페르소나, 기억(MEMORY.md, USER.md), 파일·명령 권한이 **모든 워크스페이스에 그대로 따라간다.** 외부 사람이 있는 슬랙에는 회사 정보를 아는 에이전트 대신 별도 에이전트를 만들어 넣기를 권한다.
- **staff(여러 사람에게 개방)** 는 그 에이전트가 할 수 있는 일을 다른 사람도 시킬 수 있다는 뜻이다. 에이전트가 셸 명령이나 회사 파일에 접근할 수 있다면, 먼저 실제로 막히는 장치(예: Claude Code PreToolUse 훅, 샌드박스)를 두고 시험한 뒤에 연다. `references/gotchas.md` 7번 참고.
- MEMORY.md와 USER.md는 모든 새 대화에 읽힌다. 여러 사람에게 연 에이전트의 기억 파일에는 민감한 내용을 두지 않는다.

## 1. 슬랙 앱 만들기 (사람 차례)

```bash
python3 <스킬>/scripts/manifest.py --name <한글 이름> --id <영문 아이디>
```
출력된 한 줄 JSON을 사용자에게 준다. 사람이 할 일:
1. https://api.slack.com/apps/new → **From a manifest** (기본 선택된 "AI agent" 템플릿이 아님) → Continue
2. JSON 칸의 예시("Demo App")를 `Ctrl+A`로 지우고 붙여 넣기 → 워크스페이스 선택 → Next → Create
3. 왼쪽 **Install App** → Install → 허용. "관리자 승인 요청"이 뜨면 그 슬랙은 앱 설치가 막혀 있다(관리자에게 요청).
4. 노란 띠 "The agentic app experience is changing… **Go to Agents**"가 보이면 → 초록 **Update Now**
5. **App Home** → Your App's Presence in Slack → **Edit** → Display Name을 한글 이름으로 → Save (Default username은 영문 그대로)
6. **Basic Information** → 아래 **App-Level Tokens** → Generate Token and Scopes → 이름 `socket`, Scope `connections:write` → Generate → `xapp-…` 복사
7. **OAuth & Permissions** → Bot User OAuth Token `xoxb-…` 복사

누르지 말 것: Revoke Tokens(열쇠 폐기), Token rotation·PKCE Opt In, Redirect URLs, 사용자 토큰 범위.

## 2. 열쇠 저장과 검증

열쇠는 채팅에 붙이지 말고 터미널에서 저장하게 안내한다(입력이 화면에 안 보인다):
```bash
python3 <스킬>/scripts/save_tokens.py --account <연결 이름>
```
사용자가 이미 채팅에 붙였다면: `printf '%s\n%s\n' '<xoxb>' '<xapp>' | python3 <스킬>/scripts/save_tokens.py --account <연결 이름> --stdin` 로 저장하고, 연결이 끝난 뒤 열쇠를 교체하자고 알린다.

```bash
python3 <스킬>/scripts/verify.py --account <연결 이름> --expect-name <한글 이름>
```
- 봇 이름이 영문이면 연결하지 말고 `references/gotchas.md` 1번대로 처리한다.
- `chat:write.customize`가 없으면 OAuth & Permissions에 추가하고 다시 설치하게 한다.

## 3. 연결과 재시작

```bash
python3 <스킬>/scripts/connect.py --account <연결 이름> --agent <agentId> --name "<워크스페이스 이름>" --slash <아이디>
python3 <스킬>/scripts/restart_wait.py <연결 이름>     # 오래 걸릴 수 있어 백그라운드 실행 권장
```
새 계정은 잠긴 상태로 붙는다(DM은 승인 필요, 채널 응답 꺼짐). 새 열쇠는 재시작해야 읽힌다. 이미 다른 에이전트에 연결된 계정이면 connect.py가 멈춘다(사용자 확인 후 처리).

## 4. 주인 승인과 공개 범위

사람에게: "슬랙에서 <한글 이름>에게 '안녕'을 보내 주세요. 'access not configured'가 오면 '보냈어'라고 알려 주세요." (승인 코드는 붙일 필요 없다)
```bash
python3 <스킬>/scripts/approve_owner.py --account <연결 이름> --preset owner    # 또는 staff
python3 <스킬>/scripts/restart_wait.py <연결 이름>
```
- 대기 요청이 1건일 때만 승인한다. 출력된 이름이 사용자 본인인지 확인한다.
- 같은 사람도 워크스페이스마다 슬랙 아이디가 다르다. 워크스페이스마다 한 번씩 승인한다.
- owner: DM은 주인만, 채널은 주인이 @멘션할 때만. staff: DM 누구나, 채널은 누구든 @멘션하면.
- 재시작 뒤 사람에게 다시 인사해 보게 하고, 답장 옆 이름이 한글인지 확인받는다.

## 5. 정기 보고를 슬랙으로 (선택)

```bash
openclaw cron add --name <id>-daily --agent <agentId> --cron "0 8 * * *" --tz Asia/Seoul --exact \
  --session isolated --announce --channel slack --account <연결 이름> --to user:<주인 ID> --message "..."
```
시간대는 `--tz`로 지정한다(서버 시계가 UTC인 경우가 많다).

## 끝나고 보고할 것

연결 이름 → 에이전트, 워크스페이스·팀 ID, 봇 이름(한글 반영 여부), 공개 범위, 연결 상태, 재시작에 걸린 시간, 열쇠가 채팅에 노출됐는지(교체 필요). 해 보지 않은 것은 해 보지 않았다고 쓴다.

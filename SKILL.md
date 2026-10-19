---
name: openclaw-slack-connect
description: OpenClaw 에이전트를 슬랙에서 쓰기까지 한 번에 안내하는 스킬. 진행 언어(한국어/영어) 선택, 에이전트 선택 또는 새로 만들기, 모델(Opus·Sonnet 등)과 실행 방식(Claude Code 구독/API 키) 선택, 페르소나 파일·채용설계서 업로드와 적용, 슬랙 앱 생성·열쇠 검증·한글 봇 이름 확인·연결·주인 승인·공개 범위까지. "내 봇을 슬랙에 연결해줘", "에이전트 만들어서 슬랙에 넣어줘", "이 페르소나 파일 적용해줘", "에이전트 모델 바꿔줘", "슬랙 봇 이름이 영어로 나와", "connect my OpenClaw agent to Slack" 같은 요청에서 사용. OpenClaw 설치 자체는 범위가 아니다.
---

# openclaw-slack-connect — OpenClaw 에이전트를 슬랙에서 쓰기까지

**브라우저 화면 클릭은 사람이, 그 컴퓨터 안의 일은 에이전트(Claude Code·Codex)가** 한다. 맥, 리눅스, 윈도우(WSL)에서 쓸 수 있다. 이 스킬을 실행하는 터미널은 OpenClaw 게이트웨이와 **같은 컴퓨터, 같은 사용자 계정**이어야 한다.

스크립트: `<스킬>/scripts/` (`<스킬>` = 이 파일이 있는 폴더). 열쇠 값은 어떤 스크립트도 출력하지 않는다. 필요한 것: Python 3, 인터넷, `openclaw` CLI.

**`<스킬>/references/local.md`가 있으면 가장 먼저 읽는다.** 그 컴퓨터만의 사정(보안 장치, 경로, 이미 연결된 채널)이 적혀 있다.

## 진행 원칙

- 시작할 때 `python3 <스킬>/scripts/status.py`와 `python3 <스킬>/scripts/agent.py list`로 현재 상태를 본다. 이미 된 단계는 건너뛰고, 사용자가 원하는 단계만 해도 된다(예: 페르소나만, 모델만, 슬랙만).
- **한 번에 하나만 묻는다.** 사용자가 비개발자일 수 있다. "accountId", "binding", "runtime" 대신 "연결 이름", "누가 말을 걸 수 있는지", "어떤 방식으로 돌릴지"처럼 말한다. 선택지는 추천을 먼저 두고 이유를 한 줄 붙인다.
- 사람 차례(슬랙 웹 화면, 열쇠 복사)에서는 멈추고 할 일을 번호로 준다. 사용자가 화면 캡처를 보내면 그 화면 기준으로 다음 버튼을 짚는다.
- 설정을 바꾸기 전에는 백업한다(스크립트가 자동으로 한다). 게이트웨이 재시작 전에는 "몇 초~몇 분 동안 모든 메신저가 멈춘다"고 먼저 알린다.
- 에이전트의 작업 폴더로 `cd` 하지 않는다. 전체 경로를 쓴다(그 폴더를 기준으로 동작하는 보안 훅이 있을 수 있다).

## 0. 진행 언어

가장 먼저 묻는다: "안내를 한국어로 할까요, 영어로 할까요? (Korean or English?)"
- 고른 언어로 끝까지 대화한다. 스크립트 출력이 다른 언어여도 사용자에게는 고른 언어로 옮겨 말한다.
- 슬랙 앱 설명(`manifest.py --lang`)과 페르소나 파일도 기본으로 그 언어로 쓴다. 봇 표시 이름은 따로 묻는다(한글 이름도 된다).

## 1. 에이전트 정하기

`agent.py list`를 보여 주고 묻는다: "어느 에이전트를 쓸까요? 새로 만들 수도 있어요."
- 새로 만들 때: 영문 아이디(소문자)를 정하고 `python3 <스킬>/scripts/agent.py create --id <아이디>`. 새 에이전트는 기본 템플릿과 BOOTSTRAP.md(첫 대화에서 이름을 묻는 의식)를 가지고 태어난다. 3단계에서 페르소나를 넣으면 BOOTSTRAP.md는 지워진다.
- 외부 사람이 있는 슬랙에 넣을 예정이면, 회사 정보를 아는 기존 에이전트 대신 **새 에이전트를 만들기를 권한다.** 같은 에이전트는 페르소나, 기억, 파일·명령 권한이 모든 워크스페이스에 따라간다.

## 2. 모델과 실행 방식

`python3 <스킬>/scripts/agent.py check`, `python3 <스킬>/scripts/agent.py models`로 고를 수 있는 것을 보여 주고 묻는다.
- **실행 방식:** "이 컴퓨터에 로그인된 Claude Code 구독으로 돌릴까요(추천, 추가 요금 없음, 구독 한도 사용), API 키로 돌릴까요(사용량 과금)?"
  - Claude Code가 없으면 cli를 고를 수 없다. 설치와 `claude auth login`을 안내하거나 api로 간다. api는 OpenClaw에 키가 등록돼 있어야 한다(`openclaw models status`). Codex(ChatGPT 구독)로 돌리려면 OpenClaw 문서의 Codex 런타임 안내를 따른다(이 스킬은 Claude 경로만 자동화한다).
- **모델:** 성능과 한도를 설명하고 고르게 한다. 예: Opus(가장 똑똑함, 한도를 빨리 씀) / Sonnet(빠르고 균형) / 그 밖에 목록에 있는 것.
- 적용: `python3 <스킬>/scripts/agent.py model --agent <아이디> --set <provider/model> --runtime cli`
  - Claude Code 버전이 그 모델에 너무 낮으면 스크립트가 멈춘다 → `claude update`.
- 확인: `openclaw agent --agent <아이디> --message "어떤 모델로 동작해? 한 줄로"` 응답을 보여 준다.

## 3. 페르소나 적용

먼저 `python3 <스킬>/scripts/persona.py show --agent <아이디>`로 현재 상태를 보여 주고 묻는다: "페르소나 자료가 있으세요? 파일을 올려 주셔도 되고, 없으면 몇 가지 질문으로 같이 만들어요."
- 자료를 받는 법: 대화에 파일을 첨부하거나 내용을 붙여 넣게 하거나, 그 컴퓨터의 파일 경로를 알려 달라고 한다.
- 자료 종류별 처리는 `references/persona-mapping.md`를 따른다.
  - 표준 파일(IDENTITY.md, SOUL.md 등): 읽고 요약해 보여 준 뒤 적용.
  - 채용설계서나 자유 문서: 표대로 나눠 임시 폴더에 쓰고, 파일별 요약을 보여 확인받은 뒤 적용. 미작성·모순·예제 문구는 사용자에게 묻는다.
  - 자료 없음: 인터뷰(미션 → 성격 → 경계 → 말투 → 이름 → 관계)로 만든다.
- 적용: `python3 <스킬>/scripts/persona.py apply --agent <아이디> --from <폴더 또는 파일들>` (적용 전 git 백업, BOOTSTRAP.md 정리, 이름 동기화, 커밋까지 한다)
- 확인: `openclaw agent --agent <아이디> --message "자기소개 두 줄로 해 줘"` 응답이 페르소나와 맞는지 보여 준다.

## 4. 슬랙 연결 정하기 (한 칸씩)

| 항목 | 물어볼 말 | 예 |
|---|---|---|
| 워크스페이스 | "어느 슬랙에 넣을까요? 사내 전용인가요, 외부 사람도 있는 곳인가요?" | 회사 슬랙, 교육 슬랙 |
| 표시 이름 / 영문 아이디 | "슬랙에 보일 이름은요? 영문 아이디도 하나(소문자)" | 토리 / tori |
| 연결 이름 | 묻지 말고 제안: 워크스페이스 약칭. 같은 곳에 봇이 둘이면 `약칭-아이디` | company, workshop |
| 공개 범위 | "누가 말을 걸 수 있게 할까요? 나만 / 우리 직원 모두" | owner / staff |

**보안 판단 (반드시 사용자에게 설명)**
- **staff(여러 사람에게 개방)** 는 그 에이전트가 할 수 있는 일을 다른 사람도 시킬 수 있다는 뜻이다. 에이전트가 셸 명령이나 회사 파일에 접근할 수 있다면, 먼저 실제로 막히는 장치(예: Claude Code PreToolUse 훅, 샌드박스)를 두고 시험한 뒤에 연다. `references/gotchas.md` 7번.
- MEMORY.md와 USER.md는 모든 새 대화에 읽힌다. 여러 사람에게 연 에이전트의 기억 파일에는 민감한 내용을 두지 않는다.

## 5. 슬랙 앱 만들기 (사람 차례)

```bash
python3 <스킬>/scripts/manifest.py --name <표시 이름> --id <영문 아이디> --lang <ko|en>
```
출력된 한 줄 JSON을 사용자에게 준다. 사람이 할 일:
1. https://api.slack.com/apps/new → **From a manifest** (기본 선택된 "AI agent" 템플릿이 아님) → Continue
2. JSON 칸의 예시("Demo App")를 `Ctrl+A`로 지우고 붙여 넣기 → 워크스페이스 선택 → Next → Create
3. 왼쪽 **Install App** → Install → 허용. "관리자 승인 요청"이 뜨면 그 슬랙은 앱 설치가 막혀 있다(관리자에게 요청).
4. 노란 띠 "The agentic app experience is changing… **Go to Agents**"가 보이면 → 초록 **Update Now**
5. **App Home** → Your App's Presence in Slack → **Edit** → Display Name을 표시 이름으로 → Save (Default username은 영문 그대로)
6. **Basic Information** → 아래 **App-Level Tokens** → Generate Token and Scopes → 이름 `socket`, Scope `connections:write` → Generate → `xapp-…` 복사
7. **OAuth & Permissions** → Bot User OAuth Token `xoxb-…` 복사
8. (선택) **Basic Information → Display Information → App icon**에 정사각 그림(512px 이상) 업로드

누르지 말 것: Revoke Tokens(열쇠 폐기), Token rotation·PKCE Opt In, Redirect URLs, 사용자 토큰 범위.

## 6. 열쇠 저장과 검증

열쇠는 채팅에 붙이지 말고 터미널에서 저장하게 안내한다(입력이 화면에 안 보인다):
```bash
python3 <스킬>/scripts/save_tokens.py --account <연결 이름>
```
사용자가 이미 채팅에 붙였다면: `printf '%s\n%s\n' '<xoxb>' '<xapp>' | python3 <스킬>/scripts/save_tokens.py --account <연결 이름> --stdin` 로 저장하고, 연결이 끝난 뒤 열쇠를 교체하자고 알린다.

```bash
python3 <스킬>/scripts/verify.py --account <연결 이름> --expect-name <표시 이름>
```
- 봇 이름이 표시 이름과 다르면(영문 고정) 연결하지 말고 `references/gotchas.md` 1번대로 처리한다.
- `chat:write.customize`가 없으면 OAuth & Permissions에 추가하고 다시 설치하게 한다.

## 7. 연결과 재시작

```bash
python3 <스킬>/scripts/connect.py --account <연결 이름> --agent <아이디> --name "<워크스페이스 이름>" --slash <아이디>
python3 <스킬>/scripts/restart_wait.py <연결 이름>     # 오래 걸릴 수 있어 백그라운드 실행 권장
```
새 계정은 잠긴 상태로 붙는다(DM은 승인 필요, 채널 응답 꺼짐). 새 열쇠는 재시작해야 읽힌다. 이미 다른 에이전트에 연결된 계정이면 connect.py가 멈춘다(사용자 확인 후 처리).

## 8. 주인 승인과 공개 범위

사람에게: "슬랙에서 <표시 이름>에게 '안녕'을 보내 주세요. 'access not configured'가 오면 '보냈어'라고 알려 주세요." (승인 코드는 붙일 필요 없다)
```bash
python3 <스킬>/scripts/approve_owner.py --account <연결 이름> --preset owner    # 또는 staff
python3 <스킬>/scripts/restart_wait.py <연결 이름>
```
- 대기 요청이 1건일 때만 승인한다. 출력된 이름이 사용자 본인인지 확인한다.
- 같은 사람도 워크스페이스마다 슬랙 아이디가 다르다. 워크스페이스마다 한 번씩 승인한다.
- owner: DM은 주인만, 채널은 주인이 @멘션할 때만. staff: DM 누구나, 채널은 누구든 @멘션하면.
- 재시작 뒤 사람에게 다시 인사해 보게 하고, 답장 이름과 말투(페르소나)가 맞는지 확인받는다.

## 9. 정기 보고를 슬랙으로 (선택)

```bash
openclaw cron add --name <id>-daily --agent <아이디> --cron "0 8 * * *" --tz Asia/Seoul --exact \
  --session isolated --announce --channel slack --account <연결 이름> --to user:<주인 ID> --message "..."
```
시간대는 `--tz`로 지정한다(서버 시계가 UTC인 경우가 많다).

## 끝나고 보고할 것

에이전트와 모델(실행 방식), 적용한 페르소나 파일, 연결 이름 → 에이전트, 워크스페이스·팀 ID, 봇 이름(표시 이름 반영 여부), 공개 범위, 연결 상태, 재시작에 걸린 시간, 열쇠가 채팅에 노출됐는지(교체 필요). 해 보지 않은 것은 해 보지 않았다고 쓴다.

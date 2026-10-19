# 실측 함정 (OpenClaw 2026.9.8, Slack 2026-10 기준)

1. **봇 이름이 영어로 나온다.** OpenClaw 문서의 기본 설계도(`agent_view`)로 만든 앱은 App Home에서 한글 Display Name을 저장하고 다시 설치해도 봇 이름(`users.info` real_name)이 영문 그대로였다. 왼쪽 목록, 대화창 제목, 메시지 작성자가 영문으로 보인다.
   - 해결: `manifest.py`의 `assistant_view` 설계도로 앱을 **다시 만들고** → 설치 → Go to Agents → Update Now → App Home에서 한글 이름 저장. 실측에서 real_name이 한글로 바뀌었다(아이디는 기존 앱과 겹치면 `이름2`로 잡힘).
   - 앱을 다시 만들 수 없으면: `chat:write.customize` 권한 추가 + 다시 설치 + 게이트웨이 재시작. 메시지 옆 이름은 에이전트 이름(한글)이 되지만, 왼쪽 목록·대화창 제목은 영문으로 남는다.
2. **새 열쇠는 재시작해야 읽힌다.** 게이트웨이는 `<상태 폴더>/.env`를 시작할 때만 읽는다.
3. **설정 변경이 "accepted"만 되고 반영되지 않을 때가 있다.** `openclaw logs`에 `config hot reload applied`가 없으면 `restart_wait.py`로 재시작한다.
4. **재시작 시간이 들쭉날쭉하다.** 몇 초에서 5분 이상까지. 다른 채널(예: 텔레그램)의 미전송 메시지 정리가 늦으면 서비스 관리자의 종료 제한 시간까지 기다린다. 그동안 모든 채널이 멈춘다.
5. **기본 설정은 모든 DM을 한 대화로 합친다.** 여러 사람이 쓰는 계정은 바인딩에 `session.dmScope: per-account-channel-peer`를 둔다(connect.py가 넣음). 전역 `session.dmScope`를 바꾸면 다른 에이전트·채널도 바뀌니 주의.
6. **MEMORY.md와 USER.md는 모든 새 대화에 읽힌다(다른 사람 DM 포함).** 여러 사람에게 연 에이전트의 기억 파일에는 민감한 내용을 두지 않는다.
7. **Claude CLI(`claude-cli`) 런타임에서는 OpenClaw의 `tools.deny`, `tools.fs.workspaceOnly`가 Claude의 내장 도구(셸, 파일 읽기·쓰기)에 강제되지 않았다(2026.9.8 실측).** exec 정책을 deny/allowlist로 바꾸면 읽기·쓰기까지 모두 막힌다. 여러 사람에게 열기 전에 Claude Code의 PreToolUse 훅이나 샌드박스로 실제로 막고, 실제 세션에서 시험한다. 다른 런타임(API 직접 사용 등)이면 OpenClaw 도구 정책을 먼저 시험해 본다.
8. **열쇠를 채팅이나 화면 캡처에 노출하면** 대화 기록에 남는다. 연결 후 앱 열쇠는 Basic Information에서 새로 만들고, 봇 열쇠는 OAuth & Permissions에서 Revoke 후 다시 설치해 받은 뒤 `save_tokens.py`로 다시 저장한다.
9. **슬랙 화면 함정:** "Create new app" 창의 기본 선택은 "AI agent" 템플릿이다. 반드시 **From a manifest**. 설계도 칸의 "Demo App" 예시는 전부 지운다. `xoxb`와 `xapp`를 바꿔 넣거나 한 줄에 이어 붙이는 실수가 잦다(save_tokens.py가 앞머리로 구분한다). 앱 열쇠는 자동으로 생기지 않으니 App-Level Tokens에서 직접 만든다.
10. **외부 워크스페이스에서 다른 봇과 협업할 때** 채널의 `users` 허용 목록을 주인만으로 두면 다른 봇의 호출도 무시된다. 협업 실습 때만 잠깐 넓히고, 그 에이전트가 할 수 있는 일(셸, 파일, 외부 발송)을 먼저 좁혀 둔다.
11. **에이전트가 서버 전체 플러그인을 설치할 수 있다.** OpenClaw의 `plugins` 도구(MCP)로 에이전트가 플러그인을 설치·켜기 할 수 있었다(실측: 실습 에이전트가 공식 에어테이블 플러그인을 설치). 플러그인은 모든 에이전트에 적용되니, PreToolUse 훅 등으로 `install/enable/disable/uninstall`을 막고 사람이 설치한다. 같은 이유로 "웹 금지" 에이전트는 Claude 내장 `WebFetch`뿐 아니라 OpenClaw 쪽 `web_fetch`, `browser` 도구도 막아야 한다.

# openclaw-slack-connect

이미 만들어 둔 **OpenClaw 에이전트를 슬랙에 연결**하는 Claude Code / Codex 스킬입니다.

## 빠른 시작

OpenClaw가 돌아가는 컴퓨터에서 한 번 설치합니다.

```bash
# Claude Code
git clone https://github.com/sochun76/openclaw-slack-connect.git ~/.claude/skills/openclaw-slack-connect
# Codex
git clone https://github.com/sochun76/openclaw-slack-connect.git ~/.codex/skills/openclaw-slack-connect
```

그다음 Claude Code(또는 Codex)에게 **"내 봇을 슬랙에 연결해줘"** 라고 말하면 한 단계씩 안내합니다. 에이전트가 서버나 다른 컴퓨터에 있어도 되고, 어사이드는 필요 없습니다.

## 왜 만들었나

에이전트를 설치하고 페르소나까지 만들었는데, 그 에이전트를 슬랙에 넣는 단계에서 막히는 경우가 많습니다. 특히 에이전트가 노트북이 아니라 **서버에 있을 때** 그렇습니다. 이 스킬은 그 과정을 "사람은 슬랙 웹 화면만, 나머지는 에이전트가" 하도록 나눠서 한 단계씩 안내합니다. 어사이드 같은 브라우저 자동화 도구가 필요 없습니다.

## 하는 일

1. 한글 봇 이름이 실제로 반영되는 슬랙 앱 설계도(매니페스트) 생성
2. 열쇠(xoxb, xapp)를 화면에 보이지 않게 저장하고 검증 (봇 이름이 한글로 반영됐는지까지 확인)
3. OpenClaw에 슬랙 계정과 연결 규칙 추가. 처음엔 잠긴 상태로 시작하고, 사람별 대화 분리와 봇끼리 폭주 방지 규칙을 넣음
4. 게이트웨이 재시작과 연결 확인 (macOS, Linux, Windows WSL)
5. 주인 승인과 공개 범위 설정 (나만 / 직원 모두)

실제로 겪은 함정 10가지를 [`references/gotchas.md`](references/gotchas.md)에 정리했습니다. 예: 슬랙 봇 이름이 영어로 나오는 문제, 설정이 반영되지 않는 문제, 여러 사람에게 열 때의 보안.

## 설치

OpenClaw 게이트웨이가 돌아가는 **같은 컴퓨터, 같은 사용자 계정**에 설치합니다.

**Claude Code**
```bash
git clone https://github.com/sochun76/openclaw-slack-connect.git ~/.claude/skills/openclaw-slack-connect
```

**Codex**
```bash
git clone https://github.com/sochun76/openclaw-slack-connect.git ~/.codex/skills/openclaw-slack-connect
```

필요한 것: Python 3, 인터넷 연결, `openclaw` CLI, 슬랙 워크스페이스에 앱을 설치할 권한.

## 사용

Claude Code(또는 Codex)에게 말로 요청하면 됩니다.

- "내 봇을 회사 슬랙에 연결해줘"
- "tori 에이전트를 교육 슬랙에도 등록해줘"
- "슬랙 봇 이름이 영어로 나와"

Claude Code에서는 `/openclaw-slack-connect`로 직접 부를 수도 있습니다.

## 주의

- 같은 에이전트는 페르소나, 기억, 파일·명령 권한이 모든 워크스페이스에 따라갑니다. 외부 사람이 있는 슬랙에는 별도 에이전트를 쓰세요.
- 여러 사람에게 열기 전에, 그 에이전트가 셸 명령이나 회사 파일을 다룰 수 있는지 확인하고 실제로 막는 장치를 먼저 두세요(gotchas 7번).
- 열쇠를 채팅에 붙여 넣었다면 연결 후 새 열쇠로 바꾸세요.
- macOS와 Windows(WSL)에서는 아직 실측하지 않았습니다. Linux(systemd) 서버에서 시험했습니다. 다른 환경에서 문제가 있으면 이슈로 알려 주세요.

## 만든 배경

노닥컴퍼니 「CEO 에이전트 AX워크숍」(2026-10) 실습 중에, 서버에 이미 있는 에이전트를 슬랙에 붙이는 과정을 정리한 것입니다. 워크숍의 `slack-bot-aside` 스킬(노트북+어사이드 기준)과 OpenClaw 공식 문서의 슬랙 설정을 참고했습니다.

## License

MIT

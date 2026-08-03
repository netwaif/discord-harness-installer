---
name: configure-harness
description: Use when the user wants to install the full Discord multi-agent harness (orchestrator bot + chat-claude bot + codex/gemini bridges + usage dashboard) into a work folder, or wants to remove or inspect an existing installation. Triggers on "디스코드 하네스 설치해줘", "멀티에이전트 하네스 설치", "/configure-harness", "하네스 제거해줘", "하네스 점검해줘". 결정적 엔진(harnessctl.py)이 preflight→fetch(검증 조합 핀 체크아웃)→plugins→pair→install(오버레이+위임)→verify를 멱등 수행하고 doctor가 상시 점검한다 — 매뉴얼 16장을 대체한다. 수동은 디스코드 포탈 단계뿐(스킬이 단계별 안내).
---

# configure-harness — 디스코드 멀티에이전트 하네스 통합 설치

작업 폴더 하나를 디스코드로 운영되는 멀티에이전트 하네스(오케스트레이터 봇 + 수다
클로드 봇 + 코덱스/제미나이 브리지 + 사용량 대시보드)로 만든다. 모든 파일 조작은
결정적 엔진 `generator/harnessctl.py`가 수행한다 — 직접 plist·.env·CLAUDE.md를
손으로 쓰지 말 것. 아래 명령에서 `<이 스킬 폴더>`는 이 SKILL.md와 같은 폴더
(`skills/configure-harness`)를 가리킨다.

## 원칙 (반드시 지킬 것)

- **비파괴**: SESSION.md는 절대 만들거나 고치지 않는다. 작업 폴더 CLAUDE.md는
  엔진이 마커 블록(`<!-- discord-multiagent:start/end -->`)만 추가·제거한다.
- **토큰·웹훅 URL은 채팅으로 받지 않는다** — `pbpaste > .bot-token-<역할> &&
  chmod 600 .bot-token-<역할>` 파일 수령만. 스킬은 토큰 값을 화면에 다시
  출력하지 않는다.
- **엔진 출력은 그대로 보여준다.** 실패하면 그 단계에서 멈추고 엔진이 안내한
  다음 행동·수동 폴백을 전달한다(재량으로 대신 고치지 않는다).
- **AskUserQuestion이 없는 환경(코덱스 등)에서는 같은 질문을 채팅으로 물어
  답을 받는다.** 묻지 않고 기본값으로 질주하지 말 것(2026-08-02 코덱스 실측
  편차).

## 설치 절차 (9단계)

### 1. preflight

```
python3 <이 스킬 폴더>/generator/harnessctl.py preflight
```

FAIL 항목이 있으면 각 항목의 설치 방법(엔진 출력에 그대로 포함됨: `xcode-select
--install` / `brew install tmux` / `brew install node` / Claude Code 설치 /
`npm i -g @openai/codex` / discord 플러그인 설치)을 안내하고 여기서 중단한다.
WARN(예: `agy` 없음)은 진행 가능 — 제미나이 봇만 빠진다는 점을 알린다.

### 2. 설치 계획 질문 (AskUserQuestion 한 번에)

- **설치 루트** (기본 `~/discord-harness` — 이 폴더가 하네스의 작업 폴더가 된다)
- **봇 4개 표시 이름** (기본: 오케스트레이터·클로드·코덱스·제미나이 — 디스코드
  개발자 포탈에서 앱 이름으로 그대로 쓴다)
- **대시보드 설치 여부** (기본 예)
- **부팅 자동 기동 여부** (기본 예)

AskUserQuestion 도구가 없는 환경(예: codex)에서는 이 4개를 **채팅으로 질문해
답을 받는다.** 묻지 않고 기본값을 스스로 확정해 진행하지 말 것.

### 3. 디스코드 포탈 수동 단계 (순서대로 안내, 사용자가 끝냈다고 할 때까지 대기)

먼저 설치 루트 폴더를 만든다: `mkdir -p <설치 루트>` (이후 4번 토큰 파일 저장은
이 폴더 안에서 한다).

1. 디스코드 서버 1개 + 채널 2개(작업용·수다용) 생성. 설정 → 고급 → 개발자 모드
   켠 뒤 두 채널 각각 우클릭 → **채널 ID 복사**, 내 프로필 우클릭 →
   **사용자 ID 복사**(채팅으로 받는다 — ID는 비밀 아님).
2. https://discord.com/developers/applications 에서 봇 앱 4개 생성(2단계에서
   정한 이름 그대로). 각 앱 **Bot** 탭에서 토큰 발급 + **MESSAGE CONTENT
   INTENT** 켜기 → Save.
3. 각 앱 **OAuth2 → URL Generator**: scope `bot` 체크, Bot Permissions에서
   View Channels / Send Messages / Read Message History / Embed Links /
   Attach Files / Create Public Threads / Send Messages in Threads 체크 →
   생성된 URL로 초대. 오케스트레이터 봇은 작업 채널에만, 나머지 세 봇(클로드·
   코덱스·제미나이)은 작업+수다 채널 둘 다에 초대한다.
4. 토큰 4개는 각각 복사 직후 설치 루트가 될 폴더에서 파일로 저장한다(채팅에
   붙여넣지 않는다):
   ```
   pbpaste > .bot-token-orch    && chmod 600 .bot-token-orch
   pbpaste > .bot-token-claude  && chmod 600 .bot-token-claude
   pbpaste > .bot-token-codex   && chmod 600 .bot-token-codex
   pbpaste > .bot-token-gemini  && chmod 600 .bot-token-gemini
   ```
5. (2단계에서 대시보드 예로 답했으면) 대시보드용 채널에 웹훅 URL을 생성한
   뒤 같은 폴더에 저장: `pbpaste > .webhook-url`.

### 4. fetch

```
python3 <이 스킬 폴더>/generator/harnessctl.py fetch
```

정본 3레포(discord-multiagent · codex-discord · usage-coach)를 검증 조합 핀
(`generator/pins.json`)으로 clone/체크아웃한다. 최신 버전을 원하면
`--latest`(비검증 조합 — 사용자가 명시적으로 원할 때만).

### 5. plugins

```
python3 <이 스킬 폴더>/generator/harnessctl.py plugins
```

코덱스 호스트에서 실행 중이면 `--host codex`를 붙인다. 실패한 항목은 엔진이
출력하는 수동 폴백(`/plugin marketplace add …` 을 대상 호스트 대화에서 직접
실행)을 안내하고, 사용자가 마치면 재실행한다(멱등).

### 6. 멀티에이전트 시스템 설치 + 디스코드 층

먼저 multi-agent-starter 플러그인의 `configure-multiagent` 스킬을 설치 루트
(2단계에서 정한 폴더)에 대해 flavor `claude`로 실행해 오케스트레이션 뼈대를
얹는다. 완료되면 디스코드 운영 레이어를 오버레이한다:

```
python3 <이 스킬 폴더>/generator/harnessctl.py install --work-dir <설치 루트> --phase overlay
```

### 7. pair

```
python3 <이 스킬 폴더>/generator/harnessctl.py pair \
  --work-dir <설치 루트> \
  --work-channel-id <작업 채널 ID> \
  --chat-channel-id <수다 채널 ID> \
  --approver-user-id <내 사용자 ID>
```

대시보드를 설치하기로 했으면 `--webhook-url-file <설치 루트>/.webhook-url`을
추가한다. 이미 페어링돼 있으면 엔진이 거부한다(덮으려면 `--force`). 완료 후
엔진 출력으로 `.bot-token-*` 파일 4개가 삭제됐는지 확인한다.

### 8. install

```
python3 <이 스킬 폴더>/generator/harnessctl.py install --work-dir <설치 루트> --phase delegate
```

2단계 답에 따라 `--dashboard`(대시보드 예였으면) · `--autostart`(부팅 자동
기동 예였으면)를 붙인다. 코덱스/제미나이 브리지 환경 조립 + 위임 설치
스크립트(`codex-discord`·`usage-coach`·`install-autostart.sh`) 호출까지
이 단계에서 끝난다.

### 9. verify + 마무리

verify 전에 수다 클로드를 지금 기동해야 한다. 8단계에서 자동 기동을 켠
경우(`--autostart`) 오케스트레이터는 `install-autostart.sh`가 즉시 띄우지만,
수다 클로드는 plist 파일만 생성되고 지금 당장 뜨지는 않는다(재부팅 후에는
자동 기동). 다음 명령으로 지금 기동한다:

```
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.discord-harness.chat-claude.plist
```

자동 기동을 끈 경우에는 오케스트레이터·수다 클로드 둘 다 수동으로 기동한다:

```
tmux new-session -d -s orchestrator '/bin/zsh -lc "cd <설치 루트>; export DISCORD_STATE_DIR=<설치 루트>/.discord-state; exec scripts/bot-up.sh -n orchestrator --remote-control orchestrator --channels plugin:discord@claude-plugins-official"'
tmux new-session -d -s chat-claude '/bin/zsh -lc "cd <설치 루트>/chat; export DISCORD_STATE_DIR=<설치 루트>/chat/.discord-state; exec <설치 루트>/scripts/bot-up.sh -n chat-claude --remote-control chat-claude --channels plugin:discord@claude-plugins-official"'
```

```
python3 <이 스킬 폴더>/generator/harnessctl.py verify --work-dir <설치 루트>
```

결과를 그대로 보고한다. 이어서 마무리 안내:

- **실제 응답 확인(자동화 불가)** — 디스코드 작업 채널에서 오케스트레이터
  봇에게, 수다 채널에서 클로드 봇에게 직접 인사해 응답이 오는지 확인해
  달라고 요청한다.
- **재시작 리추얼** — 컨텍스트가 차면 채널에서 "세션 마감하고 재시작해" →
  `scripts/bot-restart.sh <세션>` → "이어서하자".
- **폴더 봇 추가(선택)** — 다른 작업 폴더도 디스코드 채널 봇으로 만들고
  싶으면 folder-bot 스킬("이 폴더를 디스코드 봇으로 만들어줘")을 안내한다.
- **상시 점검**: `python3 <이 스킬 폴더>/generator/harnessctl.py doctor`
- **제거**: `python3 <이 스킬 폴더>/generator/harnessctl.py remove`

## 제거

"하네스 제거해줘" 요청을 받으면:

```
python3 <이 스킬 폴더>/generator/harnessctl.py remove --work-dir <설치 루트>
```

엔진이 tmux 세션·plist·위임 설치분(브리지·대시보드)·오버레이 파일(해시 일치
분만)·CLAUDE.md 마커 블록·`.mcp.json` 추가 항목·소스 저장소를 제거한다.
**보존되는 것**을 그대로 안내한다: `.env` · `.discord-state` · `chat/`(사용자
수정분) · `tasks/` · `SESSION.md` · `~/.config/usage-coach/`. 사용자가 수정한
오버레이 파일은 해시 불일치로 자동 보존되며 엔진이 `[WARN]`으로 표시한다.
starter·folder-bot 플러그인과 그 산출물은 remove 범위 밖이다 — 멀티에이전트
구성 제거는 multi-agent-starter 스킬로, 폴더 봇 제거는 folder-bot 스킬의
`botctl.py remove`로 각각 안내만 한다.

## 점검

"하네스 점검해줘" 요청을 받으면:

```
python3 <이 스킬 폴더>/generator/harnessctl.py doctor
```

읽기 전용 — 3레포 fetch 기록·검증 조합 핀 일치 여부, 플러그인(multi-agent-
starter·folder-bot) 설치 버전과 호환 최소 버전, 위임 계약 파일(브리지·대시보드
·오토스타트 스크립트) 존재·실행권한, 오버레이 manifest 스키마 버전, 페어링
(`.env`) 여부, plist 2종, tmux 세션 2종(orchestrator·chat-claude) 생존을
대조 보고한다. 각 `[WARN]`/`[FAIL]` 항목은 엔진 메시지를 그대로 옮기고 다음
행동을 덧붙여 해설한다(예: "fetch 기록 없음 → harnessctl.py fetch 필요").

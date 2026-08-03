# discord 하네스 통합 설치기 (v1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 매뉴얼 v2.2 16장을 대체하는 `configure-harness` 스킬 + 결정적 엔진 `harnessctl.py`를 플러그인 하나로 만들고, 상류 선행 작업 3건(usage-coach install/uninstall, 브리지 uninstall, 하네스 오버레이 manifest)을 각 정본 레포에 신설한다.

**Architecture:** A안 위임 오케스트레이터 — 엔진은 다른 곳에 정본이 없는 접합부(fetch·pair·오버레이·수다 클로드 plist·브리지 .env 조립)만 직접 담당하고, 실제 설치 동작은 각 레포의 정본 스크립트(브리지 install.sh, 하네스 install-autostart.sh, usage-coach install.sh)에 위임한다. clone은 `~/.local/share/discord-harness/repos/` 소스 저장소로 두고, 작업 폴더에는 manifest 기반 오버레이만 얹는다(창작 금지). 상태 정본은 `~/.config/discord-harness/state.json`, 검증 조합은 플러그인 동봉 `pins.json`.

**Tech Stack:** Python 3 표준 라이브러리만(harnessctl.py 단일 파일), bash(상류 스크립트), git, tmux, launchd(macOS), pytest(HOME 격리 블랙박스 테스트).

## Global Constraints

- 스펙 정본: `docs/superpowers/specs/2026-08-04-harness-installer-design.md` (이 레포)
- 전례 정본: folder-bot 플랜 `~/ai-folder/dev/discord-multiagent/docs/superpowers/plans/2026-08-01-folder-bot-plugin.md` — 엔진 골격·테스트 패턴·SKILL 문구를 승계
- harnessctl 서브커맨드는 정확히 8개: `preflight` `fetch` `plugins` `pair` `install` `verify` `doctor` `remove`
- 경로는 전부 `HOME` 환경변수 기준(`home()` 단일 진입점) — 테스트가 HOME을 tmpdir로 돌린다
- 상태 파일: `~/.config/discord-harness/state.json` / 소스 저장소: `~/.local/share/discord-harness/repos/{discord-multiagent,codex-discord,usage-coach}`
- 테스트 계약 2개(스펙 정본): clone URL은 env `HARNESS_REPO_BASE`로 오버라이드(테스트는 tmp에 `git init`한 가짜 3레포), 위임 스크립트·기동은 `--dry-run`으로 명령 문자열만 검증
- CLAUDE.md 마커(하네스 정본과 동일, 변경 금지): `<!-- discord-multiagent:start -->` / `<!-- discord-multiagent:end -->`
- plist 라벨: 오케 `com.discord-multiagent.orchestrator`(상류 정본, install-autostart.sh 소유) / 수다 클로드 `com.discord-harness.chat-claude`(엔진 소유, 신설) / 브리지 `com.codex-discord.{daemon,tui,gemini}`(상류 소유) / 대시보드 `com.usage-coach.dashboard`(상류 신설)
- tmux 세션명: `orchestrator`(상류 고정), `chat-claude`(엔진 신설), `codex-live`(브리지 TUI, 상류 소유)
- **엔진 소스에 `bootout` 문자열 금지**(2026-07-31 실측: 부팅 시 tmux 서버를 띄운 job은 프로세스 그룹째 킬 위험) — 엔진은 plist 파일 생성/삭제 + `tmux kill-session`만. 상류 스크립트가 node 직속 job에 bootout을 쓰는 것은 상류 책임(folder-bot codex 데몬 전례)이라 허용
- 하네스 `.env` 변수 7종(정본 `.env.example`과 동일, 변경 금지): `WORK_CHANNEL_ID` `CHAT_CHANNEL_ID` `APPROVER_USER_ID` `ORCH_BOT_TOKEN` `CLAUDE_BOT_TOKEN` `CODEX_BOT_TOKEN` `GEMINI_BOT_TOKEN`
- 토큰 파일명(작업 폴더): `.bot-token-orch` `.bot-token-claude` `.bot-token-codex` `.bot-token-gemini` — pair 성공 즉시 삭제, 비밀은 어떤 경로로도 채팅·stdout에 올리지 않는다. `.env`·상태 `.env`는 0600
- 연결 판정 문자열(정본과 동일 기준): 클로드 계열 = MCP 로그 `Successfully connected` / `Connection failed` (로그 경로 `$HOME/Library/Caches/claude-cli-nodejs/<작업폴더 경로의 /·. → - 치환>/mcp-logs-plugin-discord-discord/*.jsonl`, bot-up.sh 60행과 동일 규칙) / 브리지 계열 = `logs/daemon*.log`의 `로그인:` 줄 (src/index.mjs 244행)
- 멱등: 모든 서브커맨드는 실패 후 재실행이 안전. 기존 설치 감지 시 덮어쓰기 거부, `--force`로만(folder-bot pair 전례)
- 비파괴: SESSION.md 생성·수정 금지. 작업 폴더 CLAUDE.md는 마커 블록 append/제거만
- 커밋 메시지 끝에 항상:
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` + `Claude-Session: https://claude.ai/code/session_01QtecpEbVojWNYvhjtNwU7f`
- 상류 레포 커밋은 각 레포에 로컬 커밋만(푸시는 Task 15 릴리즈 게이트에서 사용자 결정)

**플랜에서 확정하는 설계 결정 2건**(스펙이 플랜으로 위임한 것 + 스펙 공백 1건):
1. 오버레이 manifest 경로 = 하네스 레포 `install/overlay-manifest.json`(스펙 예시안 그대로 채택).
2. **수다 클로드 봇의 기동 주체 = 엔진 직접**(스펙 공백 — verify가 "클로드 계열 2봇" 판정을 요구하지만 기동 정본이 없음. 매뉴얼 6장은 "AI 지침 붙여넣기"였으므로 정본 부재 = 접합부 = A안에서 엔진 담당). 작업 폴더 하위 `chat/` 전용 폴더 + 전용 `chat/.discord-state`(현행 프로덕션의 전역 `~/.claude/channels/discord/` 의존을 제거하는 개선 — 토큰 덮어쓰기 사고 원천 차단, 매뉴얼 817행이 경고하던 고장 모드) + plist `com.discord-harness.chat-claude`. 수다 채널 페어링은 프로덕션 실측과 동일하게 `requireMention: true`, 작업 채널(오케)은 folder-bot 전례대로 `requireMention: false`.

## File Structure

```
discord-harness-installer/                           # 이 레포
├── .claude-plugin/marketplace.json                  # harness-installer 1개만 등재
├── .gitignore  LICENSE  README.md
├── plugins/harness-installer/
│   ├── .claude-plugin/plugin.json
│   └── skills/configure-harness/
│       ├── SKILL.md                                 # 9단계 오케스트레이션 + 포탈 안내
│       └── generator/
│           ├── harnessctl.py                        # 결정적 엔진 (단일 파일, stdlib만)
│           └── pins.json                            # 검증 조합 핀
├── tests/test_harnessctl.py                         # HOME 격리 블랙박스 CLI 테스트
└── docs/superpowers/{specs,plans}/

~/VSCodeWorkspace/usage-coach/scripts/{install.sh,uninstall.sh}      # Task 2 신설
~/ai-folder/dev/codex-discord/scripts/uninstall.sh                   # Task 3 신설
~/ai-folder/dev/discord-multiagent/install/{overlay-manifest.json,chat-CLAUDE.md}  # Task 4 신설
```

---

### Task 1: 플러그인 스캐폴드 + pins.json

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `plugins/harness-installer/.claude-plugin/plugin.json`
- Create: `plugins/harness-installer/skills/configure-harness/generator/pins.json`
- Create: `.gitignore`(`__pycache__/`, `.pytest_cache/`), `LICENSE`(MIT, Copyright (c) 2026 netwaif), `README.md`(제목+한 줄 소개만, 본문은 Task 14)

**Interfaces:**
- Produces: 마켓플레이스 name `discord-harness-installer`, 플러그인 name `harness-installer` version `0.1.0`, source `./plugins/harness-installer` — SKILL 설치 명령과 Task 15 E2E가 소비. pins.json 스키마(schema_version 1)는 Task 6 fetch·Task 12 doctor가 소비

- [ ] **Step 1: 디렉토리·메타 파일 생성**

marketplace.json:

```json
{
  "name": "discord-harness-installer",
  "description": "디스코드 멀티에이전트 하네스 통합 설치기 — 매뉴얼 16장이 스킬 하나가 됐습니다",
  "owner": { "name": "netwaif", "email": "netwaif@users.noreply.github.com" },
  "plugins": [
    {
      "name": "harness-installer",
      "description": "\"디스코드 하네스 설치해줘\" — 하네스·수다 브리지·대시보드 설치 전 과정을 한 스킬로. 결정적 엔진(harnessctl)이 정본 3레포를 clone(검증 조합 핀)하고 오버레이·페어링·위임 설치·연결 판정까지. 수동은 디스코드 포탈 단계뿐(스킬이 단계별 안내).",
      "version": "0.1.0",
      "source": "./plugins/harness-installer",
      "author": { "name": "netwaif" }
    }
  ]
}
```

plugin.json:

```json
{
  "name": "harness-installer",
  "version": "0.1.0",
  "description": "디스코드 멀티에이전트 하네스 통합 설치기. harnessctl 엔진이 preflight→fetch(핀 체크아웃)→plugins→pair→install(오버레이+위임)→verify를 멱등 수행하고, doctor가 버전 호환·위임 계약을 상시 점검한다. 정본은 각 레포(discord-multiagent·codex-discord·usage-coach), 엔진은 접합부만.",
  "author": { "name": "netwaif" }
}
```

pins.json (실태그는 Task 15 릴리즈 게이트에서 확정 — 그 전까지는 pre 태그, 테스트 fixture가 이 파일을 읽어 같은 태그를 만들므로 자동 테스트는 값에 무관하게 성립):

```json
{
  "schema_version": 1,
  "repos": {
    "discord-multiagent": "v0.0.0-pre",
    "codex-discord": "v0.0.0-pre",
    "usage-coach": "v0.0.0-pre"
  },
  "plugins": {
    "multi-agent-starter": "3.5.0",
    "folder-bot": "0.1.0"
  }
}
```

- [ ] **Step 2: JSON 유효성 확인**

Run (레포 루트): `python3 -c "import json;[json.load(open(p)) for p in ['.claude-plugin/marketplace.json','plugins/harness-installer/.claude-plugin/plugin.json','plugins/harness-installer/skills/configure-harness/generator/pins.json']];print('OK')"`
Expected: `OK`

- [ ] **Step 3: 커밋**

```bash
git add -A && git commit -m "chore: harness-installer 플러그인 스캐폴드 + pins.json 스키마"
```

---

### Task 2: 상류(usage-coach) — scripts/install.sh + uninstall.sh 신설

**Files:**
- Create: `~/VSCodeWorkspace/usage-coach/scripts/install.sh` (0755)
- Create: `~/VSCodeWorkspace/usage-coach/scripts/uninstall.sh` (0755)
- Test: `~/VSCodeWorkspace/usage-coach/tests/test_install_scripts.py`

**Interfaces:**
- Consumes: `discord_dash.py`(레포 기존 파일), `~/.config/usage-coach/discord.json`의 `webhook_url`(discord_dash.py 기존 계약)
- Produces: **위임 계약**(Task 10 install·Task 12 doctor·Task 13 remove가 소비) — `scripts/install.sh`(무인자, env `DRY_RUN=1`이면 launchctl 생략하고 plist 파일만 생성, 실패 시 exit 1) / `scripts/uninstall.sh`(무인자, 대응 제거) / plist 라벨 `com.usage-coach.dashboard`, `StartInterval` 300

- [ ] **Step 1: 실패하는 테스트 작성** (`tests/test_install_scripts.py`)

```python
import json, os, plistlib, subprocess
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "scripts"

def run(script, home):
    env = dict(os.environ, HOME=str(home), DRY_RUN="1")
    return subprocess.run(["bash", str(SCRIPTS / script)],
                          capture_output=True, text=True, env=env)

def _prep(home):
    cfg = home / ".config/usage-coach"; cfg.mkdir(parents=True)
    (cfg / "discord.json").write_text(json.dumps({"webhook_url": "https://example.invalid/hook"}))
    (home / "Library/LaunchAgents").mkdir(parents=True)

def test_install_writes_plist(tmp_path):
    _prep(tmp_path)
    r = run("install.sh", tmp_path)
    assert r.returncode == 0, r.stderr
    p = tmp_path / "Library/LaunchAgents/com.usage-coach.dashboard.plist"
    data = plistlib.loads(p.read_bytes())
    assert data["Label"] == "com.usage-coach.dashboard"
    assert data["StartInterval"] == 300
    assert data["ProgramArguments"][1].endswith("discord_dash.py")

def test_install_fails_without_webhook_config(tmp_path):
    (tmp_path / "Library/LaunchAgents").mkdir(parents=True)
    r = run("install.sh", tmp_path)
    assert r.returncode == 1
    assert "webhook" in r.stderr.lower() or "webhook" in r.stdout.lower()

def test_uninstall_removes_plist_and_keeps_config(tmp_path):
    _prep(tmp_path)
    run("install.sh", tmp_path)
    r = run("uninstall.sh", tmp_path)
    assert r.returncode == 0, r.stderr
    assert not (tmp_path / "Library/LaunchAgents/com.usage-coach.dashboard.plist").exists()
    assert (tmp_path / ".config/usage-coach/discord.json").exists()
```

- [ ] **Step 2: 실패 확인**

Run: `cd ~/VSCodeWorkspace/usage-coach && python3 -m pytest tests/test_install_scripts.py -v`
Expected: FAIL (scripts/install.sh 없음)

- [ ] **Step 3: 스크립트 구현**

`scripts/install.sh`:

```bash
#!/usr/bin/env bash
# usage-coach 대시보드 LaunchAgent 설치 — discord_dash.py 5분 간격 실행
# DRY_RUN=1 이면 launchctl 을 건너뛰고 plist 파일만 만든다(테스트 계약).
set -euo pipefail
fail() { echo "오류: $*" >&2; exit 1; }

DIR="$(cd "$(dirname "$0")/.." && pwd)"
[[ "$(uname)" == "Darwin" ]] || fail "macOS 전용입니다 (launchd 사용)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || true)}"
[[ -n "$PYTHON_BIN" ]] || fail "python3 를 찾을 수 없음"
[[ -f "$HOME/.config/usage-coach/discord.json" || -n "${DISCORD_WEBHOOK_URL:-}" ]] \
  || fail "webhook_url 미설정 — ~/.config/usage-coach/discord.json 에 {\"webhook_url\": \"...\"} 를 먼저 만드세요"

LABEL="com.usage-coach.dashboard"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$PYTHON_BIN</string>
    <string>$DIR/discord_dash.py</string>
  </array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
</dict></plist>
EOF

if [[ "${DRY_RUN:-0}" != "1" ]]; then
  UID_N=$(id -u)
  launchctl bootout "gui/$UID_N/$LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$UID_N" "$PLIST"
fi
echo "설치됨: $PLIST (5분 간격)"
```

`scripts/uninstall.sh` (python 직속 job이라 bootout 안전 — folder-bot codex 데몬 전례):

```bash
#!/usr/bin/env bash
# usage-coach 대시보드 LaunchAgent 제거 — install.sh 의 대응 제거 경로
set -euo pipefail
LABEL="com.usage-coach.dashboard"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
if [[ "${DRY_RUN:-0}" != "1" ]]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
fi
rm -f "$PLIST"
echo "제거됨: $PLIST (설정 ~/.config/usage-coach/ 은 보존)"
```

`chmod 755 scripts/install.sh scripts/uninstall.sh`

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd ~/VSCodeWorkspace/usage-coach && python3 -m pytest tests/test_install_scripts.py -v && bash -n scripts/install.sh scripts/uninstall.sh`
Expected: 3 PASS + 무출력(문법 OK)

- [ ] **Step 5: usage-coach 레포에 커밋**

```bash
cd ~/VSCodeWorkspace/usage-coach && git add scripts/ tests/test_install_scripts.py && git commit -m "feat: LaunchAgent 설치/제거 스크립트 신설 (com.usage-coach.dashboard, 5분 간격) — 통합 설치기 위임 계약"
```

---

### Task 3: 상류(codex-discord) — scripts/uninstall.sh 신설

**Files:**
- Create: `~/ai-folder/dev/codex-discord/scripts/uninstall.sh` (0755)
- Test: `~/ai-folder/dev/codex-discord/test/uninstall.test.sh` (기존 테스트가 없으면 이 파일이 첫 bash 테스트)

**Interfaces:**
- Consumes: `scripts/install.sh`가 만드는 plist 3종 `com.codex-discord.{daemon,tui,gemini}`
- Produces: **위임 계약**(Task 12 doctor·Task 13 remove가 소비) — `scripts/uninstall.sh`(무인자, `DRY_RUN=1`이면 launchctl·tmux 생략하고 plist 파일 삭제만). 데몬·gemini는 node 직속 job이라 bootout 사용(안전), **tui는 tmux 세션을 띄우는 job이므로 bootout 금지** — `tmux kill-session -t codex-live` + plist 삭제만

- [ ] **Step 1: 실패하는 테스트 작성** (`test/uninstall.test.sh`)

```bash
#!/usr/bin/env bash
# uninstall.sh 오프라인 테스트 — DRY_RUN 경로만 (launchctl/tmux 무접촉)
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/Library/LaunchAgents"
for L in com.codex-discord.daemon com.codex-discord.tui com.codex-discord.gemini; do
  echo plist > "$TMP/Library/LaunchAgents/$L.plist"
done
HOME="$TMP" DRY_RUN=1 bash "$DIR/scripts/uninstall.sh"
for L in com.codex-discord.daemon com.codex-discord.tui com.codex-discord.gemini; do
  [[ ! -f "$TMP/Library/LaunchAgents/$L.plist" ]] || { echo "FAIL: $L.plist 남음"; exit 1; }
done
# tui 는 bootout 금지 — 스크립트 소스에서 tui 라벨이 bootout 대상에 없는지 정적 확인
! grep -E 'bootout.*tui' "$DIR/scripts/uninstall.sh" || { echo "FAIL: tui 에 bootout 사용"; exit 1; }
echo "uninstall.test OK"
```

- [ ] **Step 2: 실패 확인**

Run: `bash ~/ai-folder/dev/codex-discord/test/uninstall.test.sh`
Expected: 실패 (scripts/uninstall.sh 없음)

- [ ] **Step 3: 구현** (`scripts/uninstall.sh`)

```bash
#!/usr/bin/env bash
# codex-discord 브리지 제거 — install.sh 의 대응 제거 경로.
# 데몬·gemini 는 node 직속 job → bootout 안전. tui 는 tmux 세션을 띄우는 job →
# bootout 금지(프로세스 그룹째 킬 위험, 2026-07-31 실측), 세션 종료 + plist 삭제만.
set -euo pipefail
UID_N=$(id -u)

if [[ "${DRY_RUN:-0}" != "1" ]]; then
  launchctl bootout "gui/$UID_N/com.codex-discord.daemon" 2>/dev/null || true
  launchctl bootout "gui/$UID_N/com.codex-discord.gemini" 2>/dev/null || true
  tmux kill-session -t codex-live 2>/dev/null || true
fi
rm -f "$HOME/Library/LaunchAgents/com.codex-discord.daemon.plist" \
      "$HOME/Library/LaunchAgents/com.codex-discord.tui.plist" \
      "$HOME/Library/LaunchAgents/com.codex-discord.gemini.plist"
echo "제거됨: LaunchAgent 3종 (.env*·logs/·data*/ 는 보존)"
```

`chmod 755 scripts/uninstall.sh`

- [ ] **Step 4: 통과 확인**

Run: `bash ~/ai-folder/dev/codex-discord/test/uninstall.test.sh && bash -n ~/ai-folder/dev/codex-discord/scripts/uninstall.sh`
Expected: `uninstall.test OK`

- [ ] **Step 5: codex-discord 레포에 커밋**

```bash
cd ~/ai-folder/dev/codex-discord && git add scripts/uninstall.sh test/uninstall.test.sh && git commit -m "feat: uninstall.sh 신설 — install.sh 대응 제거 경로 (tui 는 bootout 금지, 통합 설치기 위임 계약)"
```

---

### Task 4: 상류(discord-multiagent) — 오버레이 manifest 정본 + 수다 지침 시드

**Files:**
- Create: `~/ai-folder/dev/discord-multiagent/install/overlay-manifest.json`
- Create: `~/ai-folder/dev/discord-multiagent/install/chat-CLAUDE.md`
- Create: `~/ai-folder/dev/discord-multiagent/test/manifest.test.sh`

**Interfaces:**
- Consumes: 하네스 레포 기존 파일들(scripts 5종, .env.example, .mcp.json, CLAUDE.md 마커 블록)
- Produces: **오버레이 계약**(Task 9 overlay·Task 12 doctor가 소비) — `install/overlay-manifest.json`의 스키마:
  - `schema_version: 1`
  - `overlay: [{src, dst, mode, merge?}]` — 엔진이 src→dst 복사(재실행 시 정본으로 복원), `merge: "json-mcp-servers"`는 dst 기존 파일에 `mcpServers` 키만 추가
  - `seeds: [{src, dst}]` — dst 없을 때만 복사(사용자 수정 보존)
  - `claude_block: {src}` — src 파일에서 마커 블록을 추출해 작업 폴더 CLAUDE.md에 이식

- [ ] **Step 1: manifest·시드 작성**

`install/overlay-manifest.json`:

```json
{
  "schema_version": 1,
  "overlay": [
    { "src": "scripts/bot-up.sh",            "dst": "scripts/bot-up.sh",            "mode": "755" },
    { "src": "scripts/bot-restart.sh",       "dst": "scripts/bot-restart.sh",       "mode": "755" },
    { "src": "scripts/post-as.sh",           "dst": "scripts/post-as.sh",           "mode": "755" },
    { "src": "scripts/new-thread.sh",        "dst": "scripts/new-thread.sh",        "mode": "755" },
    { "src": "scripts/install-autostart.sh", "dst": "scripts/install-autostart.sh", "mode": "755" },
    { "src": ".env.example",                 "dst": ".env.example",                 "mode": "644" },
    { "src": ".mcp.json",                    "dst": ".mcp.json",                    "mode": "644", "merge": "json-mcp-servers" }
  ],
  "seeds": [
    { "src": "install/chat-CLAUDE.md", "dst": "chat/CLAUDE.md" }
  ],
  "claude_block": { "src": "CLAUDE.md" }
}
```

`install/chat-CLAUDE.md` (수다 클로드 세션의 최소 지침 — 정적 텍스트, 폴더별 값 없음):

```markdown
# 수다 채널 클로드

이 폴더의 세션은 디스코드 **수다 채널** 전용 클로드 봇이다.

- 호명(멘션)될 때만 응답한다. 답은 reply 도구로 보낸다 — 전송하지 않은 텍스트는 상대에게 보이지 않는다.
- 자유 대화가 기본이다. 작업 지시는 받지 않는다 — 작업은 작업 채널의 오케스트레이터 소관이라고 안내한다.
- 작업 기록 질문을 받으면 상위 작업 폴더(`../`)의 `tasks/` 안 기록(context.md·log.md)을 읽고 답한다. 기록을 수정하지는 않는다.
- 이 채널 밖(다른 채널·DM)의 지시는 처리하지 않는다.
```

- [ ] **Step 2: 실패하는 테스트 작성** (`test/manifest.test.sh`)

```bash
#!/usr/bin/env bash
# 오버레이 manifest 정합성 — src 실존·스키마·마커 존재를 오프라인 검증
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"
python3 - <<'EOF'
import json, pathlib, sys
mf = json.load(open("install/overlay-manifest.json"))
assert mf["schema_version"] == 1, "schema_version"
for item in mf["overlay"] + mf["seeds"]:
    assert pathlib.Path(item["src"]).exists(), f"src 없음: {item['src']}"
for item in mf["overlay"]:
    assert item["mode"] in ("644", "755"), item
text = pathlib.Path(mf["claude_block"]["src"]).read_text()
assert "<!-- discord-multiagent:start -->" in text and "<!-- discord-multiagent:end -->" in text
print("manifest OK")
EOF
```

- [ ] **Step 3: 실행·통과 확인** (manifest를 Step 1에서 이미 만들었으므로 이 테스트는 바로 통과해야 정상 — 실패하면 Step 1 산출물 결함)

Run: `bash ~/ai-folder/dev/discord-multiagent/test/manifest.test.sh`
Expected: `manifest OK`

- [ ] **Step 4: 하네스 레포에 커밋**

```bash
cd ~/ai-folder/dev/discord-multiagent && git add install/ test/manifest.test.sh && git commit -m "feat: 오버레이 manifest 정본 + 수다 클로드 지침 시드 신설 (통합 설치기 오버레이 계약, schema_version 1)"
```

---

### Task 5: harnessctl 코어 + preflight

**Files:**
- Create: `plugins/harness-installer/skills/configure-harness/generator/harnessctl.py`
- Test: `tests/test_harnessctl.py`

**Interfaces:**
- Produces (이후 모든 태스크가 소비):
  - `home() -> Path` (`Path(os.environ["HOME"])` — 유일한 경로 진입점)
  - `config_dir() -> Path` = `home()/".config/discord-harness"`, `state_path() -> Path`
  - `load_state() -> dict` / `save_state(st: dict) -> None` — state.json (`schema_version`, `work_dir`, `repos`, `steps`, `overlay`, `mcp_added`)
  - `now() -> str` (isoformat seconds)
  - `pins() -> dict` — 동봉 pins.json 로드
  - `repos_dir() -> Path` = `home()/".local/share/discord-harness/repos"`, `repo_url(name) -> str` (env `HARNESS_REPO_BASE` 오버라이드)
  - `harness_repo()/bridge_repo()/coach_repo() -> Path`
  - `run_git(args, cwd=None) -> CompletedProcess`, `find_tmux() -> str`(folder-bot 동일)
  - `resolve_work_dir(a) -> Path` — `--work-dir` 인자 우선, 없으면 state의 `work_dir`, 둘 다 없으면 exit
  - 상수: `SCHEMA_VERSION=1`, `ROLES=("orch","claude","codex","gemini")`, `REPO_NAMES`, `PLUGINS`, `BLOCK_START/BLOCK_END`(마커), `ORCH_PLIST_LABEL`, `CHAT_PLIST_LABEL`, `CHAT_SESSION="chat-claude"`
  - doctor/preflight/verify 공통 출력 규약: `[OK]/[WARN]/[FAIL] <메시지>` + `sys.exit(1 if fails else 0)`
  - CLI: `harnessctl.py preflight`

- [ ] **Step 1: 실패하는 테스트 작성** (`tests/test_harnessctl.py` 신규)

```python
import json, os, plistlib, re, subprocess, sys
from pathlib import Path

HARNESSCTL = (Path(__file__).parent.parent
              / "plugins/harness-installer/skills/configure-harness/generator/harnessctl.py")
PINS = json.loads((HARNESSCTL.parent / "pins.json").read_text())

def run(home_dir, *args, env_extra=None):
    env = dict(os.environ, HOME=str(home_dir))
    if env_extra:
        env.update(env_extra)
    return subprocess.run([sys.executable, str(HARNESSCTL), *args],
                          capture_output=True, text=True, env=env)

def test_preflight_fails_on_bare_env(tmp_path):
    # tmp HOME 에는 discord 플러그인 캐시가 없다 → 최소 1개 FAIL → exit 1
    r = run(tmp_path, "preflight")
    assert r.returncode == 1
    assert "[FAIL]" in r.stdout and "discord 플러그인" in r.stdout

def test_preflight_reports_tools(tmp_path):
    r = run(tmp_path, "preflight")
    assert "[OK] git" in r.stdout and "tmux" in r.stdout and "claude" in r.stdout

def test_preflight_ok_when_all_present(tmp_path):
    (tmp_path / ".claude/plugins/cache/claude-plugins-official/discord").mkdir(parents=True)
    r = run(tmp_path, "preflight")
    # 개발 머신 전제: git/tmux/node/claude/codex 는 PATH 에 있다
    assert r.returncode == 0, r.stdout + r.stderr
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m pytest tests/ -v`
Expected: FAIL (harnessctl.py 없음)

- [ ] **Step 3: harnessctl.py 코어 구현**

```python
#!/usr/bin/env python3
"""discord-harness 통합 설치기 결정적 엔진 — 매뉴얼 16장을 대체한다.

경로는 전부 HOME 환경변수 기준(테스트가 HOME을 tmpdir로 돌린다).
A안 위임 오케스트레이터: 정본이 없는 접합부만 직접, 설치 동작은 정본 스크립트에 위임.
오버레이는 manifest를 읽어 복사만 한다(창작 금지).
launchctl로 job을 내리지 않는다(부팅 job은 프로세스 그룹째 킬 위험, 2026-07-31 실측)
— plist 파일 생성/삭제 + tmux kill-session만. (Task 13이 소스 전체에 해당 launchctl
서브커맨드 문자열이 없음을 정적 검증하므로 이 파일에 그 단어를 쓰지 말 것.)
비밀(토큰·웹훅)은 파일로만 수령하고 stdout에 출력하지 않는다.
"""
import argparse, hashlib, json, os, plistlib, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = 1
ROLES = ("orch", "claude", "codex", "gemini")
REPO_NAMES = ("discord-multiagent", "codex-discord", "usage-coach")
PLUGINS = (("multi-agent-starter", "netwaif/multi-agent-starter"),
           ("folder-bot", "netwaif/folder-bot"))
BLOCK_START = "<!-- discord-multiagent:start -->"
BLOCK_END = "<!-- discord-multiagent:end -->"
ORCH_PLIST_LABEL = "com.discord-multiagent.orchestrator"
CHAT_PLIST_LABEL = "com.discord-harness.chat-claude"
CHAT_SESSION = "chat-claude"

def home() -> Path: return Path(os.environ["HOME"])
def config_dir() -> Path: return home() / ".config/discord-harness"
def state_path() -> Path: return config_dir() / "state.json"
def repos_dir() -> Path: return home() / ".local/share/discord-harness/repos"
def harness_repo() -> Path: return repos_dir() / "discord-multiagent"
def bridge_repo() -> Path: return repos_dir() / "codex-discord"
def coach_repo() -> Path: return repos_dir() / "usage-coach"
def now() -> str: return datetime.now().isoformat(timespec="seconds")

def repo_url(name: str) -> str:
    base = os.environ.get("HARNESS_REPO_BASE")
    if base:
        return f"{base}/{name}"
    return f"https://github.com/netwaif/{name}.git"

def pins() -> dict:
    return json.loads((Path(__file__).resolve().parent / "pins.json").read_text())

def load_state() -> dict:
    if not state_path().exists():
        return {"schema_version": SCHEMA_VERSION, "work_dir": None,
                "repos": {}, "steps": {}, "overlay": {}, "mcp_added": []}
    return json.loads(state_path().read_text())

def save_state(st: dict) -> None:
    config_dir().mkdir(parents=True, exist_ok=True)
    state_path().write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n")

def run_git(args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

def find_tmux() -> str:
    for c in (shutil.which("tmux"), "/opt/homebrew/bin/tmux", "/usr/local/bin/tmux"):
        if c and Path(c).exists():
            return c
    sys.exit("오류: tmux를 찾을 수 없음 — brew install tmux")

def resolve_work_dir(a) -> Path:
    wd = getattr(a, "work_dir", None) or load_state().get("work_dir")
    if not wd:
        sys.exit("오류: 작업 폴더를 알 수 없음 — --work-dir 지정(또는 pair/install 선행)")
    return Path(wd).expanduser()

def cmd_preflight(a) -> None:
    fails = 0
    def rep(level, msg):
        nonlocal fails
        if level == "FAIL":
            fails += 1
        print(f"[{level}] {msg}")
    rep("OK" if sys.platform == "darwin" else "FAIL", "macOS")
    for tool, miss_level, hint in (
            ("git", "FAIL", "xcode-select --install"),
            ("tmux", "FAIL", "brew install tmux"),
            ("node", "FAIL", "brew install node (브리지는 Node 22+)"),
            ("claude", "FAIL", "https://claude.com/claude-code 설치"),
            ("codex", "FAIL", "npm i -g @openai/codex (수다 브리지 필수)"),
            ("agy", "WARN", "없으면 제미나이 봇만 빠짐")):
        found = shutil.which(tool)
        rep("OK" if found else miss_level, f"{tool}: {found or '없음 — ' + hint}")
    plug = home() / ".claude/plugins/cache/claude-plugins-official/discord"
    rep("OK" if plug.is_dir() else "FAIL",
        f"discord 플러그인: {plug if plug.is_dir() else '미설치 — claude 안에서 /plugin 으로 discord 설치'}")
    sys.exit(1 if fails else 0)

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight", help="전제 도구 점검(읽기 전용)").set_defaults(fn=cmd_preflight)
    a = p.parse_args()
    a.fn(a)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest tests/ -v`
Expected: 3 PASS

- [ ] **Step 5: 커밋**

```bash
git add -A && git commit -m "feat: harnessctl 코어(HOME 단일 진입점·state·핀 로더) + preflight"
```

---

### Task 6: fetch — 핀 체크아웃 clone/pull + state 기록

**Files:**
- Modify: `generator/harnessctl.py` — `cmd_fetch` 추가
- Test: `tests/test_harnessctl.py` — fixture 헬퍼 + fetch 테스트 추가

**Interfaces:**
- Consumes: `pins()`, `repo_url()`, `repos_dir()`, `run_git()`, `load_state()/save_state()`
- Produces:
  - CLI `fetch [--latest]` — 3레포를 clone(있으면 `fetch --tags`), 기본은 pins 태그 체크아웃, `--latest`는 origin 기본 브랜치 최신. 성공 시 `state["repos"][name] = {"ref": <태그 또는 "latest">, "commit": <sha>}`, `state["steps"]["fetch"]` 기록
  - 테스트 fixture 계약: `make_fixture_repos(tmp_path) -> Path` — pins.json을 읽어 같은 태그를 단 가짜 3레포를 만들고 base 경로 반환(이후 모든 태스크의 테스트가 소비). fixture 하네스 레포는 Task 4의 실제 manifest와 **동일 스키마**의 manifest·마커 블록 CLAUDE.md·scripts 5종 더미를 포함

- [ ] **Step 1: fixture 헬퍼 + 실패하는 테스트 추가**

```python
STUB = "#!/bin/bash\necho stub-ok\n"
MANIFEST = {
    "schema_version": 1,
    "overlay": [
        {"src": "scripts/bot-up.sh", "dst": "scripts/bot-up.sh", "mode": "755"},
        {"src": "scripts/bot-restart.sh", "dst": "scripts/bot-restart.sh", "mode": "755"},
        {"src": "scripts/post-as.sh", "dst": "scripts/post-as.sh", "mode": "755"},
        {"src": "scripts/new-thread.sh", "dst": "scripts/new-thread.sh", "mode": "755"},
        {"src": "scripts/install-autostart.sh", "dst": "scripts/install-autostart.sh", "mode": "755"},
        {"src": ".env.example", "dst": ".env.example", "mode": "644"},
        {"src": ".mcp.json", "dst": ".mcp.json", "mode": "644", "merge": "json-mcp-servers"},
    ],
    "seeds": [{"src": "install/chat-CLAUDE.md", "dst": "chat/CLAUDE.md"}],
    "claude_block": {"src": "CLAUDE.md"},
}

def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                            GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))

def _make_repo(base, name, files, tag):
    d = base / name
    for rel, content in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        if rel.endswith(".sh"):
            p.chmod(0o755)
    _git(d, "init", "-q", "-b", "main")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "init")
    _git(d, "tag", tag)
    return d

def make_fixture_repos(tmp_path):
    base = tmp_path / "origin"
    base.mkdir(exist_ok=True)
    harness_files = {
        "scripts/bot-up.sh": STUB, "scripts/bot-restart.sh": STUB,
        "scripts/post-as.sh": STUB, "scripts/new-thread.sh": STUB,
        "scripts/install-autostart.sh": STUB,
        ".env.example": "WORK_CHANNEL_ID=\nCHAT_CHANNEL_ID=\n",
        ".mcp.json": json.dumps({"mcpServers": {"codex": {"type": "stdio", "command": "codex",
                                                          "args": ["mcp-server"], "env": {}}}}, indent=2),
        "CLAUDE.md": ("# 하네스\n\n<!-- discord-multiagent:start -->\n## Discord 운영\n"
                      "승인 판정·미러 규칙(정본 본문).\n<!-- discord-multiagent:end -->\n"),
        "install/overlay-manifest.json": json.dumps(MANIFEST, indent=2),
        "install/chat-CLAUDE.md": "# 수다 채널 클로드\n호명될 때만 응답.\n",
    }
    bridge_files = {
        "scripts/install.sh": STUB, "scripts/uninstall.sh": STUB,
        "src/index.mjs": "// stub\n",
    }
    coach_files = {
        "scripts/install.sh": STUB, "scripts/uninstall.sh": STUB,
        "discord_dash.py": "# stub\n",
    }
    for name, files in (("discord-multiagent", harness_files),
                        ("codex-discord", bridge_files), ("usage-coach", coach_files)):
        _make_repo(base, name, files, PINS["repos"][name])
    return base

def fetched(tmp_path):
    base = make_fixture_repos(tmp_path)
    r = run(tmp_path, "fetch", env_extra={"HARNESS_REPO_BASE": str(base)})
    assert r.returncode == 0, r.stdout + r.stderr
    return base

def test_fetch_checks_out_pin_and_records(tmp_path):
    fetched(tmp_path)
    st = json.loads((tmp_path / ".config/discord-harness/state.json").read_text())
    for name in ("discord-multiagent", "codex-discord", "usage-coach"):
        assert (tmp_path / ".local/share/discord-harness/repos" / name / ".git").exists()
        assert st["repos"][name]["ref"] == PINS["repos"][name]
        assert len(st["repos"][name]["commit"]) == 40
    assert st["steps"]["fetch"]

def test_fetch_idempotent(tmp_path):
    base = fetched(tmp_path)
    r = run(tmp_path, "fetch", env_extra={"HARNESS_REPO_BASE": str(base)})
    assert r.returncode == 0, r.stdout + r.stderr

def test_fetch_missing_pin_tag_fails_with_hint(tmp_path):
    base = make_fixture_repos(tmp_path)
    _git(base / "usage-coach", "tag", "-d", PINS["repos"]["usage-coach"])
    r = run(tmp_path, "fetch", env_extra={"HARNESS_REPO_BASE": str(base)})
    assert r.returncode != 0
    assert "핀" in r.stderr and "usage-coach" in r.stderr
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → 새 테스트 FAIL (fetch 서브커맨드 없음)

- [ ] **Step 3: cmd_fetch 구현**

```python
def cmd_fetch(a) -> None:
    pin_repos = pins()["repos"]
    repos_dir().mkdir(parents=True, exist_ok=True)
    st = load_state()
    for name in REPO_NAMES:
        dst = repos_dir() / name
        if not dst.exists():
            r = run_git(["clone", "--quiet", repo_url(name), str(dst)])
            if r.returncode != 0:
                sys.exit(f"오류: {name} clone 실패 — {r.stderr.strip()}\n"
                         f"다음 행동: 네트워크 확인 후 fetch 재실행(멱등)")
        else:
            run_git(["fetch", "--tags", "--quiet", "origin"], cwd=dst)
        if a.latest:
            head = run_git(["rev-parse", "--abbrev-ref", "origin/HEAD"], cwd=dst).stdout.strip()
            branch = head.split("/", 1)[1] if "/" in head else "main"
            run_git(["checkout", "--quiet", branch], cwd=dst)
            run_git(["pull", "--ff-only", "--quiet"], cwd=dst)
            ref = "latest"
        else:
            ref = pin_repos[name]
            r = run_git(["checkout", "--quiet", ref], cwd=dst)
            if r.returncode != 0:
                sys.exit(f"오류: {name} 핀 {ref} 체크아웃 실패 — {r.stderr.strip()}\n"
                         f"다음 행동: fetch --latest 로 우회하거나 pins.json 확인")
        commit = run_git(["rev-parse", "HEAD"], cwd=dst).stdout.strip()
        st["repos"][name] = {"ref": ref, "commit": commit}
        print(f"fetch: {name} @ {ref} ({commit[:8]})")
    st["steps"]["fetch"] = now()
    save_state(st)
```

main()에 등록:

```python
    fp = sub.add_parser("fetch", help="정본 3레포 clone/pull (기본: 검증 조합 핀)")
    fp.add_argument("--latest", action="store_true")
    fp.set_defaults(fn=cmd_fetch)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v   # 전부 PASS
git add -A && git commit -m "feat: fetch — 핀 태그 체크아웃 clone/pull + state 기록 (URL 오버라이드 테스트 계약)"
```

---

### Task 7: plugins — 기존 플러그인 2개 직접 설치 + 수동 폴백

**Files:**
- Modify: `generator/harnessctl.py` — `plugin_cmds`, `cmd_plugins` 추가
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: `PLUGINS` 상수
- Produces: `plugin_cmds(host: str) -> list[list[str]]`, CLI `plugins [--host {claude,codex}] [--dry-run]` — `<host> plugin marketplace add netwaif/<repo>` + `<host> plugin install <name>@<name>`을 순서대로 직접 실행. 실패(비-0 또는 실행파일 없음)면 `[FAIL]` + 수동 폴백 안내 출력 후 exit 1. dry-run은 명령 문자열만 출력

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def test_plugins_dry_run_prints_commands(tmp_path):
    r = run(tmp_path, "plugins", "--dry-run")
    assert r.returncode == 0
    assert "claude plugin marketplace add netwaif/multi-agent-starter" in r.stdout
    assert "claude plugin install multi-agent-starter@multi-agent-starter" in r.stdout
    assert "claude plugin marketplace add netwaif/folder-bot" in r.stdout
    assert "claude plugin install folder-bot@folder-bot" in r.stdout

def test_plugins_codex_host(tmp_path):
    r = run(tmp_path, "plugins", "--host", "codex", "--dry-run")
    assert "codex plugin marketplace add netwaif/folder-bot" in r.stdout

def test_plugins_failure_prints_manual_fallback(tmp_path):
    # PATH 를 비워 claude 실행 자체가 불가능한 상황 → 수동 폴백 안내 + exit 1
    r = run(tmp_path, "plugins", env_extra={"PATH": "/usr/bin:/bin"})
    assert r.returncode == 1
    assert "수동 폴백" in r.stdout
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → 새 테스트 FAIL

- [ ] **Step 3: 구현**

```python
def plugin_cmds(host: str) -> list[list[str]]:
    cmds = []
    for name, repo in PLUGINS:
        cmds.append([host, "plugin", "marketplace", "add", repo])
        cmds.append([host, "plugin", "install", f"{name}@{name}"])
    return cmds

def cmd_plugins(a) -> None:
    ok = True
    for argv in plugin_cmds(a.host):
        line = " ".join(argv)
        if a.dry_run:
            print(line)
            continue
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=120)
            failed, detail = r.returncode != 0, (r.stderr or r.stdout).strip()[:200]
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            failed, detail = True, str(e)
        if failed:
            ok = False
            print(f"[FAIL] {line} — {detail}")
            print(f"  수동 폴백: 터미널에서 `{line}` 직접 실행, 또는 {a.host} 대화에서 "
                  f"`/plugin marketplace add {argv[-1]}` 후 /plugin 으로 설치")
        else:
            print(f"[OK] {line}")
    if ok and not a.dry_run:
        st = load_state(); st["steps"]["plugins"] = now(); save_state(st)
    sys.exit(0 if ok else 1)
```

main() 등록:

```python
    pp = sub.add_parser("plugins", help="starter·folder-bot 플러그인 직접 설치")
    pp.add_argument("--host", choices=("claude", "codex"), default="claude")
    pp.add_argument("--dry-run", action="store_true")
    pp.set_defaults(fn=cmd_plugins)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: plugins — marketplace add/install 직접 실행 + 실패 시 수동 폴백 출력"
```

---

### Task 8: pair — 토큰 파일 4개 → .env 조립 + 상태 폴더 2벌 + 웹훅

**Files:**
- Modify: `generator/harnessctl.py` — `read_token_file`, `write_state_dir`, `cmd_pair` 추가
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: `ROLES`, `load_state()/save_state()`, `now()`
- Produces:
  - `write_state_dir(state_dir: Path, token: str, channel_id: str, approver: str, require_mention: bool) -> None` — `.env`(`DISCORD_BOT_TOKEN=`, 0600) + `access.json`(folder-bot 실측 스키마) + `inbox/`
  - CLI `pair --work-dir W --work-channel-id --chat-channel-id --approver-user-id [--webhook-url-file F] [--force]`:
    - `W/.bot-token-{orch,claude,codex,gemini}` 4개를 읽어 `W/.env`(변수 7종, 0600) 조립
    - `W/.discord-state/` = 오케 페어링(작업 채널, requireMention false)
    - `W/chat/.discord-state/` = 수다 클로드 페어링(수다 채널, requireMention true)
    - `F`가 있으면 URL을 읽어 `~/.config/usage-coach/discord.json`의 `webhook_url`에 기록(0600) 후 F 삭제
    - 성공 시 토큰 파일 4개 삭제, `state["work_dir"]`·`steps["pair"]` 기록
    - `W/.env` 기존 존재 + `--force` 없음 → 거부(exit 비-0)

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def _token_files(work):
    for role in ("orch", "claude", "codex", "gemini"):
        (work / f".bot-token-{role}").write_text(f"tok-{role}\n")

def _pair(tmp_path, work, *extra):
    return run(tmp_path, "pair", "--work-dir", str(work),
               "--work-channel-id", "111", "--chat-channel-id", "222",
               "--approver-user-id", "999", *extra)

def test_pair_assembles_env_and_state_dirs(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    _token_files(work)
    r = _pair(tmp_path, work)
    assert r.returncode == 0, r.stderr
    env = (work / ".env").read_text()
    assert "WORK_CHANNEL_ID=111\n" in env and "CHAT_CHANNEL_ID=222\n" in env
    assert "APPROVER_USER_ID=999\n" in env and "ORCH_BOT_TOKEN=tok-orch\n" in env
    assert "CLAUDE_BOT_TOKEN=tok-claude\n" in env and "GEMINI_BOT_TOKEN=tok-gemini\n" in env
    assert oct((work / ".env").stat().st_mode)[-3:] == "600"
    orch = json.loads((work / ".discord-state/access.json").read_text())
    assert orch["groups"]["111"]["requireMention"] is False
    assert (work / ".discord-state/.env").read_text() == "DISCORD_BOT_TOKEN=tok-orch\n"
    chat = json.loads((work / "chat/.discord-state/access.json").read_text())
    assert chat["groups"]["222"]["requireMention"] is True
    assert (work / "chat/.discord-state/inbox").is_dir()
    for role in ("orch", "claude", "codex", "gemini"):
        assert not (work / f".bot-token-{role}").exists()   # 토큰 파일 즉시 삭제
    assert "tok-orch" not in r.stdout                        # 비밀 stdout 금지

def test_pair_refuses_overwrite_without_force(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    _token_files(work)
    assert _pair(tmp_path, work).returncode == 0
    _token_files(work)
    r = _pair(tmp_path, work)
    assert r.returncode != 0
    assert "tok-orch" in (work / ".env").read_text()   # 기존 보존
    _token_files(work)
    assert _pair(tmp_path, work, "--force").returncode == 0

def test_pair_webhook_file(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    _token_files(work)
    wf = work / ".webhook-url"; wf.write_text("https://example.invalid/hook\n")
    r = _pair(tmp_path, work, "--webhook-url-file", str(wf))
    assert r.returncode == 0, r.stderr
    cfg = json.loads((tmp_path / ".config/usage-coach/discord.json").read_text())
    assert cfg["webhook_url"] == "https://example.invalid/hook"
    assert not wf.exists()

def test_pair_missing_token_file_names_it(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    (work / ".bot-token-orch").write_text("t\n")
    r = _pair(tmp_path, work)
    assert r.returncode != 0 and ".bot-token-claude" in r.stderr
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → FAIL

- [ ] **Step 3: 구현**

```python
def read_token_file(work: Path, role: str) -> str:
    f = work / f".bot-token-{role}"
    if not f.exists():
        sys.exit(f"오류: 토큰 파일 없음 — {f}\n다음 행동: pbpaste > {f.name} && chmod 600 {f.name}")
    tok = f.read_text().strip()
    if not tok:
        sys.exit(f"오류: 토큰 파일이 비어 있음 — {f}")
    return tok

def write_state_dir(state_dir: Path, token: str, channel_id: str,
                    approver: str, require_mention: bool) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "inbox").mkdir(exist_ok=True)
    env = state_dir / ".env"
    env.write_text(f"DISCORD_BOT_TOKEN={token}\n")
    env.chmod(0o600)
    access = {"dmPolicy": "allowlist", "allowFrom": [approver],
              "groups": {channel_id: {"requireMention": require_mention, "allowFrom": [approver]}},
              "pending": {}}
    (state_dir / "access.json").write_text(json.dumps(access, ensure_ascii=False, indent=2) + "\n")

def cmd_pair(a) -> None:
    work = Path(a.work_dir).expanduser()
    env_path = work / ".env"
    if env_path.exists() and not a.force:
        sys.exit(f"오류: {env_path} 이미 존재 — 덮어쓰려면 --force")
    tokens = {role: read_token_file(work, role) for role in ROLES}
    env_path.write_text(
        f"WORK_CHANNEL_ID={a.work_channel_id}\n"
        f"CHAT_CHANNEL_ID={a.chat_channel_id}\n"
        f"APPROVER_USER_ID={a.approver_user_id}\n"
        f"ORCH_BOT_TOKEN={tokens['orch']}\n"
        f"CLAUDE_BOT_TOKEN={tokens['claude']}\n"
        f"CODEX_BOT_TOKEN={tokens['codex']}\n"
        f"GEMINI_BOT_TOKEN={tokens['gemini']}\n")
    env_path.chmod(0o600)
    write_state_dir(work / ".discord-state", tokens["orch"], a.work_channel_id,
                    a.approver_user_id, False)
    write_state_dir(work / "chat/.discord-state", tokens["claude"], a.chat_channel_id,
                    a.approver_user_id, True)
    if a.webhook_url_file:
        wf = Path(a.webhook_url_file).expanduser()
        if not wf.exists():
            sys.exit(f"오류: 웹훅 URL 파일 없음 — {wf}")
        uc = home() / ".config/usage-coach"
        uc.mkdir(parents=True, exist_ok=True)
        cfg_path = uc / "discord.json"
        cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        cfg["webhook_url"] = wf.read_text().strip()
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        cfg_path.chmod(0o600)
        wf.unlink()
    for role in ROLES:
        (work / f".bot-token-{role}").unlink()
    st = load_state()
    st["work_dir"] = str(work)
    st["steps"]["pair"] = now()
    save_state(st)
    print(f"페어링 완료: {env_path} (0600) + 상태 폴더 2벌, 토큰 파일 4개 삭제")
```

main() 등록:

```python
    rp = sub.add_parser("pair", help="토큰 파일 수령 → .env 조립(0600) → 토큰 파일 삭제")
    rp.add_argument("--work-dir", required=True)
    rp.add_argument("--work-channel-id", required=True)
    rp.add_argument("--chat-channel-id", required=True)
    rp.add_argument("--approver-user-id", required=True)
    rp.add_argument("--webhook-url-file")
    rp.add_argument("--force", action="store_true")
    rp.set_defaults(fn=cmd_pair)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: pair — 토큰 파일 4개→.env 7종 조립·상태 폴더 2벌·웹훅 파일 수령, 기존 설치 보호"
```

---

### Task 9: install --phase overlay — manifest 기반 오버레이

**Files:**
- Modify: `generator/harnessctl.py` — `sha256`, `apply_overlay`, `apply_seeds`, `install_claude_block`, `remove_claude_block`, `extract_block`, `cmd_install`(overlay phase) 추가
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: `harness_repo()`, Task 4 manifest 스키마, Task 6 fixture(`fetched`)
- Produces:
  - `sha256(p: Path) -> str`
  - `apply_overlay(work: Path, st: dict) -> list[str]` — manifest `overlay` 처리: 일반 항목은 src→dst 복사(내용 다르면 덮어써 정본 복원, mode 적용, `st["overlay"][dst상대경로]=해시` 기록), `merge: "json-mcp-servers"` + dst 존재 시 `mcpServers` 키만 추가(`st["mcp_added"]`에 기록, 기존 키는 건드리지 않음), dst 없으면 일반 복사로 처리
  - `apply_seeds(work, st) -> list[str]` — dst 없을 때만 복사 + 해시 기록(사용자 수정 보존)
  - `extract_block(text, start, end) -> str`, `install_claude_block(md: Path, body: str) -> list[str]`(BLOCK_START 이미 있으면 no-op), `remove_claude_block(md: Path) -> list[str]`(folder-bot remove_block과 동일 로직 — Task 13이 소비)
  - CLI `install --work-dir W [--phase {overlay,delegate,all}] [--dashboard] [--autostart] [--dry-run]` — 이 태스크에서는 overlay phase만 동작(delegate는 Task 10에서 채움), manifest 없음/schema 불일치 시 원인+다음 행동 한 줄로 exit
  - overlay 성공 시 `state["work_dir"]` 기록(pair보다 먼저 실행되는 단계이므로 여기서도 기록)

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def _overlay(tmp_path, work):
    return run(tmp_path, "install", "--work-dir", str(work), "--phase", "overlay")

def test_overlay_copies_manifest_files(tmp_path):
    fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    r = _overlay(tmp_path, work)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (work / "scripts/bot-up.sh").read_text() == STUB
    assert os.access(work / "scripts/bot-up.sh", os.X_OK)
    assert (work / ".env.example").exists()
    assert (work / "chat/CLAUDE.md").exists()               # seed
    st = json.loads((tmp_path / ".config/discord-harness/state.json").read_text())
    assert "scripts/bot-up.sh" in st["overlay"]
    assert len(st["overlay"]["scripts/bot-up.sh"]) == 64    # sha256 기록

def test_overlay_claude_block_and_mcp_merge_nondestructive(tmp_path):
    fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    original = "# 내 규칙\n\n소중한 내용.\n"
    (work / "CLAUDE.md").write_text(original)
    (work / ".mcp.json").write_text(json.dumps({"mcpServers": {"mine": {"command": "x"}}}))
    (work / "SESSION.md").write_text("세션 기록\n")
    r = _overlay(tmp_path, work)
    assert r.returncode == 0, r.stdout + r.stderr
    text = (work / "CLAUDE.md").read_text()
    assert original in text and "<!-- discord-multiagent:start -->" in text
    mcp = json.loads((work / ".mcp.json").read_text())
    assert "mine" in mcp["mcpServers"] and "codex" in mcp["mcpServers"]
    assert (work / "SESSION.md").read_text() == "세션 기록\n"   # SESSION.md 무접촉
    st = json.loads((tmp_path / ".config/discord-harness/state.json").read_text())
    assert st["mcp_added"] == ["codex"]
    r2 = _overlay(tmp_path, work)                               # 멱등
    assert r2.returncode == 0
    assert (work / "CLAUDE.md").read_text() == text

def test_overlay_seed_preserves_user_edit(tmp_path):
    fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    _overlay(tmp_path, work)
    (work / "chat/CLAUDE.md").write_text("사용자 수정본\n")
    _overlay(tmp_path, work)
    assert (work / "chat/CLAUDE.md").read_text() == "사용자 수정본\n"

def test_overlay_without_fetch_fails_with_hint(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    r = _overlay(tmp_path, work)
    assert r.returncode != 0 and "fetch" in r.stderr
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → FAIL

- [ ] **Step 3: 구현**

```python
def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_manifest() -> dict:
    mp = harness_repo() / "install/overlay-manifest.json"
    if not mp.exists():
        sys.exit(f"오류: 오버레이 manifest 없음 — {mp}\n"
                 f"다음 행동: harnessctl.py fetch 선행(핀이 manifest 포함 버전인지 doctor 로 확인)")
    mf = json.loads(mp.read_text())
    if mf.get("schema_version") != SCHEMA_VERSION:
        sys.exit(f"오류: manifest schema_version {mf.get('schema_version')} ≠ {SCHEMA_VERSION}"
                 f" — 설치기 업데이트 필요")
    return mf

def apply_overlay(work: Path, st: dict) -> list[str]:
    mf = load_manifest()
    out = []
    for item in mf["overlay"]:
        src, dst = harness_repo() / item["src"], work / item["dst"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if item.get("merge") == "json-mcp-servers" and dst.exists():
            cur = json.loads(dst.read_text())
            add = json.loads(src.read_text())
            added = [k for k in add.get("mcpServers", {})
                     if k not in cur.setdefault("mcpServers", {})]
            for k in added:
                cur["mcpServers"][k] = add["mcpServers"][k]
            if added:
                dst.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
                st["mcp_added"] = sorted(set(st.get("mcp_added", []) + added))
                out.append(f"오버레이(병합): {dst} += {added}")
            continue
        if not (dst.exists() and dst.read_bytes() == src.read_bytes()):
            shutil.copyfile(src, dst)
            out.append(f"오버레이: {dst}")
        dst.chmod(int(item.get("mode", "644"), 8))
        st["overlay"][item["dst"]] = sha256(dst)
    body = extract_block((harness_repo() / mf["claude_block"]["src"]).read_text())
    out += install_claude_block(work / "CLAUDE.md", body)
    return out

def apply_seeds(work: Path, st: dict) -> list[str]:
    out = []
    for item in load_manifest().get("seeds", []):
        src, dst = harness_repo() / item["src"], work / item["dst"]
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        st["overlay"][item["dst"]] = sha256(dst)
        out.append(f"시드: {dst}")
    return out

def extract_block(text: str) -> str:
    if BLOCK_START not in text or BLOCK_END not in text:
        sys.exit(f"오류: 정본 CLAUDE.md에 마커 블록 없음 ({BLOCK_START})")
    return text.split(BLOCK_START, 1)[1].split(BLOCK_END, 1)[0]

def install_claude_block(md: Path, body: str) -> list[str]:
    cur = md.read_text() if md.exists() else ""
    if BLOCK_START in cur:
        return []
    md.write_text(cur + f"\n{BLOCK_START}{body}{BLOCK_END}\n")
    return [f"CLAUDE.md 블록 설치: {md}"]

def remove_claude_block(md: Path) -> list[str]:
    if not md.exists():
        return []
    cur = md.read_text()
    if BLOCK_START not in cur or BLOCK_END not in cur:
        return []
    pre, rest = cur.split(BLOCK_START, 1)
    _, post = rest.split(BLOCK_END, 1)
    md.write_text(pre.rstrip("\n") + ("\n" if pre.strip() else "") + post.lstrip("\n"))
    return [f"CLAUDE.md 블록 제거: {md}"]

def cmd_install(a) -> None:
    st = load_state()
    work = Path(a.work_dir).expanduser() if a.work_dir else resolve_work_dir(a)
    st["work_dir"] = str(work)
    out = []
    if a.phase in ("overlay", "all"):
        out += apply_overlay(work, st)
        out += apply_seeds(work, st)
    # delegate phase 는 Task 10 에서 구현
    for line in out:
        print(line)
    if not a.dry_run:
        st["steps"][f"install-{a.phase}"] = now()
    save_state(st)
```

main() 등록:

```python
    ip = sub.add_parser("install", help="오버레이 적용 + 위임 설치 호출")
    ip.add_argument("--work-dir")
    ip.add_argument("--phase", choices=("overlay", "delegate", "all"), default="all")
    ip.add_argument("--dashboard", action="store_true")
    ip.add_argument("--autostart", action="store_true")
    ip.add_argument("--dry-run", action="store_true")
    ip.set_defaults(fn=cmd_install)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: install --phase overlay — manifest 복사·CLAUDE.md 블록 이식·mcp 병합·해시 기록 (창작 금지)"
```

---

### Task 10: install --phase delegate — 접합 조립 + 위임 호출 + 수다 클로드 plist

**Files:**
- Modify: `generator/harnessctl.py` — `parse_env`, `write_bridge_envs`, `build_chat_cmd`, `write_chat_plist`, `delegate`, `cmd_install` delegate phase 채움
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: Task 8 pair 산출물(`W/.env`), Task 9 overlay 산출물(`W/scripts/`), 위임 계약(Task 2·3·상류 install-autostart.sh), `find_tmux()`, `CHAT_PLIST_LABEL`, `CHAT_SESSION`
- Produces:
  - `parse_env(path: Path) -> dict`
  - `write_bridge_envs(work: Path) -> list[str]` — 브리지 clone에 `.env`(codex)·`.env.gemini`(agy) 조립(이미 있으면 보존 — 멱등), 키: `DISCORD_TOKEN`(W/.env의 CODEX/GEMINI_BOT_TOKEN), `ALLOWED_USER_IDS`(APPROVER_USER_ID), `CODEX_WORKDIR`(`W/chat`), `CHANNEL_IDS`·`NAME_TRIGGER_CHANNEL_IDS`(CHAT_CHANNEL_ID), `TRIGGER_NAME`(코덱스/제미나이), gemini는 추가로 `ENGINE=agy`, `DATA_DIR=data-gemini`, `AGY_BIN=$(which agy)`. 0600
  - `build_chat_cmd(work) -> str` / `write_chat_plist(work) -> list[str]` — `~/Library/LaunchAgents/com.discord-harness.chat-claude.plist`, ProgramArguments `[tmux, new-session, -d, -s, chat-claude, <CMD>]`(bot-restart.sh 파서 호환 모양 — folder-bot Global Constraints 승계), CMD = `/bin/zsh -lc 'cd <W>/chat; export PATH="…"; export DISCORD_STATE_DIR=<W>/chat/.discord-state; exec <W>/scripts/bot-up.sh -n chat-claude --remote-control chat-claude --channels plugin:discord@claude-plugins-official'`
  - `delegate(argv, cwd, dry, log_hint)` — dry면 `위임(dry-run): …` 출력만, 실패면 종료 코드 전파 + 로그 위치 안내(엔진이 대신 고치지 않음)
  - delegate phase 실행 순서: `write_bridge_envs` → 브리지 `scripts/install.sh` → (`--dashboard`) usage-coach `scripts/install.sh` → (`--autostart`) `W/scripts/install-autostart.sh` + `write_chat_plist`

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def _installed(tmp_path):
    """fetch → overlay → pair 까지 마친 작업 폴더를 준비한다."""
    base = fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    assert _overlay(tmp_path, work).returncode == 0
    _token_files(work)
    assert _pair(tmp_path, work).returncode == 0
    (tmp_path / "Library/LaunchAgents").mkdir(parents=True, exist_ok=True)
    return base, work

def test_delegate_dry_run_prints_commands_only(tmp_path):
    base, work = _installed(tmp_path)
    r = run(tmp_path, "install", "--work-dir", str(work), "--phase", "delegate",
            "--dashboard", "--autostart", "--dry-run")
    assert r.returncode == 0, r.stdout + r.stderr
    repos = tmp_path / ".local/share/discord-harness/repos"
    assert f"위임(dry-run): (cd {repos}/codex-discord)" in r.stdout
    assert "codex-discord/scripts/install.sh" in r.stdout
    assert "usage-coach/scripts/install.sh" in r.stdout
    assert "scripts/install-autostart.sh" in r.stdout
    assert not (tmp_path / "Library/LaunchAgents/com.discord-harness.chat-claude.plist").exists()

def test_delegate_assembles_bridge_envs(tmp_path):
    base, work = _installed(tmp_path)
    r = run(tmp_path, "install", "--work-dir", str(work), "--phase", "delegate", "--dry-run")
    assert r.returncode == 0, r.stdout + r.stderr
    bridge = tmp_path / ".local/share/discord-harness/repos/codex-discord"
    env = (bridge / ".env").read_text()
    assert "DISCORD_TOKEN=tok-codex" in env and "ALLOWED_USER_IDS=999" in env
    assert f"CODEX_WORKDIR={work}/chat" in env and "CHANNEL_IDS=222" in env
    assert "TRIGGER_NAME=코덱스" in env
    gem = (bridge / ".env.gemini").read_text()
    assert "DISCORD_TOKEN=tok-gemini" in gem and "ENGINE=agy" in gem
    assert "DATA_DIR=data-gemini" in gem and "TRIGGER_NAME=제미나이" in gem
    assert oct((bridge / ".env").stat().st_mode)[-3:] == "600"
    # 멱등 — 재실행해도 기존 .env 보존
    (bridge / ".env").write_text("DISCORD_TOKEN=user-edited\n")
    run(tmp_path, "install", "--work-dir", str(work), "--phase", "delegate", "--dry-run")
    assert (bridge / ".env").read_text() == "DISCORD_TOKEN=user-edited\n"

def test_delegate_real_run_writes_chat_plist(tmp_path):
    base, work = _installed(tmp_path)
    r = run(tmp_path, "install", "--work-dir", str(work), "--phase", "delegate", "--autostart")
    assert r.returncode == 0, r.stdout + r.stderr   # fixture 위임 스크립트 = echo stub
    p = tmp_path / "Library/LaunchAgents/com.discord-harness.chat-claude.plist"
    args = plistlib.loads(p.read_bytes())["ProgramArguments"]
    assert args[args.index("-s") + 1] == "chat-claude" and "new-session" in args
    cmd = args[-1]
    assert f"cd {work}/chat" in cmd
    assert f"DISCORD_STATE_DIR={work}/chat/.discord-state" in cmd
    assert "scripts/bot-up.sh" in cmd and "--channels plugin:discord@claude-plugins-official" in cmd
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → FAIL

- [ ] **Step 3: 구현**

```python
def parse_env(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out

def write_bridge_envs(work: Path) -> list[str]:
    if not (work / ".env").exists():
        sys.exit(f"오류: {work / '.env'} 없음 — pair 선행 필요(SKILL 7단계)")
    env = parse_env(work / ".env")
    chat = work / "chat"
    chat.mkdir(exist_ok=True)
    out = []
    plans = [(".env", env["CODEX_BOT_TOKEN"], "코덱스", []),
             (".env.gemini", env["GEMINI_BOT_TOKEN"], "제미나이",
              ["ENGINE=agy", "DATA_DIR=data-gemini",
               f"AGY_BIN={shutil.which('agy') or 'agy'}"])]
    for fname, token, trigger, extra in plans:
        p = bridge_repo() / fname
        if p.exists():
            continue  # 멱등 — 기존(사용자 수정 포함) 보존
        lines = [f"DISCORD_TOKEN={token}",
                 f"ALLOWED_USER_IDS={env['APPROVER_USER_ID']}",
                 f"CODEX_WORKDIR={chat}",
                 f"CHANNEL_IDS={env['CHAT_CHANNEL_ID']}",
                 f"NAME_TRIGGER_CHANNEL_IDS={env['CHAT_CHANNEL_ID']}",
                 f"TRIGGER_NAME={trigger}", *extra]
        p.write_text("\n".join(lines) + "\n")
        p.chmod(0o600)
        out.append(f"브리지 환경 조립: {p}")
    return out

def build_chat_cmd(work: Path) -> str:
    chat = work / "chat"
    path_esc = os.environ.get("PATH", "").replace("&", "&amp;")
    parts = [f"cd {chat}",
             f'export PATH="{path_esc}"',
             f"export DISCORD_STATE_DIR={chat}/.discord-state",
             f"exec {work}/scripts/bot-up.sh -n {CHAT_SESSION} --remote-control {CHAT_SESSION}"
             " --channels plugin:discord@claude-plugins-official"]
    return "/bin/zsh -lc '" + "; ".join(parts) + "'"

def chat_plist_path() -> Path:
    return home() / f"Library/LaunchAgents/{CHAT_PLIST_LABEL}.plist"

def write_chat_plist(work: Path) -> list[str]:
    p = chat_plist_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"Label": CHAT_PLIST_LABEL,
            "ProgramArguments": [find_tmux(), "new-session", "-d", "-s", CHAT_SESSION,
                                 build_chat_cmd(work)],
            "RunAtLoad": True}
    blob = plistlib.dumps(data)
    if p.exists() and p.read_bytes() == blob:
        return []
    p.write_bytes(blob)
    return [f"plist 생성: {p} (다음 부팅부터 수다 클로드 자동 기동)"]

def delegate(argv: list, cwd: Path, dry: bool, log_hint: str) -> None:
    line = " ".join(str(x) for x in argv)
    if dry:
        print(f"위임(dry-run): (cd {cwd}) {line}")
        return
    r = subprocess.run([str(x) for x in argv], cwd=cwd)
    if r.returncode != 0:
        sys.exit(f"오류: 위임 스크립트 실패(exit {r.returncode}) — {line}\n"
                 f"로그: {log_hint}\n다음 행동: 원인 해결 후 install 재실행(멱등)")
```

`cmd_install`의 delegate phase (Task 9의 `# delegate phase 는 Task 10 에서 구현` 자리를 교체):

```python
    if a.phase in ("delegate", "all"):
        for line in write_bridge_envs(work):
            print(line)
        delegate(["bash", bridge_repo() / "scripts/install.sh"], bridge_repo(),
                 a.dry_run, str(bridge_repo() / "logs"))
        if a.dashboard:
            delegate(["bash", coach_repo() / "scripts/install.sh"], coach_repo(),
                     a.dry_run, "~/.config/usage-coach/")
        if a.autostart:
            delegate(["bash", work / "scripts/install-autostart.sh"], work,
                     a.dry_run, "launchctl print gui/$(id -u)/" + ORCH_PLIST_LABEL)
            if a.dry_run:
                print(f"위임(dry-run): plist 생성 예정 — {chat_plist_path()}")
            else:
                for line in write_chat_plist(work):
                    print(line)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: install --phase delegate — 브리지 .env 조립·위임 3종 호출·수다 클로드 plist (dry-run 계약)"
```

---

### Task 11: verify — 봇 유형별 판정 소스 2종

**Files:**
- Modify: `generator/harnessctl.py` — `mcp_log_dir`, `judge_mcp`, `judge_bridge`, `cmd_verify` 추가
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: `resolve_work_dir`, `bridge_repo()`, `find_tmux()`, state
- Produces:
  - `mcp_log_dir(workdir: Path) -> Path` — `home()/"Library/Caches/claude-cli-nodejs"/<경로의 /·. → - 치환>/mcp-logs-plugin-discord-discord` (bot-up.sh `${PWD//[\/.]/-}` 와 동일 치환)
  - `judge_mcp(workdir) -> (level, msg)` — `*.jsonl`에서 `Successfully connected` → OK / `Connection failed` → FAIL / 없음 → WARN
  - `judge_bridge(logname) -> (level, msg)` — `logs/<logname>`에 `로그인:` → OK / 없음 → FAIL(파일 자체가 없으면 FAIL)
  - CLI `verify [--work-dir W] [--skip-webhook]` — 판정: 오케(W)·수다 클로드(W/chat) MCP / 코덱스(daemon.log)·제미나이(daemon-gemini.log, 브리지 `.env.gemini` 없으면 WARN 스킵) / 데몬 pid 생존(`data*/daemon.pid`, WARN) / tmux 세션 orchestrator·chat-claude(WARN) / plist 파일 존재(WARN) / 웹훅 시험 발사 1회(urllib POST, 실패 FAIL, `--skip-webhook`이면 생략 — 테스트 계약). FAIL 없으면 exit 0 + `steps["verify"]` 기록

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def _mcp_log(tmp_path, workdir, line):
    mangled = re.sub(r"[/.]", "-", str(workdir))
    d = tmp_path / "Library/Caches/claude-cli-nodejs" / mangled / "mcp-logs-plugin-discord-discord"
    d.mkdir(parents=True, exist_ok=True)
    (d / "2026-08-04.jsonl").write_text(json.dumps({"msg": line}) + "\n")

def test_verify_ok_with_fixture_logs(tmp_path):
    base, work = _installed(tmp_path)
    bridge = tmp_path / ".local/share/discord-harness/repos/codex-discord"
    run(tmp_path, "install", "--work-dir", str(work), "--phase", "delegate", "--dry-run")
    _mcp_log(tmp_path, work, "Successfully connected to Discord")
    _mcp_log(tmp_path, work / "chat", "Successfully connected to Discord")
    (bridge / "logs").mkdir(exist_ok=True)
    (bridge / "logs/daemon.log").write_text("로그인: codex#1 / 엔진 codex\n")
    (bridge / "logs/daemon-gemini.log").write_text("로그인: gem#1 / 엔진 agy\n")
    (bridge / "data").mkdir(exist_ok=True)
    (bridge / "data/daemon.pid").write_text(str(os.getpid()))
    r = run(tmp_path, "verify", "--work-dir", str(work), "--skip-webhook")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "[OK] 오케스트레이터" in r.stdout and "[OK] 수다 클로드" in r.stdout
    assert "[OK] 코덱스" in r.stdout and "[OK] 제미나이" in r.stdout

def test_verify_connection_failed_is_fail(tmp_path):
    base, work = _installed(tmp_path)
    _mcp_log(tmp_path, work, "Connection failed: invalid token")
    r = run(tmp_path, "verify", "--work-dir", str(work), "--skip-webhook")
    assert r.returncode == 1
    assert "[FAIL] 오케스트레이터" in r.stdout
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → FAIL

- [ ] **Step 3: 구현**

```python
def mcp_log_dir(workdir: Path) -> Path:
    mangled = re.sub(r"[/.]", "-", str(workdir))
    return home() / "Library/Caches/claude-cli-nodejs" / mangled / "mcp-logs-plugin-discord-discord"

def judge_mcp(workdir: Path):
    d = mcp_log_dir(workdir)
    files = sorted(d.glob("*.jsonl")) if d.is_dir() else []
    text = "".join(f.read_text(errors="ignore") for f in files)
    if "Successfully connected" in text:
        return "OK", "MCP 연결 성공"
    if "Connection failed" in text:
        return "FAIL", "MCP 연결 실패 — 토큰 오입력·인텐트 미설정·초대 누락 확인"
    return "WARN", f"판정 로그 없음(미기동?): {d}"

def judge_bridge(logname: str):
    p = bridge_repo() / "logs" / logname
    if p.exists() and "로그인:" in p.read_text(errors="ignore"):
        return "OK", f"브리지 로그인 확인({logname})"
    return "FAIL", f"브리지 로그인 없음 — {p} 확인"

def cmd_verify(a) -> None:
    work = resolve_work_dir(a)
    fails = 0
    def rep(level, msg):
        nonlocal fails
        if level == "FAIL":
            fails += 1
        print(f"[{level}] {msg}")
    for label, wd in (("오케스트레이터", work), ("수다 클로드", work / "chat")):
        lvl, msg = judge_mcp(wd)
        rep(lvl, f"{label}: {msg}")
    bridge_specs = [("코덱스", "daemon.log", "data/daemon.pid")]
    if (bridge_repo() / ".env.gemini").exists():
        bridge_specs.append(("제미나이", "daemon-gemini.log", "data-gemini/daemon.pid"))
    else:
        rep("WARN", "제미나이: 브리지 .env.gemini 없음 — 미구성으로 건너뜀")
    for label, logname, pidrel in bridge_specs:
        lvl, msg = judge_bridge(logname)
        rep(lvl, f"{label}: {msg}")
        pid_p = bridge_repo() / pidrel
        alive = False
        if pid_p.exists():
            try:
                os.kill(int(pid_p.read_text().split()[0]), 0)
                alive = True
            except (ValueError, ProcessLookupError, PermissionError):
                pass
        rep("OK" if alive else "WARN",
            f"{label} 데몬 {'생존' if alive else '죽음/미기동'}: {pid_p}")
    for sess in ("orchestrator", CHAT_SESSION):
        alive = subprocess.run([find_tmux(), "has-session", "-t", sess],
                               capture_output=True).returncode == 0
        rep("OK" if alive else "WARN", f"tmux 세션 {sess} {'생존' if alive else '없음'}")
    for label, p in ((ORCH_PLIST_LABEL, home() / f"Library/LaunchAgents/{ORCH_PLIST_LABEL}.plist"),
                     (CHAT_PLIST_LABEL, chat_plist_path())):
        rep("OK" if p.exists() else "WARN", f"plist {label}: {'있음' if p.exists() else '없음'}")
    if not a.skip_webhook:
        cfg = home() / ".config/usage-coach/discord.json"
        if not cfg.exists():
            rep("WARN", f"웹훅 설정 없음: {cfg}")
        else:
            import urllib.request
            url = json.loads(cfg.read_text()).get("webhook_url", "")
            try:
                req = urllib.request.Request(
                    url, data=json.dumps({"content": "harness-installer verify: 웹훅 OK"}).encode(),
                    headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10)
                rep("OK", "웹훅 시험 발사 성공")
            except Exception as e:
                rep("FAIL", f"웹훅 발사 실패: {e}")
    if not fails:
        st = load_state(); st["steps"]["verify"] = now(); save_state(st)
    sys.exit(1 if fails else 0)
```

main() 등록:

```python
    vp = sub.add_parser("verify", help="기동 후 연결 판정(판정 소스 2종, 읽기 전용)")
    vp.add_argument("--work-dir")
    vp.add_argument("--skip-webhook", action="store_true")
    vp.set_defaults(fn=cmd_verify)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: verify — MCP 로그·브리지 로그인 판정 소스 2종 + 데몬/tmux/plist/웹훅 점검"
```

---

### Task 12: doctor — 버전 호환 검사 + 위임 계약 방어

**Files:**
- Modify: `generator/harnessctl.py` — `version_tuple`, `installed_plugin_version`, `cmd_doctor` 추가
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: `pins()`, state, `run_git`, 위임 계약 파일 경로들, `load_manifest` 상수(직접 재사용하지 않고 존재·스키마만 검사)
- Produces:
  - `version_tuple(v: str) -> tuple` (숫자 3개 추출 비교)
  - `installed_plugin_version(name: str) -> str | None` — `~/.claude/plugins/cache/<name>/<name>/<버전>/` 중 최고 버전(실측 캐시 레이아웃)
  - CLI `doctor [--work-dir W]` — 읽기 전용, 항목별 `[OK]/[WARN]/[FAIL]`, FAIL 있으면 exit 1:
    1. **핀 대조**: state.repos[ref] ≠ pins.repos → WARN("설치기·부품 버전 어긋남"), ref 일치라도 현재 HEAD ≠ 기록 commit → WARN("임의 pull 감지"), fetch 기록 없음 → WARN
    2. **플러그인 버전**: 미설치 WARN / 설치버전 < pins 최소 WARN / 이상 OK
    3. **위임 계약 방어**: 브리지 install.sh·uninstall.sh, usage-coach install.sh·uninstall.sh, 하네스 install-autostart.sh — 존재+실행권한 확인(누락 WARN). manifest 존재(누락 WARN) + schema_version 일치(불일치 FAIL)
    4. **기존 축**: work_dir 있으면 페어링(.env)·plist 2종·tmux 세션 2종 확인(누락 WARN)

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def test_doctor_warns_on_pin_mismatch(tmp_path):
    fetched(tmp_path)
    sp = tmp_path / ".config/discord-harness/state.json"
    st = json.loads(sp.read_text())
    st["repos"]["usage-coach"]["ref"] = "v9.9.9"
    sp.write_text(json.dumps(st))
    r = run(tmp_path, "doctor")
    assert "[WARN]" in r.stdout and "usage-coach" in r.stdout and "v9.9.9" in r.stdout

def test_doctor_warns_on_missing_contract_file(tmp_path):
    fetched(tmp_path)
    (tmp_path / ".local/share/discord-harness/repos/usage-coach/scripts/uninstall.sh").unlink()
    r = run(tmp_path, "doctor")
    assert "[WARN]" in r.stdout and "uninstall.sh" in r.stdout

def test_doctor_fails_on_manifest_schema_mismatch(tmp_path):
    fetched(tmp_path)
    mp = tmp_path / ".local/share/discord-harness/repos/discord-multiagent/install/overlay-manifest.json"
    mf = json.loads(mp.read_text()); mf["schema_version"] = 99
    mp.write_text(json.dumps(mf))
    r = run(tmp_path, "doctor")
    assert r.returncode == 1 and "schema_version" in r.stdout

def test_doctor_plugin_version_check(tmp_path):
    fetched(tmp_path)
    old = tmp_path / ".claude/plugins/cache/folder-bot/folder-bot/0.0.1"
    old.mkdir(parents=True)
    r = run(tmp_path, "doctor")
    assert "folder-bot" in r.stdout and "[WARN]" in r.stdout
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → FAIL

- [ ] **Step 3: 구현**

```python
def version_tuple(v: str) -> tuple:
    nums = re.findall(r"\d+", v)
    return tuple(int(x) for x in nums[:3]) or (0,)

def installed_plugin_version(name: str):
    base = home() / ".claude/plugins/cache" / name / name
    if not base.is_dir():
        return None
    vers = [d.name for d in base.iterdir() if d.is_dir()]
    return max(vers, key=version_tuple) if vers else None

def cmd_doctor(a) -> None:
    fails = 0
    def rep(level, msg):
        nonlocal fails
        if level == "FAIL":
            fails += 1
        print(f"[{level}] {msg}")
    pn = pins()
    st = load_state()
    for name in REPO_NAMES:
        got = st.get("repos", {}).get(name)
        pin = pn["repos"][name]
        if not got:
            rep("WARN", f"{name}: fetch 기록 없음 — harnessctl.py fetch 필요")
            continue
        if got["ref"] != pin:
            rep("WARN", f"{name}: 설치 {got['ref']} ≠ 검증 조합 {pin} — 설치기·부품 버전 어긋남")
            continue
        cur = run_git(["rev-parse", "HEAD"], cwd=repos_dir() / name).stdout.strip()
        if cur and cur != got["commit"]:
            rep("WARN", f"{name}: HEAD가 기록과 다름(임의 pull?) — 검증 조합 이탈")
        else:
            rep("OK", f"{name}: {got['ref']}")
    for pname, _ in PLUGINS:
        v = installed_plugin_version(pname)
        need = pn["plugins"][pname]
        if v is None:
            rep("WARN", f"플러그인 {pname} 미설치 — harnessctl.py plugins 필요")
        elif version_tuple(v) < version_tuple(need):
            rep("WARN", f"플러그인 {pname} {v} < 호환 최소 {need}")
        else:
            rep("OK", f"플러그인 {pname} {v}")
    for p in (bridge_repo() / "scripts/install.sh", bridge_repo() / "scripts/uninstall.sh",
              coach_repo() / "scripts/install.sh", coach_repo() / "scripts/uninstall.sh",
              harness_repo() / "scripts/install-autostart.sh"):
        if not p.exists():
            rep("WARN", f"위임 계약 파일 없음: {p}")
        elif not os.access(p, os.X_OK):
            rep("WARN", f"위임 계약 실행권한 없음: {p}")
        else:
            rep("OK", f"위임 계약: {p.parent.parent.name}/{p.parent.name}/{p.name}")
    mp = harness_repo() / "install/overlay-manifest.json"
    if not mp.exists():
        rep("WARN", f"오버레이 manifest 없음: {mp}")
    else:
        sv = json.loads(mp.read_text()).get("schema_version")
        rep("OK" if sv == SCHEMA_VERSION else "FAIL",
            f"manifest schema_version {sv}" + ("" if sv == SCHEMA_VERSION else f" ≠ {SCHEMA_VERSION} — 설치기 업데이트 필요"))
    wd = getattr(a, "work_dir", None) or st.get("work_dir")
    if wd:
        work = Path(wd).expanduser()
        rep("OK" if (work / ".env").exists() else "WARN",
            f"페어링(.env): {'있음' if (work / '.env').exists() else '없음 — pair 필요'}")
        for label, p in ((ORCH_PLIST_LABEL, home() / f"Library/LaunchAgents/{ORCH_PLIST_LABEL}.plist"),
                         (CHAT_PLIST_LABEL, chat_plist_path())):
            rep("OK" if p.exists() else "WARN", f"plist {label}: {'있음' if p.exists() else '없음'}")
        for sess in ("orchestrator", CHAT_SESSION):
            alive = subprocess.run([find_tmux(), "has-session", "-t", sess],
                                   capture_output=True).returncode == 0
            rep("OK" if alive else "WARN", f"tmux 세션 {sess} {'생존' if alive else '없음'}")
    sys.exit(1 if fails else 0)
```

main() 등록:

```python
    dp = sub.add_parser("doctor", help="종합 점검 + 버전 호환 + 위임 계약 방어(읽기 전용)")
    dp.add_argument("--work-dir")
    dp.set_defaults(fn=cmd_doctor)
```

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: doctor — 핀 대조·플러그인 버전·위임 계약 방어·기존 축 점검 (읽기 전용)"
```

---

### Task 13: remove — 설치기가 만든 것만, diff 0

**Files:**
- Modify: `generator/harnessctl.py` — `cmd_remove` 추가
- Test: `tests/test_harnessctl.py` 추가

**Interfaces:**
- Consumes: state(`overlay` 해시·`mcp_added`·`work_dir`), `remove_claude_block`, `find_tmux`, 상류 uninstall 계약(Task 2·3), `chat_plist_path`
- Produces: CLI `remove [--work-dir W]` — 처리 순서(소스 저장소 삭제는 위임 호출 뒤):
  1. tmux 세션 `orchestrator`·`chat-claude` 종료 + plist 2종 파일 삭제(**bootout 미사용** — 엔진 소스 전체에 bootout 문자열 없음)
  2. 브리지·대시보드: 각 clone의 `scripts/uninstall.sh` 위임 호출(없으면 WARN + 수동 안내)
  3. 오버레이·시드 파일: 기록 해시와 대조 — 일치 시 삭제, 불일치(사용자 수정) 보존+WARN
  4. CLAUDE.md 마커 블록 제거(블록 외 원문 보존), `.mcp.json`은 `mcp_added` 키만 제거
  5. 소스 저장소 전체 삭제, state.json 삭제
  6. 보존(무접촉): `W/.env`, `.discord-state/`(2벌), `chat/`의 사용자 수정분, `tasks/`, SESSION.md, `~/.config/usage-coach/`

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def test_remove_diff_zero_and_preserves_user_data(tmp_path):
    fetched(tmp_path)
    (tmp_path / "Library/LaunchAgents").mkdir(parents=True, exist_ok=True)
    work2 = tmp_path / "work2"; work2.mkdir()
    orig_md = "# 내 규칙\n\n소중한 내용.\n"
    orig_mcp = json.dumps({"mcpServers": {"mine": {"command": "x"}}}, indent=2) + "\n"
    (work2 / "CLAUDE.md").write_text(orig_md)
    (work2 / ".mcp.json").write_text(orig_mcp)
    (work2 / "SESSION.md").write_text("세션\n")
    assert _overlay(tmp_path, work2).returncode == 0
    _token_files(work2)
    assert _pair(tmp_path, work2).returncode == 0
    r = run(tmp_path, "install", "--work-dir", str(work2), "--phase", "delegate", "--autostart")
    assert r.returncode == 0, r.stdout + r.stderr
    r = run(tmp_path, "remove", "--work-dir", str(work2))
    assert r.returncode == 0, r.stdout + r.stderr
    # diff 0: 설치 전 존재하던 파일은 원문 동일
    assert (work2 / "CLAUDE.md").read_text() == orig_md
    mcp = json.loads((work2 / ".mcp.json").read_text())
    assert "mine" in mcp["mcpServers"] and "codex" not in mcp["mcpServers"]
    assert (work2 / "SESSION.md").read_text() == "세션\n"
    # 설치기가 만든 것은 제거
    assert not (work2 / "scripts/bot-up.sh").exists()
    assert not (work2 / ".env.example").exists()
    assert not (tmp_path / "Library/LaunchAgents/com.discord-harness.chat-claude.plist").exists()
    assert not (tmp_path / ".local/share/discord-harness/repos").exists()
    assert not (tmp_path / ".config/discord-harness/state.json").exists()
    # 사용자 데이터·비밀 보존
    assert (work2 / ".env").exists()
    assert (work2 / ".discord-state/.env").exists()
    assert (work2 / "chat/.discord-state/.env").exists()

def test_remove_preserves_user_modified_overlay(tmp_path):
    base, work = _installed(tmp_path)
    (work / "scripts/post-as.sh").write_text("#!/bin/bash\n# 사용자 수정\n")
    r = run(tmp_path, "remove", "--work-dir", str(work))
    assert r.returncode == 0
    assert (work / "scripts/post-as.sh").exists()
    assert "[WARN]" in r.stdout and "post-as.sh" in r.stdout

def test_engine_source_never_mentions_bootout():
    assert "bootout" not in HARNESSCTL.read_text()
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest tests/ -v` → FAIL

- [ ] **Step 3: 구현**

```python
def cmd_remove(a) -> None:
    st = load_state()
    work = resolve_work_dir(a)
    tmux = find_tmux()
    for sess in ("orchestrator", CHAT_SESSION):
        subprocess.run([tmux, "kill-session", "-t", sess], capture_output=True)
    for p in (home() / f"Library/LaunchAgents/{ORCH_PLIST_LABEL}.plist", chat_plist_path()):
        if p.exists():
            p.unlink()
            print(f"plist 제거: {p}")
    for script, cwd in ((bridge_repo() / "scripts/uninstall.sh", bridge_repo()),
                        (coach_repo() / "scripts/uninstall.sh", coach_repo())):
        if script.exists():
            subprocess.run(["bash", str(script)], cwd=cwd)
        else:
            print(f"[WARN] 제거 스크립트 없음(수동 확인 필요): {script}")
    for rel, saved in sorted(st.get("overlay", {}).items()):
        p = work / rel
        if not p.exists():
            continue
        if sha256(p) == saved:
            p.unlink()
            print(f"제거: {p}")
        else:
            print(f"[WARN] 사용자 수정 감지 — 보존: {p}")
    for line in remove_claude_block(work / "CLAUDE.md"):
        print(line)
    mcp_path = work / ".mcp.json"
    if st.get("mcp_added") and mcp_path.exists():
        cur = json.loads(mcp_path.read_text())
        for k in st["mcp_added"]:
            cur.get("mcpServers", {}).pop(k, None)
        mcp_path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
        print(f".mcp.json 항목 제거: {st['mcp_added']}")
    if repos_dir().exists():
        shutil.rmtree(repos_dir())
        print(f"소스 저장소 제거: {repos_dir()}")
    if state_path().exists():
        state_path().unlink()
    print("제거 완료 — 보존: .env·.discord-state·chat/(사용자 수정분)·tasks/·SESSION.md·~/.config/usage-coach/")
```

main() 등록:

```python
    xp = sub.add_parser("remove", help="설치기가 만든 것만 제거(diff 0, 사용자 데이터 보존)")
    xp.add_argument("--work-dir")
    xp.set_defaults(fn=cmd_remove)
```

주의: `.mcp.json`이 오버레이 **복사**로 생성된 경우(설치 전 부재)는 3단계 해시 대조가 파일째 지우고, **병합**이었던 경우는 4단계가 키만 걷어낸다 — 두 경로가 겹치지 않음(복사 시 `overlay`에 기록, 병합 시 `mcp_added`에만 기록, Task 9 구현 참조).

- [ ] **Step 4: 통과 확인 + 커밋**

```bash
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: remove — 해시 대조 diff 0·사용자 데이터 보존·bootout 불사용(소스 정적 검증 포함)"
```

---

### Task 14: SKILL.md (9단계 오케스트레이션) + README

**Files:**
- Create: `plugins/harness-installer/skills/configure-harness/SKILL.md`
- Modify: `README.md` — 본문 작성

**Interfaces:**
- Consumes: harnessctl CLI 전체(Task 5~13의 서브커맨드·플래그를 정확히 그 이름으로)
- Produces: 스킬 트리거 문구("디스코드 하네스 설치해줘", "멀티에이전트 하네스 설치", "/configure-harness", "하네스 제거해줘", "하네스 점검해줘")

- [ ] **Step 1: SKILL.md 작성** — frontmatter(name: configure-harness, description: 트리거 문구 포함) + 본문에 다음 구조를 그대로 반영 (folder-bot SKILL.md 전례 승계: 번호 안내·완료 대기·기본값 질주 금지·토큰 채팅 금지):

상단 고정 원칙:
- **비파괴**: SESSION.md는 절대 만들거나 고치지 않는다. 작업 폴더 CLAUDE.md는 엔진이 마커 블록만 추가·제거한다.
- **토큰·웹훅 URL은 채팅으로 받지 않는다** — `pbpaste > .bot-token-<역할> && chmod 600 .bot-token-<역할>` 파일 수령만. 스킬은 토큰 값을 화면에 다시 출력하지 않는다.
- **엔진 출력은 그대로 보여준다**. 실패하면 그 단계에서 멈추고 엔진이 안내한 다음 행동·수동 폴백을 전달한다(재량으로 대신 고치지 않는다).
- AskUserQuestion이 없는 환경(코덱스 등)에서는 같은 질문을 **채팅으로 물어 답을 받는다**. 묻지 않고 기본값으로 질주하지 말 것(2026-08-02 코덱스 실측 편차).

9단계 절차 (`ENGINE="<이 스킬 폴더>/generator/harnessctl.py"`):
1. **preflight**: `python3 $ENGINE preflight` — FAIL 있으면 항목별 설치 방법 안내 후 중단.
2. **설치 계획 질문(한 번에)**: 설치 루트(기본 `~/discord-harness` — 작업 폴더가 됨) / 봇 4개 표시 이름(기본: 오케스트레이터·클로드·코덱스·제미나이 — 포탈 앱 이름에 사용) / 대시보드 설치 여부(기본 예) / 부팅 자동 기동 여부(기본 예).
3. **디스코드 포탈 수동 단계** (순서대로 안내, 사용자가 끝냈다고 할 때까지 대기):
   - 서버 1개 + 채널 2개(작업·수다) 생성, 개발자 모드로 채널 ID 2개·본인 사용자 ID 복사(채팅으로 받기 — ID는 비밀 아님)
   - https://discord.com/developers/applications 에서 봇 앱 4개 생성(2단계에서 정한 이름), 각각 Bot 탭 토큰 발급 + **MESSAGE CONTENT INTENT** 켜기
   - OAuth2 URL Generator(scope `bot`, 권한 View Channels/Send Messages/Read Message History/Embed Links/Attach Files/Create Public Threads/Send Messages in Threads)로 초대 — 오케 봇은 작업 채널, 나머지 셋은 작업+수다 채널
   - 토큰 4개는 각각 복사 직후 작업 폴더에서 `pbpaste > .bot-token-orch` (·claude·codex·gemini) + `chmod 600`
   - (대시보드 예이면) 대시보드용 채널 웹훅 URL 생성 후 `pbpaste > .webhook-url`
4. **fetch**: `python3 $ENGINE fetch` — 소스 저장소에 3레포 clone(검증 조합 핀).
5. **plugins**: `python3 $ENGINE plugins` (코덱스 호스트면 `--host codex`) — 실패 항목은 출력된 수동 폴백을 안내하고 사용자가 마치면 재실행.
6. **멀티에이전트 시스템 설치 + 디스코드 층**: multi-agent-starter의 `configure-multiagent` 스킬을 설치 루트에 대해 실행(flavor claude) → `python3 $ENGINE install --work-dir <루트> --phase overlay`.
7. **pair**: `python3 $ENGINE pair --work-dir <루트> --work-channel-id … --chat-channel-id … --approver-user-id …` (+대시보드면 `--webhook-url-file <루트>/.webhook-url`) — 토큰 파일 4개가 삭제됐는지 엔진 출력으로 확인.
8. **install**: `python3 $ENGINE install --work-dir <루트> --phase delegate` (+2단계 답에 따라 `--dashboard` `--autostart`).
9. **verify + 마무리**: `python3 $ENGINE verify --work-dir <루트>` 결과 보고 → 마무리 안내: 디스코드 작업 채널에서 오케 봇에게, 수다 채널에서 클로드 봇에게 인사해 실제 응답 확인 요청(자동화 불가) / 재시작 리추얼("세션 마감하고 재시작해" → `scripts/bot-restart.sh <세션>` → "이어서하자") / 폴더 봇 추가는 선택 — folder-bot 스킬("이 폴더를 디스코드 봇으로 만들어줘") 안내 / 상시 점검 `python3 $ENGINE doctor` / 제거 `python3 $ENGINE remove`.

제거·점검 절(본문 하단): "하네스 제거해줘" → `remove` 실행(보존 목록 안내), "하네스 점검해줘" → `doctor` 실행·항목 해설.

- [ ] **Step 2: README.md 본문** — 사용자 관점: 설치 명령 2줄(`claude` 안에서 `/plugin marketplace add netwaif/discord-harness-installer` → harness-installer 설치), "디스코드 하네스 설치해줘" 한마디, 수동은 포탈 단계뿐, 검증 조합 핀(pins.json) 설명, 매뉴얼 v2.2 16장을 대체한다는 위치 선언, macOS 전용 명시.

- [ ] **Step 3: 정합성 검사**

Run: `grep -oE 'harnessctl\.py [a-z]+' plugins/harness-installer/skills/configure-harness/SKILL.md | sort -u`
Expected: `harnessctl.py doctor` / `fetch` / `install` / `pair` / `plugins` / `preflight` / `remove` / `verify` 만 등장(8개 외 오타 없음)

Run: `python3 -m pytest tests/ -v`
Expected: 전부 PASS (회귀 없음)

- [ ] **Step 4: 커밋**

```bash
git add -A && git commit -m "docs: configure-harness SKILL.md 9단계 오케스트레이션 + README"
```

---

### Task 15: 릴리즈 게이트 — E2E 2종 + pins.json 확정

**Files:**
- Modify: `plugins/harness-installer/skills/configure-harness/generator/pins.json` — 실태그·실버전으로 갱신
- Modify: 없음(그 외 검증 태스크) — 발견된 결함은 해당 태스크 파일로 돌아가 수정

**Interfaces:**
- Consumes: 플러그인 전체, 상류 3레포 커밋(Task 2~4), 별도 macOS 사용자 계정 + 테스트 디스코드 서버 + 테스트 봇 앱 4개(스펙 E2E 환경 — 1회 구축 후 재사용, 프로덕션 계정에서는 돌리지 않는다)

- [ ] **Step 1: 자동 테스트 전체 통과 확인** — 이 레포 `python3 -m pytest tests/ -v`(diff 0 포함) + usage-coach `pytest tests/test_install_scripts.py` + codex-discord `bash test/uninstall.test.sh` + 하네스 `bash test/manifest.test.sh` 전부 PASS.
- [ ] **Step 2: 상류 푸시 + 태깅(사용자 게이트)** — AskUserQuestion으로 확인 후: 3레포에 태그(`discord-multiagent` `codex-discord` `usage-coach` 각 `vX.Y.Z`) 생성·푸시. `discord-multiagent`는 refspec 주의(작업 브랜치 release-snapshot → 원격 main, 로컬 main 브랜치 없음).
- [ ] **Step 3: pins.json 갱신** — Step 2의 실태그 3개 + starter·folder-bot 현행 버전(3.5.0·0.1.0 또는 그 시점 최신)으로 교체, 커밋.
- [ ] **Step 4: 클로드 4봇 E2E(사용자 게이트)** — 별도 macOS 계정에서: 마켓플레이스 add → configure-harness 전체 흐름(포탈 단계는 테스트 서버·테스트 봇 4개) → verify 통과 → 디스코드에서 4봇 실제 응답 확인(작업 채널 오케 지시 1회, 수다 채널 클로드·코덱스·제미나이 호명 1회씩) → `remove` 실행 → 작업 폴더 diff 0 확인(`git status` 또는 사전 백업 대비 diff).
- [ ] **Step 5: 코덱스 스모크 E2E(사용자 게이트)** — 같은 계정에서 codex 호스트로: `codex plugin marketplace add` 경로 설치 → SKILL 절차 기동 → 봇 응답 확인 수준(심층 검증은 비범위).
- [ ] **Step 6: 결과 기록 + 릴리즈 커밋**

```bash
git add -A && git commit -m "release: v0.1.0 — 릴리즈 게이트 통과(자동 테스트·클로드 4봇 E2E·코덱스 스모크), pins 확정"
```

- [ ] **Step 7: 후속 작업 확인** — SESSION.md의 "MultiAgent 레포 custom registry 별도 스펙 착수"(긱님 약속, 2026-08-03)가 다음 단계 목록에 남아 있는지 확인(이 플랜이 지우지 않았는지). 남아 있으면 그대로 종료.

## Self-Review 결과 (플랜 작성 시 수행)

- **스펙 커버리지**: 확정 결정 6건 → 1(마켓플레이스 통합·직접 실행·폴백) T1·T7, 버전 호환 T12 / 2(git clone+핀) T6 / 3(코덱스 호환+스모크 게이트) T7 `--host`·T14·T15 / 4(긱님 분리) T15 Step 7 + 비범위 유지 / 5(A안 위임) T2·T3·T10·T12 / 6(clone=소스 저장소+오버레이) T6·T9. 서브커맨드 8개 전부 태스크 보유. 상류 선행 3건(usage-coach install·manifest·제거 경로 계약) T2~T4. 에러 처리(멱등·비-0+다음 행동·위임 실패 전파·--force) 각 태스크 구현에 반영. remove 표 전 항목 T13(플러그인 2종·`~/.local/bin`은 엔진이 만들지 않으므로 자연 보존). 테스트 전략의 계약 2종(URL 오버라이드·dry-run) T6·T10. 릴리즈 게이트 4항목 T15.
- **잔여 리스크(구현 중 확인)**: ① fixture 브리지 `install.sh`가 stub이므로 실제 브리지 install.sh의 `.env` 필수 키 검증은 E2E에서만 잡힌다(T15 Step 4). ② `TRIGGER_NAME`·`NAME_TRIGGER_CHANNEL_IDS` 값은 프로덕션 실측(.env.gemini) 기준 — 브리지 README와 어긋나면 T10에서 정정. ③ `fetch --latest` 후 재-pin 시나리오(detached HEAD 복귀)는 T6 구현이 checkout으로 처리하나 테스트 미포함 — E2E 전 수동 확인.

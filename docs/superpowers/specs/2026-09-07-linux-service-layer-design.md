# 디스코드 하네스 리눅스 서비스 층 설계 (launchd → systemd 사용자 유닛)

날짜 2026-09-07. 배경: agentlayer 저장소 `docs/linux-wsl2-verification.md`(1차) — 설치기 preflight가 macOS만 허용하고 정본 3레포가 봇 자동 기동을 launchd plist로 한다.

## 목표
리눅스(VPS Ubuntu, WSL2 Ubuntu)에서 `디스코드 하네스 설치해줘` 흐름이 끝까지 돌고, 봇 4개·브리지·대시보드가 systemd 사용자 유닛으로 기동·재기동·제거된다. macOS 동작은 바이트 단위로 불변.

## 사용 환경 판단(사용자 승인 2026-09-07)
- **VPS**: 설치 뒤 손 안 댐. `loginctl enable-linger`로 부팅 자동 기동. 맥과 같은 경험.
- **WSL2**: 우분투가 켜져 있는 동안만 봇이 산다(터미널 하나 열어 두기). systemd가 꺼져 있으면 설치기가 `/etc/wsl.conf` `[boot] systemd=true` + `wsl --shutdown` 안내 후 멈춘다. 매뉴얼에 "하네스는 VPS 권장, WSL2는 터미널 열어 두기" 명시.

## 유닛 대응표
| launchd Label | systemd 사용자 유닛 | 형태 |
|---|---|---|
| com.discord-multiagent.orchestrator | `discord-multiagent-orchestrator.service` | oneshot+RemainAfterExit, ExecStart=tmux new-session -d -s orchestrator "<CMD>", ExecStop=tmux kill-session, KillMode=process |
| com.discord-harness.chat-claude | `discord-harness-chat-claude.service` | 위와 동형(세션 chat-claude), harnessctl이 생성 |
| com.codex-discord.daemon | `codex-discord-daemon.service` | simple, node --env-file=.env src/index.mjs, Restart=always |
| com.codex-discord.gemini | `codex-discord-gemini.service` | simple, .env.gemini |
| com.codex-discord.tui | `codex-discord-tui.service` | oneshot+RemainAfterExit, bash scripts/tui-up.sh |
| com.usage-coach.dashboard | `usage-coach-dashboard.service`+`.timer` | oneshot + OnBootSec=1min/OnUnitActiveSec=5min |

공통: `~/.config/systemd/user/`, `Environment=PATH=<설치 시점 PATH>`, `WorkingDirectory`, 로그는 `StandardOutput=append:<repo>/logs/*.log`. tmux 세션 유닛은 `KillMode=process`(공유 tmux 서버를 죽이지 않기 위해 — 다른 봇 세션 보호). 각 tmux 유닛 옆에 `<unit>.tmux-cmd` 사이드카(세션 명령 원문) — bot-restart.sh가 plist 대신 이것을 읽는다.

## 스크립트 분기 규칙
- 각 정본 스크립트는 자기 안에서 `os_name()`(= `${HARNESS_OS:-$(uname -s)}`, 테스트 override)으로 Darwin/Linux 분기. 공용 라이브러리 없음(정본은 각 레포 자립).
- `DRY_RUN=1` 계약 유지: 파일만 쓰고 systemctl/launchctl 무접촉. 테스트는 `HARNESS_OS=Linux DRY_RUN=1 HOME=<tmp>`로 유닛 생성·제거를 검증.
- systemctl 호출: `daemon-reload` → `enable --now <unit>`(타이머는 .timer) → `loginctl enable-linger`(실패 무시). 제거: `disable --now`(무시) → 유닛 파일 삭제 → `daemon-reload`.
- harnessctl: preflight `sys.platform in ("darwin","linux")`; 리눅스면 `systemctl --user is-system-running` 실패 시 FAIL(+wsl.conf 안내), `/proc/version`에 microsoft면 WSL2 안내 한 줄(WARN 아님, 정보). `write_chat_plist` → OS별 `write_chat_unit`. doctor/verify/remove의 plist 경로 → `service_file(label)`이 OS별 경로 반환. `find_tmux` 힌트 OS별. delegate 로그 힌트 OS별.
- 토큰 파일 저장 안내(SKILL.md): macOS `pbpaste`, WSL2 `powershell.exe -c Get-Clipboard | tr -d '\r' > 파일`, 리눅스 데스크톱 `xclip -o`/`wl-paste`, VPS(ssh)는 `cat > 파일` 후 붙여넣기+Ctrl-D.
- claude MCP 로그 경로: macOS `~/Library/Caches/claude-cli-nodejs`, 리눅스 `~/.cache/claude-cli-nodejs`(bot-restart.sh·harnessctl judge_mcp).

## 배포
정본 3레포 패치 태그(discord-multiagent v0.1.2, codex-discord v0.1.7, usage-coach v0.1.3) → 설치기 pins.json 갱신, plugin.json 0.1.15, SKILL.md 리눅스 절. 매뉴얼(discord-multiagent-manual) 2장 "리눅스·윈도우 미검증" 문구는 검증 뒤 별도.

## 검증
1. 각 레포 기존 테스트 + 리눅스 분기 테스트(맥에서 HARNESS_OS=Linux로 실행).
2. VM(Ubuntu 24.04, systemd --user running): `harnessctl preflight/fetch(새 핀)/plugins/pair(가짜 토큰)/install --autostart --dashboard` → 유닛 6개 생성·active, tmux 세션 orchestrator·chat-claude 생존, node 데몬이 토큰 오류로 재시작 루프(Restart=always 증명), `remove`로 전부 제거. 실제 디스코드 연결은 사용자 VPS에서.

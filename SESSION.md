# SESSION — 세션 이어가기 기록

<!-- 이 파일은 다음 세션(기억 0)이 처음 읽는 유일한 문서다.
     섹션 5개는 고치거나 빼지 말 것. 갱신 규칙은 섹션마다 주석으로 표시. -->

## 목표
<!-- 이 폴더에서 하는 일. 거의 고정 — 바뀔 때만 명시적으로 수정 -->

통합 설치기 플러그인(v3): configure-harness 스킬 + harnessctl.py 결정적 엔진으로
하네스·브리지·대시보드 설치 전 과정을 플러그인 하나에. 훅: "매뉴얼 16장이 스킬
하나가 됐습니다". 착수 배경은 `시작-브리프.md`.

## 현재 상태
<!-- 덮어쓰기. 항상 짧게 — 지금 어디까지 왔는지 스냅샷만 -->

Task 15 릴리즈 게이트 — 3차 촬영 실패 후 결함 대량 발견·정본 수정 완료(8/5 종일).
설치기 0.1.11(4a6a6ac, 테스트 42개) / pins: discord-multiagent v0.1.1 ·
codex-discord v0.1.4 · usage-coach v0.1.2 · folder-bot 최소 0.1.1.
전 게이트 통과: 설치 9단계 · verify 13항목(프로세스·TUI·롤아웃 판정 포함) ·
실응답 4종 · 대시보드 카드(모델·% 포함) · 재시작 리추얼(하네스+folder-bot) ·
folder-bot E2E. 남은 것 = §3.9 기준선 초기화 → 재촬영(내일) → Step 6·7.
게이트 문서 정본: `/Users/Shared/harness-e2e-ct-reply-2026-08-05.md` (§3.5~3.17,
회신 색인 겸용) + checklist 최신판.

## 다음 단계
<!-- 덮어쓰기. 첫 항목 = 다음 세션이 바로 집어들 일 -->

1. (내일) 재촬영 — 컨트롤 세션에 ct-reply §3.9 초기화 지시(folder-bot 잔재
   ~/folder-bot-e2e·foldertest plist·bots.json 항목 + 구버전 플러그인 캐시 포함)
   → 자체 점검 보고 → 촬영. 대본 기준: 설치기 0.1.11 / 핀 4종(현재 상태 참조) /
   verify --wait 600 / 9단계 기동 전 claude mcp list 예열 / 대시보드 확인 전
   봇에 말 걸기 / 첫 기동 MCP 실패 시 폴백(재기동 1회→예열 복구)은 끊지 말고 촬영.
   촬영 전 머신 정비 1줄(사용자 실행 여부 미확인): sudo chmod -R g-w,o-w
   /usr/local/share/zsh — compinit insecure 경고 제거(터미널 화면 정리).
2. 통과 시 Step 6(release 커밋+푸시 — 기준은 0.1.11) + Step 7(아래 긱님 항목 잔존 확인)
3. Claude Code 본체 이슈 보고(#9 계열, 재료 확보됨): discord MCP 첫 spawn이
   handshake 전 사망 시 로그·재시도 없음 — 8/5 아침 하네스(09:33~09:51 전패,
   10:20 이후 전승) + 신규 폴더(23:12·23:24 실패→3수 성공, 예열 무효 사례).
   상세: diag-reply·statedump 문서군.
4. folder-bot 0.1.2 이월: ①botctl 토큰 파일 직접 삭제(평문 잔존 — 보안 우선)
   ②스킬에 MCP 실패 폴백 절 ③doctor에 MCP 연결 판정 ④eams 무조건 주입 여부
   + 미신뢰 폴더 재현 실험 (ct-reply §3.17)
5. 차기 이월분 기록 유지: #18/#19/#20/#21/#25(remove 품질)·#16(brew prefix 검사)·
   bot-up 락 240s 증폭(상류)·"수다 봇 폴더 하위 분리"는 d10e6f9로 해소됨
6. **[약속] MultiAgent 레포 custom registry 별도 스펙 착수** — 긱님(geek7942) 제안, "함께 검토하겠다" 공개 답변(2026-08-03). 1단계(등록부 병합: 원본+`_local`, update 보존)만 우선. 잊히면 안 됨.

## 결정 기록
<!-- 누적. 삭제 금지. 형식: - YYYY-MM-DD 한 줄 -->

- 2026-08-04 스펙 확정: 마켓플레이스 통합(plugins 직접 실행+수동 폴백, doctor 버전 호환) / git clone+핀(pins.json) / Claude 주력+코덱스 스모크 E2E 게이트 / 긱님 건 별도 스펙 분리 / A안 위임 오케스트레이터 / clone=소스 저장소+오버레이(근거: 즉흥 구현 편차를 정본 복사로 대체) / verify 판정 소스 2종 / remove 사용자 데이터 보존·diff 0 한정·bootout 금지 / E2E는 별도 macOS 계정+테스트 서버
- 2026-08-04 번들·혼합 수급 기각(정본 이중화·오프라인 비시나리오), B안(자체 구현 엔진) 기각(정본 이중화 재발)
- 2026-08-04 스펙 최종 승인(사용자 확정, 컨트롤타워 교차 검수 조건·정정 전원 반영 확인). 구현 플랜은 다음 세션부터(브리프 "첫 세션은 스펙까지만" 원칙)
- 2026-08-04 플랜에서 확정한 설계 2건: ①오버레이 manifest 경로 = 하네스 `install/overlay-manifest.json` ②수다 클로드 기동 주체 = 엔진 직접(`<루트>/chat/` 전용 폴더 + 전용 `.discord-state` + plist `com.discord-harness.chat-claude` — 전역 `~/.claude/channels/discord/` 의존 제거, 수다 채널 requireMention true)
- 2026-08-04 상류 선행 작업 2건→3건 확정(조사 결과 브리지·usage-coach·하네스 autostart 모두 제거 경로 부재): usage-coach install/uninstall.sh, codex-discord uninstall.sh(tui는 bootout 금지 — tmux job), 하네스 manifest
- 2026-08-04 SDD 실행(구현자 Haiku 전사 + 리뷰어 Sonnet + 최종 리뷰 Fable): Task 1~14 리뷰 클린 완료. 최종 리뷰 I-1 해소책으로 manifest `merge:"append-lines"` 타입 신설(하네스 `install/gitignore-discord`→작업 폴더 `.gitignore` 줄 추가, state.lines_added 기록, remove 역적용으로 diff 0)
- 2026-08-04 사고 기록: Task 6 구현자가 SESSION.md 무단 수정(긱님 약속 항목 삭제)→복원 커밋 4546dc3. 이후 디스패치에 "SESSION.md 무접촉·git add 경로 명시" 상시 제약
- 2026-08-04 릴리즈 게이트 전 accepted minors(선택 정리 대상): verify MCP 로그 신선도 미필터(플랜 명시 구현), .mcp.json 재직렬화 포맷 한정, doctor 전제 도구 축은 preflight 대체, tests 미사용 import pytest
- 2026-08-04 Step 2·3 완료: 3레포 v0.1.0 태깅·푸시(discord-multiagent는 release-snapshot:main), pins 확정 d339d6d. 설치기 레포 GitHub 공개(gh repo create, public). E2E 환경=harness-test 계정(비관리자, node·bun·codex·agy는 ~/.local HOME 로컬)
- 2026-08-04 1차 E2E 실패(촬영 폐기): 차단 6건(#14 bun preflight, #13/#7 권한 사전 승인, #27 state 선삭제, #3 reload-plugins, #17 웹훅 UA) 전부 수정 결정 + 기준선 A안(+플러그인 제거 보강). remove 판정 기준을 "harnessctl 소유분 diff 0"로 교체(문서 모순 해소)
- 2026-08-05 게이트 수정 반영 d8a3216 + usage-coach v0.1.1(대시보드 plist PATH 주입 — launchd 기본 PATH엔 codexbar 없음)
- 2026-08-05 2차 실측 4건 수정 a95bf31: ①코덱스 TUI 모드 채택(TUI_PANE=codex-live:0.0 — 플랜이 .env.gemini 실측만 기준 삼아 생긴 편차 정정) ②브리지 역할 멘션 인식(codex-discord v0.1.1 — @자동완성이 통합 역할을 고르면 무시되던 것) ③pair가 대시보드 bridges/claude_bots config 주입(discord_dash 기본값=저자 프로덕션 경로) ④verify MCP 신선도 판정(낡은 성공 로그 합격 오판 → since 이후·최신 파일만, 미기동 FAIL+bot-restart 폴백). 오케 MCP 미기동 근본 원인은 Claude Code 내부 경합 추정 — 검출·복구로 대응(설치기 범위 밖)
- 2026-08-05 차기 이월 확정: #18(remove --dry-run)·#19(bootout 비대칭)·#20(보존 문구 모순)·#21/#25(빈 디렉터리)·#16(brew prefix 쓰기 권한)·#9(Claude Code 본체 후보)
- 2026-08-05 (3차 게이트, 종일) 결함 대량 수정 — verify 판정 강화 3종(성공 로그+프로세스 실존 게이트 / tmux pane 내 claude 판정 / --wait 폴링, 8ad8b1a)·코덱스 TUI 판정+롤아웃 연계 판정 신설(b0645cb·c36e7a1)·버전 범프 정책 채택(동일 버전이면 /plugin update가 캐시 재복사 건너뜀 — 캐시 전달 커밋은 반드시 범프)
- 2026-08-05 브리지 작업 폴더 봇별 분리(d10e6f9) — chat/ 공유는 정본 편차·"chat/=수다 클로드 전용" 결정 위반이었음. codex-discord-workspace·gemini-discord-workspace로 정정
- 2026-08-05 코덱스 결함 4건 상류 수정: ①가드 pane_current_command→프로세스 트리 판정(npm node 런처 오탐, v0.1.2) ②tui-up 셸 타이핑→직접 실행(compinit 첫 글자 소실 2/2 재현, v0.1.2) ③세션 검출원 화면 UUID→롤아웃 session_meta cwd(v0.146.0 무표시, v0.1.3) ④readSessionMeta 4KB 고정 읽기→개행까지(첫 줄 실측 18,450B, v0.1.4 — CT 자기 결함)
- 2026-08-05 대시보드 클로드 카드 데이터원 정본화 — statusline 스냅샷 기록자가 저자 로컬 사설 스크립트였음 → usage-coach v0.1.2 scripts/statusline-command.sh(jq→python3) + 설치기가 봇 settings.local.json에 statusLine 주입(0.1.7)
- 2026-08-05 무인 권한 모드 = bot-up 세션 플래그 --permission-mode auto로 확정(discord-multiagent v0.1.1·folder-bot 0.1.1) — 프로젝트 settings defaultMode는 무효 실측(user 스코프 전용)이라 0.1.8 주입 철회(0.1.9). 근거: 프로덕션 무인 동작의 실체가 저자 전역 defaultMode auto였음
- 2026-08-05 MCP 첫 spawn 무로그·무재시도 실패 = Claude Code 본체 결함으로 잠정 확정(신규 폴더 재현 + 예열 무효 사례) — 검출·폴백으로 대응, 사용자 수용. 예열 절 문구 "보장 아님" 정정(0.1.11)
- 2026-08-05 folder-bot E2E를 게이트에 편입(사용자 지시 — 실사용 핵심 워크플로우) → 통과(무인 모드 실증 포함). 후속 3건+eams 실험은 folder-bot 0.1.2 이월
- 2026-08-05 분류기 차단 3회(권한 자동화 주제 커밋·편집) — 사용자 승인 후 중립 메시지/사용자 cp로 처리. bot-up-fixed.sh 전달 관례: /Users/Shared/ 경유

## 파일 흔적
<!-- 누적. 만든/고친 파일의 경로를 그대로 적는다. "설정 파일 고침" 같은 산문 금지 -->
<!-- 형식: - `경로` 무엇을 (함수명·핵심 식별자 포함) -->

- `docs/superpowers/specs/2026-08-04-harness-installer-design.md` 설계 스펙 (harnessctl.py 서브커맨드 8개: preflight/fetch/plugins/pair/install/verify/doctor/remove, pins.json, 오버레이 계약, 릴리즈 게이트)
- `SESSION.md` 최초 작성 (템플릿 복사 후 채움)
- `docs/superpowers/plans/2026-08-04-harness-installer.md` 구현 플랜 (Task 15개 TDD, Global Constraints, folder-bot 전례 포맷)
- `plugins/harness-installer/skills/configure-harness/generator/harnessctl.py` 결정적 엔진 (home()/load_state()/save_state()/pins()/repo_url(HARNESS_REPO_BASE 오버라이드)/apply_overlay(append-lines·json-mcp-servers 병합)/write_bridge_envs/write_chat_plist/judge_mcp/judge_bridge/cmd_preflight~cmd_remove)
- `plugins/harness-installer/skills/configure-harness/generator/pins.json` 검증 조합 핀 (repos 3종 `v0.0.0-pre` — Task 15에서 실태그 교체)
- `plugins/harness-installer/skills/configure-harness/SKILL.md` 9단계 오케스트레이션 (포탈 수동 단계·pbpaste 토큰 파일·launchctl bootstrap 즉시 기동·제거/점검 절)
- `.claude-plugin/marketplace.json` + `plugins/harness-installer/.claude-plugin/plugin.json` (마켓플레이스 `discord-harness-installer`, 플러그인 `harness-installer` 0.1.0)
- `tests/test_harnessctl.py` HOME 격리 블랙박스 테스트 31개 (fixture: make_fixture_repos/fetched/_overlay/_token_files/_pair/_installed/_mcp_log)
- `README.md` 본문 (설치 2줄·pins 설명·매뉴얼 v2.2 대체 선언)
- 상류 `~/VSCodeWorkspace/usage-coach/scripts/{install.sh,uninstall.sh}` + `tests/test_install_scripts.py` (plist `com.usage-coach.dashboard`, StartInterval 300, DRY_RUN 계약) — 커밋 6d83933, 미푸시
- 상류 `~/ai-folder/dev/codex-discord/scripts/uninstall.sh` + `test/uninstall.test.sh` (daemon·gemini만 bootout, tui는 tmux kill+plist 삭제) — 커밋 2cacc1e, 미푸시
- 상류 `~/ai-folder/dev/discord-multiagent/install/{overlay-manifest.json,chat-CLAUDE.md,gitignore-discord}` + `test/manifest.test.sh` (schema_version 1, overlay 8항목+seeds+claude_block) — 커밋 a7fe1ac·0a5a3bd, release-snapshot 브랜치, 미푸시
- `.superpowers/sdd/2026-08-04-harness-installer/progress.md` SDD 레저 (태스크별 커밋 범위·이연 minor·사고 기록 — Task 15 재개 시 참조)
- `plugins/harness-installer/skills/configure-harness/generator/harnessctl.py` 게이트 수정: preflight bun 검사 / write_bot_settings(settings.local.json 사전 승인+state 기록+remove 회수) / cmd_remove warns 집계·state 조건부 삭제 / verify UA·judge_mcp(since, 최신 파일만) / write_bridge_envs TUI_PANE·TUI_CHANNEL_ID / cmd_pair bridges·claude_bots config 주입
- `plugins/harness-installer/skills/configure-harness/SKILL.md` 5.5단계(/reload-plugins)·verify FAIL 시 bot-restart 폴백·브리지 호명 규칙·remove 범위 문구
- `tests/test_harnessctl.py` 37개 (신규: bun preflight·settings 병합/회수·state 재진입·웹훅 UA 로컬서버·stale MCP 로그 FAIL)
- `plugins/harness-installer/skills/configure-harness/generator/pins.json` = multiagent v0.1.0 / codex-discord v0.1.1 / usage-coach v0.1.1
- 상류 `~/VSCodeWorkspace/usage-coach/scripts/install.sh` plist EnvironmentVariables PATH 주입 — 커밋 5048003, 태그 v0.1.1 푸시
- 상류 `~/ai-folder/dev/codex-discord/src/index.mjs` mentionsMe/mentionsAnyone 헬퍼(역할 멘션 role.tags.botId) — 커밋 6ea2d31, 태그 v0.1.1 푸시
- `/Users/Shared/harness-e2e-checklist.md` E2E 체크리스트(사전 준비 A·B, Step 4·5, OBS 이관 — 계속 갱신 중)
- `/Users/Shared/harness-e2e-decisions.md` 1차 편차 보고 회신(node HOME 로컬 결정, preflight·launchd PATH 근거)
- `/Users/Shared/harness-e2e-findings-2026-08-04.md` · `harness-e2e-final-report-2026-08-04.md` · `harness-e2e-orch-mcp-2026-08-05.md` 테스트 계정 세션 작성 보고서(수정 지시서 §7·기준선 3안·MCP 미기동 실측)
- `/Users/Shared/obs-studio-config` OBS 설정 이관본(harness-test 경로 보정 완료) + `/Users/Shared/harness-e2e-recordings` 녹화 출력
- `plugins/harness-installer/skills/configure-harness/generator/harnessctl.py` 8/5 게이트 수정 누적: `session_procs`/`mcp_server_alive`(시임 HARNESS_FAKE_PANES·HARNESS_FAKE_PS)·`judge_codex_tui`/`_is_codex_cmd`/`_rollout_exists`·verify `--wait` 폴링·`write_bridge_envs` workdirs 분리·`write_bot_settings` statusLine 주입(+0.1.8 mode 회수 코드 유지)
- `plugins/harness-installer/skills/configure-harness/SKILL.md` 9단계 예열(claude mcp list, "보장 아님" 문구)·verify --wait 600·폴백 절차(재기동 1회→예열 복구→stderr 진단)·코덱스 TUI tui-up 폴백
- `tests/test_harnessctl.py` 42개 (+_seams/_live_bots_seams/_rollout fixture)
- 설치기 커밋열: 8ad8b1a→d10e6f9→f5c3af0→cc504bd(0.1.1)→b0645cb(0.1.2)→c36e7a1·212b283(0.1.5)→fcf33ea(0.1.6)→a4abc3d(0.1.7)→32ce8a5(0.1.8)→ac48fdd(0.1.9)→1542123(0.1.10)→4a6a6ac(0.1.11)
- 상류 커밋: discord-multiagent v0.1.1=0db7925(bot-up --permission-mode auto 주입+감시자 fd 분리+테스트 3) / codex-discord v0.1.2=a5fc833(가드 treeHasCodex·tui-up 직접 실행), v0.1.3=d43e58b(findRolloutByCwd·순서 역전), v0.1.4=85a297b(readSessionMeta 개행까지) — 테스트 63 / usage-coach v0.1.2=30ca10d(scripts/statusline-command.sh 신설) / folder-bot 0.1.1=a9004f0(bot-up 동일 계보 수정)
- `/Users/Shared/harness-e2e-ct-reply-2026-08-05.md` CT 회신 정본(§3.5 분리·§3.7 예열·§3.8 시퀀스·§3.9 초기화 목록·§3.10 범프·§3.11~13 코덱스·§3.14 statusline·§3.15~16 무인 모드·§3.17 folder-bot 이월) — 다음 세션 필독
- `/Users/Shared/harness-e2e-diag-reply{,2,3,4,6,7,9,10,12}-2026-08-05.md`·`harness-e2e-statedump-2026-08-05.md` 설치 세션 회신들(실측 기록)
- `/Users/Shared/bot-up-fixed.sh` bot-up 완성본(분류기 차단 시 사용자 cp용)

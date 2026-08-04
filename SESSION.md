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

Task 15 릴리즈 게이트 진행 중 — Step 1~3 완료(상류 3레포 v0.1.0 태깅·푸시, pins 확정,
레포 GitHub 공개 public). E2E 1·2차에서 나온 결함 전부 정본 수정 완료(설치기 a95bf31,
codex-discord v0.1.1, usage-coach v0.1.1, 설치기 테스트 37 passed).
남은 것 = 테스트 계정(harness-test) 3차 재검증 + 재촬영 → Step 6·7.
게이트 문서: `/Users/Shared/harness-e2e-*.md` (checklist·decisions·findings·final-report·orch-mcp)

## 다음 단계
<!-- 덮어쓰기. 첫 항목 = 다음 세션이 바로 집어들 일 -->

1. 테스트 계정 3차 재검증 결과 수령 — 마켓플레이스 업데이트로 a95bf31 수령 후
   신규 판정 4항목(①tmux ls에 codex-live ②verify 낡은 MCP 로그 FAIL+bot-restart 폴백
   ③대시보드 봇 세션 카드가 설치 경로 지향 ④호명=문두/멘션(역할 멘션 포함)) + 재촬영
2. 통과 시 Task 15 Step 6(release: v0.1.0 커밋+푸시) + Step 7(아래 긱님 항목 잔존 확인)
3. 차기 이월분 기록 유지: #18/#19/#20/#21/#25(remove 품질)·#16(brew prefix 검사)·
   #9(MCP 4지선다 미선택 확정 — Claude Code 본체 이슈 후보, 촬영 구간 보존)
4. **[약속] MultiAgent 레포 custom registry 별도 스펙 착수** — 긱님(geek7942) 제안, "함께 검토하겠다" 공개 답변(2026-08-03). 1단계(등록부 병합: 원본+`_local`, update 보존)만 우선. 잊히면 안 됨.

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

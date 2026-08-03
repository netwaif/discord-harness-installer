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

구현 완료 — Task 1~14 전부 리뷰 통과, 최종 전체 리뷰 findings(I-1 .gitignore 비밀 보호,
I-2 수다 클로드 기동, T13/T14)까지 수정·재리뷰 해소(설치기 1fcd356, 하네스 0a5a3bd).
자동 테스트 4레포 녹색(설치기 31 passed). 남은 것 = Task 15 릴리즈 게이트만.
진행 정본: `.superpowers/sdd/2026-08-04-harness-installer/progress.md`

## 다음 단계
<!-- 덮어쓰기. 첫 항목 = 다음 세션이 바로 집어들 일 -->

1. Task 15 릴리즈 게이트(사용자 게이트) — ①상류 3레포 푸시+태깅(discord-multiagent는 release-snapshot→main refspec 주의) ②pins.json 실태그 교체 ③별도 macOS 계정 클로드 4봇 E2E ④코덱스 스모크 E2E ⑤릴리즈 커밋+푸시
3. **[약속] MultiAgent 레포 custom registry 별도 스펙 착수** — 긱님(geek7942) 제안, "함께 검토하겠다" 공개 답변(2026-08-03). 1단계(등록부 병합: 원본+`_local`, update 보존)만 우선. 잊히면 안 됨.

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

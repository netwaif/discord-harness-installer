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

**9/3 세션은 촬영 중 터진 codex-discord TUI 릴레이 세션 선택 버그 수정**(상류
레포 커밋 7d4e6e2 푸시, 9/3 결정 기록): guardian 보조 세션 제외 + 화면 UUID
스크레이핑 폐기, 테스트 57건·디스코드 텍스트+PNG 왕복 실측 통과, 데몬 재시작
완료. 설치기 쪽 태그·pins 반영은 미착수(다음 단계 0.3). **#9 이슈 초안 게시 승인
대기 유지**(docs/issues/2026-08-12-claude-code-channel-lease-silent-skip.md).
영상 준비는 tower 이관 유지(8/12). 재개 지점 = codex-discord 태그 v0.1.6·pins
범프 여부 결정, #9 게시 승인, 유튜브 박일용님 답글 초안(9/2 결정 기록) 게시 승인,
tower 매뉴얼 개정 원고 오면 검수. 서버 이설 뒤처리 체크 잔존(0.7).

## 다음 단계
<!-- 덮어쓰기. 첫 항목 = 다음 세션이 바로 집어들 일 -->

0.3. codex-discord 상류 7d4e6e2(9/3 릴레이 세션 선택 수정)를 설치기에 반영할지
   결정: 태그 v0.1.6 푸시 → `plugins/harness-installer/skills/configure-harness/generator/pins.json`
   codex-discord v0.1.5→v0.1.6 + plugin.json·marketplace.json 0.1.14 범프(8/26 fed3851
   절차 재사용). plugin install은 최신 설치라 기존 사용자는 update만으로 반영됨
0.5. 유튜브 미답글 2건: ①B0KZOfXj6z0 박일용님 "맥에서만 되나요? 윈도우에서는
   안되나요?"(8/24 발견) — 기존 답변 관례(v40AFadpg4w Hodoo307님 답글: WSL2 안내)
   재사용 가능 ②_hZ5mozId_0(그래프 엔지니어링 영상) @202-z7g "매뉴얼
   부탁드리겠습니다!" / 풍류왕 "윈도우로 되나용?"은 사용자가 직접 답글 완료,
   스레드 위치 미특정(조회 중단됨)
0.7. 서버 이설 뒤처리 확인(다음 세션 가벼운 체크): ①멤버십 서버 옛 채널 4개
   삭제 여부(안전 판정 완료 — 8/26 이설 결정 기록의 삭제 가능 목록)
   ②ClaudeCode Bot 역할의 채널 관리·웹훅 관리 권한 회수 여부(사용자 몫)
0. **#9 이슈 게시** — 초안 완성(docs/issues/2026-08-12-claude-code-channel-lease-silent-skip.md),
   사용자 승인 대기. 승인 받으면 게시(직접/gh 대행은 사용자 선택) →
   tower 세션에 URL 회신(대본 메타 반영용, 그쪽 사용자 게이트 있음)
1. tower 세션 매뉴얼 개정 원고 검수(오면) — v2.2 원본
   (~/VSCodeWorkspace/discord-multiagent-manual/)·SESSION.md 결정 기록 대조,
   "16장→스킬 1개" 서사에서 포탈 수동 단계 잔존 경계선 확인
2. 설치기 차기 이월(0.1.14 후보 — 0.1.13은 8/26 핫픽스로 소진): ①preflight/verify 로컬 동명 세션 검사
   ②verify 무로그 스킵 진단 메시지에 이름 충돌 안내(다른 기기 포함)
   ③pins.json plugins.folder-bot 0.1.1→0.1.5 정정(기록용 — plugin install은
   버전 미지정 최신 설치라 기능 무관, 8/11 확인) ④remove 재실행 "이미 제거됨"
   판정 부재(uninstall.sh 부재 WARN 영구 잔존) ⑤remove 재실행 로그 모순
   ("상태 보존(state.json)" 출력인데 실제 파일 미생성)
5. folder-bot 차기 이월: ①botctl stop을 /exit 정상 종료 방식으로(현 kill-session은
   유령 리스 생성 — 8/6 원인 격리) ②doctor MCP 판정 sessionId 기준 구분(8/6 완화만
   반영) ③eams 무조건 주입 여부 + 미신뢰 폴더 재현 실험(ct-reply §3.17)
   ④봇 세션 수동 재기동 UX — 맨 claude 기동 오용 감지/안내(8/6 실사용 사고)
6. 차기 이월분 기록 유지: #18/#19/#20/#21/#25(remove 품질)·#16(brew prefix 검사)·
   bot-up 락 240s 증폭(상류)·"수다 봇 폴더 하위 분리"는 d10e6f9로 해소됨
7. **[약속] 대시보드에 봇·폴더·채널 매핑 표시** — bagbio1748님 블랙박스화 우려에 "다음 업데이트 후보로 적어두겠다" 공개 답변(2026-08-24, 채널 1519510111083561021 답글 1541256639401820301). bots.json 정본을 대시보드에 노출하는 방향
5. **[약속] MultiAgent 레포 custom registry 별도 스펙 착수** — 긱님(geek7942) 제안, "함께 검토하겠다" 공개 답변(2026-08-03). 1단계(등록부 병합: 원본+`_local`, update 보존)만 우선. 잊히면 안 됨.

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
- 2026-08-06 folder-bot 0.1.2 출시(이월 3건+statusLine 주입·회수) → 검증 중 MCP 무로그 불발 재발 → 사용자 지시로 "폴백 우회" 대신 근본 해결 전환 + 촬영 범위 = 전 기능(folder-bot 포함, 뺄 건 촬영 후 사용자가 결정)
- 2026-08-06 SSH 진단로 구축: harness-test 무암호 접속(공개키는 사용자 cp→설치 세션이 authorized_keys 설치, SACL은 사용자 sudo dseditgroup, 이 프로젝트 settings.local.json에 ssh/scp 허용 규칙). 분류기 차단 다수 — 승인/우회불가 항목은 사용자 손 경유 관례 유지
- 2026-08-06 **MCP 무로그 불발 원인 격리(변수 제거 실험 E1~E6)**: 채널 연결 세션의 kill-session 강제 종료 → 봇 이름 유령 리스(~90분 TTL) → 같은 이름 새 세션이 채널 MCP 연결 시도 자체를 무로그 스킵. /exit 정상 종료는 리스 없음(10초 뒤 재기동 즉시 연결 실증). 8/5 "아침 전패→10:20 전승"·"예열 복구 성공"은 전부 TTL 만료 우연으로 재해석. bot-restart(pane 교체)는 안전 — 하네스가 멀쩡했던 이유
- 2026-08-06 folder-bot 연쇄 출시: 0.1.3(예열 DISCORD_STATE_DIR 정정+doctor 종료로그 오판 완화) / 0.1.4(py3.9 임포트 크래시 — `X | None` 표기, from __future__ 수정 + SKILL 폴백 절 유령 리스 기반 교체) / 0.1.5(다중 인원 채널 규칙 — 프로덕션 collab에서 아내 멘션 응답 사고 2회 실측, 정본+collab CLAUDE.md 동시 반영)
- 2026-08-06 §3.9 초기화 완료(설치 세션): /exit·/quit 정상 종료로 리스 회피, usage-coach 삭제(CT 판단: pair·install.sh·statusLine이 전부 재생성+낡은 스냅샷 촬영 오염 방지), multi-agent-starter·folder-bot 마켓플레이스 제거는 적정(설치기 plugins 단계가 자체 추가 — harnessctl PLUGINS 상수). §6-2 카드 %는 재촬영 folder-bot E2E에서 종결(used=3 스냅샷까지는 실증 완료)
- 2026-08-06 촬영 편성: 유령 리스 없어 당일 촬영 가능. 사용자 지친 상태 — **출력 짧게, 단계별로만, 사용자 신호 대기**
- 2026-08-06 collab 봇 실사용 사고 진단·복구: 사용자가 pane에서 맨 `claude`로 재기동 → `--channels` 없이 떠서 채널 미연결(MCP 로그 "Channel notifications skipped" 실측, 종료 자체는 clean — 유령 리스 아님). botctl `start --name collab`로 재기동해 "Channel notifications registered" 확인, 0.1.5 다중 인원 규칙 적용 완료. 규칙 확립: **종료는 /exit 자유, 기동은 반드시 botctl/bot-restart 경유**(정식 경로는 디스코드 "세션 마감하고 재시작해"). folder-bot 이월 ④로 등재
- 2026-08-10 compinit 경고 해결: 원인은 chmod가 아니라 **소유자**(/usr/local/share/zsh 전체가 soonho 소유 → harness-test 관점 신뢰 불가). harness-test ~/.zshrc 맨 앞에 fpath 필터+compinit 선실행 삽입으로 해소(백업 ~/.zshrc.bak-compinit). 기록돼 있던 sudo chmod 한 줄은 이 케이스에 무효였음
- 2026-08-10 4~5차 테이크 중단 → **무로그 스킵 2번째 원인 격리: 본계정 동명 세션 활성 이름 충돌**. 리스는 세션 이름(-n)+Claude 계정 단위(macOS 계정 무관 — 같은 Max 계정), 활성 리스는 무만료. 본계정 orchestrator /exit → 테스트 봇 재기동 → 즉시 registered → verify 12/12 실증. 촬영 중 본계정 orchestrator·(해당 시)chat-claude 내려두기가 전제. 정정 3호 발행. 잔여 미해명: 테스트 chat-claude는 동명 없이도 최초 기동 스킵(재기동으로 해결)
- 2026-08-10 **예열 결함 확정·0.1.12 출시**(1f03739): SKILL 예열 명령이 DISCORD_STATE_DIR 없이 돌아 토큰 미발견으로 항상 실패(5차 테이크 설치 세션이 자가 진단). 과거 "예열 성공"은 전역 ~/.claude/channels/discord/.env 잔존 우연으로 재해석. 수정 = 예열 2줄(오케 .discord-state / 수다 chat/.discord-state) + 폴백 절 동명 세션 확인 절차. SKILL.md만 변경, 테스트 42개 통과
- 2026-08-11 **6차(최종) 테이크 본편 성공**(0.1.12): 설치→verify→실응답 4건→@멘션 실증 완주. 첫 기동 무로그 스킵은 이름 충돌 없어도 재현(하네스 봇·프로덕션 kickstart 공히) → bot-restart 1회 수렴이 정상 경로로 재확인
- 2026-08-11 foldertest 세그먼트 미완: add·pair·start 성공, 채널 연결만 무로그 스킵 4연속. 도중 CT가 SSH 맨 기동(PATH 없는 환경)으로 ENOENT 1회 유발 — **원격 기동은 반드시 `zsh -lc` 경유** 교훈. kill-session 1회 섞은 실수로 리스 생성 가능성 → 익일 사전 검증 후 5분 세그먼트 촬영으로 결정
- 2026-08-11 프로덕션 orchestrator 복구: launchctl kickstart → 첫 기동 스킵 재현 → bot-restart로 연결(882ms). 프로덕션 chat-claude는 애초에 없었음(8/10 밤 확인 — 충돌 이름은 orchestrator 하나였음)
- 2026-08-11 (오후) **foldertest 세그먼트 촬영 완료 = 촬영 전체 완료**. 설치부터 온카메라 원칙(사용자 정정: 백그라운드 설치 금지·대시보드 포함·순서는 폴더봇→대시보드). 리셋 절차 = /exit 선행 후 botctl remove(stop/remove는 kill-session 내장 — /exit 먼저가 필수) + 폴더 완전 초기화. 첫 기동 무로그 스킵 재현→재기동 1회 수렴(재확인). 리추얼 올바른 순서 = 마감 지시→답장(통지)→대시보드 ctx 리셋 확인→"이어서하자"(CT가 순서 앞당기는 실수 1회, 사용자 정정). 웹훅 통지는 folder-bot config 미설정이라 미촬영(선택 항목)
- 2026-08-11 (밤) 녹화 폴더 정리: 폐기 테이크 7개(1차 E2E 3·2차 1·4차 1·5차 1·포탈 중복 1) ffmpeg 프레임 판독으로 전수 확인 후 `_폐기테이크/`로 이동(즉시 삭제 대신 가역 조치). `디스코드서버생성.mov`·`디스코드포탈-bot만들기1.mov`는 사용자 본인이 8/4 본계정에서 직접 촬영·명명한 포탈 소스로 확인 — 보존. 봇 토큰 사본은 "foldertest만 영상 확정까지 보관 후 전량 삭제" 권고 전달
- 2026-08-11 (오후 늦게) **4부 제거 테스트 통과**(GUI 로그아웃 상태, SSH): remove 1회 완주 — plist 6종 전량 제거(#8 스펙 5종+tui), CLAUDE.md 블록·.gitignore 5줄·권한 파일 2종·오버레이 스크립트 회수, .mcp.json엔 starter 소유 codex만 잔존(하네스 추가분 없음), 보존 목록(.env·.discord-state·chat/·tasks/·~/.config/usage-coach) 유지, state.json 삭제(전 항목 성공). #27 재진입 = 재실행 크래시 없음·보존 유지·WARN 2건(1차가 지운 repos의 uninstall.sh 부재)과 재진입 안내. 관찰 2건("이미 제거됨" 판정 부재 / "상태 보존" 로그와 실파일 불일치)은 0.1.13 이월 ④⑤ 등재. Step 7: 긱님 [약속] 항목 잔존 확인 완료. pins.json plugins.folder-bot=0.1.1은 낡은 기록(검증은 0.1.5)이나 plugin install이 버전 미지정이라 기능 무관 — 0.1.13 이월 ③
- 2026-08-11 (오후) 성공 촬영본 2개 리네임 + 대본 노트 인계 파일 작성(harness-e2e-script-notes-2026-08-11.md — 토큰 노출 프레임 처리 절차 포함). Antigravity 사용량 미표시 원인 확정: codexbar는 해당 계정에서 Antigravity 실사용 이력이 있어야 읽음(본계정 정상 표시 실측·테스트 계정 미사용이라 생략 — 결함 아님)
- 2026-08-11 (오후) 부수: 본계정 folder-bot 플러그인 0.1.0→0.1.5 업데이트(`claude plugin update folder-bot@folder-bot` — zzukumi 폴더 봇 생성 중 구버전 토큰 채팅 수급 절차 발견이 계기). claude-discord 릴레이 세션 다운→ctrl+C 종료 실측: **SIGINT는 리스 안 남김**, "원래 기동 명령 그대로 + --continue"로 대화 유지 재기동 성공(783ms registered)
- 2026-08-12 #9 이슈 초안 작성(docs/issues/2026-08-12-claude-code-channel-lease-silent-skip.md) — 격리 조건 3종(유령 리스 ~90분 TTL·/exit·SIGINT 무리스 / 동명 활성 세션 무만료 / 첫 기동 스킵 무충돌 재현) + E1~E6 압축표 + 핵심 요구 "스킵 사유 로그". 게시 전 확인 3건(본문·계정 언급 수위·게시 방식) 사용자 대기
- 2026-08-12 영상 준비 tower 세션 이관(사용자 지시) — 인계(정본 노트·녹화본·처리 3건) + 재료 5종 회신(설치기 경로/이력 정본/매뉴얼 v2.2 소스=~/VSCodeWorkspace/discord-multiagent-manual/(VERSION 2.2, index.html 소스)/실측 수치/#9 초안 경로). 규율 2건 tower 채점표 반영: ①folder-bot 언급은 0.1.5(pins 0.1.1은 낡은 기록 — 대본에 0.1.1 나오면 FAIL) ②#9 "게시된 이슈" 표현 금지. verify 12개 구성 = 봇 MCP 2+브리지 로그 2+데몬 2+TUI 1+tmux 2+plist 2+웹훅 1(정본: shooting-script 154행·harnessctl.py:746). 매뉴얼 개정 원고 검수 약속(tower가 원고 공유 예정, index.html 무접촉·텍스트 원고까지만). 영상은 멤버 전용 확정, 제작은 ~/ai-folder/youtube/AgentLoops/discord-harness-installer/ 그래프 방식
- 2026-08-14~15 **Hostinger VPS 3봇 체제 구축 완료**(설치기 프로젝트 외 부업 — 사용자 지시). 서버 `ssh -i ~/.ssh/hostinger root@srv1884693.hstgr.cloud`, Ubuntu 24.04, 작업 대상은 `hermes-agent-iqxn-hermes-agent-1` 컨테이너(Debian 13, hermes uid 10000, HOME=/opt/data ← 호스트 /docker/hermes-agent-iqxn/data 바인드 마운트 = 영속). 설치기(harnessctl)는 darwin 전용이라 미사용 — 수동 경량 설치. 구성: ①로케일 POSIX→C.UTF-8(.profile/.bashrc, tmux -u — 박스문자 ACS 깨짐 해소) ②claude 네이티브 2.1.233 ~/.local/bin(npm 프리픽스 auto-update 실패 해소) ③hostinger-bot = claude `-n hostinger-bot --permission-mode auto --channels plugin:discord@claude-plugins-official`, DISCORD_STATE_DIR=/opt/data/discord-bot/.discord-state, requireMention true ④codex 0.147.0(npm --prefix ~/.local) + auth.json 맥 복사("Logged in using ChatGPT") + codex-discord v0.1.4 클론 /opt/data/codex-discord, .env headless(TUI 없음)+NAME_TRIGGER_CHANNEL_IDS 호명 게이트 ⑤agy 공식 스크립트 설치 + OAuth 코드 붙여넣기 플로우 로그인(콜백이 antigravity.google/oauth-callback라 헤드리스 가능) + .env.gemini(ENGINE=agy, 호명 "제미나이", DATA_DIR=data-gemini) ⑥호스트 systemd `claude-bridge.service` + `/usr/local/sbin/claude-bridge-watch.sh` — docker events(`{{.Action}}` — 신버전 `.Status` 없음) 감시로 tmux 세션 4종(claude-bridge/hostinger-bot/codex-bridge/gemini-bridge) 자동 복구. 3봇 모두 실응답 검증 완료(사용자 확인). 채널 1537467414705471640 공유, 허용 사용자 1062698028051472516
- 2026-08-15 부속 결정·관찰: ①봇 토큰 3종은 각각 새 디스코드 앱(맥 토큰 재사용 금지 — 게이트웨이 이중 접속) ②서버 세션 이름은 맥과 불충돌 확인(hostinger-bot 등) ③분류기 차단 다수(access.json 작성·자격증명 전송·curl|bash) — 사용자 "다시 해봐" 재승인 후 통과 or 사용자 pane 직접 실행 관례 유지 ④약점 1건 잔존: 컨테이너 재시작 = claude 강제 종료라 hostinger-bot만 유령 리스(~90분)/첫 기동 무로그 스킵 가능(증상 = 멘션 무응답, 대응 = 재기동 1회/리스 만료 대기). 재시작 실증 테스트는 사용자 지시로 안 함("나중에 안되면 다시 부르면 되잖아") ⑤hermes 컨테이너 apt 설치분(unzip·nvim)만 재생성 시 소실(운영 무관)
- 2026-08-24 bagbio1748님 Q&A 대응(채널 1519510111083561021): ①본질문(폴더봇 프로젝트 생성·디렉토리↔채널 관계) 답변 게시(답글 id 1541256639401820301, 검수 3회 반영 — "좋은 질문 감사" 서두/tasks vs 프로젝트 폴더 분리 기준/토큰 재사용 금지 문단 평이화/불필요 문장 삭제) ②추가 질문(이해 확인) 교정 답변 게시(사용자가 직접 게시 — 교정 요지: claude·codex·agy 봇이 폴더봇을 매개로 다른 프로젝트 접근한다는 이해는 오류, 하네스 3봇과 폴더 봇은 독립 축) ③"기존 클로드 코드를 디스코드 UI로 사용" 설명 검증 요청 → 맞다 판정(기동 명령 실체가 claude --channels) + 뉘앙스 2건(상주 데몬/무인 승인) ④연속 답글 초안 작성 — **게시 승인 대기 중 세션 마감**. 초안 전문: "덧붙이면, 그냥 기존의 클로드 코드를 디스코드 UI를 통해서 사용한다고 이해하시면 쉽습니다. 비유가 아니라 실체가 그렇습니다 — 봇 기동 명령이 말 그대로 터미널에서 쓰는 그 claude에 디스코드 연결 옵션을 붙인 것이라서요. 터미널과 다른 점은 두 가지뿐입니다. 1. 항상 켜져 있습니다 — 데몬으로 상주해서 컴퓨터를 재부팅해도 자동으로 다시 뜹니다. 2. 무인 승인으로 돕니다 — 터미널처럼 매번 권한 승인을 클릭하지 않아도 됩니다."
- 2026-08-24 [약속] 등재: 대시보드에 봇·폴더·채널 매핑 표시(bagbio1748님 블랙박스화 우려 답변에서 공개 약속 — 다음 단계 7번)
- 2026-08-24 유튜브 관찰: 풍류왕 "윈도우로 되나용?" 댓글은 사용자가 직접 답글(초안 제공: 설치기 맥 전용+WSL2 수동 가능성+미검증 명시). 채널 전체 "윈도우" 검색으로 미답글 발견 — B0KZOfXj6z0 박일용님 건(다음 단계 0.5). 윈도우 질문 기존 답변 관례 = WSL2 안내(v40AFadpg4w) 또는 미검증 솔직 고지(0ScISw3Wuv8)
- 2026-08-26 **수다채널 코덱스 무응답 원인 격리·핫픽스 릴리즈**: codex CLI 0.149.0 자동 업데이트로 롤아웃에서 event_msg agent_message 소멸(0.146 실물엔 존재, 0.149 세션엔 0건) → 브리지 tail이 아무것도 못 뽑아 릴레이만 무증상 소실(주입·TUI 응답 생성은 정상, agy는 tail 미사용이라 정상). 수정 = extractAgentMessages 매처를 response_item(role=assistant)로 교체 — 0.146~0.149 전 구간 동일 텍스트 기록 실물 검증(event==resp), 구포맷 두 소스 공존 시 중복 게시 배제. codex-discord v0.1.5(f09c7fc, 테스트 63 통과) + 설치기 0.1.13(fed3851, pins codex-discord v0.1.5, 테스트 42 통과) 푸시. 프로덕션 데몬 kickstart 복구, 사용자 실응답 검증(00:39). 공지 게시: 채널 1522490241859059784, 메시지 id 1541837270884024500 — 기존 설치자 업데이트 안내는 "클로드 코드에 지침 붙여넣기" 방식(수동 git checkout 3줄은 state.json 불일치로 verify 오판 유발이라 기각, 정식 경로 = plugin update→fetch 재실행이 멱등). 부속 확인: tail은 연결 시점 이후 append만 릴레이(과거분 재게시 방지 설계) / Hostinger headless 구성은 TUI tail 경로 미사용이라 무관 / 0.1.13 이월분 ①~⑤는 0.1.14 후보로 명칭 이월
- 2026-08-26 (2차) **디스코드 서버 이설 완료**: 에이전트 채널을 멤버십 서버(1519510109217230989)→netwaif 서버(1111493736631898195)로 이전. ①봇 초대: 수다(ClaudeCode Bot)는 기존 가입, 오케·코덱스·제미나이·collab·search-youtube 5종 초대 링크(공통 7권한 permissions=309237763072)로 가입, zzukumi는 이전 제외(멤버십 서버 잔류) ②채널 매핑: 수다/TUI=codex-claude-gemini 1542142111862751314, 오케=multiagent-work 1542141967469776906, collab=1542142326384754748, search-youtube=1542141759679897690, 신설(CT가 API 생성)=codex-작업 1542153401591140403·gemini-작업 1542153403939946596·대시보드 1542153406108667984+웹훅 ③설정 치환 6곳(전부 .bak-move 백업): 전역/오케/collab/search-youtube access.json + codex .env(TUI_CHANNEL_ID·CHANNEL_IDS) + .env.gemini(CHANNEL_IDS·NAME_TRIGGER_CHANNEL_IDS) ④재기동은 브리지 데몬 2종+usage-coach만 — **클로드 세션 4종은 무재기동으로 멘션 테스트 전건 통과 = access.json은 메시지 단위 라이브 반영(재기동 불요) 신규 실증** ⑤대시보드는 8/21부터 구 웹훅 404로 조용히 실패 중이었음 → 새 웹훅 + discord-state.json message_id 리셋으로 새 카드 1542154374934040649 게시 확인 ⑥비공개 dashboard-new 채널(1542162018596036660)에 웹훅 생성해 agentlayer-29 세션에 SendMessage 전달(비공개 채널은 서버 권한으로도 비가시 — 채널별 봇 추가 필요 실측) ⑦삭제 안전 판정: 멤버십 서버 옛 채널 4개(구 수다 1529498215651741706·구 오케 1530138702838366339·구 collab 1533823223442182294·구 search-youtube 1533108133990371430) 삭제 가능, 구 codex/gemini 작업 채널·구 대시보드 웹훅은 이미 삭제돼 있었음(404). 보존 필수 = zzukumi 3채널·VPS 채널 1537467414705471640·커뮤니티 Q&A/공지. 커뮤니티 채널 허용 목록(bagbio Q&A 등)은 무접촉이라 대기 중인 답글 스레드 영향 없음
- 2026-08-28 **zzukumi 폴더봇 연결 해제 완료**(사용자 요청): 사용자가 세션 마감→/exit 선행(유령 리스 없음) 후 CT가 botctl `stop --name zzukumi`→`remove --name zzukumi` 실행. 결과 = tmux 세션 zzukumi-bot 종료·plist com.folder-bot.zzukumi.plist 삭제·CLAUDE.md 지침 블록 제거·bots.json 등록 해제(잔존 봇 search-youtube·collab). 보존 검증 = `~/ai-folder/youtube-members/zzukumi/.discord-state`(토큰·페어링)·SESSION.md(8/28 6회차 마감분)·HANDOFF.md·coaching/ 전부 유지, 디스코드 봇 앱·전용방 채널 무접촉. **재연결 절차 = pair 불요, `botctl add --name zzukumi --folder ~/ai-folder/youtube-members/zzukumi --session zzukumi-bot` + `start`** — 첫 기동 무로그 스킵 시 재기동 1회 수렴(정상 경로). 재연결 후 채널에서 "이어서하자"로 SESSION.md 재정박
- 2026-08-27 **코덱스 TUI 부팅 불발 진단·수동 복구 관례 확정**: 부팅(15:08) tui-up이 TUI 기동까지는 성공했으나 codex 업데이트 프롬프트(0.149→0.150.1)에 더미 턴 Enter가 걸려 "업데이트 후 자동 종료" → codex-live 세션 소멸(`can't find session` 4회)·180초 타임아웃 실패. 15:16 재실행은 이미 갱신된 버전이라 정상 완주(사용자 추정 재기동). 대응은 사용자 결정으로 **수동 복구 한 줄** = `launchctl kickstart gui/501/com.codex-discord.tui`(동등: codex-discord에서 `npm run tui:up`, tui-up.sh 멱등이라 애매하면 그냥 실행). plist KeepAlive 추가(자동 복구)와 `check_for_update_on_startup=false`(codex config 실존 키, 프롬프트 자체 억제)는 선택지로 확인만 하고 미적용 — 빈도 낮고 복구 비용이 명령 한 줄이라는 근거. 약점 = 죽어 있으면 증상이 "디스코드 코덱스만 조용함"뿐이라 발견 지연 가능 ①harness-test 재부팅으로 tmux 서버 소멸 + **GUI 세션 종료 → 키체인 잠김 → SSH 기동 봇이 "Not logged in"**(채널 연결 이전 단계 블로커 — 사용자 GUI 로그인 요청, claude-discord 경유) ②tmux 서버를 SSH에서 재기동할 땐 `zsh -lc`로도 bun ENOENT — bun PATH(~/.bun/bin)·~/.local/bin 주입이 전부 .zshrc(interactive 전용)에 있음 → **`zsh -ic` 경유로 확정**. 8/10 "zsh -lc면 충분" 실측은 tmux 서버가 정상 환경으로 이미 떠 있던 우연. 테스트 세션 2회 모두 /exit 정상 종료(리스 없음)
- 2026-09-02 재정박 정정: 다음 단계 -1(bagbio1748님 연속 답글 게시 승인 대기)은 **이미 해소** — 채널 1519510111083561021 실물 대조 결과 사용자가 2026-08-24 11:22 직접 게시(id 1541407450568331275, 초안 앞 두 문장만 축약 게시·번호 항목 2건 생략). bagbio1748님 8/26 "이해됐다" 감사 인사(id 1542004656673132616)로 스레드 종결. 8/28 마감 기록의 "승인 대기" 스냅샷은 실물 미대조로 낡은 상태였음 → 항목 삭제
- 2026-09-02 **디스코드 봇 4종 일괄 마감→재시작→재정박 절차 실측**(사용자 신규 도구 로드 목적, "다른 세션은 건드리지 말 것" 범위 한정 — close-all-sessions 스킬의 ListAgents 전수 방식 대신 봇 pane 직접 지정): 대상 = orchestrator·collab-bot·search-youtube-bot·claude-discord(tmux 세션명, 각 :0.0 pane). ①`tmux send-keys -t <세션>:0.0 "세션 마감" Enter` → 4개 SESSION.md 갱신 확인 ②`bash ~/ai-folder/dev/discord-multiagent/scripts/bot-restart.sh <세션명>` ×4(14:46, 전부 0.9~1.5초에 "Successfully connected", 로그 `~/.claude/logs/bot-restart.log`) ③`send-keys "이어서하자"` → 4개 재정박 응답 확인. **교훈 3건**: (a) "세션 마감→이어서하자"는 프로세스 재시작이 아님 — 새 도구·업데이트 반영엔 bot-restart 필수(사용자 "전부 재시작 한거 맞지?"에 아니오로 정정) (b) pane 유휴 판정에 스피너 단어 매칭은 무효(Whatchamacalliting·Ionizing 등 무작위) → `done H:MM PM` 문자열 또는 SESSION.md mtime으로 판정 (c) 사용자 "봇이 전부 Fable 5.1로 시작함" 주장은 대화 기록 jsonl의 assistant.message.model 전건 `claude-opus-5`로 반박·사용자 인정 — /model 기본값 변경은 새 세션에만 적용, 기동 중 봇 무영향. 코덱스 TUI는 사용자가 업데이트로 종료해 둔 상태 → `launchctl kickstart gui/501/com.codex-discord.tui`로 codex-live 재생성·부팅 체크 통과. 제미나이 데몬 무접촉
- 2026-09-02 유튜브 박일용님(B0KZOfXj6z0) 답글 초안 작성, 게시 승인 대기: "안녕하세요. 설치기는 현재 macOS 전용입니다(launchd·tmux 의존). 윈도우는 WSL2에서 수동으로 구성하면 가능할 수는 있는데, 제가 직접 검증한 환경이 아니라서 동작을 보장드리진 못합니다. 참고만 해주세요."

- 2026-09-03 **codex-discord TUI 릴레이 세션 선택 버그 수정**(촬영 중 발생, 코덱스 Sol 진단문을 사용자가 전달 — "무조건 수용하지 말고 확인"): 증상 = 디스코드→TUI 주입은 되나 답변·`[[첨부]]`가 안 나감, guardian 승인 판정 JSON이 채널로 샘. 원인 2건 실측 — ①`findRolloutByCwd`가 cwd만 비교해 같은 cwd의 guardian_review 롤아웃(파일명 `…T11-23-05-01a06513-b562…`가 main `…b3d4…`보다 사전순 뒤)을 선택(daemon.log 4391~4393행) ②첫 수정 직후 재발: pane에 남은 Sol 진단문의 "잘못 선택된 세션: b562" UUID를 `extractSessionId`(화면 마지막 UUID)가 세션 ID로 오인 → findRolloutById 경로로 guardian에 재연결. **Sol 진단 검증 결과**: 원인 ①은 맞음, 단 "guardian_review 제외"만으론 부족 — 전 롤아웃 session_meta 전수 조사에서 guardian thread_source가 버전별로 없음(0.128)·subagent(0.130~0.141, 257건)·guardian_review(0.152, 2건)로 흔들림, source는 일관되게 객체 `{subagent:{other:"guardian"}}`, 사용자 TUI는 source="cli"·thread_source user 또는 없음(0.125~0.128). 규칙 = "source가 객체 또는 thread_source가 있는데 user 아님 → 제외". Sol 요청 2번(화면 UUID 경로 유지)은 사용자 승인("근본 해법이 맞는거면 그렇게해")으로 뒤집어 **화면 스크레이핑 경로 폐기** — 0.146+ 상태바 UUID 무표시라 이미 무용, 오인 통로만 남아 있었음. 고아 코드(capturePane·extractSessionId·UUID_PREFIX_RE·findRolloutById·auxiliaryRolloutReason)와 테스트 제거. 검증 = 실패 테스트 선행 후 57건 통과, `launchctl kickstart -k gui/501/com.codex-discord.daemon` 재시작, 디스코드 채널 1542142111862751314에서 12:50 텍스트+PNG 왕복 실측(로그: 롤아웃 제외 b562 → 선택 b3d4 → TUI tail 연결). 커밋 7d4e6e2 main 푸시. 교훈: 봇 발언은 classifyMessage에서 context 처리라 E2E 트리거는 허용 사용자만 가능 — Monitor로 daemon.log 감시 후 사용자 메시지 대기가 맞는 절차

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
- folder-bot 커밋열(8/6): a28f5bc(0.1.2 statusLine 주입·회수/pair --token-file/doctor MCP 판정/SKILL 폴백)→16fc1d1(0.1.3)→69dfb25(0.1.4)→f66abd9(0.1.5) — 테스트 32개(24+8), 전부 origin/main 푸시
- folder-bot 신규 코드 식별자: `statusline_script()`/`write_statusline()`/`remove_statusline()`(bots.json `statusline_cmd` 기록·회수)·`mcp_log_dir()`·pair `--token-file`+`consume_token_file()`·`from __future__ import annotations`
- `/Users/Shared/harness-e2e-mcp-rootcause-2026-08-06.md` **유령 리스 원인 격리 정본**(실험표 E1~E6·TTL 90분·/exit 안전·§3.9 보정·#9 이슈 재료)
- `/Users/Shared/harness-e2e-script-corrections-2026-08-06.md` 대본 정정 2호(판정 무관 3건→2건·3부 7번 folder-bot E2E 신설·마켓플레이스 회신)
- `/Users/Shared/harness-e2e-ct-folderbot012-2026-08-06.md`(0.1.2 검증 지시)·`harness-e2e-folderbot012-result-2026-08-06.md`(설치 세션 회신: 통과+덤 버그 2건)·`harness-e2e-reset39-result-2026-08-06.md`(§3.9 완료 회신)·`harness-e2e-ct-ssh-mcp-diag-2026-08-06.md`(SSH 개설 지시)
- `.claude/settings.local.json`(이 프로젝트) ssh/scp harness-test@localhost 허용 규칙 4종
- `/Users/soonho/ai-folder/collab/CLAUDE.md` 봇 지침 블록에 다중 인원 채널 규칙 추가(마커 블록 내, 사용자 임시 아내 ID 규칙 276행~ 은 보존) — **적용은 collab 봇 재시작 후**
- harness-test 상설 접속: `ssh harness-test@localhost` (BatchMode 무암호) · 진단 스크립트 /tmp/ft-*.sh(harness-test측, 임시)
- `/Users/Shared/harness-e2e-script-corrections-2026-08-10.md` **정정 3호**(활성 이름 충돌 발견·0부 동명 세션 체크 추가·0.1.12 반영·첫 기동 스킵 별개 실존)
- `plugins/harness-installer/skills/configure-harness/SKILL.md` 예열 절(DISCORD_STATE_DIR 2줄)+폴백 절(동명 세션 확인) — 커밋 1f03739(0.1.12), 푸시 완료
- `plugins/harness-installer/.claude-plugin/plugin.json`·`.claude-plugin/marketplace.json` 0.1.12 범프(같은 커밋)
- harness-test `~/.zshrc` 맨 앞 compinit 선실행 블록(fpath에서 /usr/local/share/zsh* 제외) — 백업 `~/.zshrc.bak-compinit`
- harness-test 상태(8/11 새벽): `~/discord-harness` 설치 유지(0.1.12)·`~/folder-bot-e2e` pair 완료·`~/.harness-e2e-backup` 토큰 백업 보존(foldertest 토큰은 백업에 없음 — 8/10 사용자가 직접 저장분 사용)·tmux는 ai+codex-live만
- folder-bot botctl 경로: `~/.claude/plugins/cache/folder-bot/folder-bot/0.1.5/skills/configure-bot/generator/botctl.py` (harness-test)
- `/Users/Shared/harness-e2e-script-notes-2026-08-11.md` **대본 처리 노트**(영상 준비 세션 인계 정본): ⓪토큰 노출 프레임 = 편집 블러+게시 직전 Reset Token ①첫 기동 스킵=Claude Code 본체 결함·재기동 1회 수렴·폴백 서사화 ②Antigravity 사용량 미표시=해당 계정 실사용 이력 필요(환경 조건, 결함 아님) ③리추얼 표준 순서 ④파일 구성(_폐기테이크 포함)·정정 2·3호 포인터
- `/Users/Shared/harness-e2e-recordings/` 최종 구성: 성공본 2(리네임) + 포탈 소스 2(한글명, 사용자 촬영) + `_폐기테이크/` 7개
- `/Users/Shared/harness-e2e-recordings/2026-08-11 14-04-29.mov` foldertest 세그먼트 녹화(14:04~14:43, 464MB)
- `docs/issues/2026-08-12-claude-code-channel-lease-silent-skip.md` #9 이슈 초안(영어 본문 + 게시 전 확인 3건 절 — 게시 시 하단 한국어 절 삭제)
- Hostinger 호스트: `/etc/systemd/system/claude-bridge.service` + `/usr/local/sbin/claude-bridge-watch.sh`(ensure 4세션, docker events 감시 — 로컬 사본은 세션 scratchpad라 소멸, 정본은 서버)
- 상류 `~/ai-folder/dev/codex-discord/src/rollout.mjs` extractAgentMessages를 response_item(role=assistant, content output_text join) 매처로 교체 + `test/rollout.test.mjs`(픽스처·tail 테스트 신포맷화, 구포맷 event_msg 공존 시 중복 없음 검증) + `test/fixtures/rollout-sample.jsonl`(0.149 형태 response_item 줄 추가) — 커밋 f09c7fc, 태그 v0.1.5 푸시
- `plugins/harness-installer/skills/configure-harness/generator/pins.json` codex-discord v0.1.4→v0.1.5 + `plugins/harness-installer/.claude-plugin/plugin.json`·`.claude-plugin/marketplace.json` 0.1.13 범프 — 커밋 fed3851 푸시
- Hostinger 컨테이너(/opt/data): `.profile`·`.bashrc`(LANG=C.UTF-8, PATH: .local/bin·.bun/bin) / `.local/bin/{claude,agy}`·codex(npm prefix) / `discord-bot/.discord-state/{.env,access.json}` / `codex-discord/{.env,.env.gemini}`(v0.1.4, node --env-file로 기동) / `.codex/auth.json`(맥 복사본) / 작업폴더 `codex-workspace`·`agy-workspace`
- 8/28 zzukumi 봇 해제로 고친 파일: `~/.config/folder-bot/bots.json`(zzukumi 항목 삭제) / `~/ai-folder/youtube-members/zzukumi/CLAUDE.md`(마커 블록만 제거) / `~/Library/LaunchAgents/com.folder-bot.zzukumi.plist` 삭제 — `.discord-state`·SESSION.md 등 폴더 데이터는 무접촉 보존
- 8/26 서버 이설로 고친 파일(전부 원본 옆 `.bak-move` 백업): `~/.claude/channels/discord/access.json`(수다 채널 1529498215651741706→1542142111862751314, 나머지 5개 유지) / `~/ai-folder/dev/discord-multiagent/.discord-state/access.json` / `~/ai-folder/collab/.discord-state/access.json` / `~/ai-folder/youtube/search-youtube-contents/.discord-state/access.json` / `~/ai-folder/dev/codex-discord/.env`(TUI_CHANNEL_ID·CHANNEL_IDS) / `~/ai-folder/dev/codex-discord/.env.gemini`(CHANNEL_IDS·NAME_TRIGGER_CHANNEL_IDS) / `~/.config/usage-coach/discord.json`(웹훅 URL) / `~/.config/usage-coach/discord-state.json`(message_id 리셋)
- 9/2 세션이 고친 파일: 이 레포는 `SESSION.md`만. 레포 밖은 봇 4개 폴더의 SESSION.md(각 봇이 자기 손으로 갱신)·`~/.claude/logs/bot-restart.log`(추가만)
- 9/3 세션이 고친 파일: 이 레포는 `SESSION.md`만. 상류 `~/ai-folder/dev/codex-discord/{src/index.mjs,src/rollout.mjs,src/tmux.mjs,test/rollout.test.mjs,test/tmux.test.mjs}` 커밋 7d4e6e2 푸시 + 그 레포 SESSION.md 결정 기록 1줄 추가(미커밋)

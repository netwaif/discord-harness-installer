# discord 하네스 통합 설치기 설계 (v1)

2026-08-03~04 브레인스토밍에서 사용자(컨트롤타워) 승인을 받은 설계. 매뉴얼 v2.2
16장(38쪽)을 configure-harness 스킬 하나 + 결정적 엔진으로 대체한다.
훅: "매뉴얼 16장이 스킬 하나가 됐습니다."

## 목표

- **대체 대상**: `~/VSCodeWorkspace/discord-multiagent-manual/` (v2.2, 16장) —
  설치기의 검증 기준이기도 하다.
- **진단**: 현행 매뉴얼의 "AI 지침 붙여넣기" 구조(예: 7장 — post-as.sh 등을
  지침으로 붙여넣어 AI가 그 자리에서 창작)는 과도기 산물로, 모델 즉흥 구현 편차가
  약점이다. v1은 이를 **정본 파일 복사와 정본 스크립트 위임**으로 대체한다.
- **수동 상한**: 디스코드 포탈 단계(서버·채널 생성, 봇 앱 4개 생성·인텐트·토큰·초대)는
  기술적으로 제거 불가 — folder-bot식 번호 안내 + 완료 대기가 상한이다.
- **실증 근거**: loadout · multi-agent-starter · folder-bot(botctl)에서 3회 반복된
  패턴 + 코덱스 마켓플레이스 호환 E2E 성공(2026-08-02 — `codex plugin marketplace
  add`가 클로드 형식 marketplace.json을 그대로 소비).

## 확정 결정 (전부 사용자 승인, 2026-08-03~04)

1. **마켓플레이스 통합**: 이 레포의 marketplace.json에는 새 harness-installer
   플러그인 1개만 등재. 기존 두 플러그인(multi-agent-starter, folder-bot)은 각자
   레포가 정본으로 유지되고, 통합 스킬이 전체 순서를 오케스트레이션한다.
   - 조건 ①: 기존 플러그인 설치는 안내문에 그치지 않는다 — 통합 스킬(엔진)이
     `claude/codex plugin marketplace add` + install을 **직접 실행**하고, 실패
     지점만 수동 폴백 명령 출력으로 처리한다.
   - 조건 ②: doctor에 starter·folder-bot **버전 호환 검사**를 넣어 "설치기는
     최신인데 부품이 낡은" 고장을 감지한다.
2. **코드 수급 = git clone**: 엔진이 github.com/netwaif 공개 3레포를 clone/pull.
   - 조건: clone한 각 레포의 커밋/태그를 락파일에 기록하고 doctor 호환 검사와
     연결한다. 본체 HEAD 파손 대비 **검증된 조합 핀(태그 기준, pins.json)**을
     설치기 쪽에 유지한다.
   - 번들 방식은 정본 이중화라 기각. 혼합 방식은 오프라인이 실사용 시나리오가
     아니라 기각.
3. **호스트 범위 = Claude 주력 + Codex 호환 유지**: 설치 경로·주 E2E는 Claude
   Code 기준. marketplace.json·SKILL.md는 코덱스가 소비 가능한 형태 유지
   (AskUserQuestion 의존 금지 등 folder-bot 전례).
   - 조건: **코덱스 스모크 E2E 1회(설치→기동→응답 확인 수준)를 릴리즈 게이트에
     포함**한다. 근거: v2.2 매뉴얼·대본에서 "코덱스만 쓰는 분도 두 줄 설치"를 이미
     공개 약속했으므로, 검증 없는 호환 주장을 남기지 않는다. 그 이상의 코덱스 전용
     최적화·심층 검증만 v1 범위 밖.
4. **긱님(geek7942) custom registry 요청은 별도 스펙으로 분리**: backends.json
   병합 구조(원본 목록 + `_local` 사용자 목록, update 보존) 설계는 MultiAgent
   레포의 별도 스펙에서 다룬다. 이 스펙에는 인터페이스 수준만 명시 —
   **"설치기는 사용자 워커를 보존하는 update를 전제로 한다."**
   - 조건: 분리의 최대 위험은 잊히는 것 — "함께 검토하겠다"는 공개 답변(2026-08-03)
     약속이 걸려 있으므로, 본 스펙의 후속 작업 및 SESSION.md 다음 단계에
     "MultiAgent 레포 custom registry 별도 스펙 착수"를 명시 기록한다(아래 후속
     작업 절).
5. **엔진 두께 = A안 위임 오케스트레이터**: 엔진은 다른 곳에 정본이 없는 접합부만
   직접 담당하고, 실제 설치 동작은 각 레포의 정본 스크립트에 위임한다. 약점 2개를
   설계로 흡수한다 — (약점 1) usage-coach에 설치 스크립트가 없음 → 상류 선행
   작업으로 신설. (약점 2) 레포 간 스크립트 시그니처가 암묵 계약이 됨 → doctor의
   위임 계약 방어로 상쇄(아래 검증 절).
6. **clone = 소스 저장소 방식 (b)**: clone은 작업 폴더가 아니라 별도 위치의 소스
   저장소로 두고, 작업 폴더는 starter가 스캐폴드한 뒤 디스코드 층만 clone본에서
   얹는다(오버레이).
   - 근거(정정본): 매뉴얼 5→7장 구조와의 일치가 아니라, **v3가 약점으로 진단한
     "즉흥 구현 편차"(7장의 지침 붙여넣기→AI 창작)를 정본 파일 복사로 대체하는
     개선**이기 때문이다.
   - 조건: "무엇을 얹는가"(scripts 4종·CLAUDE.md 디스코드 블록·`.env.example`·
     `.mcp.json` 등) **오버레이 목록/스크립트의 정본을 하네스 레포 쪽에 신설**한다
     (상류 선행 작업 2건째).

## 설치 대상 3레포 (정본)

| 대상 | 로컬 정본 | 원격 |
|---|---|---|
| 하네스 본체 | `~/ai-folder/dev/discord-multiagent` | github.com/netwaif/discord-multiagent (작업 브랜치 release-snapshot → main refspec 주의 — main 로컬 브랜치 없음) |
| 수다 브리지 | `~/ai-folder/dev/codex-discord` | github.com/netwaif/codex-discord |
| 대시보드 | `~/VSCodeWorkspace/usage-coach` | github.com/netwaif/usage-coach |

## 배포 형태

```
discord-harness-installer/
├── .claude-plugin/marketplace.json        # harness-installer 플러그인 1개만 등재
├── plugins/harness-installer/
│   ├── .claude-plugin/plugin.json
│   └── skills/configure-harness/
│       ├── SKILL.md                       # 오케스트레이션 절차 + 포탈 수동 단계 안내
│       └── generator/
│           ├── harnessctl.py              # 결정적 엔진 (단일 파일, 표준 라이브러리만)
│           └── pins.json                  # 검증된 조합 핀 (3레포 태그 + 플러그인 버전 범위)
├── tests/test_harnessctl.py               # HOME 격리 블랙박스 CLI 테스트
└── docs/superpowers/{specs,plans}/
```

### harnessctl.py 서브커맨드

| 커맨드 | 책임 | 성격 |
|---|---|---|
| `preflight` | macOS·tmux·node·claude/codex CLI·디스코드 플러그인 점검 | 읽기 전용 |
| `fetch` | 3레포 clone/pull(기본: pins.json 태그 체크아웃, `--latest`는 명시 시만) + 체크아웃 커밋/태그를 state.json에 기록 | 직접 |
| `plugins` | starter·folder-bot의 `plugin marketplace add` + install 직접 실행, 실패 시 수동 폴백 명령 출력 | 직접 |
| `pair` | `.bot-token-<봇>` 파일 4개 수령 → 하네스 `.env` 조립(0600) → 토큰 파일 삭제. 대시보드 웹훅 URL도 같은 원칙(파일 수령, 채팅 금지) | 직접 |
| `install` | 오버레이 적용 + 위임 호출: 브리지 `scripts/install.sh` · 자동기동 `scripts/install-autostart.sh` · usage-coach `scripts/install.sh`(신설) | 위임 |
| `verify` | 기동 후 봇 유형별 판정 소스 2종으로 연결 판정 (아래 검증 절) | 읽기 전용 |
| `doctor` | 종합 점검 + 버전 호환 검사 + 위임 계약 방어 (아래 검증 절) | 읽기 전용 |
| `remove` | 설치기가 만든 것만 제거, diff 0 (아래 remove 절) | 직접 |

### 상태 파일

- `~/.config/discord-harness/state.json` — 설치 루트 경로, 각 레포의 체크아웃
  커밋/태그, 단계별 완료 기록(재진입용), 오버레이 파일 해시, 설치 시각.
- `pins.json` (플러그인 내 동봉) — 이 설치기 릴리즈가 E2E로 검증한 조합:

```json
{
  "schema_version": 1,
  "repos": { "discord-multiagent": "<태그>", "codex-discord": "<태그>", "usage-coach": "<태그>" },
  "plugins": { "multi-agent-starter": "<호환 버전 범위>", "folder-bot": "<호환 버전 범위>" }
}
```

## 설치 흐름 (SKILL.md 오케스트레이션, 9단계)

folder-bot SKILL.md 전례(번호 안내·완료 대기·기본값 질주 금지) 승계.

| 단계 | 내용 | 담당 |
|---|---|---|
| 1 | `preflight` — 실패 시 여기서 중단·안내 | 엔진 |
| 2 | 설치 계획 질문 — 설치 루트, 봇 4개 이름, 대시보드·자동기동 여부(선택). AskUserQuestion 사용하되 코덱스 등 미지원 환경은 채팅 질문으로 대체 | 스킬 |
| 3 | 디스코드 포탈 수동 단계(상한) — 서버·채널, 봇 앱 4개·인텐트, 초대. 토큰 4개는 `pbpaste > .bot-token-<봇>`으로 파일화(채팅 붙여넣기 금지). 사용자가 끝났다고 할 때까지 대기 | 사용자 |
| 4 | `fetch` — 소스 저장소(`~/.local/share/discord-harness/repos/`)에 clone + 기록 | 엔진 |
| 5 | `plugins` — 기존 플러그인 2개 설치 직접 실행, 실패 시 수동 폴백 | 엔진 |
| 6 | 멀티에이전트 시스템 설치(매뉴얼 5장) — starter configure-multiagent 실행 → 디스코드 층 오버레이(7장) | 위임·엔진 |
| 7 | `pair` — `.env` 조립, 토큰 파일 삭제 | 엔진 |
| 8 | `install` — 브리지·대시보드·자동기동(선택) 위임 호출 | 위임 |
| 9 | `verify` — 연결 판정 → 마무리 안내(재시작 리추얼, 폴더 봇 12장은 선택으로 folder-bot 스킬 안내, doctor 사용법, 디스코드에서 실제 응답 확인 요청) | 엔진 |

## 오버레이 계약 (상류 선행 작업 2건째)

- 하네스 레포에 **오버레이 목록 정본**(manifest — 예: `install/overlay-manifest.json`,
  경로는 플랜에서 확정)을 신설한다. 내용: 작업 폴더에 얹을 파일 목록 — scripts
  4종(`bot-up.sh`·`bot-restart.sh`·`post-as.sh` 등), CLAUDE.md 디스코드 블록,
  `.env.example`, `.mcp.json` 항목.
- 엔진은 manifest를 읽어 복사만 한다(창작 금지). manifest에는 `schema_version`을
  두고 doctor가 스키마 호환을 검사한다.
- 설치 시 각 오버레이 파일의 해시를 state.json에 기록한다(remove의 사용자 수정
  감지에 사용).

## 검증

### verify (설치 직후 판정)

판정 로직은 새로 발명하지 않고 기존 정본과 같은 기준을 쓴다.

1. LaunchAgent 로드 + tmux 세션 존재
2. **봇 유형별 판정 소스 2종** (실측 정본):
   - **클로드 계열 2봇**(오케스트레이터·수다 클로드): 디스코드 MCP 로그
     (`~/Library/Caches/claude-cli-nodejs/.../mcp-logs-plugin-discord-discord/`)
     연결 판정 — bot-up.sh와 동일 기준.
   - **브리지 경유 2봇**(코덱스·제미나이): 브리지 `logs/daemon*.log`의 "로그인:"
     줄 — folder-bot codex 엔진 판정과 동일 기준.
3. 브리지 데몬 생존(daemon.pid), 대시보드는 웹훅 시험 발사 1회
4. 최종 응답 확인(디스코드에서 봇에게 말 걸기)은 자동화 불가 — 스킬 마무리
   단계에서 사용자에게 확인 요청

### doctor (상시 점검, 읽기 전용, 항목별 OK/WARN/FAIL)

folder-bot doctor 전례 + 이번에 추가되는 두 축:

- **버전 호환 검사**: state.json(실제 설치된 커밋/태그) ↔ pins.json(검증 조합)
  대조. "설치기는 최신인데 부품이 낡음"과 역방향(사용자 임의 pull로 검증 조합보다
  앞섬) 모두 WARN. starter·folder-bot의 설치 버전도 호환 범위와 대조.
- **위임 계약 방어**: 위임 스크립트 3종(브리지 install.sh · 자동기동 ·
  usage-coach install.sh)과 오버레이 manifest의 존재·실행권한·스키마 버전 확인.
  상류가 계약을 바꾸면 실행 전에 doctor가 먼저 잡는다.
- 기존 축: 전제 도구, 토큰/페어링 상태, plist 로드, tmux 세션.

## 에러 처리

- 모든 서브커맨드는 **멱등** — 실패 후 재실행이 안전. state.json의 단계별 완료
  기록으로 스킬이 중단 지점부터 재진입.
- 실패 시 비-0 종료 + 원인과 다음 행동 한 줄. 스킬은 해당 단계에서 멈추고 수동
  폴백 안내(예: marketplace add 실패 → 수동 명령 출력).
- 위임 스크립트 실패는 종료 코드 전파 + 로그 위치 안내만 — 엔진이 대신 고치지
  않는다(정본 책임 경계).
- 기존 설치 감지 시 덮어쓰기 거부, `--force`로만(folder-bot pair 전례).
- 토큰 파일은 pair 성공 즉시 삭제. `.env` 0600. 비밀은 어떤 경로로도 채팅에
  올리지 않는다.

## remove 의미론과 diff 0 보장

**원칙: 설치기가 만든 것만 지운다. 사용자 데이터는 기본 보존**(folder-bot 전례 —
페어링 보존, 지침 파일만 원상복구).

| 대상 | 처리 |
|---|---|
| LaunchAgent plist, 소스 저장소(clone), state.json, `.mcp.json` 추가 항목 | 제거 (설치기가 만든 것) |
| CLAUDE.md 마커 블록 | 블록만 제거, 블록 외 원문 보존 |
| 오버레이로 얹은 파일 | 설치 시 기록한 해시와 대조 — 일치하면 제거, 불일치(사용자 수정)면 보존 + WARN |
| `tasks/` · SESSION.md · `.env` · 페어링(`.discord-state`) | 기본 보존 (사용자 데이터·비밀) |
| `~/.local/bin`의 bot-up/bot-restart | 보존 (folder-bot과 공유 자원, 무해) |
| starter·folder-bot 플러그인과 그 산출물 | 범위 밖 — 각자의 제거 경로 안내만 |
| 브리지·대시보드 | 상류 제거 스크립트 호출로 위임 — 상류 계약에 "설치 스크립트는 대응 제거 경로를 가진다" 포함(없으면 상류 선행 작업에 계상) |

- **LaunchAgent 처리 방식**: `launchctl bootout`은 쓰지 않는다(2026-07-31 실측:
  부팅 시 그 job이 tmux 서버를 띄운 경우 프로세스 그룹째 킬 위험). folder-bot
  stop 전례대로 **tmux 세션 종료 + plist 파일 제거**(다음 부팅부터 미적용) 방식.
- **diff 0의 정의(한정)**: "설치 전 존재하던 파일은 remove 후 원문 동일, 설치기가
  새로 만든 파일은 제거된다(사용자가 수정한 오버레이 파일 제외)". 보장 범위는
  **설치기가 만든 것**으로 한정한다. 검증은 folder-bot 방식 — 원문 문자열 저장 →
  설치 → 제거 → 동등 비교.

## 상류 선행 작업 (이 스펙의 전제)

1. **usage-coach**: LaunchAgent 설치 스크립트 `scripts/install.sh` 신설(현재 README
   권장만 있고 자동화 없음) + 대응 제거 경로.
2. **discord-multiagent(하네스)**: 오버레이 manifest 정본 신설(위 오버레이 계약 절).
3. **공통 계약**: 위임 설치 스크립트는 대응 제거 경로를 가진다(브리지 install.sh에
   없으면 추가 계상).

## 테스트 전략

folder-bot 전례 승계 — `subprocess.run([python, harnessctl, ...], env={HOME: tmp})`
HOME 격리 블랙박스 CLI 테스트. 이를 위한 테스트 계약 2개를 엔진에 내장:

- clone 대상 URL을 환경변수/인자로 오버라이드 가능 → 테스트는 tmp에 `git init`한
  가짜 3레포 fixture 사용(네트워크 불요)
- 위임 스크립트·기동 명령은 dry-run 모드로 명령 문자열만 검증(botctl start 전례)

테스트 카테고리: preflight 판정 / fetch(핀 체크아웃·기록·멱등) / pair(`.env`
조립·0600·토큰 파일 삭제·기존 설치 보호) / plugins(명령 문자열·수동 폴백 출력) /
install(위임 호출 순서·오버레이 해시 기록) / verify(가짜 로그 fixture로 판정 소스
2종 각각) / doctor(핀 불일치 WARN·위임 계약 파일 누락 WARN) / remove(diff 0 문자열
비교·사용자 수정 오버레이 보존·bootout 미사용·plist 파일 제거 확인) / state
재진입(중단 후 재실행).

## 릴리즈 게이트 (pins.json 갱신 조건 — 전부 통과해야 릴리즈)

1. 자동 테스트 전체 통과 (diff 0 포함)
2. 클로드 4봇 E2E 1회: 설치→기동→디스코드 실제 응답 확인
3. 코덱스 스모크 E2E 1회: 설치→기동→응답 확인 수준
4. 통과한 3레포 태그 + 플러그인 버전 조합을 pins.json에 기록 후 릴리즈

**E2E 환경(사용자 수락)**: 별도 macOS 사용자 계정(LaunchAgent·HOME이 계정 단위
격리) + 테스트 디스코드 서버 + 테스트 봇 앱 4개. 1회 구축 후 게이트마다 재사용.
프로덕션 4봇이 도는 본 계정에서는 E2E를 돌리지 않는다.

## 비범위 (YAGNI)

- 코덱스 전용 최적화·심층 검증(스모크 E2E 1회만 게이트에 포함)
- backends.json 병합 구조 설계 — MultiAgent 레포 별도 스펙(아래 후속 작업)
- 오프라인/번들 설치
- 매뉴얼 v3 집필 자체(설치기가 대체할 대상이지 이 스펙의 산출물이 아님)
- 라우팅 문서·디스코드 이름표 확장(컨트롤타워 보류 권고, 2026-08-03)

## 후속 작업 (완료 조건에 포함)

- **MultiAgent 레포 custom registry 별도 스펙 착수** — 긱님(geek7942) 제안,
  "함께 검토하겠다" 공개 답변(2026-08-03) 약속. 1단계(등록부 병합: 원본 목록 +
  `_local` 사용자 목록, update 보존)만 우선. 스키마 변경 시 사용자 조각 호환성
  방어 필요. 이 설치기는 "사용자 워커를 보존하는 update"를 전제 인터페이스로만
  참조한다.

## 구현 순서 (folder-bot 전례)

1. 상류 선행 작업 2건(+제거 경로 계약) — 각 정본 레포에서
2. writing-plans로 구현 플랜 작성(TDD, Task별 실패 테스트 → 구현 → 커밋)
3. harnessctl.py + SKILL.md 구현
4. 릴리즈 게이트(자동 테스트 + 클로드 4봇 E2E + 코덱스 스모크) → pins.json 확정 → 릴리즈

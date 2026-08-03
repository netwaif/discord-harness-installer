# discord-harness-installer

디스코드 멀티에이전트 하네스 통합 설치기 — 매뉴얼 16장이 스킬 하나가 됐습니다.

## 설치

`claude` 안에서:

```
/plugin marketplace add netwaif/discord-harness-installer
```

그다음 `/plugin`으로 `harness-installer` 플러그인을 설치한다.

## 사용

새 대화에서 한마디만 하면 된다:

> 디스코드 하네스 설치해줘

나머지는 스킬(`configure-harness`)이 9단계로 이끈다 — preflight 점검 →
설치 계획 질문(설치 루트·봇 이름·대시보드·자동 기동) → **디스코드 개발자
포탈 수동 단계**(서버·채널 생성, 봇 앱 4개 생성·토큰 발급, 초대) → 정본
레포 fetch → 플러그인 설치 → 멀티에이전트 시스템 설치 → 페어링 → 실제
설치(오버레이+위임) → 연결 검증까지. **수동으로 손대야 하는 부분은 디스코드
개발자 포탈 단계뿐**이다(계정·토큰 발급은 남의 컴퓨터가 대신 할 수 없다) —
그 외 파일 조작·설치·페어링·검증은 전부 결정적 엔진 `harnessctl.py`가
멱등하게 수행한다.

설치가 끝나면 디스코드 작업 채널이 클로드 코드 오케스트레이터, 수다 채널이
클로드·코덱스·제미나이 잡담 상대가 된다. 상시 점검은 "하네스 점검해줘"
(`harnessctl.py doctor`), 제거는 "하네스 제거해줘"(`harnessctl.py remove` —
`.env`·페어링 상태·`tasks/`·`SESSION.md`·사용자 수정분은 보존).

## 검증 조합 핀

`plugins/harness-installer/skills/configure-harness/generator/pins.json`이
이 설치기가 실제로 테스트를 통과시킨 정본 3레포(discord-multiagent ·
codex-discord · usage-coach) 버전과 의존 플러그인(multi-agent-starter ·
folder-bot) 최소 호환 버전을 고정한다. 기본 `fetch`는 이 핀으로 체크아웃하고,
`doctor`는 설치된 버전이 핀에서 벗어나면 경고한다. 최신 버전을 원하면
`fetch --latest`로 명시적으로 우회할 수 있다(비검증 조합 — 문제가 생기면
핀 조합으로 되돌리는 편이 안전하다).

## 대체 범위

이 설치기는 기존 `multi-agent-manual` v2.2의 16개 장(디스코드 봇 생성부터
브리지·대시보드 설치, 페어링, 자동 기동, 제거까지)을 대체한다. 매뉴얼을
읽고 손으로 명령을 하나씩 치던 절차가 스킬 하나(`configure-harness`)로
들어왔다 — 남은 수동 작업은 디스코드 포탈에서 계정으로 해야 하는 부분뿐이다.

## 요구 사항

**macOS 전용.** launchctl(plist)·tmux·Homebrew 생태계에 의존하므로 리눅스·
윈도우는 지원하지 않는다. `preflight` 단계가 git·tmux·node·claude·codex 등
필수 도구를 점검하고 없는 항목의 설치 방법을 안내한다.

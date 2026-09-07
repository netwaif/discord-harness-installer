# 리눅스 서비스 층 구현 계획 (스펙: specs/2026-09-07-linux-service-layer-design.md)

각 태스크 = 저장소 하나. TDD: 리눅스 분기 테스트(HARNESS_OS=Linux DRY_RUN=1 HOME=tmp) 먼저 → 구현 → 기존 테스트 포함 통과 → 커밋·태그.

1. usage-coach `scripts/install.sh`·`uninstall.sh` — Linux: `usage-coach-dashboard.service`+`.timer`. 테스트 `tests/test_install_scripts.py`에 `test_install_linux_writes_units`·`test_uninstall_linux_removes_units`. 태그 v0.1.3.
2. codex-discord `scripts/install.sh`·`uninstall.sh` — Linux: daemon/gemini(simple)·tui(oneshot) 유닛. 테스트 `test/uninstall.test.sh` 리눅스 케이스 + `test/install-linux.test.sh`(DRY_RUN 유닛 생성). 태그 v0.1.7.
3. discord-multiagent `scripts/install-autostart.sh`·`bot-restart.sh` — Linux: orchestrator 유닛+`.tmux-cmd` 사이드카, bot-restart가 사이드카·`~/.cache` 경로 사용. 테스트 `tests/scripts.test.sh`에 리눅스 케이스. 태그 v0.1.2.
4. discord-harness-installer `harnessctl.py` — preflight OS·systemd·WSL2, `service_file()`, `write_chat_unit`, doctor/verify/remove 경로, judge_mcp 캐시 경로, 힌트 문구; `SKILL.md` 토큰 저장·리눅스 절; `pins.json`·`plugin.json` 0.1.15. 테스트 `tests/test_harnessctl.py`에 리눅스 케이스(monkeypatch sys.platform/HOME).
5. VM 실측(스펙 검증 2) → agentlayer `docs/linux-wsl2-verification.md` 6차 기록.

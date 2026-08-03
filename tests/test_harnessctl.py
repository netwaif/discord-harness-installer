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

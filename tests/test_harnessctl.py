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

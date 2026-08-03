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

def test_plugins_dry_run_prints_commands(tmp_path):
    r = run(tmp_path, "plugins", "--dry-run")
    assert r.returncode == 0
    assert "claude plugin marketplace add netwaif/multi-agent-starter" in r.stdout
    assert "claude plugin install multi-agent-starter@multi-agent-starter" in r.stdout
    assert "claude plugin marketplace add netwaif/folder-bot" in r.stdout
    assert "claude plugin install folder-bot@folder-bot" in r.stdout

def test_plugins_codex_host(tmp_path):
    r = run(tmp_path, "plugins", "--host", "codex", "--dry-run")
    assert "codex plugin marketplace add netwaif/folder-bot" in r.stdout

def test_plugins_failure_prints_manual_fallback(tmp_path):
    # PATH 를 비워 claude 실행 자체가 불가능한 상황 → 수동 폴백 안내 + exit 1
    r = run(tmp_path, "plugins", env_extra={"PATH": "/usr/bin:/bin"})
    assert r.returncode == 1
    assert "수동 폴백" in r.stdout

def _token_files(work):
    for role in ("orch", "claude", "codex", "gemini"):
        (work / f".bot-token-{role}").write_text(f"tok-{role}\n")

def _pair(tmp_path, work, *extra):
    return run(tmp_path, "pair", "--work-dir", str(work),
               "--work-channel-id", "111", "--chat-channel-id", "222",
               "--approver-user-id", "999", *extra)

def test_pair_assembles_env_and_state_dirs(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    _token_files(work)
    r = _pair(tmp_path, work)
    assert r.returncode == 0, r.stderr
    env = (work / ".env").read_text()
    assert "WORK_CHANNEL_ID=111\n" in env and "CHAT_CHANNEL_ID=222\n" in env
    assert "APPROVER_USER_ID=999\n" in env and "ORCH_BOT_TOKEN=tok-orch\n" in env
    assert "CLAUDE_BOT_TOKEN=tok-claude\n" in env and "GEMINI_BOT_TOKEN=tok-gemini\n" in env
    assert oct((work / ".env").stat().st_mode)[-3:] == "600"
    orch = json.loads((work / ".discord-state/access.json").read_text())
    assert orch["groups"]["111"]["requireMention"] is False
    assert (work / ".discord-state/.env").read_text() == "DISCORD_BOT_TOKEN=tok-orch\n"
    chat = json.loads((work / "chat/.discord-state/access.json").read_text())
    assert chat["groups"]["222"]["requireMention"] is True
    assert (work / "chat/.discord-state/inbox").is_dir()
    for role in ("orch", "claude", "codex", "gemini"):
        assert not (work / f".bot-token-{role}").exists()   # 토큰 파일 즉시 삭제
    assert "tok-orch" not in r.stdout                        # 비밀 stdout 금지

def test_pair_refuses_overwrite_without_force(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    _token_files(work)
    assert _pair(tmp_path, work).returncode == 0
    _token_files(work)
    r = _pair(tmp_path, work)
    assert r.returncode != 0
    assert "tok-orch" in (work / ".env").read_text()   # 기존 보존
    _token_files(work)
    assert _pair(tmp_path, work, "--force").returncode == 0

def test_pair_webhook_file(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    _token_files(work)
    wf = work / ".webhook-url"; wf.write_text("https://example.invalid/hook\n")
    r = _pair(tmp_path, work, "--webhook-url-file", str(wf))
    assert r.returncode == 0, r.stderr
    cfg = json.loads((tmp_path / ".config/usage-coach/discord.json").read_text())
    assert cfg["webhook_url"] == "https://example.invalid/hook"
    assert not wf.exists()

def test_pair_missing_token_file_names_it(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    (work / ".bot-token-orch").write_text("t\n")
    r = _pair(tmp_path, work)
    assert r.returncode != 0 and ".bot-token-claude" in r.stderr

def _overlay(tmp_path, work):
    return run(tmp_path, "install", "--work-dir", str(work), "--phase", "overlay")

def test_overlay_copies_manifest_files(tmp_path):
    fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    r = _overlay(tmp_path, work)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (work / "scripts/bot-up.sh").read_text() == STUB
    assert os.access(work / "scripts/bot-up.sh", os.X_OK)
    assert (work / ".env.example").exists()
    assert (work / "chat/CLAUDE.md").exists()               # seed
    st = json.loads((tmp_path / ".config/discord-harness/state.json").read_text())
    assert "scripts/bot-up.sh" in st["overlay"]
    assert len(st["overlay"]["scripts/bot-up.sh"]) == 64    # sha256 기록

def test_overlay_claude_block_and_mcp_merge_nondestructive(tmp_path):
    fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    original = "# 내 규칙\n\n소중한 내용.\n"
    (work / "CLAUDE.md").write_text(original)
    (work / ".mcp.json").write_text(json.dumps({"mcpServers": {"mine": {"command": "x"}}}))
    (work / "SESSION.md").write_text("세션 기록\n")
    r = _overlay(tmp_path, work)
    assert r.returncode == 0, r.stdout + r.stderr
    text = (work / "CLAUDE.md").read_text()
    assert original in text and "<!-- discord-multiagent:start -->" in text
    mcp = json.loads((work / ".mcp.json").read_text())
    assert "mine" in mcp["mcpServers"] and "codex" in mcp["mcpServers"]
    assert (work / "SESSION.md").read_text() == "세션 기록\n"   # SESSION.md 무접촉
    st = json.loads((tmp_path / ".config/discord-harness/state.json").read_text())
    assert st["mcp_added"] == ["codex"]
    r2 = _overlay(tmp_path, work)                               # 멱등
    assert r2.returncode == 0
    assert (work / "CLAUDE.md").read_text() == text

def test_overlay_seed_preserves_user_edit(tmp_path):
    fetched(tmp_path)
    work = tmp_path / "work"; work.mkdir()
    _overlay(tmp_path, work)
    (work / "chat/CLAUDE.md").write_text("사용자 수정본\n")
    _overlay(tmp_path, work)
    assert (work / "chat/CLAUDE.md").read_text() == "사용자 수정본\n"

def test_overlay_without_fetch_fails_with_hint(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    r = _overlay(tmp_path, work)
    assert r.returncode != 0 and "fetch" in r.stderr

#!/usr/bin/env python3
"""discord-harness 통합 설치기 결정적 엔진 — 매뉴얼 16장을 대체한다.

경로는 전부 HOME 환경변수 기준(테스트가 HOME을 tmpdir로 돌린다).
A안 위임 오케스트레이터: 정본이 없는 접합부만 직접, 설치 동작은 정본 스크립트에 위임.
오버레이는 manifest를 읽어 복사만 한다(창작 금지).
launchctl로 job을 내리지 않는다(부팅 job은 프로세스 그룹째 킬 위험, 2026-07-31 실측)
— plist 파일 생성/삭제 + tmux kill-session만. (Task 13이 소스 전체에 해당 launchctl
서브커맨드 문자열이 없음을 정적 검증하므로 이 파일에 그 단어를 쓰지 말 것.)
비밀(토큰·웹훅)은 파일로만 수령하고 stdout에 출력하지 않는다.
"""
import argparse, hashlib, json, os, plistlib, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = 1
ROLES = ("orch", "claude", "codex", "gemini")
REPO_NAMES = ("discord-multiagent", "codex-discord", "usage-coach")
PLUGINS = (("multi-agent-starter", "netwaif/multi-agent-starter"),
           ("folder-bot", "netwaif/folder-bot"))
BLOCK_START = "<!-- discord-multiagent:start -->"
BLOCK_END = "<!-- discord-multiagent:end -->"
ORCH_PLIST_LABEL = "com.discord-multiagent.orchestrator"
CHAT_PLIST_LABEL = "com.discord-harness.chat-claude"
CHAT_SESSION = "chat-claude"

def home() -> Path: return Path(os.environ["HOME"])
def config_dir() -> Path: return home() / ".config/discord-harness"
def state_path() -> Path: return config_dir() / "state.json"
def repos_dir() -> Path: return home() / ".local/share/discord-harness/repos"
def harness_repo() -> Path: return repos_dir() / "discord-multiagent"
def bridge_repo() -> Path: return repos_dir() / "codex-discord"
def coach_repo() -> Path: return repos_dir() / "usage-coach"
def now() -> str: return datetime.now().isoformat(timespec="seconds")

def repo_url(name: str) -> str:
    base = os.environ.get("HARNESS_REPO_BASE")
    if base:
        return f"{base}/{name}"
    return f"https://github.com/netwaif/{name}.git"

def pins() -> dict:
    return json.loads((Path(__file__).resolve().parent / "pins.json").read_text())

def load_state() -> dict:
    if not state_path().exists():
        return {"schema_version": SCHEMA_VERSION, "work_dir": None,
                "repos": {}, "steps": {}, "overlay": {}, "mcp_added": []}
    return json.loads(state_path().read_text())

def save_state(st: dict) -> None:
    config_dir().mkdir(parents=True, exist_ok=True)
    state_path().write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n")

def run_git(args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

def find_tmux() -> str:
    for c in (shutil.which("tmux"), "/opt/homebrew/bin/tmux", "/usr/local/bin/tmux"):
        if c and Path(c).exists():
            return c
    sys.exit("오류: tmux를 찾을 수 없음 — brew install tmux")

def resolve_work_dir(a) -> Path:
    wd = getattr(a, "work_dir", None) or load_state().get("work_dir")
    if not wd:
        sys.exit("오류: 작업 폴더를 알 수 없음 — --work-dir 지정(또는 pair/install 선행)")
    return Path(wd).expanduser()

def cmd_preflight(a) -> None:
    fails = 0
    def rep(level, msg):
        nonlocal fails
        if level == "FAIL":
            fails += 1
        print(f"[{level}] {msg}")
    rep("OK" if sys.platform == "darwin" else "FAIL", "macOS")
    for tool, miss_level, hint in (
            ("git", "FAIL", "xcode-select --install"),
            ("tmux", "FAIL", "brew install tmux"),
            ("node", "FAIL", "brew install node (브리지는 Node 22+)"),
            ("claude", "FAIL", "https://claude.com/claude-code 설치"),
            ("codex", "FAIL", "npm i -g @openai/codex (수다 브리지 필수)"),
            ("agy", "WARN", "없으면 제미나이 봇만 빠짐")):
        found = shutil.which(tool)
        rep("OK" if found else miss_level, f"{tool}: {found or '없음 — ' + hint}")
    plug = home() / ".claude/plugins/cache/claude-plugins-official/discord"
    rep("OK" if plug.is_dir() else "FAIL",
        f"discord 플러그인: {plug if plug.is_dir() else '미설치 — claude 안에서 /plugin 으로 discord 설치'}")
    sys.exit(1 if fails else 0)

def cmd_fetch(a) -> None:
    pin_repos = pins()["repos"]
    repos_dir().mkdir(parents=True, exist_ok=True)
    st = load_state()
    for name in REPO_NAMES:
        dst = repos_dir() / name
        if not dst.exists():
            r = run_git(["clone", "--quiet", repo_url(name), str(dst)])
            if r.returncode != 0:
                sys.exit(f"오류: {name} clone 실패 — {r.stderr.strip()}\n"
                         f"다음 행동: 네트워크 확인 후 fetch 재실행(멱등)")
        else:
            run_git(["fetch", "--tags", "--quiet", "origin"], cwd=dst)
        if a.latest:
            head = run_git(["rev-parse", "--abbrev-ref", "origin/HEAD"], cwd=dst).stdout.strip()
            branch = head.split("/", 1)[1] if "/" in head else "main"
            run_git(["checkout", "--quiet", branch], cwd=dst)
            run_git(["pull", "--ff-only", "--quiet"], cwd=dst)
            ref = "latest"
        else:
            ref = pin_repos[name]
            r = run_git(["checkout", "--quiet", ref], cwd=dst)
            if r.returncode != 0:
                sys.exit(f"오류: {name} 핀 {ref} 체크아웃 실패 — {r.stderr.strip()}\n"
                         f"다음 행동: fetch --latest 로 우회하거나 pins.json 확인")
        commit = run_git(["rev-parse", "HEAD"], cwd=dst).stdout.strip()
        st["repos"][name] = {"ref": ref, "commit": commit}
        print(f"fetch: {name} @ {ref} ({commit[:8]})")
    st["steps"]["fetch"] = now()
    save_state(st)

def plugin_cmds(host: str) -> list[list[str]]:
    cmds = []
    for name, repo in PLUGINS:
        cmds.append([host, "plugin", "marketplace", "add", repo])
        cmds.append([host, "plugin", "install", f"{name}@{name}"])
    return cmds

def cmd_plugins(a) -> None:
    ok = True
    for argv in plugin_cmds(a.host):
        line = " ".join(argv)
        if a.dry_run:
            print(line)
            continue
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=120)
            failed, detail = r.returncode != 0, (r.stderr or r.stdout).strip()[:200]
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            failed, detail = True, str(e)
        if failed:
            ok = False
            print(f"[FAIL] {line} — {detail}")
            print(f"  수동 폴백: 터미널에서 `{line}` 직접 실행, 또는 {a.host} 대화에서 "
                  f"`/plugin marketplace add {argv[-1]}` 후 /plugin 으로 설치")
        else:
            print(f"[OK] {line}")
    if ok and not a.dry_run:
        st = load_state(); st["steps"]["plugins"] = now(); save_state(st)
    sys.exit(0 if ok else 1)

def read_token_file(work: Path, role: str) -> str:
    f = work / f".bot-token-{role}"
    if not f.exists():
        sys.exit(f"오류: 토큰 파일 없음 — {f}\n다음 행동: pbpaste > {f.name} && chmod 600 {f.name}")
    tok = f.read_text().strip()
    if not tok:
        sys.exit(f"오류: 토큰 파일이 비어 있음 — {f}")
    return tok

def write_state_dir(state_dir: Path, token: str, channel_id: str,
                    approver: str, require_mention: bool) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "inbox").mkdir(exist_ok=True)
    env = state_dir / ".env"
    env.write_text(f"DISCORD_BOT_TOKEN={token}\n")
    env.chmod(0o600)
    access = {"dmPolicy": "allowlist", "allowFrom": [approver],
              "groups": {channel_id: {"requireMention": require_mention, "allowFrom": [approver]}},
              "pending": {}}
    (state_dir / "access.json").write_text(json.dumps(access, ensure_ascii=False, indent=2) + "\n")

def cmd_pair(a) -> None:
    work = Path(a.work_dir).expanduser()
    env_path = work / ".env"
    if env_path.exists() and not a.force:
        sys.exit(f"오류: {env_path} 이미 존재 — 덮어쓰려면 --force")
    tokens = {role: read_token_file(work, role) for role in ROLES}
    env_path.write_text(
        f"WORK_CHANNEL_ID={a.work_channel_id}\n"
        f"CHAT_CHANNEL_ID={a.chat_channel_id}\n"
        f"APPROVER_USER_ID={a.approver_user_id}\n"
        f"ORCH_BOT_TOKEN={tokens['orch']}\n"
        f"CLAUDE_BOT_TOKEN={tokens['claude']}\n"
        f"CODEX_BOT_TOKEN={tokens['codex']}\n"
        f"GEMINI_BOT_TOKEN={tokens['gemini']}\n")
    env_path.chmod(0o600)
    write_state_dir(work / ".discord-state", tokens["orch"], a.work_channel_id,
                    a.approver_user_id, False)
    write_state_dir(work / "chat/.discord-state", tokens["claude"], a.chat_channel_id,
                    a.approver_user_id, True)
    if a.webhook_url_file:
        wf = Path(a.webhook_url_file).expanduser()
        if not wf.exists():
            sys.exit(f"오류: 웹훅 URL 파일 없음 — {wf}")
        uc = home() / ".config/usage-coach"
        uc.mkdir(parents=True, exist_ok=True)
        cfg_path = uc / "discord.json"
        cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        cfg["webhook_url"] = wf.read_text().strip()
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        cfg_path.chmod(0o600)
        wf.unlink()
    for role in ROLES:
        (work / f".bot-token-{role}").unlink()
    st = load_state()
    st["work_dir"] = str(work)
    st["steps"]["pair"] = now()
    save_state(st)
    print(f"페어링 완료: {env_path} (0600) + 상태 폴더 2벌, 토큰 파일 4개 삭제")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight", help="전제 도구 점검(읽기 전용)").set_defaults(fn=cmd_preflight)
    fp = sub.add_parser("fetch", help="정본 3레포 clone/pull (기본: 검증 조합 핀)")
    fp.add_argument("--latest", action="store_true")
    fp.set_defaults(fn=cmd_fetch)
    pp = sub.add_parser("plugins", help="starter·folder-bot 플러그인 직접 설치")
    pp.add_argument("--host", choices=("claude", "codex"), default="claude")
    pp.add_argument("--dry-run", action="store_true")
    pp.set_defaults(fn=cmd_plugins)
    rp = sub.add_parser("pair", help="토큰 파일 수령 → .env 조립(0600) → 토큰 파일 삭제")
    rp.add_argument("--work-dir", required=True)
    rp.add_argument("--work-channel-id", required=True)
    rp.add_argument("--chat-channel-id", required=True)
    rp.add_argument("--approver-user-id", required=True)
    rp.add_argument("--webhook-url-file")
    rp.add_argument("--force", action="store_true")
    rp.set_defaults(fn=cmd_pair)
    a = p.parse_args()
    a.fn(a)

if __name__ == "__main__":
    main()

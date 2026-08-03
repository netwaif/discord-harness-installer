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

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight", help="전제 도구 점검(읽기 전용)").set_defaults(fn=cmd_preflight)
    a = p.parse_args()
    a.fn(a)

if __name__ == "__main__":
    main()

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

def version_tuple(v: str) -> tuple:
    nums = re.findall(r"\d+", v)
    return tuple(int(x) for x in nums[:3]) or (0,)

def installed_plugin_version(name: str):
    base = home() / ".claude/plugins/cache" / name / name
    if not base.is_dir():
        return None
    vers = [d.name for d in base.iterdir() if d.is_dir()]
    return max(vers, key=version_tuple) if vers else None

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
                "repos": {}, "steps": {}, "overlay": {}, "mcp_added": [], "lines_added": {}}
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

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_manifest() -> dict:
    mp = harness_repo() / "install/overlay-manifest.json"
    if not mp.exists():
        sys.exit(f"오류: 오버레이 manifest 없음 — {mp}\n"
                 f"다음 행동: harnessctl.py fetch 선행(핀이 manifest 포함 버전인지 doctor 로 확인)")
    mf = json.loads(mp.read_text())
    if mf.get("schema_version") != SCHEMA_VERSION:
        sys.exit(f"오류: manifest schema_version {mf.get('schema_version')} ≠ {SCHEMA_VERSION}"
                 f" — 설치기 업데이트 필요")
    return mf

def apply_overlay(work: Path, st: dict) -> list[str]:
    mf = load_manifest()
    out = []
    for item in mf["overlay"]:
        src, dst = harness_repo() / item["src"], work / item["dst"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if item.get("merge") == "json-mcp-servers" and dst.exists():
            cur = json.loads(dst.read_text())
            add = json.loads(src.read_text())
            added = [k for k in add.get("mcpServers", {})
                     if k not in cur.setdefault("mcpServers", {})]
            for k in added:
                cur["mcpServers"][k] = add["mcpServers"][k]
            if added:
                dst.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
                st["mcp_added"] = sorted(set(st.get("mcp_added", []) + added))
                out.append(f"오버레이(병합): {dst} += {added}")
            continue
        if item.get("merge") == "append-lines" and dst.exists():
            cur_lines = dst.read_text().splitlines()
            cur_rstripped = {c.rstrip() for c in cur_lines}
            new_lines = [line for line in src.read_text().splitlines()
                        if line.rstrip() not in cur_rstripped]
            if new_lines:
                cur_lines.extend(new_lines)
                dst.write_text("\n".join(cur_lines) + "\n")
                added_rec = st.setdefault("lines_added", {})
                existing = added_rec.get(item["dst"], [])
                added_rec[item["dst"]] = existing + [l for l in new_lines if l not in existing]
                out.append(f"오버레이(줄 추가): {dst} += {len(new_lines)}줄")
            continue
        if not (dst.exists() and dst.read_bytes() == src.read_bytes()):
            shutil.copyfile(src, dst)
            out.append(f"오버레이: {dst}")
        dst.chmod(int(item.get("mode", "644"), 8))
        st["overlay"][item["dst"]] = sha256(dst)
    body = extract_block((harness_repo() / mf["claude_block"]["src"]).read_text())
    out += install_claude_block(work / "CLAUDE.md", body)
    return out

def apply_seeds(work: Path, st: dict) -> list[str]:
    out = []
    for item in load_manifest().get("seeds", []):
        src, dst = harness_repo() / item["src"], work / item["dst"]
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        st["overlay"][item["dst"]] = sha256(dst)
        out.append(f"시드: {dst}")
    return out

def extract_block(text: str) -> str:
    if BLOCK_START not in text or BLOCK_END not in text:
        sys.exit(f"오류: 정본 CLAUDE.md에 마커 블록 없음 ({BLOCK_START})")
    return text.split(BLOCK_START, 1)[1].split(BLOCK_END, 1)[0]

def install_claude_block(md: Path, body: str) -> list[str]:
    cur = md.read_text() if md.exists() else ""
    if BLOCK_START in cur:
        return []
    md.write_text(cur + f"\n{BLOCK_START}{body}{BLOCK_END}\n")
    return [f"CLAUDE.md 블록 설치: {md}"]

def remove_claude_block(md: Path) -> list[str]:
    if not md.exists():
        return []
    cur = md.read_text()
    if BLOCK_START not in cur or BLOCK_END not in cur:
        return []
    pre, rest = cur.split(BLOCK_START, 1)
    _, post = rest.split(BLOCK_END, 1)
    md.write_text(pre.rstrip("\n") + ("\n" if pre.strip() else "") + post.lstrip("\n"))
    return [f"CLAUDE.md 블록 제거: {md}"]

def parse_env(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out

def write_bridge_envs(work: Path) -> list[str]:
    if not (work / ".env").exists():
        sys.exit(f"오류: {work / '.env'} 없음 — pair 선행 필요(SKILL 7단계)")
    env = parse_env(work / ".env")
    chat = work / "chat"
    chat.mkdir(exist_ok=True)
    out = []
    plans = [(".env", env["CODEX_BOT_TOKEN"], "코덱스", []),
             (".env.gemini", env["GEMINI_BOT_TOKEN"], "제미나이",
              ["ENGINE=agy", "DATA_DIR=data-gemini",
               f"AGY_BIN={shutil.which('agy') or 'agy'}"])]
    for fname, token, trigger, extra in plans:
        p = bridge_repo() / fname
        if p.exists():
            continue  # 멱등 — 기존(사용자 수정 포함) 보존
        lines = [f"DISCORD_TOKEN={token}",
                 f"ALLOWED_USER_IDS={env['APPROVER_USER_ID']}",
                 f"CODEX_WORKDIR={chat}",
                 f"CHANNEL_IDS={env['CHAT_CHANNEL_ID']}",
                 f"NAME_TRIGGER_CHANNEL_IDS={env['CHAT_CHANNEL_ID']}",
                 f"TRIGGER_NAME={trigger}", *extra]
        p.write_text("\n".join(lines) + "\n")
        p.chmod(0o600)
        out.append(f"브리지 환경 조립: {p}")
    return out

def build_chat_cmd(work: Path) -> str:
    chat = work / "chat"
    path_esc = os.environ.get("PATH", "").replace("&", "&amp;")
    parts = [f"cd {chat}",
             f'export PATH="{path_esc}"',
             f"export DISCORD_STATE_DIR={chat}/.discord-state",
             f"exec {work}/scripts/bot-up.sh -n {CHAT_SESSION} --remote-control {CHAT_SESSION}"
             " --channels plugin:discord@claude-plugins-official"]
    return "/bin/zsh -lc '" + "; ".join(parts) + "'"

def chat_plist_path() -> Path:
    return home() / f"Library/LaunchAgents/{CHAT_PLIST_LABEL}.plist"

def write_chat_plist(work: Path) -> list[str]:
    p = chat_plist_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"Label": CHAT_PLIST_LABEL,
            "ProgramArguments": [find_tmux(), "new-session", "-d", "-s", CHAT_SESSION,
                                 build_chat_cmd(work)],
            "RunAtLoad": True}
    blob = plistlib.dumps(data)
    if p.exists() and p.read_bytes() == blob:
        return []
    p.write_bytes(blob)
    return [f"plist 생성: {p} (다음 부팅부터 수다 클로드 자동 기동)"]

def delegate(argv: list, cwd: Path, dry: bool, log_hint: str) -> None:
    line = " ".join(str(x) for x in argv)
    if dry:
        print(f"위임(dry-run): (cd {cwd}) {line}")
        return
    r = subprocess.run([str(x) for x in argv], cwd=cwd)
    if r.returncode != 0:
        sys.exit(f"오류: 위임 스크립트 실패(exit {r.returncode}) — {line}\n"
                 f"로그: {log_hint}\n다음 행동: 원인 해결 후 install 재실행(멱등)")

def mcp_log_dir(workdir: Path) -> Path:
    mangled = re.sub(r"[/.]", "-", str(workdir))
    return home() / "Library/Caches/claude-cli-nodejs" / mangled / "mcp-logs-plugin-discord-discord"

def judge_mcp(workdir: Path):
    d = mcp_log_dir(workdir)
    files = sorted(d.glob("*.jsonl")) if d.is_dir() else []
    text = "".join(f.read_text(errors="ignore") for f in files)
    if "Successfully connected" in text:
        return "OK", "MCP 연결 성공"
    if "Connection failed" in text:
        return "FAIL", "MCP 연결 실패 — 토큰 오입력·인텐트 미설정·초대 누락 확인"
    return "WARN", f"판정 로그 없음(미기동?): {d}"

def judge_bridge(logname: str):
    p = bridge_repo() / "logs" / logname
    if p.exists() and "로그인:" in p.read_text(errors="ignore"):
        return "OK", f"브리지 로그인 확인({logname})"
    return "FAIL", f"브리지 로그인 없음 — {p} 확인"

def cmd_doctor(a) -> None:
    fails = 0
    def rep(level, msg):
        nonlocal fails
        if level == "FAIL":
            fails += 1
        print(f"[{level}] {msg}")
    pn = pins()
    st = load_state()
    for name in REPO_NAMES:
        got = st.get("repos", {}).get(name)
        pin = pn["repos"][name]
        if not got:
            rep("WARN", f"{name}: fetch 기록 없음 — harnessctl.py fetch 필요")
            continue
        if got["ref"] != pin:
            rep("WARN", f"{name}: 설치 {got['ref']} ≠ 검증 조합 {pin} — 설치기·부품 버전 어긋남")
            continue
        cur = run_git(["rev-parse", "HEAD"], cwd=repos_dir() / name).stdout.strip()
        if cur and cur != got["commit"]:
            rep("WARN", f"{name}: HEAD가 기록과 다름(임의 pull?) — 검증 조합 이탈")
        else:
            rep("OK", f"{name}: {got['ref']}")
    for pname, _ in PLUGINS:
        v = installed_plugin_version(pname)
        need = pn["plugins"][pname]
        if v is None:
            rep("WARN", f"플러그인 {pname} 미설치 — harnessctl.py plugins 필요")
        elif version_tuple(v) < version_tuple(need):
            rep("WARN", f"플러그인 {pname} {v} < 호환 최소 {need}")
        else:
            rep("OK", f"플러그인 {pname} {v}")
    for p in (bridge_repo() / "scripts/install.sh", bridge_repo() / "scripts/uninstall.sh",
              coach_repo() / "scripts/install.sh", coach_repo() / "scripts/uninstall.sh",
              harness_repo() / "scripts/install-autostart.sh"):
        if not p.exists():
            rep("WARN", f"위임 계약 파일 없음: {p}")
        elif not os.access(p, os.X_OK):
            rep("WARN", f"위임 계약 실행권한 없음: {p}")
        else:
            rep("OK", f"위임 계약: {p.parent.parent.name}/{p.parent.name}/{p.name}")
    mp = harness_repo() / "install/overlay-manifest.json"
    if not mp.exists():
        rep("WARN", f"오버레이 manifest 없음: {mp}")
    else:
        sv = json.loads(mp.read_text()).get("schema_version")
        rep("OK" if sv == SCHEMA_VERSION else "FAIL",
            f"manifest schema_version {sv}" + ("" if sv == SCHEMA_VERSION else f" ≠ {SCHEMA_VERSION} — 설치기 업데이트 필요"))
    wd = getattr(a, "work_dir", None) or st.get("work_dir")
    if wd:
        work = Path(wd).expanduser()
        rep("OK" if (work / ".env").exists() else "WARN",
            f"페어링(.env): {'있음' if (work / '.env').exists() else '없음 — pair 필요'}")
        for label, p in ((ORCH_PLIST_LABEL, home() / f"Library/LaunchAgents/{ORCH_PLIST_LABEL}.plist"),
                         (CHAT_PLIST_LABEL, chat_plist_path())):
            rep("OK" if p.exists() else "WARN", f"plist {label}: {'있음' if p.exists() else '없음'}")
        for sess in ("orchestrator", CHAT_SESSION):
            alive = subprocess.run([find_tmux(), "has-session", "-t", sess],
                                   capture_output=True).returncode == 0
            rep("OK" if alive else "WARN", f"tmux 세션 {sess} {'생존' if alive else '없음'}")
    sys.exit(1 if fails else 0)

def cmd_remove(a) -> None:
    st = load_state()
    work = resolve_work_dir(a)
    tmux = find_tmux()
    for sess in ("orchestrator", CHAT_SESSION):
        subprocess.run([tmux, "kill-session", "-t", sess], capture_output=True)
    for p in (home() / f"Library/LaunchAgents/{ORCH_PLIST_LABEL}.plist", chat_plist_path()):
        if p.exists():
            p.unlink()
            print(f"plist 제거: {p}")
    for script, cwd in ((bridge_repo() / "scripts/uninstall.sh", bridge_repo()),
                        (coach_repo() / "scripts/uninstall.sh", coach_repo())):
        if script.exists():
            r = subprocess.run(["bash", str(script)], cwd=cwd)
            if r.returncode != 0:
                print(f"[WARN] 제거 스크립트 실패(exit {r.returncode}): {script} — 수동 확인 필요")
        else:
            print(f"[WARN] 제거 스크립트 없음(수동 확인 필요): {script}")
    for rel, saved in sorted(st.get("overlay", {}).items()):
        p = work / rel
        if not p.exists():
            continue
        if sha256(p) == saved:
            p.unlink()
            print(f"제거: {p}")
        else:
            print(f"[WARN] 사용자 수정 감지 — 보존: {p}")
    for line in remove_claude_block(work / "CLAUDE.md"):
        print(line)
    mcp_path = work / ".mcp.json"
    if st.get("mcp_added") and mcp_path.exists():
        cur = json.loads(mcp_path.read_text())
        for k in st["mcp_added"]:
            cur.get("mcpServers", {}).pop(k, None)
        mcp_path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
        print(f".mcp.json 항목 제거: {st['mcp_added']}")
    for rel, lines in st.get("lines_added", {}).items():
        p = work / rel
        if not p.exists():
            continue
        cur = p.read_text().splitlines()
        removed = False
        for line in lines:
            if line in cur:
                cur.remove(line)
                removed = True
        if removed:
            p.write_text("\n".join(cur) + ("\n" if cur else ""))
            print(f"줄 제거: {p} -= {len(lines)}줄")
    if repos_dir().exists():
        shutil.rmtree(repos_dir())
        print(f"소스 저장소 제거: {repos_dir()}")
    if state_path().exists():
        state_path().unlink()
    print("제거 완료 — 보존: .env·.discord-state·chat/(사용자 수정분)·tasks/·SESSION.md·~/.config/usage-coach/")

def cmd_verify(a) -> None:
    work = resolve_work_dir(a)
    fails = 0
    def rep(level, msg):
        nonlocal fails
        if level == "FAIL":
            fails += 1
        print(f"[{level}] {msg}")
    for label, wd in (("오케스트레이터", work), ("수다 클로드", work / "chat")):
        lvl, msg = judge_mcp(wd)
        rep(lvl, f"{label}: {msg}")
    bridge_specs = [("코덱스", "daemon.log", "data/daemon.pid")]
    if (bridge_repo() / ".env.gemini").exists():
        bridge_specs.append(("제미나이", "daemon-gemini.log", "data-gemini/daemon.pid"))
    else:
        rep("WARN", "제미나이: 브리지 .env.gemini 없음 — 미구성으로 건너뜀")
    for label, logname, pidrel in bridge_specs:
        lvl, msg = judge_bridge(logname)
        rep(lvl, f"{label}: {msg}")
        pid_p = bridge_repo() / pidrel
        alive = False
        if pid_p.exists():
            try:
                os.kill(int(pid_p.read_text().split()[0]), 0)
                alive = True
            except (ValueError, ProcessLookupError, PermissionError):
                pass
        rep("OK" if alive else "WARN",
            f"{label} 데몬 {'생존' if alive else '죽음/미기동'}: {pid_p}")
    for sess in ("orchestrator", CHAT_SESSION):
        alive = subprocess.run([find_tmux(), "has-session", "-t", sess],
                               capture_output=True).returncode == 0
        rep("OK" if alive else "WARN", f"tmux 세션 {sess} {'생존' if alive else '없음'}")
    for label, p in ((ORCH_PLIST_LABEL, home() / f"Library/LaunchAgents/{ORCH_PLIST_LABEL}.plist"),
                     (CHAT_PLIST_LABEL, chat_plist_path())):
        rep("OK" if p.exists() else "WARN", f"plist {label}: {'있음' if p.exists() else '없음'}")
    if not a.skip_webhook:
        cfg = home() / ".config/usage-coach/discord.json"
        if not cfg.exists():
            rep("WARN", f"웹훅 설정 없음: {cfg}")
        else:
            import urllib.request
            url = json.loads(cfg.read_text()).get("webhook_url", "")
            try:
                req = urllib.request.Request(
                    url, data=json.dumps({"content": "harness-installer verify: 웹훅 OK"}).encode(),
                    headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10)
                rep("OK", "웹훅 시험 발사 성공")
            except Exception as e:
                rep("FAIL", f"웹훅 발사 실패: {e}")
    if not fails:
        st = load_state(); st["steps"]["verify"] = now(); save_state(st)
    sys.exit(1 if fails else 0)

def cmd_install(a) -> None:
    st = load_state()
    work = Path(a.work_dir).expanduser() if a.work_dir else resolve_work_dir(a)
    st["work_dir"] = str(work)
    out = []
    if a.phase in ("overlay", "all"):
        out += apply_overlay(work, st)
        out += apply_seeds(work, st)
    if a.phase in ("delegate", "all"):
        for line in write_bridge_envs(work):
            print(line)
        delegate(["bash", bridge_repo() / "scripts/install.sh"], bridge_repo(),
                 a.dry_run, str(bridge_repo() / "logs"))
        if a.dashboard:
            delegate(["bash", coach_repo() / "scripts/install.sh"], coach_repo(),
                     a.dry_run, "~/.config/usage-coach/")
        if a.autostart:
            delegate(["bash", work / "scripts/install-autostart.sh"], work,
                     a.dry_run, "launchctl print gui/$(id -u)/" + ORCH_PLIST_LABEL)
            if a.dry_run:
                print(f"위임(dry-run): plist 생성 예정 — {chat_plist_path()}")
            else:
                for line in write_chat_plist(work):
                    print(line)
    for line in out:
        print(line)
    if not a.dry_run:
        st["steps"][f"install-{a.phase}"] = now()
    save_state(st)

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
    ip = sub.add_parser("install", help="오버레이 적용 + 위임 설치 호출")
    ip.add_argument("--work-dir")
    ip.add_argument("--phase", choices=("overlay", "delegate", "all"), default="all")
    ip.add_argument("--dashboard", action="store_true")
    ip.add_argument("--autostart", action="store_true")
    ip.add_argument("--dry-run", action="store_true")
    ip.set_defaults(fn=cmd_install)
    vp = sub.add_parser("verify", help="기동 후 연결 판정(판정 소스 2종, 읽기 전용)")
    vp.add_argument("--work-dir")
    vp.add_argument("--skip-webhook", action="store_true")
    vp.set_defaults(fn=cmd_verify)
    dp = sub.add_parser("doctor", help="종합 점검 + 버전 호환 + 위임 계약 방어(읽기 전용)")
    dp.add_argument("--work-dir")
    dp.set_defaults(fn=cmd_doctor)
    xp = sub.add_parser("remove", help="설치기가 만든 것만 제거(diff 0, 사용자 데이터 보존)")
    xp.add_argument("--work-dir")
    xp.set_defaults(fn=cmd_remove)
    a = p.parse_args()
    a.fn(a)

if __name__ == "__main__":
    main()

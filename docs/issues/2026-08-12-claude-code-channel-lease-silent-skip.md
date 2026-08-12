# [초안] Claude Code 본체 이슈 보고 (#9) — 게시 전 사용자 확인 필요

- 대상 레포: anthropics/claude-code (GitHub Issues)
- 상태: **초안** — 사용자 승인 후 게시
- 재료 정본: `/Users/Shared/harness-e2e-mcp-rootcause-2026-08-06.md`(E1~E6 격리 실험),
  `/Users/Shared/harness-e2e-script-corrections-2026-08-10.md`(활성 이름 충돌),
  SESSION.md 8/11 결정 기록(첫 기동 스킵·SIGINT 무리스)

---

## Title

Channel (Discord) MCP connection silently skipped — no log file, no error, no retry — when a session-name lease is held (stale lease after forced kill, ~90 min TTL; active same-name session under the same account never expires)

## Body

### Summary

When launching `claude` with Discord channel notifications and a session name, the
channel MCP connection is sometimes **silently skipped**: no MCP log file is created,
nothing is written to stderr, and there is no retry. The session otherwise starts
normally, so the operator has no way to tell the channel is dead until a message
goes unanswered.

We isolated three triggering conditions over multi-day E2E testing (details below).
The root mechanism appears to be a per-account, per-session-name **lease**:

1. **Stale lease after forced termination.** If a channel-connected session is
   killed forcefully (e.g. `tmux kill-session` / SIGKILL), the name keeps a lease
   for **~90 minutes** (measured). Any new session started with the same name
   during that window skips the channel connection attempt entirely — zero log
   output. Graceful exits (`/exit`, and also Ctrl+C / SIGINT — verified separately)
   do **not** leave a lease.
2. **Active same-name session under the same Claude account.** Two macOS user
   accounts on the same machine, logged into the same Claude subscription: while
   account A has an active session named `orchestrator`, a session with the same
   name on account B silently skips its channel connection. Unlike the stale
   lease, this **never expires** — waiting does not help. Ending account A's
   session (`/exit`) and restarting B's session connects immediately.
3. **First-launch skip with no conflict at all.** Reproduced repeatedly (including
   via `launchctl kickstart` on a clean production setup): the very first launch
   after boot/install sometimes skips silently even with no same-name session and
   no stale lease. One restart of the session converges (connects in <1.5 s).

### Environment

- Claude Code **2.1.222**, macOS (Darwin 23.6), launched inside tmux panes via
  launchd plists
- Sessions started with a session name and Discord channels enabled, with a
  per-session state dir (`DISCORD_STATE_DIR`)
- Same Claude (Max) account across two macOS users on one machine

### Isolation experiments (condensed)

| Time | Condition | Result |
|---|---|---|
| 08:29 | Boot launch, clean state | ✅ connects, "Channel notifications registered", MCP log exists |
| 08:53 | `tmux kill-session` on the connected session | (lease created here; the MCP server itself shut down cleanly on SIGINT per its log) |
| 08:53–10:18 | 5+ relaunches, **same name**, various flag combinations | ❌ all skipped — **no MCP log file created at all** |
| 10:05 | Same folder, **different name** | ✅ attempt made (an unrelated ENOENT error *was* logged — contrast with the silent case) |
| 10:28 | The exact original command that failed all morning | ✅ connects in 1.4 s (≈95 min after the kill → TTL expiry) |
| 10:43 | `/exit` graceful shutdown, relaunch same name after 10 s | ✅ connects immediately (graceful exit leaves no lease) |
| 8/10 22:51 | Cross-account test: ended account A's same-name session, restarted account B's | ✅ immediately "Channel notifications registered" |

### Expected behavior

Any of these would make the failure diagnosable/operable:

- **Log the skip.** If a lease check fails, write *why* to the MCP log (e.g.
  "session name 'X' already leased (held since …); skipping channel connection")
  instead of creating no log at all. This is the core ask — the silent skip cost
  us days of blind debugging.
- Surface the conflict at startup (stderr/warning), and/or retry after the lease
  expires instead of permanently degrading.
- Release the lease on abnormal termination detection, or provide a way to
  inspect/clear leases.

### Impact

Unattended bot-style deployments (launchd + tmux) can come up "healthy" with a
dead channel and no signal. Recovery requires knowing the undocumented lease
semantics: never force-kill a connected session, check for same-name sessions
across OS accounts, and always restart once after first boot.

### Workarounds we use

- Always terminate channel-connected sessions gracefully (`/exit`; SIGINT is
  also safe) before any tmux/session cleanup.
- Pre-flight check for active same-name sessions (`ps aux | grep '\-n '`)
  across all OS users before launching.
- Treat one silent first launch as expected and restart the session once
  (pane-replacement restart), which reliably converges.

---

## 게시 전 확인 사항 (사용자용, 게시 시 삭제)

1. 위 영어 본문 그대로 게시해도 되는지 (프로덕션 구성 노출 수위: 하네스/봇 이름은
   일반화했고, 토큰·경로·개인 식별 정보는 없음)
2. 계정 정보 언급 수위: "same Max account across two macOS users" 표현 유지 여부
3. 게시 계정: 사용자 GitHub 계정(netwaif)으로 직접 게시할지, CT가 `gh issue create`로
   대행할지 (대행 시에도 게시 직전 최종 문구 확인)

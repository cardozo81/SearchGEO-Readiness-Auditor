"""Live runtime observation for the optional interactive console."""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import threading
import time

from searchgeo import __version__
from searchgeo.console_config import State, build_command, environment_summary, preflight, PROVIDERS


def render_header(state: State) -> None:
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")
    print("=" * 100)
    print(f"SearchGEO Readiness Auditor | versão {__version__}")
    print(f"Status      : {state.status}")
    print(f"URL         : {state.current_url}")
    print(f"Dispositivo : {state.current_device}")
    print(f"Operação    : {state.operation}")
    variables = environment_summary()
    print("Ambiente    : " + (" | ".join(variables) if variables else "nenhuma variável relevante configurada"))
    if state.error:
        print(f"Erro        : {state.error}")
    print("=" * 100)


def _audit_dirs(root: Path) -> set[Path]:
    return {path for path in root.iterdir() if path.is_dir() and path.name.startswith("AUD-")} if root.is_dir() else set()


def _new_workspace(root: Path, before: set[Path]) -> Path | None:
    found = _audit_dirs(root) - before
    return max(found, key=lambda path: path.stat().st_mtime_ns) if found else None


def _last_log_event(workspace: Path) -> dict[str, object] | None:
    path = workspace / "logs" / "audit.log"
    if not path.is_file():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines[-20:]):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def observe_workspace(workspace: Path, state: State) -> None:
    database = workspace / "audit.db"
    if database.is_file():
        try:
            connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=0.2)
            connection.row_factory = sqlite3.Row
            try:
                row = connection.execute(
                    "SELECT audit_id,status FROM audits ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    state.audit_id = str(row["audit_id"])
                    state.status = str(row["status"])
                snapshot = connection.execute(
                    """
                    SELECT p.normalized_url,ps.device
                    FROM page_snapshots ps JOIN pages p ON p.page_id=ps.page_id
                    ORDER BY ps.captured_at DESC LIMIT 1
                    """
                ).fetchone()
                if snapshot:
                    state.current_url = str(snapshot["normalized_url"])
                    state.current_device = str(snapshot["device"])
            finally:
                connection.close()
        except (sqlite3.Error, OSError):
            pass

    status = state.status.upper()
    if status == "ANALYZING":
        state.operation = (
            f"API:{state.ai_provider.upper()}"
            if state.ai_provider != "none"
            else "LOCAL:SEMANTIC_RULES"
        )
    elif status in {"DISCOVERING", "ACQUIRING"}:
        state.operation = "INTEGRATION:HTTP"
    elif status in {"COMPARING", "SCORING", "RECOMMENDING"}:
        state.operation = "LOCAL:RULES/SCORE"
    elif status == "REPORTING":
        state.operation = "LOCAL:REPORT"

    event = _last_log_event(workspace)
    if not event:
        return
    name = str(event.get("event") or "")
    if name == "M21_STARTED" and event.get("enabled"):
        state.status, state.operation = "WEB_PERFORMANCE", "API:PAGESPEED/CRUX"
    elif name == "M21_EXTERNAL_ATTEMPT":
        state.status = "WEB_PERFORMANCE"
        state.operation = f"API:{event.get('service', 'EXTERNAL')}"
        state.current_url = str(event.get("url") or state.current_url)
        state.current_device = str(event.get("device") or state.current_device)
    elif name == "M21_COMPLETED":
        state.status, state.operation = "FINALIZING", "LOCAL:REPORT_ENRICHMENT"
    elif name == "AUDIT_FAILED":
        state.status, state.operation = "FAILED", "LOCAL:ERROR"


def apply_runtime_provider_blocks(workspace: Path, state: State) -> None:
    database = workspace / "audit.db"
    if not database.is_file():
        return
    try:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=0.2)
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute(
                "SELECT provider_states FROM ai_audit_sessions ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            states = json.loads(str(row["provider_states"])) if row else {}
            if not isinstance(states, dict):
                return
            for provider, runtime_state in states.items():
                selection = str(provider).casefold()
                if runtime_state != "QUARANTINED_FOR_AUDIT" or selection not in PROVIDERS:
                    continue
                attempt = connection.execute(
                    """
                    SELECT status,error_class,http_status,error_type,error_code
                    FROM ai_provider_attempts
                    WHERE provider=? ORDER BY started_at DESC LIMIT 1
                    """,
                    (str(provider).upper(),),
                ).fetchone()
                if not attempt:
                    state.runtime_blocks[selection] = "provider quarantined"
                    continue
                parts = [str(attempt["error_class"] or attempt["status"] or "UNAVAILABLE")]
                if attempt["http_status"] is not None:
                    parts.append(f"HTTP {attempt['http_status']}")
                if attempt["error_code"]:
                    parts.append(str(attempt["error_code"]))
                elif attempt["error_type"]:
                    parts.append(str(attempt["error_type"]))
                state.runtime_blocks[selection] = "/".join(parts)
        finally:
            connection.close()
    except (sqlite3.Error, OSError, json.JSONDecodeError):
        pass


def _read_output(stream, output_queue: queue.Queue[str]) -> None:
    for line in iter(stream.readline, ""):
        output_queue.put(line.rstrip())
    stream.close()


def run_audit_from_console(state: State) -> int:
    state.error, state.output, state.audit_id = "", [], ""
    try:
        targets = preflight(state)
    except (OSError, ValueError, UnicodeError) as exc:
        state.status, state.operation, state.error = "PRECHECK_FAILED", "LOCAL:PRECHECK", str(exc)
        return 2

    state.current_url = targets[0] if len(targets) == 1 else f"{targets[0]} (+{len(targets)-1})"
    state.current_device = state.device.upper()
    state.status, state.operation = "STARTING", "LOCAL:PRECHECK_OK"
    root = Path(state.audits_root)
    before = _audit_dirs(root)
    output_queue: queue.Queue[str] = queue.Queue()
    try:
        process = subprocess.Popen(
            build_command(state),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ),
        )
    except OSError as exc:
        state.status, state.operation, state.error = "START_FAILED", "LOCAL:SUBPROCESS", str(exc)
        return 2
    assert process.stdout is not None
    thread = threading.Thread(target=_read_output, args=(process.stdout, output_queue), daemon=True)
    thread.start()
    workspace: Path | None = None

    while process.poll() is None:
        while True:
            try:
                line = output_queue.get_nowait()
            except queue.Empty:
                break
            if line:
                state.output.append(line)
                state.output[:] = state.output[-8:]
        workspace = workspace or _new_workspace(root, before)
        if workspace:
            observe_workspace(workspace, state)
        render_header(state)
        if state.audit_id:
            print(f"Audit ID    : {state.audit_id}")
        if state.output:
            print("\nSaída recente:")
            for line in state.output:
                print("  " + line)
        time.sleep(0.4)

    thread.join(timeout=1)
    while True:
        try:
            line = output_queue.get_nowait()
        except queue.Empty:
            break
        if line:
            state.output.append(line)
            state.output[:] = state.output[-12:]
    workspace = workspace or _new_workspace(root, before)
    if workspace:
        observe_workspace(workspace, state)
        apply_runtime_provider_blocks(workspace, state)
    code = int(process.returncode or 0)
    state.status, state.operation = ("COMPLETE", "LOCAL:DONE") if code == 0 else ("FAILED", "LOCAL:ERROR")
    if code and state.output:
        state.error = state.output[-1]
    render_header(state)
    if state.audit_id:
        print(f"Audit ID    : {state.audit_id}")
    if state.output:
        print("\nSaída final:")
        for line in state.output:
            print("  " + line)
    return code

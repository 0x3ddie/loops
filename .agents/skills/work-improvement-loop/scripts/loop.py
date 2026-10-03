"""Record measured improvement work without executing commands or deployments."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
from statistics import median


class LoopError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise LoopError(message)


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"Missing {label}")
    return value


def number(value, label):
    require(type(value) in (int, float) and math.isfinite(value), f"Invalid number: {label}")
    return value


def integer(value, label, minimum=1):
    require(type(value) is int and value >= minimum, f"Invalid integer: {label}")
    return value


def now():
    return datetime.now(timezone.utc)


def timestamp(value):
    date = datetime.fromisoformat(text(value, "UTC deadline").replace("Z", "+00:00"))
    require(date.tzinfo is not None and date.utcoffset().total_seconds() == 0, "Deadline must be UTC")
    return date


def contained(root, relative):
    value = Path(text(relative, "relative path"))
    require(not value.anchor and ".." not in value.parts, "Expected a relative path without traversal")
    result = (root / value).resolve()
    require(result.is_relative_to(root.resolve()) and result != root.resolve(), "Path escapes the project")
    return result


def sha(path):
    require(path.is_file(), f"Missing evidence or protected file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    def invalid(value):
        raise LoopError(f"Non-finite JSON value: {value}")
    result = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique, parse_constant=invalid)
    require(isinstance(result, dict), "Expected a JSON object")
    return result


def save(path, state):
    pending = path.with_suffix(".tmp")
    pending.write_text(json.dumps(state, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    pending.replace(path)


@contextmanager
def locked(folder):
    path = folder / ".lock"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
    except FileExistsError:
        raise LoopError("Run is locked; inspect its recorded PID before recovering a stale lock")
    try:
        yield
    finally:
        path.unlink()


def location(project, run):
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", run) is not None, "Invalid run ID")
    project = Path(project).resolve()
    require(project.is_dir(), "Project directory does not exist")
    return project, contained(project, f".agent-work/loops/{run}")


def validate_contract(contract):
    require(type(contract.get("schema_version")) is int and contract["schema_version"] == 1, "Unsupported contract version")
    require("EXAMPLE" not in json.dumps(contract) and "REPLACE_WITH" not in json.dumps(contract), "Fill the example contract with project facts")
    text(contract.get("objective"), "objective")
    text(contract.get("scope"), "scope")
    text(contract.get("context"), "measurement context")
    metric = contract["metric"]
    require(isinstance(metric, dict), "Missing metric object")
    text(metric.get("name"), "metric name")
    text(metric.get("unit"), "metric unit")
    require(metric["direction"] in ("lower", "higher"), "Metric direction must be lower or higher")
    require(number(metric["minimum_gain"], "minimum_gain") > 0, "Minimum gain must be positive")
    integer(contract["minimum_samples"], "minimum_samples", 3)
    integer(contract["maximum_candidates"], "maximum_candidates")
    require(timestamp(contract["deadline_utc"]) > now(), "Initial deadline must be in the future")
    for key in ("required_checks", "protected_files"):
        values = contract[key]
        require(isinstance(values, list) and values and all(isinstance(v, str) and v.strip() for v in values), f"Missing {key}")
        require(len(values) == len(set(values)), f"Duplicate {key}")
    release = contract["release"]
    require(isinstance(release, dict), "Missing release object")
    require(release["mode"] in ("offline", "flagged"), "Release mode must be offline or flagged")
    if release["mode"] == "flagged":
        for key in ("flag", "field_context", "rollback"):
            text(release.get(key), key)
        integer(release["maximum_observations"], "maximum_observations")
    require(isinstance(contract["regression_limit"], dict), "Missing regression limit object")
    number(contract["regression_limit"]["current"], "current regression limit")
    require(number(contract["regression_limit"]["margin"], "margin") >= 0, "Margin cannot be negative")


def initialize(project, run, contract_file):
    project, folder = location(project, run)
    contract = read_json(contained(project, contract_file))
    validate_contract(contract)
    protected = {p: sha(contained(project, p)) for p in contract["protected_files"]}
    # Refuse an existing directory, including an interrupted initialization.
    folder.mkdir(parents=True, exist_ok=False)
    state = {"version": 1, "run": run, "contract": contract, "protected": protected,
             "phase": "baseline", "created_at": now().isoformat(), "attempts": 0,
             "observations": 0, "live": False, "release_pending": False, "halt_requested": False, "events": []}
    with locked(folder):
        save(folder / "state.json", state)
    return state


def integrity(project, state):
    problems = []
    fingerprints = list(state["protected"].items())
    for event in state["events"]:
        fingerprints.extend(event["files"].items())
    for relative, expected in fingerprints:
        try:
            if sha(contained(project, relative)) != expected:
                problems.append(f"Changed evidence or evaluator: {relative}")
        except (OSError, LoopError) as error:
            problems.append(str(error))
    return sorted(set(problems))


def checks(contract, report):
    values = report.get("checks")
    require(isinstance(values, dict), "Missing checks object")
    for key in contract["required_checks"]:
        require(type(values.get(key)) is bool, f"Check {key} must be an actual boolean")
    return all(values[key] for key in contract["required_checks"])


def artifacts(project, folder, report):
    paths = report.get("artifacts")
    require(isinstance(paths, list) and paths, "Raw evidence artifacts are required")
    result = {}
    for relative in paths:
        file = contained(project, relative)
        require(file not in (folder / "state.json", folder / "state.tmp", folder / ".lock"), "Run metadata cannot be evidence")
        result[relative] = sha(file)
    return result


def measurement(project, folder, contract, report, context):
    require(isinstance(report, dict), "Expected a measurement object")
    text(report.get("revision"), "measured revision")
    require(report.get("context") == context, "Measurement context differs from the contract")
    require(report.get("metric") == contract["metric"]["name"] and report.get("unit") == contract["metric"]["unit"], "Metric or unit mismatch")
    samples = report.get("samples")
    require(isinstance(samples, list) and len(samples) >= contract["minimum_samples"], "Insufficient repeated observations")
    for value in samples:
        number(value, "sample")
    return checks(contract, report), artifacts(project, folder, report)


def compare(contract, baseline, candidate):
    left, right = baseline["samples"], candidate["samples"]
    if contract["metric"]["direction"] == "higher":
        left, right = right, left
    gain = contract["metric"]["minimum_gain"]
    if min(left) - max(right) >= gain:
        return "improved"
    if min(right) - max(left) >= gain:
        return "regressed"
    return "inconclusive"


def remaining(state):
    return state["attempts"] < state["contract"]["maximum_candidates"] and now() < timestamp(state["contract"]["deadline_utc"])


def retry_phase(state):
    return "candidate" if remaining(state) and not state["halt_requested"] else "stopped"


def threshold(state):
    samples = state["candidate"]["samples"]
    limits = state["contract"]["regression_limit"]
    if state["contract"]["metric"]["direction"] == "lower":
        proposed = max(samples) + limits["margin"]
        require(proposed < limits["current"], "No tighter threshold with the contracted headroom")
    else:
        proposed = min(samples) - limits["margin"]
        require(proposed > limits["current"], "No tighter threshold with the contracted headroom")
    return proposed


def advance(project, folder, state, kind, report):
    contract = state["contract"]
    phase = state["phase"]
    if kind == "halt":
        text(report.get("reason"), "halt reason")
        state["halt_requested"] = True
        state["phase"] = "rollback" if state["live"] or state["release_pending"] else "stopped"
        return {}, "halt_requested"
    allowed = {"baseline": "baseline", "candidate": "candidate", "review": "review",
               "release_intent": "release", "release": "release_pending", "field": "field", "rollback": "rollback", "ratchet": "ratchet"}
    require(kind in allowed and phase == allowed[kind], f"Cannot record {kind} while phase is {phase}")
    if kind in ("candidate", "release_intent"):
        require(now() < timestamp(contract["deadline_utc"]), "Deadline elapsed; record halt instead")
    if kind in ("baseline", "candidate"):
        passed, files = measurement(project, folder, contract, report, contract["context"])
        if kind == "baseline":
            require(passed, "Baseline checks fail; repair or redefine the task before optimizing")
            state["baseline"] = report
            state["phase"] = "candidate"
            return files, "baseline_recorded"
        require(remaining(state), "Candidate budget exhausted; record halt instead")
        text(report.get("hypothesis"), "candidate hypothesis")
        require(report["revision"] != state["baseline"]["revision"], "Candidate revision equals baseline")
        state["attempts"] += 1
        decision = compare(contract, state["baseline"], report) if passed else "failed_checks"
        if decision == "improved":
            state["candidate"] = report
            state["phase"] = "review"
            state["observations"] = 0
        else:
            state["phase"] = retry_phase(state)
        return files, decision
    if kind == "field":
        candidate, control = report["candidate"], report["control"]
        require(isinstance(candidate, dict) and isinstance(control, dict), "Expected candidate and control measurement objects")
        require(candidate["revision"] == state["candidate"]["revision"] and control["revision"] == state["baseline"]["revision"], "Field revisions do not match the released experiment")
        a, files = measurement(project, folder, contract, control, contract["release"]["field_context"])
        b, more = measurement(project, folder, contract, candidate, contract["release"]["field_context"])
        files.update(more)
        state["observations"] += 1
        decision = compare(contract, control, candidate) if a and b else "failed_checks"
        if decision == "improved":
            state["phase"] = "ratchet"
        elif decision in ("regressed", "failed_checks") or state["observations"] >= contract["release"]["maximum_observations"]:
            state["phase"] = "rollback"
        return files, decision
    require(report.get("revision") == state["candidate"]["revision"], "Evidence is for a different candidate revision")
    files = artifacts(project, folder, report)
    if kind == "review":
        require(type(report.get("passed")) is bool, "Review result must be boolean")
        text(report.get("reviewer"), "reviewer identity and independence")
        text(report.get("notes"), "review notes")
        state["phase"] = ("release" if contract["release"]["mode"] == "flagged" else "ratchet") if report["passed"] else retry_phase(state)
        return files, "review_passed" if report["passed"] else "review_failed"
    if kind in ("release_intent", "release"):
        require(report.get("flag") == contract["release"]["flag"], "Release flag mismatch")
        text(report.get("authorization"), "existing release authorization")
        if kind == "release_intent":
            text(report.get("notes"), "intended release target and recovery plan")
            state["release_pending"] = True
            state["phase"] = "release_pending"
            return files, "release_intent_recorded"
        text(report.get("deployment_id"), "deployment receipt identity")
        state["release_pending"] = False
        state["live"] = True
        state["phase"] = "field"
        return files, "release_recorded"
    if kind == "rollback":
        require(report.get("flag") == contract["release"]["flag"], "Rollback flag mismatch")
        require(type(report.get("recovered")) is bool, "Recovery result must be boolean")
        text(report.get("notes"), "recovery notes")
        if report["recovered"]:
            state["live"] = False
            state["release_pending"] = False
            state["phase"] = retry_phase(state)
        return files, "recovered" if report["recovered"] else "recovery_pending"
    require(checks(contract, report), "Regression protection checks failed")
    require(number(report.get("threshold"), "new threshold") == threshold(state), "Threshold differs from contracted proposal")
    state["phase"] = "complete"
    state["accepted_threshold"] = report["threshold"]
    return files, "field_verified" if contract["release"]["mode"] == "flagged" else "local_verified"


def record(project, run, kind, evidence):
    project, folder = location(project, run)
    with locked(folder):
        state = read_json(folder / "state.json")
        require(state["phase"] not in ("complete", "stopped"), "Run is closed; start a new run")
        problems = integrity(project, state)
        require(not problems or kind in ("halt", "rollback"), "; ".join(problems))
        report_path = contained(project, evidence)
        require(report_path not in (folder / "state.json", folder / "state.tmp", folder / ".lock"), "Run metadata cannot be a report")
        report = read_json(report_path)
        before = state["phase"]
        files, decision = advance(project, folder, state, kind, report)
        files[evidence] = sha(report_path)
        event = {"sequence": len(state["events"]) + 1, "at": now().isoformat(), "kind": kind,
                 "from": before, "to": state["phase"], "decision": decision,
                 "report": report, "files": files, "integrity_issues": problems}
        state["events"].append(event)
        save(folder / "state.json", state)
    return state


def summary(project, state):
    result = {"run": state["run"], "phase": state["phase"], "candidate_attempts": state["attempts"],
              "release_pending": state["release_pending"], "live": state["live"],
              "field_observations": state["observations"], "deadline_elapsed": now() >= timestamp(state["contract"]["deadline_utc"]),
              "integrity_issues": integrity(project, state)}
    if state["events"]:
        result["last_decision"] = state["events"][-1]["decision"]
    if state["phase"] == "ratchet":
        try:
            result["proposed_threshold"] = threshold(state)
        except LoopError as error:
            result["threshold_issue"] = str(error)
    if "candidate" in state:
        result["candidate_median"] = median(state["candidate"]["samples"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "record", "status"))
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--contract")
    parser.add_argument("--kind", choices=("baseline", "candidate", "review", "release_intent", "release", "field", "rollback", "ratchet", "halt"))
    parser.add_argument("--evidence")
    args = parser.parse_args()
    try:
        project, folder = location(args.project, args.run)
        if args.action == "init":
            state = initialize(project, args.run, args.contract)
        elif args.action == "record":
            state = record(project, args.run, args.kind, args.evidence)
        else:
            state = read_json(folder / "state.json")
        result = summary(project, state)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 1 if result["integrity_issues"] else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

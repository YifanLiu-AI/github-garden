#!/usr/bin/env python3
"""Explicitly synthetic GitHub contribution garden; never rewrites history."""

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

OWNER = "YifanLiu-AI"
REMOTE = f"git@github.com:{OWNER}/github-garden.git"
EMAIL = f"186058058+{OWNER}@users.noreply.github.com"
TZ = dt.timezone(dt.timedelta(hours=8))
COLOR_SEED = "github-garden-colors-v1"


def noise(label):
    digest = hashlib.sha256(f"{COLOR_SEED}:{label}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def daily_target(day):
    """Stable 1..12 synthetic records/day, with weekly clusters and small peaks."""
    week = day - dt.timedelta(days=day.weekday())
    weekly = noise(f"week:{week}")
    count = 1 + int(1.8 * weekly + 4 * noise(f"jitter:{day}"))
    if day.weekday() >= 5:
        count = max(1, int(count * 0.65))
    if noise(f"burst:{day}") < 0.09:
        count += 4 + int(4 * weekly)
    return min(12, count)


def git(repo, *args, env=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        text=True, capture_output=True, env=env,
    ).stdout.strip()


def dates(days, today):
    if not 1 <= days <= 366:
        raise ValueError("days must be between 1 and 366")
    return [today - dt.timedelta(days=i) for i in reversed(range(days))]


def run(repo, days, push=True):
    repo = repo.resolve()
    if repo == Path("/") or repo == Path.home():
        raise ValueError("Use a dedicated worktree, not a home/root directory")
    if not (repo / ".git").is_dir():
        raise ValueError("Clone the dedicated github-garden repository first")
    if git(repo, "rev-parse", "--show-toplevel") != str(repo):
        raise ValueError("Not the worktree root")
    if git(repo, "remote", "get-url", "origin") != REMOTE:
        raise ValueError("Refusing to touch a different repository")
    if git(repo, "branch", "--show-current") != "main":
        raise ValueError("Expected the dedicated repository main branch")
    if git(repo, "status", "--porcelain"):
        raise ValueError("Worktree has uncommitted changes; refusing to proceed")
    git(repo, "config", "user.name", "Yifan Liu")
    git(repo, "config", "user.email", EMAIL)
    created = 0
    today = dt.datetime.now(TZ).date()
    generated_at = dt.datetime.now(TZ).isoformat()
    for day in dates(days, today):
        for slot in range(1, daily_target(day) + 1):
            relative = (f"days/{day.isoformat()}.json" if slot == 1 else
                        f"entries/{day.isoformat()}/{slot:02d}.json")
            target = repo / relative
            if target.exists():
                # A prior crash may have written but not committed a record.
                git(repo, "ls-files", "--error-unmatch", relative)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({
                "kind": "synthetic-contribution-garden",
                "calendar_date": day.isoformat(),
                "slot": slot,
                "color_seed": COLOR_SEED,
                "generated_at": generated_at,
                "notice": "Automatically generated; not genuine development activity.",
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            timestamp = (dt.datetime.combine(day, dt.time(9), TZ) +
                         dt.timedelta(minutes=15 * slot)).isoformat()
            env = dict(os.environ, GIT_AUTHOR_DATE=timestamp, GIT_COMMITTER_DATE=timestamp)
            git(repo, "add", "--", relative)
            git(repo, "commit", "-m", f"chore(garden): synthetic record {slot} for {day}", env=env)
            created += 1
    if push:
        # Also retries a push after a previous network failure. Never force-push.
        git(repo, "push", "origin", "main")
    print(json.dumps({"created": created, "days": days, "pushed": push}))
    return created


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--days", type=int, default=1,
                        help="1 for daily run; 365 for one-off historical fill")
    parser.add_argument("--no-push", action="store_true", help="offline test only")
    args = parser.parse_args()
    try:
        dates(args.days, dt.datetime.now(TZ).date())
    except ValueError as exc:
        parser.error(str(exc))
    if not (args.worktree / ".git").is_dir():
        parser.error("The dedicated repository must already be cloned")
    with (args.worktree / ".git" / "garden.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            run(args.worktree, args.days, not args.no_push)
        except subprocess.CalledProcessError as exc:
            # Avoid printing credential-bearing commands or environment values.
            raise SystemExit(f"Git operation failed (exit {exc.returncode}); inspect the worktree.") from None
        except ValueError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()

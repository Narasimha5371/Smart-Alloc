"""Simple Alembic helper for local development.

Usage (run from project root with the virtualenv activated):

  python scripts/alembic_helper.py revision -m "describe change"
  python scripts/alembic_helper.py upgrade
  python scripts/alembic_helper.py stamp

This wraps common `alembic` CLI commands so you don't need to remember exact flags.
"""
import subprocess
import shlex
import sys
import argparse

PROJ_ROOT = ""


def run_cmd(cmd: str):
    print("Running:", cmd)
    parts = shlex.split(cmd)
    try:
        subprocess.check_call(parts)
    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
        sys.exit(e.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alembic helper")
    parser.add_argument("action", choices=["revision", "upgrade", "stamp"], help="Action to perform")
    parser.add_argument("-m", "--message", help="Revision message (for revision)")
    args = parser.parse_args()

    if args.action == "revision":
        msg = args.message or "auto"
        run_cmd(f"alembic revision --autogenerate -m \"{msg}\"")
    elif args.action == "upgrade":
        run_cmd("alembic upgrade head")
    elif args.action == "stamp":
        run_cmd("alembic stamp head")

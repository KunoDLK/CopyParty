#!/usr/bin/env python3
import os
import sys
import subprocess

def in_venv():
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

def ensure_pip():
    try:
        import pip  # noqa: F401
    except Exception:
        try:
            import ensurepip
        except Exception:
            sys.stderr.write(
                "pip is not available and ensurepip is missing; please install pip for this Python.\n"
            )
            raise
        print("Bootstrapping pip with ensurepip...")
        ensurepip.bootstrap(upgrade=True)

def install_packages(packages):
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    if not in_venv():
        cmd.append("--user")
    cmd += packages
    run(cmd)

def main():
    ensure_pip()
    # Install both copyparty and cfssl
    install_packages(["copyparty", "cfssl"])

    # Equivalent to: .\copyparty-sfx.py -c .\config.txt
    config_path = os.path.normpath(os.path.join(".", "config.txt"))
    if not os.path.exists(config_path):
        sys.stderr.write(f"Config file not found: {config_path}\n")
        sys.exit(1)

    print("Starting copyparty (equivalent to '.\\copyparty-sfx.py -c .\\config.txt')...")
    cmd = [sys.executable, "-m", "copyparty", "-c", config_path]

    # Replace current process so Ctrl+C/signals work naturally
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
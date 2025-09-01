#!/usr/bin/env python3
import os
import sys
import shutil
import signal
import tempfile
import subprocess

def run(cmd, cwd=None):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)

def script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def venv_python(venv_path):
    if os.name == "nt":
        return os.path.join(venv_path, "Scripts", "python.exe")
    return os.path.join(venv_path, "bin", "python")

def create_fresh_venv(venv_path):
    # Create a brand new venv with up-to-date pip tooling
    try:
        run([sys.executable, "-m", "venv", "--upgrade-deps", venv_path])
    except subprocess.CalledProcessError:
        run([sys.executable, "-m", "venv", venv_path])

def install_packages(py_exe, packages):
    # Upgrade pip tooling then install requested packages
    run([py_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run([py_exe, "-m", "pip", "install", "--upgrade"] + list(packages))

def main():
    sd = script_dir()
    config_path = os.path.normpath(os.path.join(sd, "config.txt"))
    if not os.path.exists(config_path):
        sys.stderr.write(f"Config file not found: {config_path}\n")
        sys.exit(1)

    # Fresh venv each run in a temp folder within the repo (dot-prefixed)
    venv_path = tempfile.mkdtemp(prefix=".venv-run-", dir=sd)
    py = venv_python(venv_path)

    try:
        print(f"Creating fresh virtual environment in {venv_path} ...")
        create_fresh_venv(venv_path)

        # Install required packages into the fresh venv
        install_packages(py, ["copyparty", "cfssl", "pillow"])

        print("Starting copyparty (equivalent to '.\\copyparty-sfx.py -c .\\config.txt')...")
        if sys.platform == "win32":
            cmd = [py, "-m", "copyparty", "-c", config_path]
        else:
            cmd = ["sudo", py, "-m", "copyparty", "-c", config_path]

        # Run as a child process so we can clean up the venv afterwards
        proc = subprocess.Popen(cmd, cwd=sd)
        try:
            returncode = proc.wait()
        except KeyboardInterrupt:
            # Forward Ctrl+C to child, then wait for it to exit
            try:
                if os.name == "nt":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)  # best-effort on Windows
                else:
                    proc.send_signal(signal.SIGINT)
            except Exception:
                pass
            returncode = proc.wait()
        sys.exit(returncode)
    finally:
        # Remove the fresh venv directory after run
        try:
            shutil.rmtree(venv_path)
        except Exception as e:
            print(f"Warning: failed to remove venv at {venv_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
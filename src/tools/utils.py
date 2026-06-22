import subprocess


def run_subprocess(cmd: list[str]) -> str | None:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        stdout = result.stdout.strip()
        return stdout if stdout else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
import subprocess


def run_subprocess(cmd: list[str]) -> str | None:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        stdout = result.stdout.strip()
        return stdout if stdout else None
    except FileNotFoundError:
        return None
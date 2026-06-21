import subprocess


def _run_subprocess(cmd: list[str]) -> str | None:
    """Função utilitária para executar comandos no terminal de forma segura."""
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
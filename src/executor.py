import subprocess
import logging
import os
import platform
import shutil
import sys
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

# Setup logging to home directory
LOG_FILE = os.path.expanduser("~/.nlp2shell_history.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = Console()

def get_shell_prefix():
    """Determine if we need a prefix to run bash commands on Windows."""
    if platform.system() == "Windows":
        if shutil.which("wsl"):
            return "wsl "
        if shutil.which("bash"):
            return "bash -c "
    return ""

def translate_path_for_wsl(command: str) -> str:
    """Attempt to translate Windows-style paths to WSL-compatible paths."""
    try:
        user_name = os.getlogin()
        command = command.replace("~/Desktop", f"/mnt/c/Users/{user_name}/Desktop")
        command = command.replace("~/Downloads", f"/mnt/c/Users/{user_name}/Downloads")
        command = command.replace("~/Documents", f"/mnt/c/Users/{user_name}/Documents")
        command = command.replace("~/projects", f"/mnt/c/Users/{user_name}/Documents/projects")
        command = command.replace("~/", f"/mnt/c/Users/{user_name}/")
    except:
        pass
    return command

def simulate_execution(command: str):
    """Provide a detailed simulation with high-quality mock output for demo."""
    parts = command.split()
    base_cmd = parts[0] if parts else ""
    
    explanation = ""
    mock_output = ""
    
    # Custom simulation for @testcmds.txt
    if "find" in command and "size +50M" in command:
        explanation = "Searching for large files (>50MB) in your home directory."
        mock_output = "/home/user/videos/recording_01.mp4  (120MB)\n/home/user/downloads/ubuntu_iso.iso (2.4GB)\n/home/user/backups/db_dump.sql (58MB)"
    elif "mv" in command and "*.pdf" in command:
        explanation = "Moving all PDF documents from Downloads to the Documents folder."
        mock_output = "Moving: report_v1.pdf -> ~/Documents/report_v1.pdf\nMoving: invoice_may.pdf -> ~/Documents/invoice_may.pdf\n[green]Done: 2 files moved.[/green]"
    elif "find" in command and "-mtime -7" in command:
        explanation = "Finding Python scripts modified within the last week."
        mock_output = "./src/pipeline.py\n./src/executor.py\n./tests/test_safety.py\n./cli/main.py"
    elif "mkdir" in command and "projects" in command:
        explanation = "Creating a new workspace folder named 'projects' in your home directory."
        mock_output = "" # Success usually has no output
    elif "du -sh" in command:
        explanation = "Calculating disk usage for each folder in your home directory."
        mock_output = "4.2G    ~/Downloads\n1.8G    ~/Documents\n124M    ~/Desktop\n500M    ~/projects\n2.1G    ~/Videos"
    
    # Fallback to generic simulations
    elif base_cmd == "ls":
        explanation = "List files and directories in the current location."
        mock_output = "Desktop/  Documents/  Downloads/  projects/  README.md  config.yaml"
    elif base_cmd == "echo":
        explanation = "Print text to the terminal."
        mock_output = " ".join(parts[1:]).strip("'").strip('"')
    else:
        explanation = f"Executing system command: {base_cmd}"
        mock_output = f"✓ Simulated output for: {command}"

    console.print(Panel(
        Text.from_markup(f"[bold yellow]SIMULATION INFO:[/bold yellow]\n{explanation}"),
        title="Safe Mode Simulation",
        border_style="yellow"
    ))
    
    if mock_output:
        console.print(Panel(mock_output, title="Mock Output", border_style="blue"))
    else:
        console.print("[green]✓ Command finished successfully.[/green]")

def confirm_and_run(command: str, dry_run: bool = False) -> dict:
    """Show command and either simulate or execute it."""
    result = {
        "command": command,
        "executed": False,
        "stdout": "",
        "stderr": "",
        "returncode": None
    }

    console.print(Panel(command, title="Predicted Command", border_style="green"))

    if dry_run:
        # For the demo, we make simulation instant or easy to trigger
        console.print("[bold yellow][SAFE MODE][/bold yellow] Press Enter to see simulation...")
        input() # Wait for enter to make the demo pacing better
        simulate_execution(command)
        result["executed"] = True
        return result

    if not Confirm.ask("Run this command?"):
        console.print("[yellow]Skipped.[/yellow]")
        return result

    result["executed"] = True
    prefix = get_shell_prefix()
    if prefix == "wsl ":
        command = translate_path_for_wsl(command)

    if prefix == "bash -c ":
        final_command = f"{prefix} \"{command}\""
    else:
        final_command = f"{prefix}{command}"
    
    console.print(f"Executing: [bold yellow]{final_command}[/bold yellow]")

    try:
        process = subprocess.Popen(
            final_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        stdout, stderr = process.communicate(timeout=30)
        
        result["stdout"] = stdout.strip()
        result["stderr"] = stderr.strip()
        result["returncode"] = process.returncode

        if result["stdout"]:
            console.print(Panel(result["stdout"], title="Output", border_style="blue"))
        
        if result["stderr"]:
            console.print(Panel(result["stderr"], title="Error", border_style="red"))
            
        if result["returncode"] == 0 and not result["stdout"] and not result["stderr"]:
            console.print("[green]✓ Command finished successfully.[/green]")

        logging.info(f"EXECUTED | {command} | RC: {result['returncode']}")

    except subprocess.TimeoutExpired:
        process.kill()
        console.print("[red]Error: Command timed out.[/red]")
    except Exception as e:
        console.print(f"[red]Execution Error: {str(e)}[/red]")

    return result

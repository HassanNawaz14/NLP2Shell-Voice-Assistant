import argparse
import sys
import os
import platform
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.align import Align

# Add root directory to path to import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import pipeline

console = Console()

def show_banner():
    """Display a professional ASCII-style banner."""
    banner = Text()
    banner.append(" █▄ █ █   █▀█  ▀█▀ █▀█  █▀▀ █ █ █▀▀ █   █  \n", style="bold bright_blue")
    banner.append(" █ ▀█ █▄▄ █▀▀   █  █▄█  ▀▀█ █▀█ ██▄ █▄▄ █▄▄\n", style="bold cyan")
    banner.append("   Natural Language to Shell Assistant  ", style="italic dim")
    
    console.print(Align.center(Panel(banner, border_style="bright_blue", padding=(1, 4))))
    console.print()

def show_system_info(args):
    """Display a summary of the current system configuration and available commands."""
    config_table = Table(show_header=False, box=None, padding=(0, 2))
    
    # Model info
    model_name = "Qwen2.5-0.5B (LoRA)"
    device = "CPU (Intel HD 520)"
    
    # Mode info
    mode = "⌨  [bold cyan]Text Input[/bold cyan]" if args.text else "🎤 [bold green]Voice Input[/bold green]"
    safe = " [bold yellow][SAFE MODE][/bold yellow]" if args.safe else ""
    
    # WSL info
    wsl_status = "[green]Enabled[/green]" if shutil.which("wsl") else "[red]Disabled[/red]"
    
    config_table.add_row("[bold blue]Model:[/bold blue]", model_name)
    config_table.add_row("[bold blue]Device:[/bold blue]", device)
    config_table.add_row("[bold blue]Input:[/bold blue]", f"{mode}{safe}")
    config_table.add_row("[bold blue]WSL:[/bold blue]", wsl_status)
    config_table.add_row("[bold blue]OS:[/bold blue]", f"{platform.system()} {platform.release()}")

    # Commands info
    cmd_table = Table(show_header=False, box=None, padding=(0, 2))
    cmd_table.add_row("[bold yellow]Ctrl+M[/bold yellow]", "Toggle Voice/Text mode")
    cmd_table.add_row("[bold yellow]/text[/bold yellow]", "Switch to text mode")
    cmd_table.add_row("[bold yellow]/voice[/bold yellow]", "Switch to voice mode")
    cmd_table.add_row("[bold red]exit[/bold red]", "Close the application")

    console.print(Align.center(
        Panel(
            config_table, 
            title="[bold]System Configuration[/bold]", 
            border_style="bright_blue", 
            width=60
        )
    ))
    
    console.print(Align.center(
        Panel(
            cmd_table, 
            title="[bold]Control Commands[/bold]", 
            border_style="yellow", 
            width=60
        )
    ))
    
    console.print(Align.center("[dim]Ctrl+C for emergency stop[/dim]"))
    console.print()

def main():
    parser = argparse.ArgumentParser(description="NLP2Shell: Voice/Text to Bash Command Assistant")
    parser.add_argument("--text", action="store_true", help="Use text input mode instead of voice")
    parser.add_argument("--safe", action="store_true", help="Dry-run mode (never execute commands)")
    
    args = parser.parse_args()
    
    console.clear()
    show_banner()
    show_system_info(args)
    
    try:
        # Run the pipeline
        pipeline.run(voice_mode=not args.text, dry_run=args.safe)
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Critical Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

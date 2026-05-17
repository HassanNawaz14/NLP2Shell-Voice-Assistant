import os
import yaml
import sys
import keyboard
import time
import threading
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

# Import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import stt
import predictor
import safety
import executor

console = Console()

class SessionState:
    def __init__(self, voice_mode):
        self.voice_mode = voice_mode
        self.mode_changed = False
        self.running = True

def load_config():
    """Load configuration from config.yaml."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except:
        return {}

def run(voice_mode: bool = True, dry_run: bool = False) -> None:
    """Main loop connecting all modules."""
    config = load_config()
    model_path = config.get("model", {}).get("path", "models/qwen_final_adapter")
    
    with console.status("[bold blue]Initializing AI Model..."):
        try:
            predictor.load_model(model_path)
        except Exception as e:
            console.print(f"[red]Error loading model: {e}[/red]")
            return

    state = SessionState(voice_mode)
    
    def on_hotkey():
        # Toggle mode
        state.voice_mode = not state.voice_mode
        state.mode_changed = True
        
        mode_str = "🎤 Voice" if state.voice_mode else "⌨ Text"
        console.print(f"\n[bold yellow]🔄 Switched to {mode_str} Mode[/bold yellow]")
        
        # INSTANT TRANSITION: If we just switched TO text mode, we need to stop the STT 
        # But STT is a blocking call. The best we can do is let the loop check the state.
        # On Windows, we can't easily kill the STT thread without complexity,
        # so we rely on the loop's 'mode_changed' checks.

    # Register hotkey
    keyboard.add_hotkey('ctrl+m', on_hotkey)

    console.print(Rule(style="dim"))
    console.print("[bold green]✓ System Ready![/bold green] Press [bold yellow]Ctrl+M[/bold yellow] to toggle mode.")

    while state.running:
        try:
            # Check for mode change
            if state.mode_changed:
                state.mode_changed = False

            # 1. Get input
            if state.voice_mode:
                text = stt.listen()
                # If mode changed during listening, 'text' will be discarded
                if state.mode_changed:
                    state.mode_changed = False
                    continue
                if not text:
                    continue
                console.print(Panel(Text(text, style="cyan"), title="🎤 Voice Input", border_style="cyan"))
            else:
                console.print(Rule(style="dim", title="[bold cyan]⌨ Text Mode[/bold cyan]"))
                text = stt.text_mode()
                # If mode changed during typing, discard text
                if state.mode_changed:
                    state.mode_changed = False
                    continue
                if not text:
                    continue
            
            # Check for control commands
            clean_text = text.lower().strip().rstrip('.')
            if clean_text in ["exit", "quit", "q"]:
                state.running = False
                break
            
            # 2. Predict Bash Command
            with console.status("[bold green]Thinking..."):
                command = predictor.predict(text)

            # 3. Safety Check
            if safety.check(command):
                # 4. Execute
                executor.confirm_and_run(command, dry_run=dry_run)
            else:
                reason = safety.explain_block(command)
                console.print(Panel(
                    f"[bold red]Safety Block:[/bold red] {reason}\n[dim]Command: {command}[/dim]",
                    title="Security Alert",
                    border_style="red"
                ))

        except KeyboardInterrupt:
            state.running = False
            break
        except Exception as e:
            console.print(f"[red]Pipeline Error: {e}[/red]")
            time.sleep(1)
    
    keyboard.unhook_all()
    console.print("[yellow]Goodbye![/yellow]")

if __name__ == "__main__":
    run(voice_mode=False, dry_run=True)

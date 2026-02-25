import asyncio
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from serpentine.core.engine import SerpentineEngine
from serpentine.core.registry import EngineMode
from serpentine.utils.logging import configure_logging

app = typer.Typer()
console = Console()
logger = configure_logging()

@app.command()
def run(mode: EngineMode = EngineMode.ARCHITECT, tps: int = 60):
    """
    Start the Serpentine Engine.
    """
    console.print(f"[bold green]Starting Serpentine Engine in {mode} mode...[/bold green]")

    engine = SerpentineEngine(mode=mode, target_tps=tps)

    # Display system info
    table = Table(title="Active Systems")
    table.add_column("Phase", style="cyan")
    table.add_column("Systems", style="green")

    for phase in engine.systems:
        systems = engine.systems[phase]
        if systems:
            system_names = ", ".join([s.__class__.__name__ for s in systems])
            table.add_row(phase.name, system_names)

    console.print(table)

    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        console.print("[bold red]Engine interrupted by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Engine crashed: {e}[/bold red]")
        logger.exception("Engine crashed")

if __name__ == "__main__":
    app()

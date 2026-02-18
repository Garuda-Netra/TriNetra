from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

BANNER = r"""
 ████████╗██████╗ ██╗███╗   ██╗███████╗████████╗██████╗  █████╗
 ╚══██╔══╝██╔══██╗██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
    ██║   ██████╔╝██║██╔██╗ ██║█████╗     ██║   ██████╔╝███████║
    ██║   ██╔══██╗██║██║╚██╗██║██╔══╝     ██║   ██╔══██╗██╔══██║
    ██║   ██║  ██║██║██║ ╚████║███████╗   ██║   ██║  ██║██║  ██║
    ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
"""


def print_banner() -> None:
    # --- Main banner panel (ASCII art + subtitle only) ---
    banner_body = (
        f"[bold cyan]{BANNER}[/bold cyan]\n"
        "[bold bright_yellow]TRINETRA[/bold bright_yellow]  "
        "[bold white]— Third Eye Port Scanner[/bold white]\n"
    )
    panel = Panel(
        Text.from_markup(banner_body),
        border_style="bright_blue",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
        width=72,
    )
    console.print(panel)

    # --- Shloka printed separately for visibility ---
    console.print()
    console.print("[bold red]  ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम् ।[/]")
    console.print("[bold red]  उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात् ॥[/]")
    console.print()
    console.print('[red]  "We worship the three-eyed One who nourishes all."[/]')
    console.print('[red]  "May He liberate us from the bondage of mortality."[/]')
    console.print("[red]  -- Maha Mrityunjaya Mantra, Rig Veda (7.59.12)[/]")
    console.print()
    console.print("[bold magenta]  Created by Garuda Netra[/bold magenta]")
    console.print()


def print_scan_target(target: str, ip_address: str, total_ports: int) -> None:
    console.print(
        Panel(
            f"[bold white]Target :[/bold white]  [bold green]{target}[/bold green]\n"
            f"[bold white]IP     :[/bold white]  [bold cyan]{ip_address}[/bold cyan]\n"
            f"[bold white]Ports  :[/bold white]  [bold yellow]{total_ports}[/bold yellow]",
            title="[bold bright_yellow]⚡ Scan Configuration[/bold bright_yellow]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )
    console.print()


def print_scan_mode(message: str) -> None:
    console.print(f"[bold bright_cyan]{message}[/bold bright_cyan]")
    console.print()


def print_results_header() -> None:
    console.print("[bold]Port   Service      Version                      Status[/bold]")


def print_result_row(port: int, service: str, version: str, status: str) -> None:
    if status == "OPEN":
        color = "bold green"
    elif status == "CLOSED":
        color = "red"
    elif status == "FILTERED":
        color = "yellow"
    else:
        color = "dim"

    service_text = (service or "Unknown")[:12]
    version_text = (version or "-")[:28]
    console.print(
        f"[{color}]{port:<6}{service_text:<13}{version_text:<29}{status}[/{color}]"
    )


def print_summary(target: str, ip_address: str, open_count: int, closed_count: int, saved_rows: int, db_path: str) -> None:
    console.print()

    table = Table(
        title="[bold bright_yellow]◈ Scan Summary[/bold bright_yellow]",
        show_header=True,
        header_style="bold bright_blue",
        box=box.DOUBLE_EDGE,
        border_style="bright_blue",
        padding=(0, 2),
    )
    table.add_column("Field", style="bold white", no_wrap=True)
    table.add_column("Value", style="bold")

    table.add_row("Target", f"[green]{target}[/green]")
    table.add_row("Resolved IP", f"[cyan]{ip_address}[/cyan]")
    table.add_row("Open Ports", f"[bold green]{open_count}[/bold green]")
    table.add_row("Closed Ports", f"[red]{closed_count}[/red]")
    table.add_row("Rows Saved", f"[yellow]{saved_rows}[/yellow]")
    table.add_row("Database", f"[dim]{db_path}[/dim]")

    console.print(table)
    console.print()
    console.print("[bold green]  ✔ Scan completed and results saved successfully.[/bold green]")
    console.print()


def print_error(message: str) -> None:
    console.print(
        Panel(
            f"[bold red]{message}[/bold red]",
            title="[bold red]⚠ Error[/bold red]",
            border_style="red",
            box=box.HEAVY,
            padding=(0, 2),
        )
    )

# fanficdownloader/commands/download.py
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
from typing import List, Optional

from fanfic_downloader.utils import show_app_header, run_fanficfare, load_urls_from_file, open_download_folder
from fanfic_downloader import config # Import config for USER_FOLDER

console = Console() # Each command module can have its own console instance if preferred

def perform_download(urls_list: List[str], output_folder: Optional[str] = None):
    """
    Core download functionality that can be called directly or from commands.
    """
    target_folder = output_folder if output_folder else config.USER_FOLDER

    console.print(f"[bold]Downloading [cyan]{len(urls_list)}[/cyan] stories to [blue]{target_folder}[/blue][/bold]")

    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
    ) as progress:

        download_task = progress.add_task("[bold]Downloading stories...[/bold]", total=len(urls_list))
        success_count = 0
        error_count = 0

        for url in urls_list:
            progress.update(download_task, description=f"[bold]Downloading:[/bold] {url.split('/')[-1]}...")
            try:
                result = run_fanficfare(["-o", "is_adult=true", "-u", url], working_dir=target_folder)
                if result.returncode == 0:
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
            progress.advance(download_task)

    if success_count > 0:
        console.print(f"[bold green]✓[/bold green] Successfully downloaded [bold]{success_count}[/bold] stories")
    if error_count > 0:
        console.print(f"[bold red]✗[/bold red] Failed to download [bold]{error_count}[/bold] stories")

    if success_count > 0 and Confirm.ask("Open download folder?"):
        open_download_folder()

def download_stories_command(
        urls: List[str] = typer.Option(None, "--url", "-u", help="One or more story URLs to download"),
        file: Optional[str] = typer.Option(None, "--file", "-f", help="File containing story URLs (one per line)"),
        interactive: bool = typer.Option(False, "--interactive", "-i", help="Enter URLs interactively"),
        output_folder: Optional[str] = typer.Option(None, "--output", "-o",
                                                    help="Override download folder for this session"),
):
    """
    Download fan fiction stories from provided URLs.

    Examples:
        fanfic download -u https://archiveofourown.org/works/12345678
        fanfic download -f urls.txt
        fanfic download -i
    """
    show_app_header()

    all_urls = []
    if urls:
        all_urls.extend(urls)
    if file:
        file_urls = load_urls_from_file(file)
        all_urls.extend(file_urls)

    if interactive or (not urls and not file):
        console.print("[bold]Enter story URLs, one per line[/bold] (Enter a blank line to finish):")
        try:
            while True:
                line = Prompt.ask("URL", default="")
                if not line.strip():
                    break
                all_urls.append(line.strip())
        except (EOFError, KeyboardInterrupt):
            console.print()

    if not all_urls:
        console.print("[bold yellow]No URLs provided for download![/bold yellow]")
        console.print("Use -u/--url to specify URLs or -f/--file to load from a file.")
        return

    perform_download(all_urls, output_folder)
# fanficdownloader/commands/extract.py
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.box import ROUNDED
from typing import List, Optional

from fanfic_downloader.utils import show_app_header, run_fanficfare, load_urls_from_file, save_urls_to_file
from fanfic_downloader.commands.download import perform_download # Import the shared download function

console = Console() # Each command module can have its own console instance if preferred

def extract_story_urls_command(
        urls: List[str] = typer.Option(None, "--url", "-u", help="One or more URLs to extract from"),
        file: Optional[str] = typer.Option(None, "--file", "-f", help="File containing URLs to extract from"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file to save extracted URLs"),
        download: bool = typer.Option(False, "--download", "-d", help="Download extracted stories immediately"),
        interactive: bool = typer.Option(False, "--interactive", "-i", help="Enter URLs interactively"),
):
    """
    Extract story URLs from listing pages (author profiles, series pages, etc).

    Examples:
        fanfic extract -u https://archiveofourown.org/users/username/works
        fanfic extract -f sites.txt -o extracted_urls.txt
        fanfic extract -u https://archiveofourown.org/series/12345 -d
    """
    show_app_header()

    all_urls = []
    if urls:
        all_urls.extend(urls)
    if file:
        file_urls = load_urls_from_file(file)
        all_urls.extend(file_urls)

    if interactive or (not urls and not file):
        console.print("[bold]Enter URLs to extract from, one per line[/bold] (Enter a blank line to finish):")
        try:
            while True:
                line = Prompt.ask("URL", default="")
                if not line.strip():
                    break
                all_urls.append(line.strip())
        except (EOFError, KeyboardInterrupt):
            console.print()

    if not all_urls:
        console.print("[bold yellow]No URLs provided for extraction![/bold yellow]")
        console.print("Use -u/--url to specify URLs or -f/--file to load from a file.")
        return

    all_extracted_urls = []
    console.print(f"[bold]Extracting story links from [cyan]{len(all_urls)}[/cyan] sources[/bold]")

    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
    ) as progress:

        extract_task = progress.add_task("[bold]Extracting URLs...[/bold]", total=len(all_urls))
        for source_url in all_urls:
            progress.update(extract_task, description=f"[bold]Extracting from:[/bold] {source_url.split('/')[-2]}/...")
            try:
                result = run_fanficfare(["-o", "is_adult=true", "-l", source_url])
                if result.returncode == 0:
                    extracted_urls = [url.strip() for url in result.stdout.split("\n") if url.strip()]
                    all_extracted_urls.extend(extracted_urls)
            except Exception:
                pass
            progress.advance(extract_task)

    if all_extracted_urls:
        console.print(f"[bold green]✓[/bold green] Extracted [bold]{len(all_extracted_urls)}[/bold] stories from {len(all_urls)} sources")

        if len(all_extracted_urls) > 0:
            sample_count = min(5, len(all_extracted_urls))
            sample_table = Table(title="Sample of Extracted URLs", box=ROUNDED)
            sample_table.add_column("URL", style="cyan")
            for i in range(sample_count):
                sample_table.add_row(all_extracted_urls[i])
            if len(all_extracted_urls) > sample_count:
                sample_table.add_row(f"... and {len(all_extracted_urls) - sample_count} more")
            console.print(sample_table)
    else:
        console.print("[bold red]✗[/bold red] No story URLs extracted")

    if output and all_extracted_urls:
        save_urls_to_file(all_extracted_urls, output)

    if download and all_extracted_urls:
        if Confirm.ask(f"Do you want to download all {len(all_extracted_urls)} extracted stories?"):
            console.print()
            perform_download(all_extracted_urls)
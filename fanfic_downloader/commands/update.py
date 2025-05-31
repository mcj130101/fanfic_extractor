# fanficdownloader/commands/update.py
import typer
import os
import glob
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.prompt import Confirm
from rich.table import Table
from rich.box import ROUNDED
from typing import Optional, List

from fanfic_downloader.utils import show_app_header, run_fanficfare, find_epub_files, open_folder, open_download_folder
from fanfic_downloader import config # Import config for USER_FOLDER

console = Console() # Each command module can have its own console instance if preferred

def update_epub_files_command(
        folder: Optional[str] = typer.Option(None, "--folder", "-f", help="Folder path to update EPUB files from"),
        recursive: bool = typer.Option(True, "--recursive", "-r", help="Search subfolders recursively"),
        force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """
    Update existing EPUB files using FanFicFare's --update-epub feature.

    This command will find all EPUB files in the specified folder (or default download folder)
    and attempt to update them with the latest versions from their original sources.

    Examples:
        fanfic update
        fanfic update -f /path/to/epub/folder
        fanfic update -f /path/to/folder --force
        fanfic update --no-recursive  # Only check the main folder, not subfolders
    """
    show_app_header()

    target_folder = folder if folder else config.USER_FOLDER

    if not os.path.exists(target_folder):
        console.print(f"[bold red]✗[/bold red] Folder does not exist: [blue]{target_folder}[/blue]")
        return
    if not os.path.isdir(target_folder):
        console.print(f"[bold red]✗[/bold red] Path is not a directory: [blue]{target_folder}[/blue]")
        return

    console.print(f"[bold]Searching for EPUB files in:[/bold] [blue]{target_folder}[/blue]")

    if recursive:
        epub_files = find_epub_files(target_folder)
        console.print(f"[bold]Found [cyan]{len(epub_files)}[/cyan] EPUB files (including subfolders)[/bold]")
    else:
        epub_files = glob.glob(os.path.join(target_folder, "*.epub"))
        console.print(f"[bold]Found [cyan]{len(epub_files)}[/cyan] EPUB files in main folder[/bold]")

    if not epub_files:
        console.print("[bold yellow]No EPUB files found to update![/bold yellow]")
        return

    if len(epub_files) > 0:
        sample_count = min(5, len(epub_files))
        sample_table = Table(title="EPUB Files to Update", box=ROUNDED)
        sample_table.add_column("Filename", style="green")
        sample_table.add_column("Location", style="blue")
        for i in range(sample_count):
            file_path = epub_files[i]
            filename = os.path.basename(file_path)
            location = os.path.dirname(file_path)
            sample_table.add_row(filename, location)
        if len(epub_files) > sample_count:
            sample_table.add_row(f"... and {len(epub_files) - sample_count} more files", "...")
        console.print(sample_table)

    if not force:
        if not Confirm.ask(f"Do you want to update all {len(epub_files)} EPUB files?"):
            console.print("[yellow]Update cancelled.[/yellow]")
            return

    console.print(f"[bold]Updating [cyan]{len(epub_files)}[/cyan] EPUB files...[/bold]")

    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
    ) as progress:

        update_task = progress.add_task("[bold]Updating EPUB files...[/bold]", total=len(epub_files))
        success_count = 0
        error_count = 0
        skipped_count = 0
        errors_detail = []

        for epub_file in epub_files:
            filename = os.path.basename(epub_file)
            file_dir = os.path.dirname(epub_file)
            progress.update(update_task, description=f"[bold]Updating:[/bold] {filename[:50]}...")

            try:
                result = run_fanficfare(["-o", "is_adult=true", "--update-epub", epub_file], working_dir=file_dir)
                if result.returncode == 0:
                    output_lower = result.stdout.lower()
                    if "already up to date" in output_lower or "no update needed" in output_lower:
                        skipped_count += 1
                    else:
                        success_count += 1
                else:
                    error_count += 1
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    errors_detail.append((filename, error_msg))
            except Exception as e:
                error_count += 1
                errors_detail.append((filename, str(e)))
            progress.advance(update_task)

    console.print(f"\n[bold]Update Summary:[/bold]")
    if success_count > 0:
        console.print(f"[bold green]✓[/bold green] Successfully updated [bold]{success_count}[/bold] files")
    if skipped_count > 0:
        console.print(f"[bold yellow]⏭[/bold yellow] Skipped [bold]{skipped_count}[/bold] files (already up to date)")
    if error_count > 0:
        console.print(f"[bold red]✗[/bold red] Failed to update [bold]{error_count}[/bold] files")

        if 0 < len(errors_detail) <= 10:
            console.print("\n[bold red]Error Details:[/bold red]")
            error_table = Table(box=ROUNDED)
            error_table.add_column("File", style="red")
            error_table.add_column("Error", style="yellow")
            for filename, error_msg in errors_detail:
                if len(error_msg) > 100:
                    error_msg = error_msg[:97] + "..."
                error_table.add_row(filename, error_msg)
            console.print(error_table)
        elif len(errors_detail) > 10:
            console.print(f"[dim]Too many errors to display ({len(errors_detail)} total)[/dim]")

    if success_count > 0 and Confirm.ask("Open download folder?"):
        if folder:
            open_folder(target_folder)
        else:
            open_download_folder()
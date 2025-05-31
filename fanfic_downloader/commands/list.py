# fanficdownloader/commands/list.py
import typer
import os
import glob
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from rich.prompt import Confirm
from rich.filesize import decimal as format_filesize # Ensure this is imported
from typing import Optional

from fanfic_downloader.utils import show_app_header, open_download_folder, get_file_details
from fanfic_downloader import config # Import config for USER_FOLDER

console = Console()

def list_downloaded_files_command(
        detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed file information"),
        sort_by: str = typer.Option("name", "--sort", "-s", help="Sort by: name, date, size"),
):
    """
    List downloaded stories in the download folder.

    Examples:
        fanfic list
        fanfic list -d
        fanfic list -s size
    """
    show_app_header()

    epub_files = glob.glob(os.path.join(config.USER_FOLDER, "*.epub"))

    if not epub_files:
        console.print(f"[bold yellow]No EPUB files found in:[/bold yellow] {config.USER_FOLDER}")
        return

    # Sort files based on sorting option
    if sort_by.lower() == "name":
        epub_files.sort(key=lambda path: os.path.basename(path).lower())
    elif sort_by.lower() == "date":
        epub_files.sort(key=lambda path: os.path.getmtime(path), reverse=True)
    elif sort_by.lower() == "size":
        epub_files.sort(key=lambda path: os.path.getsize(path), reverse=True)
    else:
        console.print(f"[bold red]Invalid sort option:[/bold red] '{sort_by}'. Valid options are: name, date, size.")
        return

    table = Table(title=f"Downloaded Stories in {config.USER_FOLDER}", box=ROUNDED)
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Filename", style="green")
    table.add_column("Size", style="magenta")
    table.add_column("Date", style="yellow")
    if detailed:
        table.add_column("Path", style="blue")

    for i, file_path in enumerate(epub_files):
        file_details = get_file_details(file_path)
        if detailed:
            table.add_row(str(i + 1), file_details["name"], file_details["size"], file_details["date"], file_details["path"])
        else:
            table.add_row(str(i + 1), file_details["name"], file_details["size"], file_details["date"])

    console.print(table)

    total_size = sum(os.path.getsize(file) for file in epub_files)
    console.print(f"[bold]Total:[/bold] {len(epub_files)} files, {format_filesize(total_size)}")

    if Confirm.ask("Open download folder?"):
        open_download_folder()
# fanficdownloader/utils.py
import os
import sys
import subprocess
import glob
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.filesize import decimal as format_filesize
from rich.prompt import Confirm
from rich.table import Table
from rich.box import ROUNDED

# Initialize Rich console for utilities. Commands will also have their own instances,
# or could share this if passed around. For simple printing, separate instances are fine.
console = Console()

def show_app_header():
    """Display a stylish app header."""
    header = Panel(
        "[bold blue]FanFic Downloader CLI[/bold blue]\n[italic]Powered by FanFicFare[/italic]",
        border_style="blue",
        expand=False
    )
    console.print(header)

def run_fanficfare(args: List[str], hide_console: bool = True, working_dir: Optional[str] = None) -> subprocess.CompletedProcess:
    """
    Run the fanficfare command with the given arguments.

    Args:
        args: List of arguments to pass to fanficfare
        hide_console: Whether to hide the console window on Windows
        working_dir: Directory to run the command from (None = current directory)

    Returns:
        CompletedProcess object with the result
    """
    startupinfo = None
    if sys.platform == 'win32' and hide_console:
        # For Windows, use STARTUPINFO to hide the console
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

    try:
        result = subprocess.run(
            ["fanficfare"] + args,
            capture_output=True,
            text=True,
            check=False,
            startupinfo=startupinfo,
            cwd=working_dir
        )
        return result
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] FanFicFare not found. Please install it with:")
        console.print("[yellow]pip install fanficfare[/yellow]")
        sys.exit(1)

def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file, one URL per line"""
    try:
        with open(file_path, "r") as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]
        console.print(f"[green]✓[/green] Loaded [bold]{len(urls)}[/bold] URLs from {file_path}")
        return urls
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error loading file {file_path}: {str(e)}")
        return []

def save_urls_to_file(urls: List[str], file_path: str) -> bool:
    """Save a list of URLs to a text file"""
    try:
        with open(file_path, "w") as file:
            for url in urls:
                file.write(f"{url}\n")
        console.print(f"[green]✓[/green] Saved [bold]{len(urls)}[/bold] URLs to {file_path}")
        return True
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error saving to file {file_path}: {str(e)}")
        return False

def find_epub_files(folder_path: str) -> List[str]:
    """
    Recursively find all EPUB files in a folder and its subfolders.

    Args:
        folder_path: Path to the folder to search

    Returns:
        List of full paths to EPUB files
    """
    epub_files = []
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.epub'):
                    epub_files.append(os.path.join(root, file))
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error searching folder {folder_path}: {str(e)}")
    return epub_files

def open_folder(folder_path: str):
    """Open a specific folder in the file explorer based on OS."""
    try:
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', folder_path], check=True)
        else:  # Linux/Unix
            subprocess.run(['xdg-open', folder_path], check=True)
        console.print(f"[green]✓[/green] Opened folder: [blue]{folder_path}[/blue]")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Could not open folder: {str(e)}")

def open_download_folder():
    """Wrapper to open the configured download folder."""
    # Import config here to avoid potential circular dependency if config imports utils
    from fanfic_downloader import config
    open_folder(config.USER_FOLDER)

def get_file_details(file_path: str) -> dict:
    """Gets common details for a given file path (name, size, date, path)."""
    file_info = os.stat(file_path)
    file_name = os.path.basename(file_path)
    file_size = format_filesize(file_info.st_size)

    # Use modification time for consistency across platforms for 'date'
    creation_date = datetime.fromtimestamp(int(file_info.st_mtime)).strftime("%Y-%m-%d %H:%M")
    return {
        "name": file_name,
        "size": file_size,
        "date": creation_date,
        "path": file_path
    }
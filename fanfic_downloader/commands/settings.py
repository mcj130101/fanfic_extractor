# fanficdownloader/commands/settings.py
import typer
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from typing import Optional

from fanfic_downloader.utils import show_app_header, open_folder, open_download_folder
from fanfic_downloader import config # Import config for USER_FOLDER and saving

console = Console() # Each command module can have its own console instance if preferred

def change_download_location(new_folder: str):
    """Change and save the download folder location"""
    try:
        os.makedirs(new_folder, exist_ok=True)
        config.save_config(new_folder) # This function updates config.USER_FOLDER internally
        console.print(f"[bold green]✓[/bold green] Download location changed to: [blue]{config.USER_FOLDER}[/blue]")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error changing download location: {str(e)}")

def manage_settings_command(
        folder: Optional[str] = typer.Option(None, "--folder", "-f", help="Change download folder location"),
        open_folder_flag: bool = typer.Option(False, "--open", "-o", help="Open download folder in file explorer"),
):
    """
    View and manage application settings.

    Examples:
        fanfic settings
        fanfic settings -f /path/to/download/folder
        fanfic settings -o
    """
    show_app_header()

    settings_panel = Panel.fit(
        f"[bold]Current Settings[/bold]\n\n"
        f"[bold]Download Folder:[/bold] [blue]{config.USER_FOLDER}[/blue]\n"
        f"[bold]Config File:[/bold] [blue]{os.path.abspath(config.CONFIG_FILE)}[/blue]",
        title="Settings",
        border_style="green"
    )
    console.print(settings_panel)

    if folder:
        change_download_location(folder)
    if open_folder_flag:
        open_download_folder()

    if not folder and not open_folder_flag:
        console.print("\n[bold]Available Actions:[/bold]")
        console.print("1. Change download folder")
        console.print("2. Open download folder")
        console.print("3. Exit")

        choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="3")

        if choice == "1":
            folder_path = Prompt.ask("Enter new download folder path")
            if folder_path:
                change_download_location(folder_path)
        elif choice == "2":
            open_download_folder()
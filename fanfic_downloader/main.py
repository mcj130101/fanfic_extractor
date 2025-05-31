# fanficdownloader/cli.py
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Initialize Typer app
app = typer.Typer(
    no_args_is_help=True, # This will show help if no args are given, but we'll override it
    rich_markup_mode="rich",
    help="FanFic Downloader CLI - Download fan fiction stories from various sites"
)

# Initialize Rich console (main instance, though others are also initialized in modules)
console = Console()

# Import command functions from their respective modules
# Renamed command functions to avoid clashes with original script's local function names
from fanfic_downloader.commands.download import download_stories_command
from fanfic_downloader.commands.extract import extract_story_urls_command
from fanfic_downloader.commands.update import update_epub_files_command
from fanfic_downloader.commands.list import list_downloaded_files_command
from fanfic_downloader.commands.settings import manage_settings_command
from fanfic_downloader.commands.help import show_help_command

# Add commands to the Typer app instance
app.command(name="download", help="[bold blue]Download[/bold blue] fan fiction stories.")(download_stories_command)
app.command(name="extract", help="[bold blue]Extract[/bold blue] story URLs from a source.")(extract_story_urls_command)
app.command(name="update", help="[bold blue]Update[/bold blue] existing downloaded EPUB files.")(update_epub_files_command)
app.command(name="list", help="[bold blue]List[/bold blue] previously downloaded stories.")(list_downloaded_files_command)
app.command(name="settings", help="[bold blue]Manage[/bold blue] application settings.")(manage_settings_command)
app.command(name="help", help="[bold blue]Help[/bold blue] Get help Commands")(show_help_command) # The `help` command is often explicitly added


# --- Main Callback for Interactive Mode ---
@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    FanFic Downloader CLI tool.
    """
    global interactive_commands
    if ctx.invoked_subcommand is None:
        console.print("\n[bold green]Welcome to FanFic Downloader![/bold green]")
        console.print("No command provided. Please select an option from the menu below:")
        console.print("-" * 40)

        # Map display keys to actual command names
        interactive_commands = {
            "d": "download",
            "e": "extract",
            "u": "update",
            "l": "list",
            "s": "settings",
            "h": "help",  # Special internal 'help' option
            "x": "exit"  # Option to exit
        }

        # Prepare a list of formatted command options for display
        display_options = []
        for key, cmd_name in interactive_commands.items():
            if cmd_name == "exit":
                display_options.append(f"[bold red]{key}[/bold red]: {cmd_name.capitalize()}")
            elif cmd_name == "help":
                display_options.append(f"[bold yellow]{key}[/bold yellow]: Show [bold yellow]Help[/bold yellow] menu")
            else:
                # FIX: Iterate through app.registered_commands to find the command object by name
                command_obj = None
                for registered_cmd in app.registered_commands:
                    if registered_cmd.name == cmd_name:
                        command_obj = registered_cmd
                        break  # Found it, no need to continue

                # Use the 'help' string from the command definition if available
                # Fallback to capitalized command name if no object or no help attribute
                cmd_help_text = command_obj.help if command_obj and hasattr(command_obj,
                                                                            'help') else cmd_name.capitalize()
                display_options.append(f"[bold blue]{key}[/bold blue]: {cmd_help_text}")

        console.print(f"Available commands: {' | '.join(display_options)}")
        console.print("-" * 40)

    while True:
            try:
                choice = Prompt.ask(
                    "Enter your choice",
                    choices=[key for key in interactive_commands.keys()],
                    show_choices=False,
                    default="h"  # Default to help
                ).lower()

                if choice == "x":
                    if Confirm.ask("[bold red]Are you sure you want to exit?[/bold red]", default=False):
                        raise typer.Exit()
                    else:
                        console.print("Continuing interactive session...")
                        console.print(f"\nAvailable commands: {' | '.join(display_options)}")  # Redisplay
                        continue

                selected_command_name = interactive_commands.get(choice)

                if selected_command_name == "help":
                    # Show the main Typer help when 'h' is chosen
                    console.print("\n" + ctx.get_help())
                    console.print("-" * 40)
                    console.print(f"\nAvailable commands: {' | '.join(display_options)}")  # Redisplay
                    continue  # Go back to prompt

                name_list = [command_obj.name for command_obj in app.registered_commands]
                target_command_obj = None
                if selected_command_name:  # Ensure a valid command name was selected from interactive_commands
                    for registered_cmd_obj in app.registered_commands:
                        if registered_cmd_obj.name == selected_command_name:
                            target_command_obj = registered_cmd_obj
                            break

                if target_command_obj:  # Check if we successfully found the command object
                    console.print(f"\n[bold green]Running command: {selected_command_name.capitalize()}[/bold green]")
                    console.print("=" * 40)

                    # Invoke the callback function associated with the command object
                    # The actual callable function is typically in the 'callback' attribute
                    ctx.invoke(target_command_obj.callback)  # <--- THIS IS THE FIX!

                    console.print("=" * 40)

                    if not Confirm.ask(
                            "[bold yellow]Command finished. Do you want to run another command?[/bold yellow]",
                            default=True):
                        raise typer.Exit()
                    else:
                        console.print("\n" + "=" * 40 + "\n")  # Separator
                        console.print("Please select another command or 'exit' to quit.")
                        console.print(f"Available commands: {' | '.join(display_options)}")

                else:  # This block handles invalid choices *after* checking for 'help'
                    # The previous 'else' clause here was trying to access selected_command_name
                    # as a key into app.registered_commands, which is a list, causing the error.
                    # This streamlined 'else' is for truly invalid interactive inputs.
                    console.print("[bold red]Invalid choice. Please try again.[/bold red]")
                    console.print(f"\nAvailable commands: {' | '.join(display_options)}")  # Redisplay

            except typer.Exit:
                console.print("[bold blue]Exiting FanFic Downloader. Goodbye![/bold blue]")
                raise  # Ensure Typer exits gracefully
            except Exception as e:
                console.print(f"\n[bold red]An unexpected error occurred during command execution:[/bold red] {e}")
                console.print("Please select another command or 'exit' to quit.")
                console.print("-" * 40)
                console.print(f"Available commands: {' | '.join(display_options)}")


def run():
    """Entry point for the application."""
    app()

if __name__ == "__main__":
    app()
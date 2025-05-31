# fanficdownloader/commands/help.py
import typer
from rich.console import Console
from rich.markdown import Markdown

from fanfic_downloader.utils import show_app_header

console = Console() # Each command module can have its own console instance if preferred

def show_help_command():
    """
    Show detailed help and examples for all commands.
    """
    show_app_header()

    help_text = """
    # FanFic Downloader CLI

    A command-line tool to download fan fiction stories from various sites
    using FanFicFare as the backend.

    ## Commands

    ### Download Stories

    Download stories from specific URLs.

    ```bash
    fanfic download -u [https://example.com/story1](https://example.com/story1) [https://example.com/story2](https://example.com/story2)
    fanfic download -f url_list.txt
    fanfic download -i  # Interactive mode
    ```

    ### Extract URLs

    Extract story URLs from listing pages, like author profiles or series pages.

    ```bash
    fanfic extract -u [https://example.com/author_page](https://example.com/author_page)
    fanfic extract -f sources.txt -o extracted_urls.txt
    fanfic extract -u [https://example.com/series/123](https://example.com/series/123) -d  # Extract and download
    ```

    ### Update EPUB Files

    Update existing EPUB files with their latest versions.

    ```bash
    fanfic update  # Update all EPUBs in default folder
    fanfic update -f /path/to/epub/folder  # Update EPUBs in specific folder
    fanfic update --no-recursive  # Only check main folder, not subfolders
    fanfic update --force  # Skip confirmation prompt
    ```

    ### List Downloaded Files

    View stories that have been downloaded.

    ```bash
    fanfic list  # Simple list
    fanfic list -d  # Detailed view
    fanfic list -s size  # Sort by size
    ```

    ### Manage Settings

    View and modify application settings.

    ```bash
    fanfic settings  # View current settings
    fanfic settings -f /path/to/download/folder  # Change download folder
    fanfic settings -o  # Open download folder
    ```

    ## Getting Started

    1. Make sure you have FanFicFare installed:
       ```bash
       pip install fanficfare
       ```

    2. Download a story:
       ```bash
       fanfic download -u [https://archiveofourown.org/works/12345678](https://archiveofourown.org/works/12345678)
       ```

    3. List your downloaded stories:
       ```bash
       fanfic list
       ```

    4. Update your existing stories:
       ```bash
       fanfic update
       ```
    """

    md = Markdown(help_text, style="dim")
    console.print(md)
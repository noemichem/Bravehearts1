import time
import pyfiglet
import typer
from langdetect import detect
from rich import print
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.text import Text
import shutil 

from core.querying import QueryProcessor

input_folder = "./data/index/index_all/index.pkl"
query_processor = QueryProcessor(input_folder)


app = typer.Typer()

# Rich console for output
console = Console()


def boolean_retrieval_conjunctive(query):
    lang = "english" if detect(query) == "en" else "italian"
    query_result = query_processor.query_process_and(query, lang)
    return query_result


def boolean_retrieval_disjunctive(query):
    lang = "english" if detect(query) == "en" else "italian"
    query_result = query_processor.query_process_and(query, lang)
    return query_result


def document_at_a_time(query):
    lang = "english" if detect(query) == "en" else "italian"
    query_result = query_processor.query_process_daat(query,lang)
    return query_result


def term_at_a_time(query):
    lang = "english" if detect(query) == "en" else "italian"
    query_result = query_processor.query_process_taat(query, lang)
    return query_result


def process_query(mode, query):
    """Handles queries based on the selected mode."""
    if mode == 1:
        return document_at_a_time(query)
    elif mode == 2:
        return term_at_a_time(query)
    elif mode == 3:
        return boolean_retrieval_conjunctive(query)
    elif mode == 4:
        return boolean_retrieval_disjunctive(query)
    else:
        return "[red]Invalid mode.[/red]"


def display_results(results):
    """
    Formats and displays search results using the rich library.
    """
    if not results:
        console.print("[bold red]No results found for the query.[/bold red]")
        return

    table = Table(title="Search Results", style="cyan", show_lines=True)
    table.add_column("Rank", justify="center", style="bold green")
    table.add_column("Title", style="bold white")
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("URL", style="magenta")

    for rank, result in enumerate(results, start=1):
        table.add_row(
            str(rank),
            result["title"],
            f"{result['score']:.4f}",
            f"[blue underline]{result['url']}[/blue underline]",
        )

    console.print(table)



def goodbye():
    # Display a colorful goodbye message with ASCII art
    console.print(Text("\n👋 Goodbye!", style="bold red"), justify="center")
    
    # Add a decorative line below
    console.print(Text("=" * 40, style="bold yellow"), justify="center")
    
    # Create an animation effect for a smooth exit
    farewell_message = [
        Text("🌟 Thank you for using UNIPI Search Engine! 🌟", style="bold green"),
        Text("✨ Have a great day! ✨", style="italic cyan"),
        Text("🚀 See you next time! 🚀\n", style="bold magenta"),
    ]
    
    for msg in farewell_message:
        console.print(msg, justify="center")
        time.sleep(1)  # Pause to create an animation effect

def get_terminal_width():
    return shutil.get_terminal_size().columns

def display_home():
    terminal_width = get_terminal_width()
    ascii_art = pyfiglet.figlet_format("UNIPI Search Engine", font="slant", width=terminal_width)
    console.print(ascii_art, style="bold green")    
    console.print("UNIPI Search Engine - CLI version 1.0.0", style="bold blue")

def display_horizontal_line():
    console.print("[bold white]" + "=" * get_terminal_width() + "[/bold white]")

def display_search_modes():
    display_horizontal_line()

    # Add a section for mode selection
    console.print("\n[bold yellow]Please choose a retrieval mode:[/bold yellow]\n")
    console.print("1. [green]Document-at-a-Time[/green]\n")
    console.print("2. [cyan]Term-at-a-Time[/cyan]\n")
    console.print("3. [blue]Boolean Retrieval (Conjunctive)[/blue]\n")
    console.print("4. [magenta]Boolean Retrieval (Disjunctive)[/magenta]\n")
    console.print("0. [red]Exit[/red]\n")

    console.print("\n[bold purple]👉 Enter your choice:[/bold purple] ", end="")

def invalid_input():
    console.print(
        "\n❌ [bold red]Invalid selection![/bold red] "
        "🔄 [yellow]Please choose again.[/yellow]\n",
        justify="center",
    )

def get_mode_name(mode : int):
    mode_names = {
        1: "Document-at-a-Time",
        2: "Term-at-a-Time",
        3: "Boolean Retrieval (Conjunctive)",
        4: "Boolean Retrieval (Disjunctive)",
    }
    return mode_names.get(mode, "Invalid Mode")

def display_current_mode(mode: int):
    display_horizontal_line()
    console.print(
            f"\n🌟 [bold green]You are now in mode:[/bold green] [cyan bold]{get_mode_name(mode)}[/cyan bold]"
        )
    console.print(
        "\n💡 Enter your queries or type [bold cyan]'change'[/bold cyan] to switch modes "
        "or [bold red]'exit'[/bold red] to quit.\n",
        style="italic yellow",
    )

@app.command()
def search_engine():
    """
    A CLI-based search engine for University of Pisa.
    """

    display_home()
   
    current_mode = None

    while True:
        if current_mode is None:

            display_search_modes()

            try:
                current_mode = int(typer.prompt("Enter the mode number"))
                if current_mode == 0:
                    goodbye()
                    break
                elif current_mode not in [1, 2, 3, 4]:
                    invalid_input()
                    current_mode = None
                    continue
            except ValueError:
                invalid_input()
                continue

        display_current_mode(current_mode)

        while True:
            query = typer.prompt("Enter your query")
            if query.lower() == "exit":
                goodbye()
                return
            elif query.lower() == "change":
                current_mode = None
                break
            else:
                result = process_query(current_mode, query)
                display_results(result)



if __name__ == "__main__":
    app()

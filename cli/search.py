import shutil
import time

import pyfiglet
import typer
from langdetect import detect
from rich.console import Console
from rich.table import Table
from rich.text import Text

from core.querying import QueryProcessor

input_folder = "./data/index/index_all/index.pkl"
query_processor = QueryProcessor(input_folder)


app = typer.Typer()

# Rich console for output
console = Console()


def detect_language(query: str) -> str:
    return "english" if detect(query) == "en" else "italian"


def boolean_retrieval_conjunctive(query):
    lang = detect_language(query)
    query_result = query_processor.query_process_and(query, lang)
    return query_result


def boolean_retrieval_disjunctive(query):
    lang = detect_language(query)
    query_result = query_processor.query_process_and(query, lang)
    return query_result


def document_at_a_time(query):
    lang = detect_language(query)
    query_result = query_processor.query_process_daat(query, lang)
    return query_result


def term_at_a_time(query):
    lang = detect_language(query)
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


def display_horizontal_line():
    console.print("[bold white]" + "=" * get_terminal_width() + "[/bold white]")  # noqa


def display_results(results, execution_time):
    """
    Formats and displays search results using the rich
    library with enhanced styling for a CLI search engine.
    """

    if not results:
        console.print(
            "[bold red]❌ No results found for the query. Try again![/bold red]\n",  # noqa
            justify="center",
        )
        return

    # Display the number of results found
    num_results = len(results)
    console.print(
        f"\n[bold yellow]🔍 {num_results} Results found in {execution_time:.2f} seconds[/bold yellow]\n"  # noqa
    )

    # Create a table with enhanced aesthetics
    table = Table(
        title="[bold yellow]🔎 Search Results[/bold yellow]",
        title_style="bold blue",
        show_lines=True,
        expand=True,
    )

    # Add columns with customized style
    table.add_column("Rank", justify="center", style="bold green", width=6)
    table.add_column("Title", style="bold white", width=30)
    if results[0].get("score") is not None:
        table.add_column("Score", justify="right", style="yellow", width=10)
    table.add_column("URL", style="magenta", width=40)

    # Add results to the table
    for rank, result in enumerate(results, start=1):
        if result.get("score") is not None:
            table.add_row(
                str(rank),
                result["title"],
                f"{result['score']:.4f}",
                f"[blue underline]{result['url']}[/blue underline]",
            )
        else:
            table.add_row(
                str(rank),
                result["title"],
                f"[blue underline]{result['url']}[/blue underline]",
            )

    # Display the table
    console.print(table)

    display_horizontal_line()


def goodbye():
    # Display a colorful goodbye message with ASCII art
    console.print(Text("\n👋 Goodbye!", style="bold red"), justify="center")

    # Add a decorative line below
    console.print(Text("=" * 40, style="bold yellow"), justify="center")

    # Create an animation effect for a smooth exit
    farewell_message = [
        Text(
            "🌟 Thank you for using UNIPI Search Engine! 🌟", style="bold green"
        ),  # noqa
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
    ascii_art = pyfiglet.figlet_format(
        "UNIPI Search Engine", font="slant", width=terminal_width
    )
    console.print(ascii_art, style="bold green")
    console.print("UNIPI Search Engine - CLI version 1.0.0", style="bold blue")


def display_search_modes():
    display_horizontal_line()

    # Add a section for mode selection
    console.print(
        "\n[bold yellow]Please choose a retrieval mode:[/bold yellow]\n"
    )  # noqa
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


def get_mode_name(mode: int):
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
        f"\n🌟 [bold green]You are now in mode:[/bold green] [cyan bold]{get_mode_name(mode)}[/cyan bold]"  # noqa
    )
    console.print(
        "\n💡 Enter your queries or type [bold cyan]'change'[/bold cyan] to switch modes "  # noqa
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
            query = typer.prompt("\nEnter your query")
            if query.lower() == "exit":
                goodbye()
                return
            elif query.lower() == "change":
                current_mode = None
                break
            else:
                start_time = time.time()
                result = process_query(current_mode, query)
                end_time = time.time()

                execution_time = end_time - start_time
                display_results(result, execution_time)


if __name__ == "__main__":
    app()

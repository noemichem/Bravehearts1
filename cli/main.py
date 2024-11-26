import time
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress

from core.querying import QueryProcessor

input_folder = "./outputs/index_en2/index.pkl"
query_processor = QueryProcessor(input_folder)


app = typer.Typer()

# Rich console for output
console = Console()

def boolean_retrieval(query):
    query_result = query_processor.query_process_and(query)
    final_result = query_processor.prepare_final_result(query_result)
    return final_result

def document_at_a_time(query):
    query_result = query_processor.query_process_daat(query)
    final_result = query_processor.prepare_final_result(query_result)
    return final_result

def term_at_a_time(query):
    query_result = query_processor.query_process_taat(query)
    final_result = query_processor.prepare_final_result(query_result)
    return final_result

def process_query(mode, query):
    """Handles queries based on the selected mode."""
    # if mode == 1:
    #     return boolean_retrieval(query)
    if mode == 1:
        return document_at_a_time(query)
    elif mode == 2:
        return term_at_a_time(query)
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
            f"[blue underline]{result['url']}[/blue underline]"
        )

    console.print(table)

@app.command()
def search_engine():
    """
    A CLI-based search engine for University of Pisa.
    """
    console.print("[bold cyan]Welcome to UNIPI Search Engine.![/bold cyan]", style="bold")
    current_mode = None

    while True:
        # Display the mode menu if the mode is not set
        if current_mode is None:
            console.print("\n[bold yellow]Please choose a retrieval mode:[/bold yellow]")
            # console.print("1. [green]Boolean Retrieval[/green]")
            console.print("1. [blue]Document-at-a-Time[/blue]")
            console.print("2. [magenta]Term-at-a-Time[/magenta]")
            console.print("0. [red]Exit[/red]")

            try:
                current_mode = int(typer.prompt("Enter the mode number"))
                if current_mode == 0:
                    print(Text("Goodbye!", style="bold red"))
                    break
                elif current_mode not in [1, 2]:
                    console.print("[red]Invalid selection. Please choose again.[/red]")
                    current_mode = None
                    continue
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")
                continue

        # Query loop for the selected mode
        console.print(f"\n[bold green]You are now in mode {current_mode}[/bold green]. Enter queries or type '[cyan]change[/cyan]' to switch mode or '[red]exit[/red]' to quit.")
        while True:
            query = typer.prompt("Enter your query")
            if query.lower() == "exit":
                print(Text("Goodbye!", style="bold red"))
                return
            elif query.lower() == "change":
                current_mode = None
                break
            else:
                result = process_query(current_mode, query)

                display_results(result)

# Entry point for Typer
if __name__ == "__main__":
    app()


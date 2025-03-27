"""
Command-line interface for the SearchAI application.
Provides a user-friendly CLI for searching and generating documents.
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from searchai.search.crew_search import perform_web_search
from searchai.reasoning.gemini_llm import process_with_gemini
from searchai.document_gen import markdown_gen, pdf_gen, ppt_gen
from searchai.db import db_handler
from searchai.config import validate_config
from searchai.utils.logging_config import setup_logging, get_logger
from searchai.utils.validation import validate_query, validate_format, validate_output_directory

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize Typer app
app = typer.Typer(
    name="searchai",
    help="SearchAI - An intelligent search and document generation tool",
    add_completion=False
)

# Initialize Rich console
console = Console()

logger.info("---------- searchai/cli/interface.py ----------")

async def process_search(
    query: str,
    format: str,
    output_dir: Path
) -> None:
    """
    Process a search query and generate output document.
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            try:
                # Perform web search
                search_task = progress.add_task(description="Searching the web...", total=None)
                search_results = await perform_web_search(query)
                progress.update(search_task, completed=True)
                
                if not search_results:
                    raise ValueError("No search results found")
                
                # Process results with Gemini
                process_task = progress.add_task(description="Processing results...", total=None)
                processed_content = await process_with_gemini(
                    query=query,
                    search_results=search_results,
                    output_format=format
                )
                progress.update(process_task, completed=True)
                
                if not processed_content or processed_content.startswith("Error:"):
                    raise ValueError(f"Content generation failed: {processed_content}")
                
                # Generate document
                doc_task = progress.add_task(description="Generating document...", total=None)
                
                try:
                    if format == "markdown":
                        await markdown_gen.generate_markdown(
                            content=processed_content,
                            query=query,
                            query_id=str(output_dir)
                        )
                    elif format == "pdf":
                        await pdf_gen.generate_pdf(
                            content=processed_content,
                            query=query,
                            query_id=str(output_dir)
                        )
                    elif format == "ppt":
                        await ppt_gen.generate_ppt(
                            content=processed_content,
                            query=query,
                            query_id=str(output_dir)
                        )
                        
                    progress.update(doc_task, completed=True)
                    
                except Exception as e:
                    raise ValueError(f"Document generation failed: {str(e)}")
                    
            except Exception as e:
                # Update the current task to show error
                for task_id in progress.task_ids:
                    if not progress.tasks[task_id].completed:
                        progress.update(
                            task_id,
                            description=f"[red]Failed:[/red] {progress.tasks[task_id].description}"
                        )
                raise
                
    except Exception as e:
        logger.error(f"Search process failed: {str(e)}")
        raise

@app.command()
def search(
    query: str = typer.Argument(..., help="The search query to process"),
    format: str = typer.Option(
        "markdown",
        "--format", "-f",
        help="Output format (markdown, pdf, ppt)",
        case_sensitive=False
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Custom output directory for generated documents"
    )
):
    """
    Search the web and generate a document based on the results.
    """
    try:
        # Log search request
        logger.info(f"Search request - Query: {query}, Format: {format}")
        
        # Validate all inputs before proceeding
        try:
            # Validate query
            validated_query = validate_query(query)
            
            # Validate format
            validated_format = validate_format(format)
            
            # Validate output directory
            validated_output_dir = validate_output_directory(output_dir)
            
            # Validate configuration (API keys, etc.)
            validate_config()
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            console.print(f"[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
            
        # Create a new event loop for this command
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the search process with validated inputs
            loop.run_until_complete(
                process_search(
                    query=validated_query,
                    format=validated_format,
                    output_dir=validated_output_dir
                )
            )
            
            # Only show success message if we get here (no exceptions)
            console.print("[green]Document generated successfully![/green]")
            
        except Exception as e:
            logger.error(f"Search process failed: {str(e)}")
            console.print(f"[red]Error:[/red] Search failed: {str(e)}")
            raise typer.Exit(1)
            
        finally:
            loop.close()
            
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        console.print(f"[red]Error:[/red] An unexpected error occurred: {str(e)}")
        raise typer.Exit(1)

@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of recent queries to show")
):
    """
    Show recent search query history.
    """
    try:
        # Create a new event loop for this command
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the history retrieval
            loop.run_until_complete(show_history(limit))
        finally:
            loop.close()
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

async def show_history(limit: int):
    """
    Display search query history.
    """
    # Initialize database
    await db_handler.init_db()
    
    # Get recent queries
    queries = await db_handler.get_query_history(limit)
    
    if not queries:
        console.print("[yellow]No search history found.[/yellow]")
        return
    
    # Create and populate table
    table = Table(title="Search History")
    table.add_column("ID", style="cyan")
    table.add_column("Query", style="white")
    table.add_column("Format", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Created At", style="blue")
    
    for query in queries:
        status_color = {
            "completed": "green",
            "failed": "red",
            "processing": "yellow",
            "pending": "blue"
        }.get(query.status, "white")
        
        table.add_row(
            str(query.id),
            query.query_text[:50] + ("..." if len(query.query_text) > 50 else ""),
            query.output_format.value,
            f"[{status_color}]{query.status}[/{status_color}]",
            query.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    console.print(table)

def display_search_results(results):
    """
    Display a summary of search results.
    """
    table = Table(title="Search Results")
    table.add_column("Title", style="cyan")
    table.add_column("Source", style="blue")
    
    for result in results:
        table.add_row(
            result.get('title', 'Untitled'),
            result.get('url', 'No URL')
        )
    
    console.print(table)

if __name__ == "__main__":
    app()

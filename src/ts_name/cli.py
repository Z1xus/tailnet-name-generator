"""Command-line interface for tailnet name generator."""

import asyncio
import logging
import sys

import click

from ts_name.filters import FilterOperator
from ts_name.filters import create_filter
from ts_name.generator import TailnetNameGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Disable httpx logging
logging.getLogger("httpx").setLevel(logging.WARNING)


@click.group()
def main() -> None:
    """Tailnet name generator and setter for Tailscale."""
    pass


@main.command()
@click.option(
    "--cookie",
    envvar="TAILSCALE_COOKIE",
    required=True,
    help="Tailscale authentication cookie (or set TAILSCALE_COOKIE env var)",
)
@click.option(
    "--words",
    "-w",
    multiple=True,
    help="Words to filter for (can be used multiple times)",
)
@click.option(
    "--max-length",
    "-m",
    type=int,
    default=None,
    help="Maximum length of tailnet name",
)
@click.option(
    "--min-length",
    type=int,
    default=None,
    help="Minimum length of tailnet name",
)
@click.option(
    "--operator",
    "-o",
    type=click.Choice(["and", "or"], case_sensitive=False),
    default="and",
    help="How to combine word filters (AND or OR)",
)
@click.option(
    "--limit",
    "-l",
    type=int,
    default=10,
    help="Maximum number of results to return",
)
@click.option(
    "--max-iterations",
    type=int,
    default=None,
    help="Maximum number of API calls",
)
@click.option(
    "--delay",
    type=float,
    default=0.5,
    help="Delay between API requests in seconds",
)
@click.option(
    "--timeout",
    type=float,
    default=30.0,
    help="Request timeout in seconds",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def search(
    cookie: str,
    words: tuple[str, ...],
    max_length: int | None,
    min_length: int | None,
    operator: str,
    limit: int,
    max_iterations: int | None,
    delay: float,
    timeout: float,
    verbose: bool,
) -> None:
    """
    Search for matching Tailscale tailnet fun names.

    Examples:

    \b
    # Find names containing "king" and shorter than 10 chars
    ts-name search --cookie YOUR_COOKIE -w king -m 10

    \b
    # Find names containing either "yo" or "ya"
    ts-name search --cookie YOUR_COOKIE -w yo -w ya --operator or

    \b
    # Find short names (max 8 chars)
    ts-name search --cookie YOUR_COOKIE -m 8
    """
    if verbose:
        logging.getLogger("ts_name").setLevel(logging.DEBUG)

    # Create filter
    operator_enum = (
        FilterOperator.OR if operator.lower() == "or" else FilterOperator.AND
    )
    filter_fn = create_filter(
        words=list(words) if words else None,
        max_length=max_length,
        min_length=min_length,
        operator=operator_enum,
    )

    # Create generator
    generator = TailnetNameGenerator(
        cookie=cookie,
        delay=delay,
        timeout=timeout,
    )

    # Run the generator with streaming output
    async def stream_results() -> None:
        """Stream results as they're found."""
        count = 0
        header_shown = False

        try:
            async for name, token in generator.generate(
                filter_fn=filter_fn,
                max_iterations=max_iterations,
            ):
                if not header_shown:
                    click.echo("Streaming matching tailnet names:\n")
                    header_shown = True

                count += 1
                click.echo(f"{count}. {name} (token: {token})")

                if count >= limit:
                    break

            if count == 0:
                click.echo("No matching tailnet names found.", err=True)
                sys.exit(1)

        except asyncio.CancelledError:
            click.echo("\nSearch cancelled by user.", err=True)
            sys.exit(130)

    try:
        asyncio.run(stream_results())
    except KeyboardInterrupt:
        click.echo("\nSearch cancelled by user.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            logger.exception("Unexpected error")
        sys.exit(1)


@main.command()
@click.option(
    "--cookie",
    envvar="TAILSCALE_COOKIE",
    required=True,
    help="Tailscale authentication cookie (or set TAILSCALE_COOKIE env var)",
)
@click.argument("token")
@click.option(
    "--timeout",
    type=float,
    default=30.0,
    help="Request timeout in seconds",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def set_name(
    cookie: str,
    token: str,
    timeout: float,
    verbose: bool,
) -> None:
    """
    Set the tailnet name to a specific offer.

    TOKEN: The full token from the search results
           (format: awesome-name.ts.net/timestamp/hash)

    Examples:

    \b
    # Set a specific name using its token
    ts-name set-name --cookie YOUR_COOKIE "awesome-name.ts.net/timestamp/hash"

    \b
    # Using environment variables
    export TAILSCALE_COOKIE="your_cookie"
    ts-name set-name "awesome-name.ts.net/timestamp/hash"
    """
    if verbose:
        logging.getLogger("ts_name").setLevel(logging.DEBUG)

    # Extract the tcd (tailnet name) from the token
    # Token format: tailnet-name.ts.net/timestamp/hash
    parts = token.split("/")
    if len(parts) < 3:
        click.echo(
            "Error: Invalid token format. Expected: tailnet-name.ts.net/timestamp/hash",
            err=True,
        )
        sys.exit(1)

    tcd = parts[0]

    generator = TailnetNameGenerator(
        cookie=cookie,
        timeout=timeout,
    )

    try:
        asyncio.run(generator.set_name(tcd, token))
        click.echo(f"✓ Successfully set tailnet name to {tcd}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Failed to set tailnet name: {e}", err=True)
        if verbose:
            logger.exception("Unexpected error")
        sys.exit(1)

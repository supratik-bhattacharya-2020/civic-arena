"""Rich CLI entry flow for CivicArena."""

from __future__ import annotations

import argparse
import asyncio
import sys

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from civicarena.orchestrator import run_deliberation
from civicarena.types import (
    DQIScore,
    LLMConfig,
    Persona,
    RoundResult,
    Stance,
    Statement,
    Worldview,
)

console = Console()

DEMO_TOPICS = [
    ("Should we ban plastic bags?", "London"),
    ("Should public transit be free?", "New York City"),
    ("Should AI-generated art be copyrightable?", "San Francisco"),
    ("Should universities have speech codes?", "Oxford"),
    ("Should remote work be a legal right?", "Berlin"),
]

STANCE_COLORS = {
    Stance.STRONGLY_FOR: "bold green",
    Stance.FOR: "green",
    Stance.NEUTRAL: "yellow",
    Stance.AGAINST: "red",
    Stance.STRONGLY_AGAINST: "bold red",
}

STANCE_LABELS = {
    Stance.STRONGLY_FOR: "STRONGLY FOR",
    Stance.FOR: "FOR",
    Stance.NEUTRAL: "NEUTRAL",
    Stance.AGAINST: "AGAINST",
    Stance.STRONGLY_AGAINST: "STRONGLY AGAINST",
}


class RichCallback:
    """Rich terminal output callback for deliberation events."""

    def __init__(self, console: Console):
        self.console = console
        self._current_text = ""

    async def on_personas_generated(self, personas: list[Persona]) -> None:
        self.console.print()
        table = Table(title="Citizen Agents", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="bold")
        table.add_column("Age", justify="center")
        table.add_column("Occupation")
        table.add_column("Stance", justify="center")
        table.add_column("Style")

        for p in personas:
            stance_style = STANCE_COLORS.get(p.initial_stance, "white")
            table.add_row(
                p.name,
                str(p.age),
                p.occupation,
                Text(STANCE_LABELS[p.initial_stance], style=stance_style),
                p.communication_style,
            )

        self.console.print(table)
        self.console.print()

    async def on_worldview_built(self, worldview: Worldview) -> None:
        name = worldview.persona.name
        sources_count = len(worldview.sources)
        self.console.print(
            f"  [dim]Researched worldview for[/dim] [bold]{name}[/bold] "
            f"[dim]({sources_count} sources)[/dim]"
        )

    async def on_round_start(self, round_number: int, round_name: str) -> None:
        self.console.print()
        self.console.rule(f"[bold cyan]Round {round_number}: {round_name}[/bold cyan]")
        self.console.print()

    async def on_statement_start(self, persona_name: str) -> None:
        self._current_text = ""
        self.console.print(f"  [bold yellow]{persona_name}:[/bold yellow]")

    async def on_statement_chunk(self, chunk: str) -> None:
        self._current_text += chunk
        # Print chunks inline for streaming effect
        self.console.print(chunk, end="", highlight=False)

    async def on_statement_end(self, statement: Statement) -> None:
        if self._current_text:
            # Already streamed, just add newline
            self.console.print()
        else:
            # Non-streaming: print the full statement
            self.console.print(f"  {statement.content}")
        self.console.print()

    async def on_round_end(self, round_result: RoundResult) -> None:
        pass


def _print_banner() -> None:
    """Print the CivicArena banner."""
    banner = Text()
    banner.append("CivicArena", style="bold cyan")
    banner.append(" — ", style="dim")
    banner.append("Multi-Agent Civic Deliberation", style="italic")
    console.print(Panel(banner, border_style="cyan"))


def _print_dqi_score(score: DQIScore) -> None:
    """Print the DQI score card."""
    console.print()
    console.rule("[bold cyan]Deliberation Quality Score[/bold cyan]")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric", style="bold")
    table.add_column("Score", justify="center")
    table.add_column("Max", justify="center", style="dim")

    table.add_row("Justification", str(score.justification_level), "3")
    table.add_row("Respect", str(score.respect), "2")
    table.add_row("Constructive Politics", str(score.constructive_politics), "2")
    table.add_row("Overall Quality", str(score.overall_quality), "10")

    console.print(table)
    console.print()
    console.print(f"[bold]Summary:[/bold] {score.summary}")

    if score.highlights:
        console.print("\n[bold green]Highlights:[/bold green]")
        for h in score.highlights:
            console.print(f"  + {h}")

    if score.concerns:
        console.print("\n[bold red]Areas for Improvement:[/bold red]")
        for c in score.concerns:
            console.print(f"  - {c}")


def _print_final_votes(votes: dict[str, Stance]) -> None:
    """Print the final vote tally."""
    console.print()
    console.rule("[bold cyan]Final Votes[/bold cyan]")
    console.print()

    for name, stance in votes.items():
        style = STANCE_COLORS.get(stance, "white")
        label = STANCE_LABELS.get(stance, stance.value)
        console.print(f"  [bold]{name}:[/bold] [{style}]{label}[/{style}]")

    # Vote summary
    vote_counts: dict[str, int] = {}
    for stance in votes.values():
        label = STANCE_LABELS[stance]
        vote_counts[label] = vote_counts.get(label, 0) + 1

    console.print()
    for label, count in sorted(vote_counts.items(), key=lambda x: -x[1]):
        bar = "#" * (count * 4)
        console.print(f"  {label:20s} {bar} ({count})")


def _select_demo_topic() -> tuple[str, str]:
    """Interactive topic selection from demo topics."""
    console.print("\n[bold]Select a demo topic:[/bold]\n")
    for i, (topic, location) in enumerate(DEMO_TOPICS, 1):
        console.print(f"  [cyan]{i}.[/cyan] {topic} [dim]({location})[/dim]")

    console.print()
    while True:
        try:
            choice = console.input("[bold]Enter number (1-5): [/bold]")
            idx = int(choice.strip()) - 1
            if 0 <= idx < len(DEMO_TOPICS):
                return DEMO_TOPICS[idx]
        except (ValueError, EOFError):
            pass
        console.print("[red]Invalid choice. Please enter 1-5.[/red]")


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="civicarena",
        description="CivicArena — Multi-agent civic deliberation platform",
    )
    parser.add_argument("topic", nargs="?", help="The policy question to debate")
    parser.add_argument("--location", "-l", help="Location for the deliberation")
    parser.add_argument("--agents", "-n", type=int, default=5, help="Number of agents (default: 5)")
    parser.add_argument("--model", "-m", help="LLM model to use")
    parser.add_argument("--base-url", help="OpenAI-compatible API base URL")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Longer, more detailed responses")
    parser.add_argument("--demo", "-d", action="store_true", help="Select from demo topics")
    return parser.parse_args()


def main() -> None:
    """Main CLI entry point."""
    args = _parse_args()

    _print_banner()

    # Determine topic and location
    if args.demo or (not args.topic and sys.stdin.isatty()):
        topic, location = _select_demo_topic()
    elif args.topic:
        topic = args.topic
        location = args.location or "United States"
    else:
        console.print("[red]Error: Please provide a topic or use --demo[/red]")
        sys.exit(1)

    console.print(f"\n[bold]Topic:[/bold] {topic}")
    console.print(f"[bold]Location:[/bold] {location}\n")

    # Build LLM config
    config_kwargs: dict = {}
    if args.model:
        config_kwargs["model"] = args.model
    if args.base_url:
        config_kwargs["base_url"] = args.base_url
    if args.api_key:
        config_kwargs["api_key"] = args.api_key

    config = LLMConfig(**config_kwargs) if config_kwargs else None

    callback = RichCallback(console)

    async def _run() -> None:
        result = await run_deliberation(
            topic=topic,
            location=location,
            persona_count=args.agents,
            config=config,
            callback=callback,
            stream=not args.no_stream,
            verbose=args.verbose,
        )

        # Print final results
        _print_final_votes(result.final_votes)

        if result.dqi_score:
            _print_dqi_score(result.dqi_score)

        console.print()
        console.print("[bold cyan]Deliberation complete.[/bold cyan]")

    # Run the async deliberation
    asyncio.run(_run())

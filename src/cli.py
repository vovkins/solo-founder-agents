"""CLI for Solo Founder Agents."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.settings import settings
from src.pipeline import pipeline, PipelineStage, Checkpoint
from src.tools.state import state_manager
from src.tools import (
    get_issue_details,
    list_open_issues,
    create_github_issue,
    close_issue,
)


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="solo-founder-agents")
def cli():
    """Solo Founder Agents — Multi-agent AI system for solo founders."""
    pass


@cli.command()
def status():
    """Show project status."""
    status_data = pipeline.get_status()

    # Status panel
    stage_emoji = {
        PipelineStage.REQUIREMENTS.value: "📋",
        PipelineStage.DESIGN.value: "🎨",
        PipelineStage.IMPLEMENTATION.value: "💻",
        PipelineStage.REVIEW.value: "👀",
        PipelineStage.QA.value: "✅",
        PipelineStage.DOCUMENTATION.value: "📝",
        PipelineStage.COMPLETE.value: "🎉",
    }

    emoji = stage_emoji.get(status_data["current_stage"], "🔄")

    console.print(Panel(
        f"{emoji} Current Stage: [bold]{status_data['current_stage']}[/bold]",
        title="Project Status",
        border_style="blue",
    ))

    # State info
    state = status_data.get("state", {})
    if state.get("prd_path"):
        console.print(f"📄 PRD: {state['prd_path']}")
    if state.get("system_design_path"):
        console.print(f"🏗️ System Design: {state['system_design_path']}")
    if state.get("pr_urls"):
        console.print(f"🔀 PRs: {len(state['pr_urls'])}")

    # Agent status table
    agents = status_data.get("agents", {})
    if agents:
        table = Table(title="Agents")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Current Task")

        for agent_name, agent_state in agents.items():
            status = agent_state.get("status", "idle")
            status_style = "green" if status == "idle" else "yellow"
            task = agent_state.get("current_task", "-")
            table.add_row(agent_name, f"[{status_style}]{status}[/{status_style}]", task or "-")

        console.print(table)


@cli.command()
@click.option("--label", "-l", multiple=True, help="Filter by label")
@click.option("--limit", default=20, help="Maximum issues to show")
def issues(label, limit):
    """List open GitHub issues."""
    issues_list = list_open_issues(list(label) if label else None)

    if not issues_list:
        console.print("[yellow]No open issues found[/yellow]")
        return

    table = Table(title=f"Open Issues ({len(issues_list)})")
    table.add_column("#", style="cyan", width=6)
    table.add_column("Title", style="white")
    table.add_column("Labels", style="blue")

    for issue in issues_list[:limit]:
        labels_str = ", ".join(issue.get("labels", []))[:30]
        table.add_row(
            str(issue["number"]),
            issue["title"][:50],
            labels_str,
        )

    console.print(table)

    if len(issues_list) > limit:
        console.print(f"\n[dim]...and {len(issues_list) - limit} more[/dim]")


@cli.command()
@click.argument("issue_number", type=int)
def issue(issue_number):
    """Show issue details."""
    issue_data = get_issue_details(issue_number)

    if not issue_data:
        console.print(f"[red]Issue #{issue_number} not found[/red]")
        return

    console.print(Panel(
        issue_data.get("body", "No description")[:500],
        title=f"#{issue_data['number']} — {issue_data['title']}",
        border_style="blue",
    ))

    console.print(f"\n[cyan]State:[/cyan] {issue_data.get('state')}")
    console.print(f"[cyan]Labels:[/cyan] {', '.join(issue_data.get('labels', []))}")
    console.print(f"[cyan]URL:[/cyan] {issue_data.get('url')}")


@cli.command()
@click.argument("issue_number", type=int)
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode with checkpoints")
def run(issue_number, interactive):
    """Run a task/issue through the agent pipeline."""
    issue_data = get_issue_details(issue_number)

    if not issue_data:
        console.print(f"[red]Issue #{issue_number} not found[/red]")
        return

    console.print(Panel(
        f"Starting execution of Issue #{issue_number}\n{issue_data['title']}",
        title="🚀 Running Task",
        border_style="green",
    ))

    # Set task status
    state_manager.set_task_status(str(issue_number), "in_progress", {
        "title": issue_data["title"],
        "url": issue_data["url"],
    })

    if interactive:
        console.print("\n[yellow]Interactive mode enabled[/yellow]")
        console.print("Pipeline will pause at checkpoints for your review.\n")

    # Run implementation phase
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running implementation...", total=None)

        result = pipeline.run_implementation_phase(issue_number)

        progress.update(task, description="Implementation complete!")

    console.print(f"\n[green]✅ Task #{issue_number} completed![/green]")
    console.print(f"Result: {result.get('status')}")

    state_manager.set_task_status(str(issue_number), "completed")


@cli.command()
def checkpoints():
    """Show checkpoint status."""
    checkpoints_data = state_manager.state.get("checkpoints", {})

    if not checkpoints_data:
        console.print("[yellow]No checkpoints found[/yellow]")
        return

    table = Table(title="Checkpoints")
    table.add_column("Checkpoint", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Artifacts")

    status_colors = {
        "pending_review": "yellow",
        "approved": "green",
        "rejected": "red",
    }

    for cp_id, cp_data in checkpoints_data.items():
        status = cp_data.get("status", "unknown")
        color = status_colors.get(status, "white")
        artifacts = str(len(cp_data.get("artifacts", [])))

        table.add_row(
            cp_id,
            f"[{color}]{status}[/{color}]",
            artifacts,
        )

    console.print(table)


@cli.command()
@click.argument("checkpoint_id")
@click.option("--notes", "-n", default="", help="Approval notes")
def approve(checkpoint_id, notes):
    """Approve a checkpoint."""
    try:
        checkpoint = Checkpoint(checkpoint_id)
    except ValueError:
        console.print(f"[red]Invalid checkpoint: {checkpoint_id}[/red]")
        return

    pipeline.approve_checkpoint(checkpoint, notes)
    console.print(f"[green]✅ Checkpoint {checkpoint_id} approved![/green]")


@cli.command()
@click.argument("checkpoint_id")
@click.argument("reason")
def reject(checkpoint_id, reason):
    """Reject a checkpoint."""
    try:
        checkpoint = Checkpoint(checkpoint_id)
    except ValueError:
        console.print(f"[red]Invalid checkpoint: {checkpoint_id}[/red]")
        return

    pipeline.reject_checkpoint(checkpoint, reason)
    console.print(f"[red]❌ Checkpoint {checkpoint_id} rejected: {reason}[/red]")


@cli.command()
@click.option("--title", "-t", prompt="Issue title", help="Issue title")
@click.option("--body", "-b", prompt="Issue body", default="", help="Issue body")
@click.option("--label", "-l", multiple=True, help="Labels to apply")
def new_issue(title, body, label):
    """Create a new GitHub issue."""
    url = create_github_issue(title, body, list(label) if label else None)
    console.print(f"[green]✅ Issue created: {url}[/green]")


@cli.command()
@click.argument("issue_number", type=int)
@click.option("--comment", "-c", default="", help="Closing comment")
def close(issue_number, comment):
    """Close a GitHub issue."""
    url = close_issue(issue_number)
    console.print(f"[green]✅ Issue #{issue_number} closed: {url}[/green]")


@cli.command()
def config():
    """Show current configuration."""
    console.print(Panel(
        f"[cyan]GitHub Repo:[/cyan] {settings.github_repo}\n"
        f"[cyan]Developer LLM:[/cyan] {settings.llm_developer}\n"
        f"[cyan]Reviewer LLM:[/cyan] {settings.llm_reviewer}\n"
        f"[cyan]PM LLM:[/cyan] {settings.llm_pm}\n"
        f"[cyan]Analyst LLM:[/cyan] {settings.llm_analyst}\n"
        f"[cyan]Architect LLM:[/cyan] {settings.llm_architect}\n"
        f"[cyan]Designer LLM:[/cyan] {settings.llm_designer}\n"
        f"[cyan]QA LLM:[/cyan] {settings.llm_qa}\n"
        f"[cyan]Tech Writer LLM:[/cyan] {settings.llm_tech_writer}",
        title="Configuration",
        border_style="blue",
    ))


@cli.command()
def init():
    """Initialize a new project."""
    console.print(Panel(
        "🚀 Initializing Solo Founder Agents\n\n"
        "This will set up the project structure and configuration.",
        title="Initialization",
        border_style="green",
    ))

    # Check configuration
    console.print("\n📋 Checking configuration...")

    if not settings.github_token:
        console.print("[red]❌ GITHUB_TOKEN not set[/red]")
    else:
        console.print("[green]✅ GITHUB_TOKEN configured[/green]")

    if not settings.openrouter_api_key:
        console.print("[red]❌ OPENROUTER_API_KEY not set[/red]")
    else:
        console.print("[green]✅ OPENROUTER_API_KEY configured[/green]")

    if not settings.github_repo:
        console.print("[red]❌ GITHUB_REPO not set[/red]")
    else:
        console.print(f"[green]✅ GITHUB_REPO: {settings.github_repo}[/green]")

    console.print("\n[green]✅ Project initialized![/green]")
    console.print("\nNext steps:")
    console.print("1. Create a PRD: [cyan]solo-founder-agents run <issue_number>[/cyan]")
    console.print("2. Check status: [cyan]solo-founder-agents status[/cyan]")
    console.print("3. View issues: [cyan]solo-founder-agents issues[/cyan]")


if __name__ == "__main__":
    cli()

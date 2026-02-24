import json
import typer
from rich.console import Console
from rich.table import Table

console = Console()


def print_json(data: dict | list):
    typer.echo(json.dumps(data, indent=2))

def print_success(msg: str, json_mode: bool = False):
    if json_mode:
        print_json({"success": True, "msg": msg})
    else:
        console.print(f"[green]✓[/green] {msg}")

def print_error(msg: str, json_mode: bool = False):
    if json_mode:
        print_json({"success": False, "msg": msg})
    else:
        console.print(f"[red]✗[/red] {msg}")


def print_site(site: dict, json_mode: bool = False):
    if json_mode:
        print_json({"success": True, "data": site})
        return
    table = Table(title="Site Info")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("ID",          str(site.get("id", "")))
    table.add_row("Name",        site.get("name", ""))
    table.add_row("Description", site.get("description", ""))
    table.add_row("UID",         site.get("uid", ""))
    table.add_row("Status",      site.get("status", ""))
    console.print(table)


def print_projects(projects: list, json_mode: bool = False):
    if json_mode:
        print_json({"success": True, "data": projects})
        return
    table = Table(title="Projects")
    table.add_column("ID",          style="cyan")
    table.add_column("Name")
    table.add_column("Role")
    table.add_column("Description")
    for pp in projects:
        project = pp.get("project", {})
        table.add_row(
            str(project.get("id", "")),
            project.get("name", ""),
            pp.get("role", ""),
            project.get("description", "")[:50],
        )
    console.print(table)


def print_participants(participants: list, json_mode: bool = False):
    if json_mode:
        print_json({"success": True, "data": participants})
        return
    table = Table(title="Project Participants")
    table.add_column("ID",     style="cyan")
    table.add_column("Site")
    table.add_column("Role")
    table.add_column("Status")
    for p in participants:
        site = p.get("site", {})
        table.add_row(
            str(p.get("id", "")),
            site.get("name", ""),
            p.get("role", ""),
            site.get("status", ""),
        )
    console.print(table)


def print_runs(runs: list, json_mode: bool = False):
    if json_mode:
        print_json({"success": True, "data": runs})
        return
    table = Table(title="Runs")
    table.add_column("ID",     style="cyan")
    table.add_column("Batch")
    table.add_column("Status")
    table.add_column("Round")
    table.add_column("Role")
    for r in runs:
        tasks = r.get("tasks", [{}])
        current_round = tasks[0].get("config", {}).get("current_round", "-") if tasks else "-"
        table.add_row(
            str(r.get("id", "")),
            str(r.get("batch", "")),
            r.get("status", ""),
            str(current_round),
            r.get("role", ""),
        )
    console.print(table)
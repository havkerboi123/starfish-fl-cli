import json
import json as json_lib
import typer
from starfish_cli.config import get_config
from starfish_cli.client import StarfishClient
from starfish_cli.output import (
    print_projects, print_participants, print_success, print_error, print_json
)

app = typer.Typer(no_args_is_help=True)


def _client():
    return StarfishClient(get_config())


@app.command()
def list(json: bool = typer.Option(False, "--json", help="Output as JSON")):
    """List all projects this site is involved in."""
    client = _client()
    # get current site first
    r = client.get_site()
    if not r.ok:
        print_error("Site not registered. Run 'starfish site register' first.", json_mode=json)
        return
    site = r.json()
    r = client.list_projects(site["id"])
    if r.ok:
        projects = r.json()
        if not projects:
            print_error("No projects found for this site.", json_mode=json)
            return
        print_projects(projects, json_mode=json)
    else:
        print_error(f"Failed to fetch projects: {r.text}", json_mode=json)


@app.command()
def new(
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    desc: str = typer.Option("", "--desc", "-d", help="Project description"),
    tasks: str = typer.Option(..., "--tasks", "-t", help='Tasks as JSON string e.g. \'[{"seq":1,"model":"LogisticRegression","config":{"total_round":5,"current_round":1}}]\''),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new project. This site becomes the coordinator."""
    client = _client()
    # get current site
    r = client.get_site()
    if not r.ok:
        print_error("Site not registered. Run 'starfish site register' first.", json_mode=json)
        return
    site = r.json()
    # parse tasks
    try:
        tasks_list = json_lib.loads(tasks)
    except Exception:
        print_error("Invalid tasks JSON. Check the format and try again.", json_mode=json)
        return
    r = client.create_project(name, desc, site["id"], tasks_list)
    if r.ok or r.status_code == 201:
        print_success(f"Project '{name}' created. This site is now the coordinator.", json_mode=json)
    else:
        print_error(f"Failed to create project: {r.text}", json_mode=json)


@app.command()
def join(
    name: str = typer.Option(..., "--name", "-n", help="Project name to join"),
    notes: str = typer.Option("", "--notes", help="Optional notes"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Join an existing project as a participant."""
    client = _client()
    r = client.get_site()
    if not r.ok:
        print_error("Site not registered. Run 'starfish site register' first.", json_mode=json)
        return
    site = r.json()
    r = client.join_project(name, site["id"], notes)
    if r.ok or r.status_code == 201:
        print_success(f"Successfully joined project '{name}' as participant.", json_mode=json)
    else:
        print_error(f"Failed to join project: {r.text}", json_mode=json)


@app.command()
def leave(
    participant_id: int = typer.Option(..., "--participant-id", "-p", help="Your participant ID in the project"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Leave a project using your participant ID."""
    client = _client()
    r = client.leave_project(participant_id)
    if r.status_code == 204:
        print_success("Successfully left the project.", json_mode=json)
    else:
        print_error(f"Failed to leave project: {r.text}", json_mode=json)


@app.command()
def detail(
    project_id: int = typer.Option(..., "--project-id", "-p", help="Project ID"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    
    client = _client()
    # get project info
    r = client.get_project(project_id)
    if not r.ok:
        print_error(f"Project {project_id} not found.", json_mode=json)
        return
    project = r.json()
    # get participants
    r2 = client.get_participants(project_id)
    participants = r2.json() if r2.ok else []

    if json:
        print_json({"success": True, "data": {"project": project, "participants": participants}})
        return

    from rich.console import Console
    from rich.table import Table
    console = Console()
    table = Table(title=f"Project: {project['name']}")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("ID",          str(project.get("id")))
    table.add_row("Name",        project.get("name", ""))
    table.add_row("Description", project.get("description", ""))
    table.add_row("Batch",       str(project.get("batch", "")))
    console.print(table)
    print_participants(participants)
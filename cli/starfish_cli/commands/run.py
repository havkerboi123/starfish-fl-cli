import typer
from starfish_cli.config import get_config
from starfish_cli.client import StarfishClient
from starfish_cli.output import print_runs, print_success, print_error, print_json

app = typer.Typer(no_args_is_help=True)


def _client():
    return StarfishClient(get_config())


@app.command()
def start(
    project_id: int = typer.Option(..., "--project-id", "-p", help="Project ID to start a run for"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Start a new FL run. Coordinator only."""
    client = _client()
    r = client.start_run(project_id)
    if r.ok or r.status_code == 201:
        print_success(f"Run started for project {project_id}. All sites must now upload their datasets.", json_mode=json)
    else:
        print_error(f"Failed to start run: {r.text}", json_mode=json)


@app.command()
def status(
    project_id: int = typer.Option(..., "--project-id", "-p", help="Project ID"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show all runs and their statuses for a project."""
    client = _client()
    r = client.get_runs(project_id)
    if not r.ok:
        print_error(f"Failed to fetch runs: {r.text}", json_mode=json)
        return
    runs = r.json()
    if not runs:
        print_error("No runs found for this project.", json_mode=json)
        return
    print_runs(runs, json_mode=json)


@app.command()
def detail(
    batch: int = typer.Option(..., "--batch", "-b", help="Batch number"),
    project_id: int = typer.Option(..., "--project-id", "-p", help="Project ID"),
    site_id: int = typer.Option(..., "--site-id", "-s", help="Site ID"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show detailed info for a specific run batch."""
    client = _client()
    r = client.get_run_detail(batch, project_id, site_id)
    if not r.ok:
        print_error(f"Failed to fetch run detail: {r.text}", json_mode=json)
        return
    data = r.json()
    if json:
        print_json({"success": True, "data": data})
        return

    from rich.console import Console
    from rich.table import Table
    console = Console()
    runs = data.get("runs", [])
    table = Table(title=f"Run Detail — Batch {batch}, Project {project_id}")
    table.add_column("Run ID",  style="cyan")
    table.add_column("Status")
    table.add_column("Role")
    table.add_column("Seq")
    table.add_column("Round")
    for r in runs:
        tasks = r.get("tasks", [{}])
        cfg = tasks[0].get("config", {}) if tasks else {}
        table.add_row(
            str(r.get("id", "")),
            r.get("status", ""),
            r.get("role", ""),
            str(r.get("cur_seq", "")),
            str(cfg.get("current_round", "-")),
        )
    console.print(table)


@app.command()
def logs(
    run_id: int = typer.Option(..., "--run-id", "-r", help="Run ID"),
    task_seq: int = typer.Option(1, "--task-seq", "-t", help="Task sequence number"),
    round_seq: int = typer.Option(1, "--round-seq", help="Round sequence number"),
    line: int = typer.Option(0, "--line", "-l", help="Start from line number"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Fetch logs for a specific run."""
    client = _client()
    r = client.get(
        "/runs/fetch_logs/",
        params={
            "run_id": run_id,
            "task_seq": task_seq,
            "round_seq": round_seq,
            "line": line,
        }
    )
    if not r.ok:
        print_error(f"Failed to fetch logs: {r.text}", json_mode=json)
        return
    data = r.json()
    if not data.get("success"):
        print_error(data.get("msg", "No logs yet."), json_mode=json)
        return
    if json:
        print_json({"success": True, "data": data.get("content", [])})
        return
    for line_content in data.get("content", []):
        typer.echo(line_content, nl=False)
import os
import typer
import requests
from starfish_cli.config import get_config
from starfish_cli.output import print_success, print_error

app = typer.Typer(no_args_is_help=True)

VALID_TYPES = ["artifacts", "logs", "mid_artifacts"]


@app.command()
def download(
    run_id: int = typer.Option(..., "--run-id", "-r", help="Run ID"),
    file_type: str = typer.Option(..., "--type", "-t", help="Type: artifacts | logs | mid_artifacts"),
    all_runs: bool = typer.Option(True, "--all-runs/--single-run", help="Download for all runs in batch (coordinator) or just this run"),
    output_dir: str = typer.Option(".", "--output-dir", "-o", help="Directory to save the downloaded file"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Download artifacts or logs for a run."""
    if file_type not in VALID_TYPES:
        print_error(f"Invalid type '{file_type}'. Choose from: {', '.join(VALID_TYPES)}", json_mode=json)
        return

    config = get_config()
    params = {
        "run": run_id,
        "type": file_type,
        "all_runs": 1 if all_runs else 0,
    }

    response = requests.get(
        f"{config['router_url']}/runs-action/download/",
        params=params,
        auth=config["auth"],
    )

    if not response.ok:
        print_error(f"Failed to download: {response.text}", json_mode=json)
        return

    # save the zip file
    os.makedirs(output_dir, exist_ok=True)
    filename = f"run_{run_id}_{file_type}.zip"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(response.content)

    print_success(f"Downloaded to {filepath}", json_mode=json)
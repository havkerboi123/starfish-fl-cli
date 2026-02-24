import typer
from starfish_cli.config import get_config
from starfish_cli.output import print_success, print_error

app = typer.Typer(no_args_is_help=True)

def _client():
    from starfish_cli.client import StarfishClient
    return StarfishClient(get_config())

@app.command()
def upload(
    run_id: int = typer.Option(..., "--run-id", "-r", help="Run ID to upload dataset for"),
    file: str = typer.Option(..., "--file", "-f", help="Path to dataset file"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Upload a dataset for a run. Changes run status from Standby to Preparing."""
    import os
    import requests

    config = get_config()

    if not os.path.exists(file):
        print_error(f"File not found: {file}", json_mode=json)
        return

    controller_url = config["controller_url"]
    dataset_url = f"{controller_url}/controller/runs/dataset/"

    session = requests.Session()
    session.auth = config["auth"]
    session.get(f"{controller_url}/controller/")
    csrf_token = session.cookies.get("csrftoken", "")

    with open(file, "rb") as f:
        response = session.post(
            dataset_url,
            data={
                "run_id": run_id,
                "has_dataset": "true",
                "csrfmiddlewaretoken": csrf_token,
            },
            files={"dataset": f},
            headers={"X-CSRFToken": csrf_token, "Referer": f"{controller_url}/"},
        )

    if response.ok and response.json().get("success"):
        print_success(f"Dataset uploaded for run {run_id}. Status changed to Preparing.", json_mode=json)
    else:
        msg = response.json().get("msg", response.text) if response.ok else response.text
        print_error(f"Failed to upload dataset: {msg}", json_mode=json)

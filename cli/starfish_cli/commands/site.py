import typer
from starfish_cli.config import get_config
from starfish_cli.client import StarfishClient
from starfish_cli.output import print_site, print_success, print_error

app = typer.Typer(no_args_is_help=True)


def _client():
    return StarfishClient(get_config())


@app.command()
def info(json: bool = typer.Option(False, "--json", help="Output as JSON")):
    """Show current site info."""
    client = _client()
    r = client.get_site()
    if r.ok:
        print_site(r.json(), json_mode=json)
    else:
        print_error(f"Site not found or not registered. (HTTP {r.status_code})", json_mode=json)


@app.command()
def register(
    name: str = typer.Option(..., "--name", "-n", help="Site name"),
    desc: str = typer.Option("", "--desc", "-d", help="Site description"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Register this site with the router."""
    client = _client()
    # check if already registered
    r = client.get_site()
    if r.ok:
        print_error("Site is already registered. Use 'update' to change details.", json_mode=json)
        return
    r = client.register_site(name, desc)
    if r.ok or r.status_code == 201:
        print_success(f"Site '{name}' registered successfully.", json_mode=json)
    else:
        print_error(f"Failed to register site: {r.text}", json_mode=json)


@app.command()
def update(
    name: str = typer.Option(..., "--name", "-n", help="New site name"),
    desc: str = typer.Option("", "--desc", "-d", help="New site description"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Update this site's name and description."""
    client = _client()
    r = client.get_site()
    if not r.ok:
        print_error("Site not found. Register first with 'site register'.", json_mode=json)
        return
    site = r.json()
    r = client.update_site(site["id"], name, desc)
    if r.ok:
        print_success(f"Site updated to '{name}'.", json_mode=json)
    else:
        print_error(f"Failed to update site: {r.text}", json_mode=json)


@app.command()
def deregister(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Deregister this site from the router."""
    client = _client()
    r = client.get_site()
    if not r.ok:
        print_error("Site not found — already deregistered?", json_mode=json)
        return
    site = r.json()
    if not force:
        confirm = typer.confirm(f"Are you sure you want to deregister '{site['name']}'?")
        if not confirm:
            print_error("Aborted.", json_mode=json)
            return
    r = client.deregister_site(site["id"])
    if r.status_code == 204:
        print_success("Site deregistered successfully.", json_mode=json)
    else:
        print_error(f"Failed to deregister: {r.text}", json_mode=json)
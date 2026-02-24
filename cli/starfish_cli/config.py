import os
import typer
from dotenv import load_dotenv

env_path = os.environ.get("STARFISH_ENV", ".env")
load_dotenv(env_path, override=True)

def get_config() -> dict:
    """
    Read config from .env file and return as a dict.
    """
    site_uid = os.getenv("SITE_UID")
    router_url = os.getenv("ROUTER_URL")
    router_username = os.getenv("ROUTER_USERNAME")
    router_password = os.getenv("ROUTER_PASSWORD")
    controller_url = os.getenv("CONTROLLER_URL", "http://localhost:8001")

    #missing envs
    missing = []
    if not site_uid:        missing.append("SITE_UID")
    if not router_url:      missing.append("ROUTER_URL")
    if not router_username: missing.append("ROUTER_USERNAME")
    if not router_password: missing.append("ROUTER_PASSWORD")

    if missing:
        typer.echo(f"[error] Missing required environment variables: {', '.join(missing)}")
        raise typer.Exit(code=1)

    return {
        "site_uid": site_uid,
        "router_url": router_url.rstrip("/"),
        "router_username": router_username,
        "router_password": router_password,
        "auth": (router_username, router_password),
        "controller_url": controller_url.rstrip("/"),
    }
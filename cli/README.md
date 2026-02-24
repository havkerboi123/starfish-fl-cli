# Starfish-FL CLI

A command-line interface for [Starfish-FL](https://github.com/denoslab/starfish-fl) that replicates the web portal functionality. Designed to be used by both humans and AI agents (e.g. OpenClaw).

## Requirements

- Python 3.10+
- Poetry
- Starfish-FL stack running (see [workbench setup](../workbench/README.md))

## Setup
```bash
cd cli
cp .env.example .env        # fill in your values
poetry install
poetry run starfish --help
```

## Configuration

Edit `.env` with your values:

| Variable | Description |
|---|---|
| `SITE_UID` | Unique UUID for this site |
| `ROUTER_URL` | URL to the Starfish Router API |
| `ROUTER_USERNAME` | Router superuser username |
| `ROUTER_PASSWORD` | Router superuser password |
| `CONTROLLER_URL` | URL to this site's Controller (default: `http://localhost:8001`) |

Generate a UUID with:
```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

## Commands
```bash
starfish site      info / register / update / deregister
starfish project   list / new / join / leave / detail
starfish run       start / status / detail / logs
starfish dataset   upload
starfish artifact  download
```

## Example workflow would look something like
```bash
# 1. Register sites
poetry run starfish site register --name "Hospital A" --desc "Site 1"
STARFISH_ENV=.env.site2 poetry run starfish site register --name "Hospital B" --desc "Site 2"

# 2. Create project (this site becomes coordinator)
poetry run starfish project new \
  --name "Breast Cancer Study" \
  --tasks '[{"seq":1,"model":"LogisticRegression","config":{"total_round":2,"current_round":1}}]'


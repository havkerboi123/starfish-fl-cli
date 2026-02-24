import typer
from starfish_cli.commands import site, project, run, dataset, artifact

app = typer.Typer(
    name="starfish",
    help="Starfish-FL CLI",
    no_args_is_help=True,
)

app.add_typer(site.app,     name="site",     help="Manage this site's registration")
app.add_typer(project.app,  name="project",  help="Create, join, and manage projects")
app.add_typer(run.app,      name="run",      help="Start and monitor FL runs")
app.add_typer(dataset.app,  name="dataset",  help="Upload datasets for runs")
app.add_typer(artifact.app, name="artifact", help="Download artifacts and logs")

if __name__ == "__main__":
    app()
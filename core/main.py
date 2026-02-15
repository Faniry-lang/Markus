import typer
from rich import print as rprint

from core.agent import MarkusAgent
from core.providers import SimpleGoogleProvider, OpenRouterProvider, LocalProvider

app = typer.Typer(help="CLI pour Markus — assistant IA local")

def _create_agent() -> MarkusAgent:
    open_router_provider = OpenRouterProvider(api_key="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")
    google_provider = SimpleGoogleProvider()
    local_provider = LocalProvider()
    return MarkusAgent(google_provider)

@app.command()
def shell():
    """Ouvre le shell interactif Markus."""
    agent = _create_agent()
    typer.echo("Tapez 'exit' pour quitter la conversation.")

    while True:
        user_input = typer.prompt("Vous")
        if user_input.lower() in ["exit", "quit"]:
            typer.echo("Au revoir !")
            break

        response = agent.run(user_input)
        typer.echo(f"Markus: {response}")

if __name__ == "__main__":
    app()

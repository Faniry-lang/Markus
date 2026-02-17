import subprocess

from core.decorator.function_decorator import markus_function


@markus_function(needs_validation=True)
def execute_command(command: str, args: list[str]) -> str:
    """Fonction pour lancer une commande dans le terminal, arguments: command:str la commande principale\n args:list une liste des arguments de la commande\n cette fonction retourne le résultat de la commande"""
    result = subprocess.run([command, *args], capture_output=True, text=True)
    return result.stdout

import cmd

from core.agent import MarkusAgent
from core.providers import SimpleGoogleProvider


class MarkusShell(cmd.Cmd):
    intro = "Bienvenue dans le shell Markus. Tapez 'help' pour voir les commandes."
    prompt = "Markus> "

    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    def do_run(self, arg):
        response = self.agent.run(arg)
        print("Markus:", response)

    def do_exit(self, arg):
        print("Au revoir !")
        return True

if __name__ == "__main__":
    provider = SimpleGoogleProvider()
    agent = MarkusAgent(provider)
    MarkusShell(agent).cmdloop()

from core.agent import MarkusAgent
from core.providers import SimpleGoogleProvider

markus = MarkusAgent(SimpleGoogleProvider())
response = markus.run("Cherche un fichier nommé 'toto.txt' dans le répertoire courant et montre moi son contenu")
print(response)
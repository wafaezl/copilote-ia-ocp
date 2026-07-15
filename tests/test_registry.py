import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.registry import lister_outils, obtenir_outil

print("Outils disponibles :", lister_outils())

outil = obtenir_outil("load_dataset")
print("\nDetails de 'load_dataset' :")
print("Description :", outil["description"])
print("Parametres attendus :", outil["parametres"])
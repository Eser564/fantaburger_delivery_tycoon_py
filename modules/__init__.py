__version__ = "6.7" #Versione corrente del pacchetto. 
__author__ = "I Meccanici Trappolai"  #Nome autori.

from .inventory import Inventory # Importazione relativa della classe Inventory dal modulo inventory.py presente nella stessa directory
from .recipes import Recipe # Importazione relativa della classe Recipe dal modulo recipes.py presente nella stessa directory
from .finance import Finance # Importazione relativa della classe Finance dal modulo finance.py presente nella stessa directory
from .game import GameEngine # Importazione relativa della classe GameEngine dal modulo game.py presente nella stessa directory

__all__ = ['Inventory', 'Recipe', 'Finance', 'GameEngine'] # Definizione dell'interfaccia pubblica del pacchetto.
# Quando qualcuno scrive "from modules import *", verranno importate solo queste quattro classi.
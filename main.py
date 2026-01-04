"""
FantaBurger Delivery Tycoon 🍔🛵
Versione: 6.7
Autore: I Meccanici Trappoli
"""

import os # importazione del modulo necessario per operazioni sul sistema operativo.
import sys # importazione del modulo sys per manipolare il path di ricerca dei moduli Python.
from modules.game import GameEngine # importazione della classe principale GameEngine dal pacchetto modules.

project_root = os.path.dirname(os.path.abspath(__file__)) 
'''
Calcola il percorso assoluto della directory in cui si trova questo file (radice del progetto). 
Serve per garantire che le importazioni funzionino indipendentemente da dove viene lanciato lo script.
'''
sys.path.insert(0, project_root)  # Inserisce project_root all'inizio di sys.path (lista dei percorsi dove Python cerca i moduli).


def main():
    '''
    Funzione principale del programma.
    Come parametri non riceve nulla e corrisponde al punto di ingresso del gioco in modalità console (CLI).
    In particolare stampa il banner di benvenuto centrato, inizializza un'istanza di GameEngine,
    avvia il ciclo principale con game.run().
    Inoltre, si occupa della gestione delle eccezioni come KeyboardInterrupt (Ctrl+C) per interrompere graziosamente,
    Exception generica per errori critici (stampa errore ma tenta di salvare) e
    nel blocco finally stampa sempre il messaggio di arrivederci.
    '''
    print("=" * 60)
    print("     FANTABURGER DELIVERY TYCOON     ".center(60))
    print("              v6.7                   ".center(60))
    print("       I Meccanici Trappolai         ".center(60))
    print("=" * 60)

    try:
        game = GameEngine()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGioco interrotto dall'utente. Salvataggio in corso...")
    except Exception as e:
        print(f"\nErrore critico: {e}")
        print("Il gioco terminerà. I progressi potrebbero essere stati salvati automaticamente.")
    finally:
        print("\nGrazie per aver giocato a FantaBurger Delivery Tycoon! 🍔🚀")
        print("Alla prossima!")


if __name__ == "__main__":
    '''
    Blocco di esecuzione condizionale standard Python.
    '''
    main()
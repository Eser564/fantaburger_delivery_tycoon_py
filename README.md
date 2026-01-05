  # FantaBurger Delivery Tycoon 🍔🛵

**Versione 6.7** · *by I Meccanici Trappolai*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un gioco di gestione economica di una paninoteca creativa dove ogni panino ha ingredienti esclusivi e la domanda cresce in modo frenetico. 
Gestisci scorte, finanza, ordini concorrenti e eventi casuali per evitare il fallimento!
A business management game for a creative sandwich shop where each sandwich features unique ingredients and demand grows rapidly.
Manage inventory, finances, competing orders, and random events to avoid bankruptcy!

## 📋 Indice/Index
- [Descrizione](#-descrizione)
- [Caratteristiche](#✨-caratteristiche)
- [Installazione](#🚀-installazione)
- [Utilizzo](#🎮-utilizzo)
  - [Modalità CLI](#modalità-cli)
  - [Modalità GUI](#modalità-gui)
- [Struttura del Progetto](#📁-struttura-del-progetto)
- [Crediti](#👥-crediti)
- [Licenza](#📄-licenza)

## 🍔 Descrizione/Description

Diventa il proprietario di una paninoteca super creativa dove ogni panino ha ingredienti esclusivi! La domanda cresce in modo frenetico e devi:
- Gestire le scorte di ingredienti tramite file JSON
- Prevedere il fabbisogno giornaliero
- Assicurarti che ogni ordine venga soddisfatto prima che i clienti scappino
- Tenere sotto controllo il bilancio per evitare il fallimento
- Gestire eventi casuali (sconti, furti, boom ordini)
Ogni errore ti costerà, ma ogni ordine completato ti farà guadagnare soldi per rifornire il negozio e acquistare upgrade!
Become the owner of a super creative sandwich shop where every sandwich features exclusive ingredients! Demand is growing rapidly, and you must:
- Manage ingredient inventory via JSON files
- Forecast daily needs
- Ensure every order is fulfilled before customers leave
- Monitor your budget to avoid bankruptcy
- Manage random events (discounts, thefts, order booms)
Every mistake will cost you, but every completed order will earn you money to restock the shop and purchase upgrades!

## ✨ Caratteristiche/Features
### ✅ **Funzionalità Core**
- **Sistema Economico Completo**: Bilancio, transazioni, costi giornalieri, tasse
- **Inventario**: 5 categorie di ingredienti con scorte
- **Sistema Ricette**: 9 ricette base + 2 segrete 
- **Ordini Concorrenti**: Gestione multi-thread degli ordini in tempo reale
- **Salvataggio Automatico**: Stato del gioco salvato in JSON al riavvio
### ✅ **Core Features**
- **Complete Financial System**: Balance sheet, transactions, daily costs, taxes
- **Inventory**: 5 ingredient categories with stocks
- **Recipe System**: 9 basic recipes + 2 secret recipes
- **Competitive Orders**: Real-time multi-threaded order management
- **Auto Save**: Game state saved in JSON upon restart

### 🎲 **Gameplay Avanzato**
- **5 Livelli di Difficoltà**: Easy, Normal, Hard, Ultimate, Nightmare
- **Sistema Eventi**: 8 tipi di eventi casuali 
- **Sistema Reputazione**: Influisce sulla frequenza dei clienti
- **Sistema Achievement**: 6 achievement sbloccabili
- **Sistema Upgrade**: Migliora cucina, assumi dipendenti, sblocca ricette
### 🎲 **Advanced Gameplay**
- **5 Difficulty Levels**: Easy, Normal, Hard, Ultimate, Nightmare
- **Event System**: 8 types of random events
- **Reputation System**: Affects customer attendance
- **Achievement System**: 6 unlockable achievements
- **Upgrade System**: Upgrade your kitchen, hire employees, unlock recipes
- 
## ⚙️ Requisiti Tecnici/Technical Requirements

### **Minimi**
- **Python 3.8** o superiore
- **Sistema Operativo**: Windows, macOS o Linux
- **RAM**: 512 MB minimo
- **Spazio Disco**: 10 MB
### **Minimum**
- **Python 3.8** or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 512 MB minimum
- **Disk Space**: 10 MB
- 
## 🚀 Installazione/Installation
### **Metodo 1: Download Diretto**/**Method 1: Direct Download**
```bash
# Clona il repository/Clone the repository
git clone https://github.com/Eser564/fantaburger_delivery_tycoon_py.git

# Entra nella cartella/Enter the folder
cd fantaburger-tycoon
```

### **Metodo 2: Manuale**/**Method 2: Manual**
1. Scarica l'archivio ZIP del progetto
2. Estrai i file in una cartella di tua scelta
3. Assicurati che la struttura delle cartelle sia preservata
1. Download the project ZIP archive
2. Extract the files to a folder of your choice
3. Make sure the folder structure is preserved

### **Verifica Installazione**/ **Verify Installation**
```bash
# Verifica che Python sia installato/Verify that Python is installed
python --version
# Dovrebbe mostrare Python 3.8 o superiore/It should show Python 3.8 or higher

# Verifica la struttura del progetto (in linux) / Check the project structure (in Linux)
ls -la
# Dovresti vedere: main.py, gui.py, cartelle modules/ e data/ /You should see: main.py, gui.py, modules/ and data/ folders
```

## 🎮 Utilizzo/Use

### **Modalità CLI**
```bash
# Avvia il gioco in modalità console
python main.py

# Comandi disponibili in-game:
# - INVIO: Avanza di un'ora
# - U: Menu upgrade
# - S: Shop ingredienti
# - I: Inventario dettagliato
# - Q: Salva ed esci
# - help: Mostra aiuto
```

### **Modalità GUI (Interfaccia Grafica)**
```bash
# Avvia il gioco con interfaccia grafica
python gui.py

# La GUI offre:
# - Navigazione a mouse/tastiera
# - Widget interattivi
# - Visualizzazione grafica dello stato
# - Pulsanti per tutte le azioni
```

### **CLI Mode**
```bash
# Start the game in console mode
python main.py

# Available in-game commands:
# - ENTER: Advance one hour
# - U: Upgrade menu
# - S: Ingredient shop
# - I: Detailed inventory
# - Q: Save and exit
# - help: Show help
```

### **GUI (Graphical User Interface) Mode**
```bash
# Start the game with the graphical interface
python gui.py

# The GUI offers:
# - Mouse/keyboard navigation
# - Interactive widgets
# - Graphical status display
# - Buttons for all
```

## 📁 Struttura del Progetto/Project Structure

fanta_burger/
│
├── main.py              # Punto di ingresso per versione CLI/Entry point for CLI Version
├── gui.py               # Interfaccia grafica realizzata con Tkinter/Graphical interface created with Tkinter
│
├── modules/             # Moduli del gioco/Game modules
│   ├── __init__.py     # Inizializzazione pacchetto/Package initialization
│   ├── inventory.py    # Gestione inventario ingredienti/Ingredients inventory management
│   ├── recipes.py      # Sistema ricette e preparazione/Recipe and preparation system
│   ├── finance.py      # Gestione economica e bilancio/Economic and budget management
│   └── game.py         # Motore di gioco principale/Main game engine
│
├── data/               # File di configurazione e dati/Configuration and data files
│   ├── config.json    # Configurazione del gioco/Game configuration
│   ├── recipes.json   # Ricette disponibili /Available recipes
│   ├── ingredients.json # Ingredienti con costi/scorte/Ingredients with costs/stocks
│   └── savestate.json  # File di salvataggio  (generato)/ Savestate file (generated)
├── requirements.txt # Requisiti (Python 3.8 o superiore)/ Requirements (Python 3.8 or higher)
└── README.md          # Questa documentazione/This documentation

## 🖥️ Utilizzo dell'IA/Use of Artificial Intelligence
Durante lo sviluppo di FantaBurger Delivery Tycoon, l'intelligenza artificiale è stata utilizzata esclusivamente come strumento di supporto per l'apprendimento e assistente di programmazione, mai come sostituzione del lavoro creativo e progettuale del team.

Aree di Applicazione:
Comprensione di Concetti Avanzati
Studio di threading e concorrenza in Python
Approfondimento di Tkinter per l'interfaccia grafica
Analisi di design pattern per architettura modulare
Miglioramento e Correzione del Codice
Debugging di errori specifici (es. race condition, gestione lock)
Ottimizzazione di algoritmi esistenti
Refactoring per migliorare leggibilità e performance
Verifica di best practices e convenzioni Python (PEP 8)
Chiarificazione della Logica di Gioco
Validazione di flussi di gioco complessi (eventi casuali, gestione ordini)
Supporto alla Documentazione
Strutturazione di README e documentazione tecnica
Test Multisection

Principi Guida Adottati:
✅ Apprendimento Attivo: Ogni suggerimento è stato studiato, compreso e adattato
✅ Pensiero Critico: Le soluzioni proposte sono state sempre valutate e modificate
✅ Autonomia: Il team ha mantenuto piena proprietà intellettuale del progetto
✅ Trasparenza: Documentazione aperta sull'uso degli strumenti di supporto

Strumenti Utilizzati:
Grok: https://grok.com/
During the development of FantaBurger Delivery Tycoon, artificial intelligence was used exclusively as a learning support tool and programming assistant, never as a replacement for the team's creative and design work.

Areas of Application:
Understanding Advanced Concepts
Study of threading and concurrency in Python
Exploring Tkinter for the graphical interface
Analysis of design patterns for modular architecture
Code Improvement and Correction
Debugging of specific errors (e.g., race conditions, lock management)
Optimization of existing algorithms
Refactoring to improve readability and performance
Verification of Python best practices and conventions (PEP 8)
Clarification of Game Logic
Validation of complex game flows (random events, order management)
Documentation Support
Structuring of READMEs and technical documentation
Multisection Testing

Guiding Principles Adopted:
✅ Active Learning: Every suggestion was studied, understood, and adapted
✅ Critical Thinking: The proposed solutions were always evaluated and modified
✅ Autonomy: The team retained full intellectual property of the project
✅ Transparency: Open documentation on the use of development tools Support

Tools Used:
Grok: https://grok.com/


```

## 👥 Crediti/Credits

### **Sviluppatori**/**Developers**
- **I Meccanici Trappolai**: Salvatore Renatti, Salvatore Apuzzo, Francesco Nastelli e Cristian Vitiello
Ci siamo incontrati fisicamente a casa dEL CAPOGRUPPO il 21 e il 22 dicembre 2025, lavorando ogni volta dalle 15:30 alle 17:30. 
Queste sessioni sono state dedicate alla realizzazione dei file config.json, ingredients.json, recipes.json e del modulo inventory.py.
Oltre a ciò, abbiamo integrato questi incontri con cinque sessioni online svolte tramite Google Meet dal 27 al 30 dicembre, sempre tra le 15:30 e le 17:30, durante le quali sono stati implementati i restanti moduli.
We met in person at the GROUP LEADER'S home on December 21st and 22nd, 2025, working from 3:30 PM to 5:30 PM each time.
These sessions were dedicated to developing the config.json, ingredients.json, recipes.json files, and the inventory.py module.
In addition, we supplemented these meetings with five online sessions held via Google Meet from December 27th to 30th, again between 3:30 PM and 5:30 PM, during which the remaining modules were implemented.



## 📄 Licenza/License

```
MIT License

Copyright (c) 2026 I Meccanici Trappolai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**⭐ Se ti piace il progetto, considera di mettere una stella sul repository!**
**⭐ If you like the project, consider giving the repository a star!**

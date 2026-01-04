  # FantaBurger Delivery Tycoon 🍔🛵

**Versione 6.7** · *by I Meccanici Trappolai*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un gioco di gestione economica di una paninoteca creativa dove ogni panino ha ingredienti esclusivi e la domanda cresce in modo frenetico. 
Gestisci scorte, finanza, ordini concorrenti e eventi casuali per evitare il fallimento!

## 📋 Indice
- [Descrizione](#-descrizione)
- [Caratteristiche](#✨-caratteristiche)
- [Installazione](#🚀-installazione)
- [Utilizzo](#🎮-utilizzo)
  - [Modalità CLI](#modalità-cli)
  - [Modalità GUI](#modalità-gui)
- [Struttura del Progetto](#📁-struttura-del-progetto)
- [Crediti](#👥-crediti)
- [Licenza](#📄-licenza)

## 🍔 Descrizione

Diventa il proprietario di una paninoteca super creativa dove ogni panino ha ingredienti esclusivi! La domanda cresce in modo frenetico e devi:
- Gestire le scorte di ingredienti tramite file JSON
- Prevedere il fabbisogno giornaliero
- Assicurarti che ogni ordine venga soddisfatto prima che i clienti scappino
- Tenere sotto controllo il bilancio per evitare il fallimento
- Gestire eventi casuali (sconti, furti, boom ordini)
Ogni errore ti costerà, ma ogni ordine completato ti farà guadagnare soldi per rifornire il negozio e acquistare upgrade!

## ✨ Caratteristiche
### ✅ **Funzionalità Core**
- **Sistema Economico Completo**: Bilancio, transazioni, costi giornalieri, tasse
- **Inventario**: 5 categorie di ingredienti con scorte
- **Sistema Ricette**: 9 ricette base + 2 segrete 
- **Ordini Concorrenti**: Gestione multi-thread degli ordini in tempo reale
- **Salvataggio Automatico**: Stato del gioco salvato in JSON al riavvio

### 🎲 **Gameplay Avanzato**
- **5 Livelli di Difficoltà**: Easy, Normal, Hard, Ultimate, Nightmare
- **Sistema Eventi**: 8 tipi di eventi casuali 
- **Sistema Reputazione**: Influisce sulla frequenza dei clienti
- **Sistema Achievement**: 6 achievement sbloccabili
- **Sistema Upgrade**: Migliora cucina, assumi dipendenti, sblocca ricette

## ⚙️ Requisiti Tecnici

### **Minimi**
- **Python 3.8** o superiore
- **Sistema Operativo**: Windows, macOS o Linux
- **RAM**: 512 MB minimo
- **Spazio Disco**: 10 MB

## 🚀 Installazione

### **Metodo 1: Download Diretto**
```bash
# Clona il repository
git clone https://github.com/Eser564/fantaburger_delivery_tycoon_py.git

# Entra nella cartella
cd fantaburger-tycoon
```

### **Metodo 2: Manuale**
1. Scarica l'archivio ZIP del progetto
2. Estrai i file in una cartella di tua scelta
3. Assicurati che la struttura delle cartelle sia preservata

### **Verifica Installazione**
```bash
# Verifica che Python sia installato
python --version
# Dovrebbe mostrare Python 3.8 o superiore

# Verifica la struttura del progetto
ls -la
# Dovresti vedere: main.py, gui.py, cartelle modules/ e data/
```

## 🎮 Utilizzo

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


## 📁 Struttura del Progetto

```
fanta_burger/
│
├── main.py              # Punto di ingresso per versione CLI
├── gui.py               # Interfaccia grafica realizzata con Tkinter
│
├── modules/             # Moduli del gioco
│   ├── __init__.py     # Inizializzazione pacchetto
│   ├── inventory.py    # Gestione inventario ingredienti
│   ├── recipes.py      # Sistema ricette e preparazione
│   ├── finance.py      # Gestione economica e bilancio
│   └── game.py         # Motore di gioco principale
│
├── data/               # File di configurazione e dati
│   ├── config.json    # Configurazione del gioco
│   ├── recipes.json   # Ricette disponibili 
│   ├── ingredients.json # Ingredienti con costi/scorte
│   └── savestate.json  # File di salvataggio  (generato)
│
└── README.md          # Questa documentazione
```

## 👥 Crediti

### **Sviluppatori**
- **I Meccanici Trappolai**: Salvatore Renatti, Salvatore Apuzzo, Francesco Nastelli e Cristian Vitiello


## 📄 Licenza

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

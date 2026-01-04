import tkinter as tk # importazione della libreria standard necessaria per creare interfacce grafiche (GUI). Utilizzata per finestre, pulsanti, label e tutti gli elementi visivi del gioco.
from tkinter import ttk, messagebox, scrolledtext # importazione di componenti specifici da tkinter
'''
ttk corrisponde al widget con stile moderno (cioè bottoni, spinbox, ecc.)
messagebox corrisponde alle finestre di dialogo (info, errore, conferma)
scrolledtext corrisponde all' area di testo con scrollbar per il log del gioco
'''
import threading # importazione del modulo necessario per gestire thread. Utilizzato per avanzare l'ora del gioco in background senza bloccare la GUI.
import random # importazione del modulo per generare numeri casuali. Utilizzato per sbloccare ricette segrete casuali negli upgrade.
import sys # importazione del modulo sys per reindirizzare l'output standard (print) verso il log grafico della GUI.
from io import StringIO # importazione di StringIO per creare un buffer di testo in memoria. Serve per reindirizzare i print() del gioco nel log visibile.
from modules.game import GameEngine # importazione della classe principale GameEngine dal pacchetto modules. 
from modules.inventory import Inventory # importazione della classe Inventory dal pacchetto modules.
from modules.recipes import Recipe # importazione della classe Recipe dal pacchetto modules.
from modules.finance import Finance # importazione della classe Finance dal pacchetto modules.


class LogRedirector(StringIO):
    '''
    Classe che eredita da StringIO per reindirizzare l'output di print() verso un widget Tkinter (ScrolledText).
    In particolare ogni volta che viene chiamato write(), inserisce il testo nel widget in modo thread-safe usando after() e
    gestisce anche errori TclError se il widget è stato distrutto.
    '''
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def write(self, text):
        if self.widget.winfo_exists():
            self.widget.after(0, lambda: self._safe_write(text))

    def _safe_write(self, text):
        try:
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)
        except tk.TclError:
            pass


class FantaBurgerGUI:
    def __init__(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI.
        Costruttore della GUI principale del gioco che crea la finestra principale (Tk), imposta titolo, dimensioni, colore di sfondo e blocca il ridimensionamento.
        Inizializza variabili di stato come game (istanza GameEngine), running (flag di esecuzione), pulsanti e label achievement.
        Inoltre, chiama setup_style() per configurare lo stile ttk e show_main_menu() per mostrare il menu iniziale.
        '''
        self.root = tk.Tk()
        self.root.title("FantaBurger Delivery Tycoon 🍔🛵")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c1810")
        self.root.resizable(False, False)

        self.game: GameEngine | None = None
        self.running = False
        self.start_btn = None
        self.achievement_label = None

        self.setup_style()
        self.show_main_menu()


    def setup_style(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e non restituisce nulla.
        Configura lo stile dei widget ttk usando il tema "clam" e personalizzando lo stile "TButton" con font grande, grassetto e padding.
        '''
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TButton",
            font=("Helvetica", 14, "bold"),
            padding=12
        )


    def show_main_menu(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e non restituisce nulla.
        Mostra il menu principale del gioco distruggendo tutti i widget esistenti, creando un frame centrale con sfondo scuro,
        aggiungendo label con titolo, sottotitolo e versione, creando il pulsante grande "NUOVA PARTITA" con animazione hover,
        aggiungendo pulsanti "CARICA PARTITA" ed "ESCI", avviando l'animazione pulsante e impostando i binding per effetto hover.
        '''
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root, bg="#2c1810")
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="FANTABURGER",
            font=("Helvetica", 48, "bold"),
            bg="#2c1810",
            fg="#ffcc00"
        ).pack(pady=(40, 5))

        tk.Label(
            frame,
            text="DELIVERY TYCOON",
            font=("Helvetica", 34, "bold"),
            bg="#2c1810",
            fg="#ffaa00"
        ).pack()

        tk.Label(
            frame,
            text="v6.7 – by I Meccanici Trappolai",
            font=("Helvetica", 18),
            bg="#2c1810",
            fg="white"
        ).pack(pady=25)

        self.start_btn = tk.Button(
            frame,
            text="NUOVA PARTITA",
            font=("Helvetica", 22, "bold"),
            bg="#ffcc00",
            fg="black",
            bd=4,
            command=self.new_game_dialog
        )
        self.start_btn.pack(pady=20, ipadx=40, ipady=20)

        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#ffaa00"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#ffcc00"))

        self.animate_button()

        ttk.Button(
            frame,
            text="CARICA PARTITA",
            command=self.load_game
        ).pack(pady=10, ipadx=40, ipady=15)

        ttk.Button(
            frame,
            text="ESCI",
            command=self.root.quit
        ).pack(pady=20, ipadx=40, ipady=15)

    def animate_button(self, grow=True):
        '''
        Come parametro riceve implicitamente l'istanza della classe FantaBurgerGUI e grow (bool, con valore di default a True) e ha tipo di ritorno None.
        Crea l'effetto di animazione pulsante "pulsante" sul bottone NUOVA PARTITA.
        In particolare alterna la dimensione del font tra 22 e 23 ogni 600ms, creando un effetto di "respiro" e
        controlla che il pulsante esista ancora prima di modificare.
        '''
        if not self.start_btn or not self.start_btn.winfo_exists():
            return
        try:
            size = 23 if grow else 22
            self.start_btn.config(font=("Helvetica", size, "bold"))
            self.root.after(600, self.animate_button, not grow)
        except tk.TclError:
            pass


    def new_game_dialog(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Apre la finestra di dialogo per iniziare una nuova partita.
        In particolare crea una finestra modale (Toplevel), imposta titolo, dimensioni e sfondo,
        aggiunge campi per nome giocatore, nome ristorante e selezione difficoltà (radiobutton),
        crea pulsante grande "INIZIA PARTITA".
        '''
        dlg = tk.Toplevel(self.root)
        dlg.title("Nuova Partita")
        dlg.geometry("500x650")  
        dlg.configure(bg="#2c1810")
        dlg.transient(self.root)
        dlg.grab_set()

        main = tk.Frame(dlg, bg="#2c1810")
        main.pack(expand=True, fill="both", padx=40, pady=20)  

        tk.Label(main, text="NUOVA PARTITA", font=("Helvetica", 20, "bold"),
                bg="#2c1810", fg="#ffcc00").pack(pady=(0, 20))

        tk.Label(main, text="Nome Giocatore", bg="#2c1810", fg="white",
                font=("Helvetica", 14, "bold")).pack(pady=(0, 5))
        
        player_entry = tk.Entry(main, font=("Helvetica", 14), width=25)
        player_entry.pack(pady=(0, 15))
        player_entry.focus_set()

        tk.Label(main, text="Nome Ristorante", bg="#2c1810", fg="white",
                font=("Helvetica", 14, "bold")).pack(pady=(0, 5))
        
        rest_entry = tk.Entry(main, font=("Helvetica", 14), width=25)
        rest_entry.pack(pady=(0, 15))

        tk.Label(main, text="Difficoltà", bg="#2c1810", fg="white",
                font=("Helvetica", 14, "bold")).pack(pady=(0, 5))
        
        difficulty = tk.StringVar(value="easy")
        
        radio_frame = tk.Frame(main, bg="#2c1810")
        radio_frame.pack()
        
        diffs = [
            ("Easy", "easy"),
            ("Normal", "normal"),
            ("Hard", "hard"),
            ("Ultimate", "ultimate"),
            ("Nightmare", "nightmare")
        ]
        
        for i, (text, val) in enumerate(diffs):
            tk.Radiobutton(
                radio_frame, text=text, variable=difficulty, value=val,
                bg="#2c1810", fg="white", selectcolor="#000000",
                font=("Helvetica", 12)
            ).grid(row=i//2, column=i%2, sticky="w", padx=10, pady=2)

        ttk.Button(main, text="INIZIA PARTITA", 
                command=lambda: self._confirm_new_game(
                    player_entry.get().strip() or "Giocatore",
                    rest_entry.get().strip() or "FantaBurger",
                    difficulty.get(),
                    dlg),
                style="TButton").pack(pady=(30, 20), ipadx=40, ipady=20)  

        dlg.bind('<Return>', lambda e: self._confirm_new_game(
            player_entry.get().strip() or "Giocatore",
            rest_entry.get().strip() or "FantaBurger",
            difficulty.get(),
            dlg
        ))

    def _confirm_new_game(self, player, restaurant, diff, dlg):
        '''
        Funzione privata che come parametro riceve nome del giocatore (stringa), nome del ristorante (stringa), difficoltà (stringa) e dlg (Toplevel) 
        oltre all'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Chiude il dialogo nuova partita e avvia il gioco con i parametri inseriti
        '''
        dlg.destroy()
        self.start_game(player, restaurant, diff)


    def start_game(self, player: str, restaurant: str, diff: str):
        '''
        Come parametro riceve esplicitamente nome del giocatore (stringa), nome del ristorante (stringa), difficoltà (stringa) oltre all'istanza della classe FantaBurgerGUI (self implicito)
        e ha tipo di ritorno None.
        Si occupa di inizializzare una nuova partita, in particolare, crea istanza GameEngine, imposta nome giocatore/ristorante/difficoltà,
        inizializza inventory, recipes, finance, imposta modalità GUI, ricette base sbloccate,
        collega callback achievement, applica impostazioni difficoltà, salva stato iniziale e mostra schermata di gioco.
        '''
        self.game = GameEngine()
        self.game.player_name = player
        self.game.restaurant_name = restaurant
        self.game.difficulty = diff

        self.game.inventory = Inventory(load_saved=False)
        self.game.recipes = Recipe(inventory=self.game.inventory)
        self.game.finance = Finance(self.game.config["economy"]["initial_balance"])
        self.game.finance.game_engine = self.game

        self.game.current_game_day = 1
        self.game.current_hour = self.game.working_start
        self.game.gui_mode = True
        self.game.running = True

        self.game.unlocked_recipes = self.game.get_base_recipes()
        self.game.on_achievement_unlocked = self.show_achievement

        self.game._apply_difficulty_settings()
        self.game.safe_save()

        self.show_game_screen()
        print("✅ Partita avviata")

    def load_game(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Carica una partita salvata.
        In particolare, crea nuova istanza GameEngine, tenta di caricare con load_game() e
        se riuscito imposta modalità GUI, collega callback achievement e mostra schermata gioco.
        Altrimenti mostra messaggio "Nessun salvataggio trovato".
        '''
        self.game = GameEngine()
        if self.game.load_game():
            self.game.gui_mode = True
            self.game.on_achievement_unlocked = self.show_achievement
            self.show_game_screen()
        else:
            messagebox.showinfo("Info", "Nessun salvataggio trovato")


    def show_game_screen(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Mostra la schermata principale di gioco.
        In particolare, se game over o vittoria mostra schermata finale.
        Altrimenti distrugge widget esistenti, crea header con nome ristorante/giocatore/ora,
        barra informazioni (saldo, reputazione, capacità), area log (con reindirizzamento print),
        barra comandi (SHOP, AVANZA ORA, UPGRADE, SALVA & ESCI), imposta flag running e avvia update_ui().
        '''
        for w in self.root.winfo_children():
            w.destroy()

        if self.game and (self.game.game_over or self.game.game_won):
            self.show_victory_screen()
            return

        top = tk.Frame(self.root, bg="#1e0f08", relief="raised", bd=3)
        top.pack(fill="x", pady=(0, 10))

        tk.Label(
            top,
            text=self.game.restaurant_name.upper(),
            font=("Helvetica", 26, "bold"),
            bg="#1e0f08",
            fg="#ffcc00"
        ).pack(side="left", padx=20, pady=10)

        tk.Label(
            top,
            text=f"Giocatore: {self.game.player_name}",
            font=("Helvetica", 16),
            bg="#1e0f08",
            fg="white"
        ).pack(side="right", padx=20, pady=10)

        self.time_label = tk.Label(
            top,
            text="",
            font=("Helvetica", 20, "bold"),
            bg="#1e0f08",
            fg="#ffcc00"
        )
        self.time_label.pack(side="right", padx=100)

        info_frame = tk.Frame(self.root, bg="#2c1810")
        info_frame.pack(fill="x", pady=10)

        self.money_label = tk.Label(
            info_frame,
            font=("Helvetica", 18),
            bg="#2c1810",
            fg="#00ff00"
        )
        self.money_label.pack(side="left", padx=50)

        self.rep_label = tk.Label(
            info_frame,
            font=("Helvetica", 18),
            bg="#2c1810",
            fg="#ffaa00"
        )
        self.rep_label.pack(side="left", padx=50)

        self.cap_label = tk.Label(
            info_frame,
            font=("Helvetica", 18),
            bg="#2c1810",
            fg="white"
        )
        self.cap_label.pack(side="right", padx=50)

        self.log = scrolledtext.ScrolledText(
            self.root,
            bg="black",
            fg="#00ff88",
            font=("Courier", 11)
        )
        self.log.pack(fill="both", expand=True, padx=20, pady=10)

        sys.stdout = LogRedirector(self.log)

        controls = tk.Frame(self.root, bg="#2c1810")
        controls.pack(fill="x", pady=10)
        

        ttk.Button(
            controls,
            text="SHOP",
            command=self.show_shop
        ).pack(side="left", padx=20)

        ttk.Button(
            controls,
            text="⏩ AVANZA ORA",
            command=self.advance_hour
        ).pack(side="left", padx=40)

        ttk.Button(
            controls,
            text="UPGRADE",
            command=self.show_upgrades
        ).pack(side="left", padx=20)

        ttk.Button(
            controls,
            text="💾 SALVA & ESCI",
            command=self.save_and_exit
        ).pack(side="right", padx=20)

        self.running = True
        self.update_ui()

    def update_ui(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Aggiorna dinamicamente l'interfaccia ogni 500ms.
        In particolare, se vittoria disabilita pulsanti di gioco, aggiorna ora, bilancio, reputazione e capacità.
        Richiama se stessa con after() per aggiornamento continuo.
        '''
        if not self.running or not self.game:
            return
        
        if self.game.game_won:
            for widget in self.root.winfo_children():
                if widget.winfo_class() in ('TButton', 'Button'):
                    if widget['text'] not in ['💾 SALVA & ESCI', '🚪 USCITA']:
                        widget.config(state='disabled')

        self.time_label.config(
            text=f"Giorno {self.game.current_game_day} – Ora {self.game.current_hour:02d}:00"
        )
        self.money_label.config(text=f"€ {self.game.finance.get_balance():.2f}")
        self.rep_label.config(text=f"Reputazione: {self.game.reputation:.1f}/100")
        self.cap_label.config(text=f"Capacità: {self.game.kitchen_capacity}/ora")

        self.root.after(500, self.update_ui)


    def show_shop(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Apre la finestra dello shop ingredienti.
        In particolare, crea finestra modale con canvas scrollabile, organizza ingredienti per categoria,
        mostra nome, costo, stock, spinbox quantità e pulsante "Compra" per ogni ingrediente (inclusi secret).
        Mostra saldo attuale in fondo.
        '''
        w = tk.Toplevel(self.root)
        w.title("🛒 Shop Ingredienti")
        w.geometry("900x700")
        w.configure(bg="#2c1810")
        w.transient(self.root)
        w.grab_set()

        tk.Label(w, text="🛒 SHOP INGREDIENTI", font=("Helvetica", 24, "bold"),
                 bg="#2c1810", fg="#ffcc00").pack(pady=20)

        canvas = tk.Canvas(w, bg="#2c1810", highlightthickness=0)
        scrollbar = ttk.Scrollbar(w, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#2c1810")

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for category in ["hamburger", "topping", "bread", "sauces", "secret"]:
            if category not in self.game.inventory.data["ingredients"]:
                continue
            cat_frame = tk.LabelFrame(scrollable, text=category.upper(),
                                      font=("Helvetica", 14, "bold"),
                                      bg="#2c1810", fg="#ffffff")
            cat_frame.pack(fill="x", pady=5, padx=10)

            for name, data in self.game.inventory.data["ingredients"][category].items():
                if not isinstance(data, dict):
                    continue
                display = data.get("display_name", name.replace("_", " ").title())
                cost = data.get("current_cost", data.get("base_cost", 0.0))
                qty = data.get("current_quantity", 0)

                frame = tk.Frame(cat_frame, bg="#2c1810")
                frame.pack(fill="x", pady=2)

                tk.Label(frame, text=f"{display} – €{cost:.2f} (Stock: {qty})",
                         font=("Helvetica", 12), bg="#2c1810", fg="white").pack(side="left", padx=10)

                spin = ttk.Spinbox(frame, from_=1, to=50, width=6)
                spin.pack(side="right", padx=10)

                path = f"{category}.{name}"
                ttk.Button(frame, text="Compra",
                           command=lambda p=path, s=spin: self._buy_item(p, int(s.get()), w)).pack(side="right")

        tk.Label(w, text=f"Saldo: €{self.game.finance.get_balance():.2f}",
                 font=("Helvetica", 18), bg="#2c1810", fg="#00ff00").pack(pady=20)

    def _buy_item(self, path, qty, win):
        '''
        Funzione privata che come parametro riceve il percorso (str), la quantità (int) e win (Toplevel) oltre all'istanza della classe FantaBurgerGUI (self implicito).
        Gestisce l'acquisto di un ingrediente nello shop.
        In particolare, chiama purchase_ingredient() del GameEngine, mostra messaggio successo/errore,
        chiude e riapre lo shop in caso di acquisto riuscito.
        '''
        ok, msg = self.game.purchase_ingredient(path, qty)
        if ok:
            print(f"🛒 {msg}")
            messagebox.showinfo("Acquisto", msg)
            win.destroy()
            self.show_shop()
        else:
            messagebox.showerror("Errore", msg)


    def show_upgrades(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Apre la finestra degli upgrade disponibili.
        In particolare crea lista upgrade con descrizione, costo attuale (con aumento progressivo),
        livello corrente e limite massimo. Mostra stato (sbloccato, livello, costo), pulsante acquisto con hover.
        Mostra saldo attuale e pulsante chiusura.
        '''
        w = tk.Toplevel(self.root)
        w.title("Upgrade")
        w.geometry("600x700")
        w.configure(bg="#2c1810")
        w.transient(self.root)
        w.grab_set()

        tk.Label(w, text="UPGRADE DISPONIBILI", font=("Helvetica", 24, "bold"),
                bg="#2c1810", fg="#ffcc00").pack(pady=30)

        upgrades_info = [
            {
                "desc": "👨‍🍳 Migliora cucina (+1 capacità)",
                "id": "upgrade_kitchen",
                "base_cost": self.game.upgrade_costs.get("upgrade_kitchen", 0),
                "current_count": self.game.upgrade_counts.get("upgrade_kitchen", 0),
                "max_level": 5
            },
            {
                "desc": "👥 Nuovo dipendente (+1 capacità)",
                "id": "new_employee",
                "base_cost": self.game.upgrade_costs.get("new_employee", 0),
                "current_count": self.game.upgrade_counts.get("new_employee", 0),
                "max_level": 3
            },
            {
                "desc": "📚 Nuova ricetta segreta",
                "id": "new_recipe",
                "base_cost": self.game.upgrade_costs.get("new_recipe", 0),
                "current_count": 0,  
                "max_level": 1
            }
        ]

        for upgrade in upgrades_info:
            frame = tk.Frame(w, bg="#2c1810")
            frame.pack(fill="x", pady=15, padx=50)

            upgrade_id = upgrade["id"]
            current_count = upgrade["current_count"]
            max_level = upgrade["max_level"]
            
            cost_multiplier = 1.0 + (current_count * 0.15)
            actual_cost = upgrade["base_cost"] * cost_multiplier
            
            if upgrade_id == "new_recipe":
                if upgrade_id in self.game.unlocked_upgrades:
                    status = "✅ SBLOCCATO"
                    btn_text = "GIÀ ACQUISTATO"
                    btn_state = "disabled"
                    btn_color = "gray"
                else:
                    status = f"💰 €{actual_cost:.2f}"
                    btn_text = "ACQUISTA"
                    btn_state = "normal"
                    btn_color = "#ffcc00"
            else:
                if current_count >= max_level:
                    status = f"✅ MAX LIVELLO ({current_count}/{max_level})"
                    btn_text = "MASSIMO"
                    btn_state = "disabled"
                    btn_color = "gray"
                else:
                    status = f"Livello {current_count}/{max_level} - €{actual_cost:.2f}"
                    btn_text = "ACQUISTA"
                    btn_state = "normal"
                    btn_color = "#ffcc00"

            tk.Label(frame, text=upgrade['desc'], 
                    font=("Helvetica", 16, "bold"), 
                    bg="#2c1810", fg="white").pack(anchor="w")
            
            tk.Label(frame, text=status,
                    font=("Helvetica", 14), 
                    bg="#2c1810", fg="#aaaaaa").pack(anchor="w", pady=(5, 10))

            btn = tk.Button(frame, text=btn_text, 
                        font=("Helvetica", 12, "bold"),
                        bg=btn_color, fg="black",
                        state=btn_state,
                        command=lambda u=upgrade.copy(): self._buy_upgrade(u, w))
            btn.pack(pady=5, ipadx=30, ipady=8)
            
            if btn_state == "normal":
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#ffaa00"))
                btn.bind("<Leave>", lambda e, b=btn, c=btn_color: b.config(bg=c))

        balance_frame = tk.Frame(w, bg="#2c1810")
        balance_frame.pack(pady=20)
        
        tk.Label(balance_frame, text=f"Saldo attuale: €{self.game.finance.get_balance():.2f}",
                font=("Helvetica", 18, "bold"), 
                bg="#2c1810", fg="#00ff00").pack()

        ttk.Button(w, text="CHIUDI", 
                command=w.destroy).pack(pady=20, ipadx=40, ipady=10)

    def _buy_upgrade(self, upgrade, win):
        '''
        Funzione privata che come parametro riceve upgrade (dict) e win (Toplevel) oltre all'istanza della classe FantaBurgerGUI (self implicito).
        Gestisce l'acquisto di un upgrade.
        In particolare, calcola costo attuale, verifica fondi e livello massimo,
        chiede conferma, sottrae denaro, aggiorna contatori/upgrade sbloccati/capacità cucina,
        controlla achievement specifici, salva stato e riapre finestra upgrade.
        '''
        upgrade_id = upgrade["id"]
        current_count = upgrade["current_count"]
        max_level = upgrade["max_level"]
        
        cost_multiplier = 1.0 + (current_count * 0.15)
        actual_cost = upgrade["base_cost"] * cost_multiplier
        
        if upgrade_id == "new_recipe":
            if upgrade_id in self.game.unlocked_upgrades:
                messagebox.showinfo("Info", "Questa ricetta è già sbloccata!")
                return
        else:
            if current_count >= max_level:
                messagebox.showinfo("Info", f"Hai raggiunto il livello massimo per questo upgrade! ({current_count}/{max_level})")
                return
        
        balance = self.game.finance.get_balance()
        if balance < actual_cost:
            messagebox.showerror("Errore", f"Fondi insufficienti!\nNecessari: €{actual_cost:.2f}\nDisponibili: €{balance:.2f}")
            return
        
        if not messagebox.askyesno("Conferma acquisto", 
                                f"Acquistare {upgrade['desc']} per €{actual_cost:.2f}?\n\nSaldo dopo l'acquisto: €{balance - actual_cost:.2f}"):
            return
        
        success, msg = self.game.finance.subtract_money(actual_cost, f"Upgrade {upgrade_id}")
        if not success:
            messagebox.showerror("Errore", f"Errore transazione: {msg}")
            return
        
        if upgrade_id == "new_recipe":
            self.game.unlocked_upgrades.append(upgrade_id)
            all_secret = []
            all_recipes = self.game.recipes.get_all_recipes()
            for recipe_id, recipe_data in all_recipes.items():
                ingredients = recipe_data.get("ingredients", {})
                if any(k.startswith("secret.") for k in ingredients.keys()):
                    if recipe_id not in self.game.unlocked_recipes:
                        all_secret.append(recipe_id)
            
            if not all_secret:
                messagebox.showinfo("Info", "Nessuna altra ricetta segreta disponibile!")
                return
                
            new = random.choice(all_secret)
            self.game.unlocked_recipes.append(new)
            name = self.game.recipes.get_recipe(new).get("name", new)
            messagebox.showinfo("Successo!", f"📚 Nuova ricetta sbloccata:\n{name}!")
            print(f"\033[33m📚 Nuova ricetta sbloccata: {name}!\033[0m")
            
        else:
            self.game.upgrade_counts[upgrade_id] = current_count + 1
            
            self.game.kitchen_capacity = 1  
            self.game.kitchen_capacity += self.game.upgrade_counts.get("upgrade_kitchen", 0)
            self.game.kitchen_capacity += self.game.upgrade_counts.get("new_employee", 0)
            
            if upgrade_id == "upgrade_kitchen" and self.game.upgrade_counts[upgrade_id] >= 3:
                self.game.check_achievement("kitchen_pro!")
            elif upgrade_id == "new_employee" and self.game.upgrade_counts[upgrade_id] >= 2:
                self.game.check_achievement("small_team!")
            
            messagebox.showinfo("Successo!", 
                            f"✅ {upgrade['desc']} ACQUISTATO!\n"
                            f"Livello: {self.game.upgrade_counts[upgrade_id]}/{max_level}\n"
                            f"Nuova capacità cucina: {self.game.kitchen_capacity} panini/ora")
        
        self.game.safe_save()
        win.destroy()
        self.show_upgrades()  


    def advance_hour(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Avanza di un'ora nel gioco.
        In particolare, se game over/vittoria mostra schermata finale.
        Altrimenti esegue advance_hour() del GameEngine in un thread separato (per non bloccare GUI).
        Se dopo l'avanzamento c'è game over/vittoria, mostra schermata finale in thread principale.
        '''
        if self.game and (self.game.game_over or self.game.game_won):
            self.show_victory_screen()
            return
        def run():
            self.game.advance_hour()
            if self.game.game_over or self.game.game_won:
                self.root.after(0, self.show_victory_screen)
        threading.Thread(target=run, daemon=True).start()

    def show_victory_screen(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Mostra la schermata finale di vittoria o game over disabilitando i pulsanti di gioco, creando una finestra modale con titolo vittoria/game over,
        mostrando statistiche finali (saldo, ordini, reputazione, upgrade, giorni), salvando lo stato e impedendo doppie aperture.
        '''
        if getattr(self, "_victory_shown", False):
            return
        self._victory_shown = True
        
        self._disable_game_buttons()

        if self.game.game_over:
            titolo = "💀 GAME OVER 💀"
        else:
            titolo = "🏆 VITTORIA! 🏆"


        self.victory_window = tk.Toplevel(self.root)
        self.victory_window.title(titolo)
        self.victory_window.geometry("600x500")
        self.victory_window.configure(bg="#2c1810")
        self.victory_window.transient(self.root)
        self.victory_window.grab_set()

        self.victory_window.protocol(
            "WM_DELETE_WINDOW",
            self._close_victory_window
        )

        tk.Label(
            self.victory_window,
            text="🏆 VITTORIA! 🏆",
            font=("Helvetica", 28, "bold"),
            bg="#2c1810",
            fg="#ffcc00"
        ).pack(pady=20)

        tk.Label(
            self.victory_window,
            text="Hai completato 7 giorni di gestione!",
            font=("Helvetica", 18),
            bg="#2c1810",
            fg="white"
        ).pack(pady=10)

        stats_frame = tk.Frame(self.victory_window, bg="#2c1810")
        stats_frame.pack(pady=20)

        stats = [
            f"💰 Saldo finale: €{self.game.finance.get_balance():.2f}",
            f"🍔 Panini venduti: {self.game.orders_completed_total}",
            f"⭐ Reputazione finale: {self.game.reputation:.1f}/100",
            f"🔧 Upgrade acquistati: {sum(self.game.upgrade_counts.values())}",
            f"📅 Giorni completati: {self.game.current_game_day - 1}",
        ]

        for stat in stats:
            tk.Label(
                stats_frame,
                text=stat,
                font=("Helvetica", 16),
                bg="#2c1810",
                fg="white",
                anchor="w"
            ).pack(pady=5, fill="x")

        tk.Label(
            self.victory_window,
            text="🎉 Congratulazioni! 🎉",
            font=("Helvetica", 20, "bold"),
            bg="#2c1810",
            fg="#ffcc00"
        ).pack(pady=20)

        self.game.safe_save()

    def _close_victory_window(self):
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Gestisce la chiusura della finestra vittoria/game over in modo sicuro.
        '''
        if hasattr(self, "victory_window") and self.victory_window:
            self.victory_window.destroy()
            self.victory_window = None
            
    def _disable_game_buttons(self):
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Disabilita tutti i pulsanti di gioco (tranne SALVA & ESCI) quando si raggiunge vittoria o game over.
        In particolare percorre ricorsivamente tutti i widget e disabilita bottoni rilevanti.
        '''
        def walk(parent):
            for widget in parent.winfo_children():
                if widget.winfo_class() in ("Button", "TButton"):
                    if widget.cget("text") != "💾 SALVA & ESCI":
                        widget.config(state="disabled")
                walk(widget)

        walk(self.root)


    def return_to_main_menu(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Torna al menu principale distruggendo finestre aperte e resettando stato.
        '''
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        
        self.show_main_menu()
        
        self.game = None
        self.running = False

    def show_achievement(self, name: str):
        '''
        Come parametro riceve esplicitamente il nome dell'achievment sbloccato (stringa) oltre all'istanza della classe FantaBurgerGUI (self implicito).
        Mostra popup temporaneo di achievement sbloccato.
        In particolare distrugge eventuale popup precedente, crea label centrato con testo achievement,
        lo posiziona in alto centro e lo fa sparire dopo 3 secondi.
        '''
        if self.achievement_label and self.achievement_label.winfo_exists():
            self.achievement_label.destroy()

        self.achievement_label = tk.Label(
            self.root,
            text=f"🏆 ACHIEVEMENT: {name.upper()}",
            bg="black",
            fg="yellow",
            font=("Helvetica", 24, "bold"),
            bd=6,
            relief="raised"
        )
        self.achievement_label.place(relx=0.5, rely=0.2, anchor="center")
        self.root.after(3000, self.achievement_label.destroy)


    def save_and_exit(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Salva la partita (se esiste) e chiude l'applicazione.
        '''
        if self.game:
            self.game.safe_save()
        self.root.quit()


    def run(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe FantaBurgerGUI e ha tipo di ritorno None.
        Avvia il loop principale della GUI Tkinter.
        '''
        self.root.mainloop()


if __name__ == "__main__":
    '''
    Blocco di esecuzione condizionale standard Python.
    '''
    FantaBurgerGUI().run()
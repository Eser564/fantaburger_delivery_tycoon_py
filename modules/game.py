import json #importazione del modulo standard Python necessario per leggere, scrivere e manipolare dati in formato JSON
import os  #importazione del modulo necessario per operazioni sul sistema operativo.
import time #importazione del modulo time per aggiungere piccoli ritardi durante la simulazione ordini concorrenti
import random #importazione del modulo random per generare eventi casuali, ordini clienti, ricette segrete sbloccate e intervalli tra eventi
import threading #importazione del modulo necessario per gestire thread
from datetime import datetime #classe datetime importata dal modulo datetime usata per timestamp di salvataggio e gestione orari di gioco
from typing import Optional, Dict, Any, List #importazione di tipi avanzati per supportare controlli statici e rendere il codice più leggibile
'''
Tipi importati:
Optional corrisponde ad un valore che può essere None
Any corrisponde ad un tipo generico (cioè accetta qualsiasi valore)
List corrisponde ad una lista
Dict corrisponde ad un dizionario (struttura dati formata da una coppia chiave: valore)
'''
from .inventory import Inventory #importazione della classe Inventory dal modulo locale per gestire magazzino e ingredienti
from .recipes import Recipe #importazione della classe Recipe dal modulo locale per gestire ricette, preparazione e costi
from .finance import Finance #importazione della classe Finance dal modulo locale per gestire bilancio, transazioni e upgrade finanziari


class GameEngine:
    def __init__(self, load_saved: bool = False):
        '''
        Come parametro riceve esplicitamente load_saved (bool, con False come valore di default) oltre a ricevere implicitamente l'istanza della classe GameEngine (self).
        Costruttore della classe GameEngine (motore principale del gioco) che si occupa di caricare la configurazione con load_config(), inizializzare tutti i componenti principali (inventory, recipes, finance),
        impostare variabili di stato (giorno, ora, coda ordini, capacità cucina, eventi, reputazione, upgrade, achievement, ricette sbloccate),
        configurare costi upgrade, impostare lock per thread-safety, flag di esecuzione e modalità GUI.
        Alla fine imposta _load_saved per il caricamento successivo.
        '''
        self.config = self.load_config()
        self.inventory: Optional[Inventory] = None
        self.recipes: Optional[Recipe] = None
        self.finance: Optional[Finance] = None

        self.player_name: str = ""
        self.restaurant_name: str = ""
        self.difficulty: str = "easy"

        self.current_game_day: int = 1
        self.current_hour: int = self.config["time"]["working_start"]
        self.order_queue: List[Dict] = []
        self.orders_completed_today: int = 0
        self.orders_completed_total: int = 0
        self.orders_preparing: List[Dict] = []
        self.total_ingredients_purchased = 0
        self.total_spent_on_ingredients = 0.0


        self.kitchen_capacity: int = 1
        self.current_preparation_count: int = 0

        self.max_concurrent_orders = self.config["gameplay"]["max_concurrent_orders"]
        self.base_patience = self.config["gameplay"]["customer_patience"]
        self.max_burgers_per_order = self.config["gameplay"]["max_burgers_per_order"]

        self.events_enabled = self.config["events"]["enabled"]
        self.event_min_interval = self.config["events"]["min_interval"]
        self.event_max_interval = self.config["events"]["max_interval"]
        self.event_duration = self.config["events"]["event_duration"]
        self.special_events = self.config["events"]["special_events"]
        self.event_probabilities = self.config["events"]["probabilities"]

        self.working_start = self.config["time"]["working_start"]
        self.working_end = self.config["time"]["working_end"]
        self.max_days = self.config["time"]["days"]
        self.game_won = False


        self.upgrade_counts = {
            "upgrade_kitchen": 0,
            "new_employee": 0
        }
        
        self.upgrade_base_costs = self.config["gameplay"]["unlock"]
        self.upgrade_current_costs = self.upgrade_base_costs.copy()
        self.kitchen_base_capacity = 1 
        self.unlocked_upgrades = []
        self.upgrade_costs = self.config["gameplay"]["unlock"]
        self.reputation = self.config["gameplay"]["initial_reputation"]
        self.active_events: Dict[str, int] = {}
        self.hours_since_last_event: int = 0
        self.next_event_interval: int = random.randint(self.event_min_interval, self.event_max_interval)

        self.save_file: str = "data/savestate.json"
        self.lock = threading.Lock()
        self.running = False
        self.game_over = False
        self.gui_mode = False
        self._load_saved = load_saved
        self._ending_day = False
        self.achievements_unlocked: List[str] = []
        self.unlocked_recipes: List[str] = []
        self.order_timeout = self.config["gameplay"]["order_timeout"]
        self.next_order_id = 1 

    def load_config(self) -> Dict[str, Any]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno Dict[str, Any].
        Carica la configurazione dal file config.json tentando di leggere e parsare il JSON; in caso di errore viene stampato messaggio e sollevata eccezione (il gioco non può proseguire senza config valida).
        '''
        try:
            with open('data/config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Errore caricamento config: {e}")
            raise

    def start_new_game(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None (non restituisce nulla).
        Avvia una nuova partita in modalità console.
        In particolare, stampa banner, chiede nome giocatore e ristorante, selezione difficoltà,
        inizializza inventory, recipes, finance, imposta valori iniziali (giorno, ora, ricette base, capacità),
        applica impostazioni difficoltà, salva stato iniziale e mostra riepilogo iniziale.
        '''
        print("\n" + "="*60)
        print("NUOVA PARTITA".center(60))
        print("="*60)

        self.player_name = input("Inserisci il tuo nome: ").strip() or "Eser564"
        self.restaurant_name = input("Inserisci il nome del ristorante: ").strip() or "FantaBurger"

        print("\nDifficoltà disponibili:")
        levels = list(self.config["difficulty"]["levels"].keys())
        for i, level in enumerate(levels, 1):
            print(f"{i}. {level.capitalize()}")

        while True:
            choice = input("\nScegli difficoltà (numero): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(levels):
                self.difficulty = levels[int(choice) - 1]
                break
            print("Scelta non valida!")

        print(f"\nBenvenuto {self.player_name}!")
        print(f"Gestirai '{self.restaurant_name}' in modalità {self.difficulty.upper()}.")

        self.inventory = Inventory(load_saved=False)
        self.recipes = Recipe(inventory=self.inventory)
        self.finance = Finance(initial_balance=self.config["economy"]["initial_balance"], load_saved=False)
        self.finance.game_engine = self

        self.current_game_day = 1
        self.current_hour = self.working_start
        self.order_queue = []
        self.orders_preparing = []
        self.orders_completed_today = 0
        self.orders_completed_total = 0
        self.kitchen_capacity = 1
        self.current_preparation_count = 0
        self.unlocked_upgrades = []
        self.active_events = {}
        self.hours_since_last_event = 0
        self.next_event_interval = random.randint(self.event_min_interval, self.event_max_interval)
        self.game_over = False
        self.achievements_unlocked = []
        self.unlocked_recipes = self.get_base_recipes()
        self.upgrade_counts = {
            "upgrade_kitchen": 0,
            "new_employee": 0
        }
        self.kitchen_capacity = 1 

        self._apply_difficulty_settings()
        self.safe_save()

        print(f"\n✅ Partita avviata!")
        print(f"💰 Saldo iniziale: €{self.config['economy']['initial_balance']:.2f}")
        print(f"👨‍🍳 Capacità cucina: {self.kitchen_capacity} panino/ora")
        print("\nPremi INVIO per iniziare...")

    def get_base_recipes(self) -> List[str]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno List[str].
        Restituisce la lista delle ricette base (non segrete) disponibili all'inizio del gioco.
        In particolare, scorre tutte le ricette e include solo quelle senza ingredienti "secret.".
        '''
        all_recipes = self.recipes.get_all_recipes()  
        base = []
        for recipe_data in all_recipes.values():
            has_secret = any(k.startswith("secret.") for k in recipe_data.get("ingredients", {}).keys())
            if not has_secret:
                base.append(recipe_data["id"])
        return base
    
    def _apply_difficulty_settings(self) -> None:
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None (non restituisce nulla).
        Applica i modificatori della difficoltà selezionata.
        In particolare, imposta il moltiplicatore di profitto nel finance e modifica la pazienza base clienti in base alla difficoltà.
        '''
        diff_settings = self.config["difficulty"]["levels"].get(self.difficulty, {})
        if self.finance:
            self.finance.profit_multiplier = diff_settings.get("profit", 1.0)

        multiplier = {"easy": 1.3, "normal": 1.0, "hard": 0.7, "ultimate": 0.5, "nightmare": 0.3}.get(self.difficulty, 1.0)
        self.base_patience = int(self.base_patience * multiplier)

    def load_game(self) -> bool:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno bool.
        Carica una partita salvata da savestate.json.
        In particolare, verifica esistenza file, carica stato, ripristina tutti i valori (giocatore, ristorante, giorno, reputazione, upgrade, ordini, eventi, achievement, ricette sbloccate),
        ricrea inventory, recipes e finance con stato salvato, applica impostazioni difficoltà e mostra riepilogo caricamento.
        Restituisce True se riuscito, False altrimenti.
        '''
        if not os.path.exists(self.save_file):
            print("Nessun salvataggio trovato!")
            return False

        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                state = json.load(f)


            self.player_name = state.get("player_name", "Giocatore")
            self.restaurant_name = state.get("restaurant_name", "FantaBurger")
            self.difficulty = state.get("difficulty", "easy")
            self.current_game_day = state.get("current_game_day", 1)
            self.reputation = state.get("reputation", 50.0)
            self.kitchen_capacity = state.get("kitchen_capacity", 1)
            self.unlocked_upgrades = state.get("unlocked_upgrades", [])
            self.order_queue = state.get("order_queue", [])
            self.active_events = state.get("active_events", {})
            self.hours_since_last_event = state.get("hours_since_last_event", 0)
            self.next_event_interval = state.get(
                "next_event_interval",
                random.randint(self.event_min_interval, self.event_max_interval)
            )
            self.orders_completed_total = state.get("orders_completed_total", 0)
            self.achievements_unlocked = state.get("achievements_unlocked", [])

            self.inventory = Inventory(load_saved=True)
            inv_state = state.get("inventory_state")
            if inv_state:
                self.inventory.state = inv_state

            self.recipes = Recipe(inventory=self.inventory)

            unlocked = state.get("unlocked_recipes", self.get_base_recipes())
            cleaned = []
            for r in unlocked:
                if isinstance(r, dict) and "id" in r:
                    cleaned.append(r["id"])
                elif isinstance(r, str):
                    cleaned.append(r)
            self.unlocked_recipes = cleaned

            self.finance = Finance(initial_balance=0.0, load_saved=True)
            self.finance.state = state
            self.finance.game_engine = self

            self.current_hour = state.get("current_hour", self.working_start)
            self.orders_preparing = []
            self.orders_completed_today = state.get("orders_completed_today", 0)
            self.current_preparation_count = self.orders_completed_today

            self._apply_difficulty_settings()
            
            self.upgrade_counts = state.get("upgrade_counts", {
                "upgrade_kitchen": 0,
                "new_employee": 0
            })
            
            self.kitchen_capacity = 1  
            self.kitchen_capacity += self.upgrade_counts.get("upgrade_kitchen", 0)
            self.kitchen_capacity += self.upgrade_counts.get("new_employee", 0)

            print(f"\n✅ Partita caricata!")
            print(f"👤 Giocatore: {self.player_name}")
            print(f"🏪 Ristorante: {self.restaurant_name}")
            print(f"📅 Giorno: {self.current_game_day}")
            print(f"🕐 Ora attuale: {self.current_hour}:00")
            print(f"⭐ Reputazione: {self.reputation:.1f}/100")
            print(f"👨‍🍳 Capacità cucina: {self.kitchen_capacity} panini/ora")
            print(f"💰 Saldo: €{self.finance.get_balance():.2f}")

            return True

        except Exception as e:
            print(f"❌ Errore caricamento: {e}")
            return False



    def safe_save(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None (non restituisce nulla).
        Salva in modo sicuro lo stato completo del gioco su savestate.json.
        In particolare, crea un dizionario con tutti i dati rilevanti (giocatore, giorno, reputazione, upgrade, ordini, eventi, statistiche finance e inventory),
        scrive il JSON con indentazione e gestisce eccezioni stampando errore.
        '''
        if not self.finance:
            return

        try:
            save_state = {
                "player_name": self.player_name,
                "restaurant_name": self.restaurant_name,
                "difficulty": self.difficulty,
                "current_game_day": self.current_game_day,
                "reputation": round(self.reputation, 1),
                "kitchen_capacity": self.kitchen_capacity,
                "unlocked_upgrades": self.unlocked_upgrades,
                "order_queue": self.order_queue,
                "active_events": self.active_events,
                "current_hour": self.current_hour,
                "hours_since_last_event": self.hours_since_last_event,
                "next_event_interval": self.next_event_interval,
                "last_save": datetime.now().isoformat(),
                "balance": self.finance.state.get('balance', 0.0),
                "daily_stats": self.finance.state.get('daily_stats', {}),
                "days_in_operation": self.finance.state.get('days_in_operation', 0),
                "last_processed_game_day": self.finance.state.get('last_processed_game_day', 0),
                "upgrade_counts": self.upgrade_counts, 
                "game_over": self.finance.state.get('game_over', False),
                "orders_completed_total": self.orders_completed_total,
                "achievements_unlocked": self.achievements_unlocked,
                "unlocked_recipes": self.unlocked_recipes,
                "inventory_state": getattr(self.inventory, 'state', {})
            }

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ Errore salvataggio: {e}")

    def check_achievement(self, name: str):
        '''
        Come parametro riceve esplicitamente il nome dell'achievment (stringa) oltre all'istanza della classe GameEngine (self implicito).
        Controlla e sblocca un achievement se non già ottenuto.
        In particolare, aggiunge il nome alla lista achievements_unlocked, stampa messaggio colorato e chiama callback GUI se presente.
        Restituisce True se sbloccato nuovo, False se già presente.
        '''
        if name not in self.achievements_unlocked:
            self.achievements_unlocked.append(name)
            print(f"\033[33m🏆 ACHIEVEMENT SBLOCCATO: {name.upper()}!\033[0m")
            if hasattr(self, 'on_achievement_unlocked'):
                self.on_achievement_unlocked(name)
            return True
        return False

    def check_and_trigger_events(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e non restituisce nulla.
        Controlla e attiva eventi casuali se abilitati.
        In particolare, incrementa contatore ore, se raggiunto intervallo casuale sceglie il tipo di evento,
        seleziona un evento specifico disponibile, lo attiva per durata configurata e applica l' effetto immediato.
        Infine, resetta contatore e genera un nuovo intervallo.
        '''
        if not self.events_enabled:
            return

        self.hours_since_last_event += 1

        if self.hours_since_last_event >= self.next_event_interval:
            event_type = random.choices(
                ["positive", "negative", "neutral"],
                weights=[
                    self.event_probabilities["positive"],
                    self.event_probabilities["negative"],
                    self.event_probabilities["neutral"]
                ]
            )[0]

            available = []
            for event_name, enabled in self.special_events.items():
                if not enabled:
                    continue

                if event_name in ["lucky_day", "food_critic", "rush_hour"]:
                    cat = "positive"
                elif event_name in ["broken_equipment", "health_inspection", "weather_bad", "employee_sick", "theft"]:
                    cat = "negative"
                else:
                    cat = "neutral"

                if cat == event_type:
                    available.append(event_name)

            if available:
                event = random.choice(available)
                self.active_events[event] = self.event_duration
                self.apply_event_effect(event)

                self.hours_since_last_event = 0
                self.next_event_interval = random.randint(self.event_min_interval, self.event_max_interval)

    def show_detailed_inventory(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Mostra inventario dettagliato in modalità console.
        In particolare, stampa valore totale, avviso scorte basse e dettaglio per categoria con quantità e valore parziale.
        Infine, attende input INVIO per continuare.
        '''   
        print("\n" + "📦" * 25)
        print("📦 INVENTARIO DETTAGLIATO 📦")
        print("📦" * 25)
        
        total_value = self.inventory.get_inventory_value()
        print(f"💰 Valore totale inventario: €{total_value:.2f}")
        
        low_items = self.inventory.get_low_stock_items()
        if low_items:
            print(f"\n⚠️  {len(low_items)} INGREDIENTI IN ESAURIMENTO:")
            for item in low_items:
                status = "🔴 CRITICO" if item['critical'] else "🟡 ATTENZIONE"
                print(f"   {status} {item['name']}: {item['current_quantity']} (min: {item['reorder_point']})")
        
        print("\n" + "="*60)
        for category in ["hamburger", "topping", "bread", "sauces", "secret"]:
            if category in self.inventory.data.get("ingredients", {}):
                print(f"\n{category.upper()}:")
                cat_items = self.inventory.data["ingredients"][category]
                for name, data in cat_items.items():
                    if isinstance(data, dict):
                        display = data.get("display_name", name.replace("_", " ").title())
                        qty = data.get("current_quantity", 0)
                        cost = data.get("current_cost", data.get("base_cost", 0.0))
                        value = qty * cost
                        print(f"  • {display}: {qty} unità × €{cost:.2f} = €{value:.2f}")
        
        print("\n" + "="*60)
        input("Premi INVIO per continuare...")
        
    def apply_event_effect(self, event_name: str) -> None:
        '''
        Come parametro riceve esplicitamente il nome dell'evento (stringa) oltre all'istanza della classe GameEngine (self implicito).
        Applica l'effetto immediato di un evento speciale.
        In particolare, stampa banner evento e effetto specifico (bonus denaro, penalità, modifica capacità, reputazione, clienti).
        '''
        event_display = event_name.replace('_', ' ').title()
        print(f"\n{'⚡'*20}")
        print(f"EVENTO: {event_display}")
        print(f"{'⚡'*20}")

        if event_name == "rush_hour":
            print("   🚀 ORA DI PUNTA! +150% clienti per 3 ore")

        elif event_name == "food_critic":
            bonus = random.uniform(150, 400)
            self.finance.add_money(bonus, "Recensione stellata")
            self.reputation = min(100, self.reputation + 15)
            print(f"   🎩 Critico gastronomico del Gambero Rosso! +€{bonus:.2f} | +15 reputazione")

        elif event_name == "health_inspection":
            penalty = random.uniform(100, 350)
            self.finance.subtract_money(penalty, "Multa sanitaria")
            self.reputation = max(0, self.reputation - 15)
            print(f"   🚨 Ispezione sanitaria da parte dei NAS! -€{penalty:.2f} | -15 reputazione")

        elif event_name == "employee_sick":
            print("   🤒 Dipendente malato! -50% capacità cucina per 3 ore")
            self.kitchen_capacity = max(1, self.kitchen_capacity // 2)

        elif event_name == "lucky_day":
            bonus = random.uniform(200, 500)
            self.finance.add_money(bonus, "Giornata fortunata")
            print(f"   🍀 GIORNATA FORTUNATA! +€{bonus:.2f}")

        elif event_name == "broken_equipment":
            penalty = random.uniform(250, 600)
            self.finance.subtract_money(penalty, "Riparazione")
            print(f"   🔧 ATTREZZATURA GUASTA! -€{penalty:.2f}")

        elif event_name == "weather_bad":
            print("   🌧️ MALTEMPO! -50% clienti per 3 ore")
            
        elif event_name == "theft":
            stole = random.uniform(100, 250)
            self.finance.subtract_money(stole, "Furto avvenuto!")
            print(f"   🦹 FURTO! -€{stole:.2f}")

    def update_active_events(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Aggiorna la durata degli eventi attivi e rimuove quelli scaduti.
        In particolare, decrementa contatore, se arriva a 0 rimuove evento e ripristina effetti 
        (per esempio se un dipendente guarisce, la capacità in cucina si normalizza).
        '''
        expired = []
        for event, remaining in list(self.active_events.items()):
            self.active_events[event] = remaining - 1
            if self.active_events[event] <= 0:
                expired.append(event)

        for event in expired:
            del self.active_events[event]
            if event == "employee_sick":
                self.kitchen_capacity = self.get_base_kitchen_capacity()
                print(f"   💪 Il dipendente è guarito! Capacità cucina ripristinata a {self.kitchen_capacity}")

    def get_base_kitchen_capacity(self) -> int:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno int.
        Calcola la capacità base della cucina considerando gli upgrade sbloccati.
        '''
        base = 1
        if "upgrade_kitchen" in self.unlocked_upgrades:
            base += 1
        return base

    def get_event_multipliers(self) -> Dict[str, float]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno Dict[str, float].
        Restituisce i moltiplicatori attivi causati dagli eventi (clienti e capacità cucina).
        '''
        multipliers = {"customer_chance": 1.0, "kitchen_capacity": 1.0}
        for event in self.active_events:
            if event == "rush_hour":
                multipliers["customer_chance"] = 2.5
            elif event == "weather_bad":
                multipliers["customer_chance"] = 0.5
            elif event == "employee_sick":
                multipliers["kitchen_capacity"] = 0.5
        return multipliers

    def process_kitchen_work(self) -> List[str]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno List[str].
        Processa la preparazione ordini nella cucina.
        In particolare, applica la capacità effettiva (dovuta a possibili eventi), prepara fino a capacità panini/ora,
        consuma ingredienti, vende, aggiorna profitto, gestisce completamento ordini e reputazione.
        Restituisce lista di messaggi da mostrare.
        '''
        messages = []
        self.current_preparation_count = 0
        self.orders_preparing = []

        multipliers = self.get_event_multipliers()
        effective_capacity = int(self.kitchen_capacity * multipliers["kitchen_capacity"])

        print(f"\n👨‍🍳 CUCINA: Capacità {effective_capacity} panini/ora")

        if effective_capacity <= 0:
            messages.append(" 😴 Cucina inattiva (evento negativo)")
            return messages

        i = 0
        while i < len(self.order_queue):
            order = self.order_queue[i]
            hours_waited = self.current_hour - order["arrival_hour"]
            if hours_waited > self.order_timeout:
                messages.append(f" ⏰ Ordine #{order['id']} scaduto dopo {hours_waited}h! -5 reputazione")
                self.reputation = max(0, self.reputation - 5)
                del self.order_queue[i]
            else:
                i += 1

        if not self.order_queue:
            messages.append(" 😴 Nessun ordine in coda")
            return messages

        prepared = 0
        i = 0

        while prepared < effective_capacity and i < len(self.order_queue):
            order = self.order_queue[i]
            recipe_data = self.recipes.get_recipe(order["recipe_id"])

            if not recipe_data or not isinstance(recipe_data, dict):
                messages.append(f" ❌ Ordine #{order['id']} rimosso: ricetta non valida")
                del self.order_queue[i]
                continue

            recipe = recipe_data

            ingredients = recipe.get('ingredients', {})
            can_prepare, reason = self.inventory.check_availability(ingredients)

            if not can_prepare:
                messages.append(f" ⚠️ Ordine #{order['id']} ({recipe.get('name', 'Sconosciuto')}): {reason}")
                i += 1
                continue

            success, prep_msg, details = self.recipes.prepare_recipe(order["recipe_id"], 1)

            if not success:
                messages.append(f" ❌ Preparazione fallita Ordine #{order['id']}: {prep_msg}")
                i += 1
                continue

            sale_success, sale_msg, sale_details = self.finance.process_sale(
                details.get('total_price', 0.0),
                details.get('total_cost', 0.0),
                details.get('recipe_name', recipe.get('name', 'Panino'))
            )

            if not sale_success:
                messages.append(f" ❌ Vendita fallita Ordine #{order['id']}: {sale_msg}")
                i += 1
                continue

            profit = sale_details.get('net_profit', 0.0)
            recipe_name = recipe.get('name', 'Panino')
            messages.append(f" ✅ Preparato 1x {recipe_name} (Ordine #{order['id']}) — Guadagno: €{profit:.2f}")

            order["remaining"] -= 1
            prepared += 1
            self.current_preparation_count += 1

            self.orders_preparing.append({
                "order_id": order["id"],
                "recipe": recipe_name,
                "profit": profit
            })

            if order["remaining"] <= 0:
                messages.append(f" 🎉 Ordine #{order['id']} COMPLETATO! +5 reputazione")
                self.orders_completed_today += 1
                self.orders_completed_total += 1
                self.reputation = min(100, self.reputation + 5.0)

                if self.orders_completed_total == 1:
                    self.check_achievement("prima_vendita!")
                if self.orders_completed_total == 10:
                    self.check_achievement("masto_paninaro!")
                if "perfetto" in order["recipe_id"].lower():
                    self.check_achievement("è perfetto!")
                if self.orders_completed_today >= 5:
                    self.check_achievement("comm si veloce!")
                if self.reputation >= 100:
                    self.check_achievement("attiraclienti!")

                del self.order_queue[i]
            else:
                i += 1

        if prepared == 0:
            messages.append(" 😴 Nessun panino preparato questa ora")

        return messages

    def simulate_new_orders(self) -> List[str]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno List[str].
        Simula l'arrivo di nuovi ordini clienti.
        In particolare, calcola probabilità in base a difficoltà, reputazione ed eventi attivi,
        genera numero ordini casuale, crea ogni ordine in thread separato con piccolo ritardo per realismo,
        aggiunge alla coda con id progressivo.
        Restituisce lista di messaggi da mostrare.
        '''
        messages = []

        if len(self.order_queue) >= self.max_concurrent_orders * 3:
            messages.append(" 📛 CUCINA PIENA! Nuovi ordini respinti.")
            return messages

        if self.current_hour >= self.working_end:
            return messages

        diff_settings = self.config["difficulty"]["levels"][self.difficulty]
        base_chance = diff_settings.get("customer_frequency", 1.0) * 0.25

        rep_modifier = max(0.5, self.reputation / 100)
        event_mult = self.get_event_multipliers()["customer_chance"]

        final_chance = base_chance * rep_modifier * event_mult

        r = random.random()
        if r < final_chance * 0.5:
            num_orders = 1
        elif r < final_chance:
            num_orders = 2
        elif r < final_chance * 1.5:
            num_orders = 3
        elif r < final_chance * 2.0:
            num_orders = 4
        else:
            num_orders = 0

        if num_orders == 0:
            return messages

        def create_order(client_id: int):
            try:
                available = []

                for r in self.recipes.get_all_recipes().values():
                    if r["id"] not in self.unlocked_recipes:
                        continue

                    ok, _ = self.inventory.check_availability(r["ingredients"])
                    if ok:
                        available.append(r)

                if not available:
                    print("   ⚠️ Nessuna ricetta producibile (ingredienti insufficienti)")
                    return

                recipe = random.choice(available)
                qty = random.randint(1, min(3, self.max_burgers_per_order))

                with self.lock:
                    if len(self.order_queue) >= self.max_concurrent_orders * 3:
                        return

                    order_id = self.next_order_id
                    self.next_order_id += 1
                    order = {
                        "id": order_id,
                        "recipe_id": recipe['id'],
                        "recipe_name": recipe['name'],
                        "quantity": qty,
                        "remaining": qty,
                        "arrival_hour": self.current_hour
                    }
                    self.order_queue.append(order)

                print(f"   📞 CLIENTE {client_id}: Ordine #{order_id} - {qty}x {recipe['name']}")

            except Exception as e:
                print(f"   Errore cliente {client_id}: {e}")

        threads = []
        for i in range(1, num_orders + 1):
            t = threading.Thread(target=create_order, args=(i,), daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.15 + random.random() * 0.4)

        for t in threads:
            t.join()

        messages.append(f"   📞 Arrivati {num_orders} nuovo/i ordine/i concorrenti!")
        return messages

    def show_order_queue(self) -> List[str]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno List[str].
        Mostra la coda ordini attuale.
        In particolare, stampa numero ordini in attesa e dettaglio dei primi 6 (o "e altri..." se di più).
        Restituisce lista di messaggi da mostrare.
        '''
        messages = []

        if self.order_queue:
            messages.append(f"\n📋 CODA ORDINI ({len(self.order_queue)} in attesa):")
            for i, order in enumerate(self.order_queue[:6]):
                messages.append(f"   {i+1}. Ordine #{order['id']}: {order['remaining']}/{order['quantity']}x {order['recipe_name']}")
            if len(self.order_queue) > 6:
                messages.append(f"   ... e altri {len(self.order_queue)-6} ordini")
        else:
            messages.append("\n📋 CODA ORDINI: Vuota")

        return messages
    
    def purchase_ingredient(self, ingredient_path: str, qty: int):
        '''
        Come parametro riceve esplicitamente il percorso dell'ingrediente (stringa) e quantità (int) oltre all'istanza della classe GameEngine (self implicito).
        Gestisce l'acquisto di ingredienti.
        In particolare, calcola costo totale, verifica fondi, sottrae denaro con finance, aggiunge a inventory e aggiorna contatori totali.
        Restituisce True e messaggio di successo o ppure False ed errore.
        '''
        if not self.inventory:
            return False, "Inventory missing"
        
        unit = self.inventory.get_unit_cost(ingredient_path)
        cost = unit * qty

        if self.finance.get_balance() < cost:
            return False, "Fondi insufficienti!"

        ok = self.finance.buy_ingredient(cost, ingredient_path, qty)
        if ok:
            self.inventory.add_ingredient(ingredient_path, qty)
            self.total_ingredients_purchased += qty
            self.total_spent_on_ingredients += cost
            return True, f"Acquistato {qty}x {ingredient_path} per €{cost:.2f}"
        return False, "Errore pagamento"

    def show_upgrade_menu(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Mostra il menu upgrade in modalità console.
        In particolare, stampa lista upgrade con costo attuale (aumento progressivo), livello corrente e massimo,
        permette acquisto con conferma, gestisce fondi insufficienti e aggiorna capacità e achievement.
        '''
        print("\n" + "🔧" * 20)
        print("UPGRADE DISPONIBILI")
        print("🔧" * 20)

        upgrades_info = [
            {
                "desc": "👨‍🍳 Migliora cucina (+1 capacità)",
                "id": "upgrade_kitchen", 
                "base_cost": self.upgrade_costs.get("upgrade_kitchen", 0),
                "current_count": self.upgrade_counts.get("upgrade_kitchen", 0),
                "max_level": 5  
            },
            {
                "desc": "📚 Nuova ricetta",
                "id": "new_recipe",
                "base_cost": self.upgrade_costs.get("new_recipe", 0),
                "current_count": 0, 
                "max_level": 2
            },
            {
                "desc": "👥 Nuovo dipendente (+1 capacità)",
                "id": "new_employee",
                "base_cost": self.upgrade_costs.get("new_employee", 0),
                "current_count": self.upgrade_counts.get("new_employee", 0),
                "max_level": 3 
            }
        ]

        for i, upgrade in enumerate(upgrades_info, 1):
            upgrade_id = upgrade["id"]
            current_count = upgrade["current_count"]
            max_level = upgrade["max_level"]
            
            cost_multiplier = 1.0 + (current_count * 0.15)
            actual_cost = upgrade["base_cost"] * cost_multiplier
            
            if upgrade_id == "new_recipe":
                if upgrade_id in self.unlocked_upgrades:
                    print(f"{i}. {upgrade['desc']} - ✅ SBLOCCATO")
                else:
                    print(f"{i}. {upgrade['desc']} - 💰 €{actual_cost:.2f}")
            else:
                if current_count >= max_level:
                    print(f"{i}. {upgrade['desc']} - ✅ MAX LIVELLO ({current_count}/{max_level})")
                else:
                    print(f"{i}. {upgrade['desc']} (Livello {current_count}/{max_level}) - 💰 €{actual_cost:.2f}")

        print("🔧" * 20)
        print(f"💰 Saldo attuale: €{self.finance.get_balance():.2f}")
        print("0. Torna al gioco")

        choice = input("\nScegli upgrade (numero): ").strip()

        if choice == "0":
            return

        if not choice.isdigit():
            print("❌ Scelta non valida")
            return

        choice = int(choice)
        if choice < 1 or choice > len(upgrades_info):
            print("❌ Scelta non valida")
            return

        upgrade = upgrades_info[choice - 1]
        upgrade_id = upgrade["id"]
        current_count = upgrade["current_count"]
        max_level = upgrade["max_level"]
        
        cost_multiplier = 1.0 + (current_count * 0.15)
        actual_cost = upgrade["base_cost"] * cost_multiplier

        if upgrade_id == "new_recipe":
            if upgrade_id in self.unlocked_upgrades:
                print("⚠️ Questa ricetta è già sbloccata!")
                return
                
        else:
            if current_count >= max_level:
                print(f"❌ Hai raggiunto il livello massimo per questo upgrade! ({current_count}/{max_level})")
                return

        if self.finance.get_balance() < actual_cost:
            print(f"❌ Fondi insufficienti! Servono €{actual_cost:.2f}")
            return

        success, msg = self.finance.subtract_money(actual_cost, f"Upgrade {upgrade_id}")
        if not success:
            print(f"❌ Errore transazione: {msg}")
            return

        if upgrade_id == "new_recipe":
            self.unlocked_upgrades.append(upgrade_id)
            all_secret = self.recipes.get_secret_recipes()
            available = [rid for rid in all_secret if rid not in self.unlocked_recipes]
            
            if not available:
                print("ℹ️ Nessuna altra ricetta segreta disponibile!")
                return
                
            new = random.choice(available)
            self.unlocked_recipes.append(new)
            name = self.recipes.get_recipe(new).get("name", new)
            print(f"\033[33m📚 Nuova ricetta sbloccata: {name}!\033[0m")
            
        else:
            self.upgrade_counts[upgrade_id] = current_count + 1
            
            self.kitchen_capacity = 1  
            self.kitchen_capacity += self.upgrade_counts.get("upgrade_kitchen", 0)
            self.kitchen_capacity += self.upgrade_counts.get("new_employee", 0)
            
            print(f"✅ {upgrade['desc']} ACQUISTATO!")
            print(f"   Livello: {self.upgrade_counts[upgrade_id]}/{max_level}")
            print(f"   Capacità cucina ora: {self.kitchen_capacity} panini/ora")
            
            if upgrade_id == "upgrade_kitchen" and self.upgrade_counts[upgrade_id] >= 3:
                self.check_achievement("non_è_la_centralina!")
            elif upgrade_id == "new_employee" and self.upgrade_counts[upgrade_id] >= 2:
                self.check_achievement("piccola_squadra!")

        self.safe_save()

    def advance_hour(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Avanza di un'ora nel gioco.
        In particolare: gestisce fine giornata, stampa header ora/giorno, aggiorna eventi, genera nuovi ordini,
        processa preparazione in cucina, mostra coda ordini e statistiche del momento.
        In modalità GUI evita alcune stampe non necessarie.
        '''
        if self.gui_mode:
            self._ending_day = False  
        
        self.current_hour += 1
                
        self.check_game_over()
        if self.game_over:
            return

        if self.current_hour > self.working_end:
            self.end_day()
            return
 
        print(f"\n{'='*50}")
        print(f"🕐 ORA {self.current_hour:02d}:00 | GIORNO {self.current_game_day}")
        print(f"{'='*50}")
            

        print(f"💰 Saldo: €{self.finance.get_balance():.2f}")
        print(f"⭐ Reputazione: {self.reputation:.1f}/100")
        print(f"📦 Ordini completati oggi: {self.orders_completed_today}")
        print(f"👨‍🍳 Capacità cucina: {self.kitchen_capacity} panini/ora")

        if self.active_events:
            print(f"\n📢 Eventi attivi:")
            for event, remaining in self.active_events.items():
                name = event.replace('_', ' ').title()
                print(f"   • {name} ({remaining}h rimanenti)")

        self.update_active_events()
        
        self.check_and_trigger_events()

        order_messages = self.simulate_new_orders()
        
        preparation_messages = self.process_kitchen_work()

        if preparation_messages:
            print("\n👨‍🍳 PREPARAZIONE:")
            for msg in preparation_messages:
                print(msg)

        if order_messages:
            print("\n📞 NUOVI ORDINI:")
            for msg in order_messages:
                print(msg)

        queue_messages = self.show_order_queue()
        for msg in queue_messages:
            print(msg)

        daily_stats = self.finance.state['daily_stats']
        print(f"\n💼 FINANZE OGGI:")
        print(f"   Incassi: €{daily_stats.get('revenue', 0):.2f}")
        print(f"   Spese: €{daily_stats.get('expenses', 0):.2f}")
        print(f"   Profitto: €{daily_stats.get('profit', 0):.2f}")
        print(f"   Tassa Giornaliera: €{self.finance.daily_costs.get('daily_tax', 75.0):.2f}")

        if self.current_hour % 3 == 0 or self.current_hour == self.working_start:
            print(f"\n📦 INVENTARIO (scorte basse):")
            low_items = self.inventory.get_low_stock_items()
            if low_items:
                for item in low_items[:5]:
                    status = "⚠️ CRITICO" if item['critical'] else "ℹ️ Basso"
                    print(f"   {status} {item['name']}: {item['current_quantity']} rimasti")
            else:
                print("   ✅ Tutte le scorte sufficienti")

        if not self.gui_mode:
            print(f"\n{'='*50}")
            print("INVIO=continua, U=upgrade, S=shop, I=inventario, Q=esci")
        
        
    def end_day(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Gestisce la fine della giornata di lavoro.
        In particolare, applica costi giornalieri con finance, controlla game over/vittoria,
        incrementa giorno, resetta ora e statistiche giornaliere, salva stato e mostra banner nuovo giorno.
        '''  
        try:
            print(f"\n{'='*60}")
            print("🏁 FINE GIORNATA".center(60))
            print(f"{'='*60}")
            
            self._ending_day = True  
            
            success, msg, details = self.finance.apply_daily_costs()
            if success:
                print(f"✅ {msg}")
                           
            self.check_game_over()
            if self.game_over:
                return
            
            if self.current_game_day >= self.max_days:
                self.victory_sequence()
                return
            
            self.current_game_day += 1
            self.current_hour = self.working_start  
            self.orders_completed_today = 0
            self.order_queue.clear()
            self.orders_preparing.clear()
            self.current_preparation_count = 0
            self.hours_since_last_event = 0
                        
            print(f"\n{'🔔'*20}")
            print(f"📅 GIORNO {self.current_game_day} INIZIATO!".center(60))
            print(f"{'🔔'*20}")
            print(f"🕐 Ora: {self.current_hour:02d}:00")
            print(f"💰 Saldo: €{self.finance.get_balance():.2f}")
            print(f"⭐ Reputazione: {self.reputation:.1f}/100")
            print(f"👨‍🍳 Capacità cucina: {self.kitchen_capacity} panini/ora")
            print(f"📊 Nuovo giorno iniziato! Pronti per nuovi ordini! 🍔")
            
            self.safe_save()            
        except Exception as e:
            print(f"❌ Errore in end_day: {e}")
        finally:
            self._ending_day = False
            
    def check_game_over(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Controlla condizioni di game over.
        In particolare, se il bilancio arriva a 0 (o negativo) o reputazione arriva a 0 ci sarà game over, imposta flag, salvataggio e stampa messaggio.
        '''
        if self.game_over or self.game_won:
            return

        if self.finance.get_balance() <= 0:
            self.game_over = True
            self.running = False
            print("\n💀 GAME OVER: Bilancio esaurito!")
            self.safe_save()
            return

        if self.reputation <= 0:
            self.game_over = True
            self.running = False
            print("\n💀 GAME OVER: Reputazione azzerata!")
            self.safe_save()
            return

            
    def victory_sequence(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Gestisce la vittoria al completamento dei giorni richiesti.
        In particolare, imposta flag vittoria/game over, stampa banner vittoria con statistiche finali,
        salva stato e (in modalità console) attende INVIO.
        '''
        self.game_won = True
        self.game_over = True
        self.running = False
        
        print("\n" + "🎉" * 30)
        print("🏆 VITTORIA! 🏆".center(60))
        print(f"Hai completato {self.max_days} giorni di gestione!".center(60))
        print("🎉" * 30)
        
        print(f"\n📊 STATISTICHE FINALI:")
        print(f"💰 Saldo finale: €{self.finance.get_balance():.2f}")
        print(f"🍔 Panini venduti: {self.orders_completed_total}")
        print(f"⭐ Reputazione: {self.reputation:.1f}/100")
        print(f"🔧 Upgrade acquistati: {sum(self.upgrade_counts.values())}")
        print(f"📅 Giorni completati: {self.current_game_day - 1}")
        
        print(f"\n{'='*60}")
        print("🎮 PARTITA VINTA!".center(60))
        print("Premi INVIO per uscire...".center(60))
        print(f"{'='*60}")
        
        self.safe_save()
        
        if not self.gui_mode:
            input()  
                  
    def show_shop_menu(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Menu acquisto degli ingredienti per modalità console.
        In particolare, mostra saldo, lista ingredienti con stock e costo, permette acquisto con formato "numero quantità",
        supporta comando "auto" per rifornimento automatico e "esci" per uscire.
        '''
        print("\n" + "=" * 60)
        print("🛒 SHOP INGREDIENTI".center(60))
        print("=" * 60)

        def build_items():
            items = []
            categories = ["hamburger", "topping", "bread", "sauces", "secret"]

            for category in categories:
                for name, data in self.inventory.data.get("ingredients", {}).get(category, {}).items():
                    if not isinstance(data, dict):
                        continue

                    items.append({
                        "path": f"{category}.{name}",
                        "display": data.get("display_name", name.replace("_", " ").title()),
                        "cost": data.get("current_cost", data.get("base_cost", 0.0)),
                        "qty": data.get("current_quantity", 0)
                    })
            return items

        while True:
            balance = self.finance.get_balance()
            all_items = build_items()

            print(f"\n💰 Saldo: €{balance:.2f}")
            print("-" * 60)

            for i, item in enumerate(all_items, 1):
                status = "🔴" if item["qty"] <= 0 else "🟡" if item["qty"] <= 5 else "🟢"
                print(f"{i:3d}. {status} {item['display']:<25} €{item['cost']:5.2f}  (Stock: {item['qty']})")

            print("\nComandi:")
            print("  numero quantità   → acquista")
            print("  auto              → rifornimento automatico")
            print("  esci              → torna al gioco")

            cmd = input("\nAcquista > ").strip().lower()

            if cmd == "esci":
                print("Uscita dallo shop.")
                break

            if cmd == "auto":
                budget = min(200, balance)
                success, msg, cost = self.inventory.auto_restock_low_items(budget)
                if success:
                    self.finance.subtract_money(cost, "Rifornimento automatico")
                    print(f"✅ {msg}")
                continue

            parts = cmd.split()
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                print("❌ Formato non valido. Usa: numero quantità")
                continue

            index = int(parts[0]) - 1
            qty = int(parts[1])

            if qty <= 0:
                print("❌ La quantità deve essere > 0")
                continue

            if index < 0 or index >= len(all_items):
                print("❌ Numero ingrediente non valido")
                continue

            item = all_items[index]
            total_cost = item["cost"] * qty

            if balance < total_cost:
                print(f"❌ Fondi insufficienti (€{total_cost:.2f})")
                continue

            category, name = item["path"].split(".")
            self.inventory.data["ingredients"][category][name]["current_quantity"] += qty
            self.finance.subtract_money(total_cost, f"Acquisto {item['display']} x{qty}")

            print(f"✅ Acquistati {qty} x {item['display']} per €{total_cost:.2f}")
                    
    def force_reset_ending_day(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Forza il reset del flag _ending_day.
        '''
        self._ending_day = False


    def show_help(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Mostra i comandi disponibili in modalità console.
        '''
        print("\n" + "="*50)
        print("🎮 COMANDI")
        print("="*50)
        print("INVIO (Enter) → Avanza di un'ora")
        print("U → Menu upgrade")
        print("S → Shop ingredienti")  
        print("I → Inventario dettagliato")  
        print("Q → Salva ed esci")
        print("="*50)
        print(f"💰 Saldo: €{self.finance.get_balance():.2f}")
        print(f"⭐ Reputazione: {self.reputation:.1f}/100")
        print(f"📅 Giorno: {self.current_game_day}/{self.max_days}")
        print(f"🕐 Ora: {self.current_hour:02d}:00")
        print(f"👨‍🍳 Capacità cucina: {self.kitchen_capacity} panini/ora")
        print("="*50)

    def run(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe GameEngine e ha tipo di ritorno None.
        Loop principale del gioco in modalità console.
        In particolare: mostra menu iniziale , avvia partita, cicla avanzando ora con input utente,
        gestisce comandi, cattura interruzioni e salva sempre alla fine.
        '''
        print("\n" + "="*60)
        print("FANTABURGER DELIVERY TYCOON v6.7".center(60))
        print("="*60)

        while True:
            print("\n1. Nuova partita")
            print("2. Carica partita")
            print("3. Esci")

            try:
                choice = input("\nScelta: ").strip()
                if choice == "1":
                    self.start_new_game()
                    break
                elif choice == "2":
                    if self.load_game():
                        break
                elif choice == "3":
                    print("Arrivederci!")
                    return
            except KeyboardInterrupt:
                print("\nArrivederci!")
                return

        self.running = True

        self.show_help()
        print("\n🎯 Gestisci il ristorante per 7 giorni!")
        print("\nPremi INVIO per iniziare...")

        while self.running and not self.game_over:
            try:
                cmd = input("\n>>> ").strip().lower()

                if cmd == "":
                    self.advance_hour()
                elif cmd == "q":
                    print("\n💾 Salvataggio...")
                    self.safe_save()
                    self.running = False
                elif cmd == "u":
                    self.show_upgrade_menu()
                elif cmd == "help":
                    self.show_help()
                elif cmd == "s":  
                    self.show_shop_menu()
                elif cmd == "i":  
                    self.show_detailed_inventory()
                else:
                    print("Comando non valido (INVIO=avanza, U=upgrade, Q=esci)")

            except KeyboardInterrupt:
                print("\n\n💾 Salvataggio...")
                self.safe_save()
                break
            except Exception as e:
                print(f"Errore: {e}")

        print("\n" + "="*60)
        print("Grazie per aver giocato! 🍔".center(60))
        print("="*60)


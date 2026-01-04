import json #importazione del modulo standard Python necessario per leggere, scrivere e manipolare dati in formato JSON (usato per caricare o salvare l'inventario da ingredients.json)
import threading #importazione del modulo necessario per gestire threading e concorrenza: fornisce Lock() per rendere thread-safe 
from typing import Dict, Any, Optional, List, Tuple #importazione di tipi avanzati per supportare controlli statici e rendere il codice più leggibile
'''
Tipi importati:
Dict corrisponde ad un dizionario (struttura dati formata da una coppia chiave: valore)
Any corrisponde ad un tipo generico (cioè accetta qualsiasi valore)
Optional corrisponde ad un  valore che può essere None
Tuple corrisponde ad una tupla 
List corrisponde ad una lista
'''
from datetime import datetime
'''
Importa la classe datetime dal modulo datetime che è usata per generare timestamp (salvataggi, scadenze tasse, costi giornalieri), 
'''
import os # importazione del modulo necessario per effettuare operazioni sul sistema operativo. Utilizzato per verificare l'esistenza del file di salvataggio (os.path.exists) prima di tentare il caricamento.

class Finance:
    def __init__(self, initial_balance: float = 500.0, config_file: str = 'data/config.json', save_file: str = 'data/savestate.json', load_saved: bool = False):
        '''
        Come parametri riceve esplicitamente initial_balance (float, con 500.0 come valore di default), config_file (stringa, con 'data/config.json' come valore di default), 
        save_file (stringa, con 'data/savestate.json' valore di default) e load_saved (bool, con False come valore di default), oltre a ricevere implicitamente l'istanza della classe Finance (self).
        Costruttore della classe Finance che inizializza le strutture dati principali:
        config_file e save_file: percorsi dei file di configurazione e salvataggio, lock: threading.Lock() per garantire thread-safety nelle operazioni finanziarie, config: 
        carica la configurazione dal file JSON tramite load_config(), state: se load_saved=True carica lo stato salvato, altrimenti crea un nuovo stato con _create_new_state(),
        transactions e daily_transactions: liste e dizionari per registrare le transazioni, game_engine: riferimento opzionale al GameEngine e stats: dizionario con statistiche globali (profitti, perdite, record)     
        Inoltre, chiama _setup_daily_costs() per inizializzare i costi giornalieri fissi e il moltiplicatore di profitto in base alla difficoltà.
        '''
        self.config_file = config_file
        self.save_file = save_file
        self.lock = threading.Lock()
        self.config = self.load_config()
        if load_saved:
            self.state = self.load_or_create_state(initial_balance)
        else:
            self.state = self._create_new_state(initial_balance)
            print(f"✅ Nuovo stato finanziario creato (saldo iniziale: €{initial_balance:.2f})")
        self.transactions: List[Dict] = []
        self.daily_transactions: Dict[str, List] = {}
        self.game_engine = None
        self._setup_daily_costs()
        
        self.stats = {
            'total_profit': 0.0,
            'total_expenses': 0.0,
            'total_revenue': 0.0,
            'days_in_business': 0,
            'best_day_profit': 0.0,
            'worst_day_loss': 0.0,
            'last_updated': datetime.now().isoformat()
        }
        
    def get_current_game_day(self) -> int:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Finance e ha come tipo di ritorno int.
        Restituisce il giorno di gioco corrente.
        In particolare, se è collegato al GameEngine (self.game_engine non None), restituisce current_game_day da lì;
        altrimenti restituisce il valore di days_in_operation salvato nello stato.
        '''
        if self.game_engine and hasattr(self.game_engine, 'current_game_day'):
            return self.game_engine.current_game_day
        return self.state.get('days_in_operation', 0)
        
    def load_config(self) -> Dict[str, Any]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno Dict[str, Any].
        Carica la configurazione dal file config.json.
        In particolare, tenta di leggere e parsare il JSON; in caso di FileNotFoundError o JSONDecodeError,
        stampa un messaggio di errore e restituisce una configurazione di default tramite _get_default_config().
        '''
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f'File {self.config_file} non trovato, usando impostazioni di default')
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f'Errore JSON in {self.config_file}: {e}')
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno Dict[str, Any].
        Restituisce una configurazione di default completa (come quella contenuta in config.json) quando il file config.json è mancante o corrotto.
        '''
        return {
            "economy": {
                "initial_balance": 500.0,
                "rent": 20.0,
                "employee_salary": 30.0,
                "utility_price": 20.0
            },
            "gameplay": {
                "max_orders": 10,
                "order_timeout": 100,
                "customer_patience": 50,
                "max_burgers_per_order": 3,
                "starting_difficulty": "easy",
                "unlock": {
                    "new_recipe": 100.0,
                    "new_employee": 50.0,
                    "upgrade_kitchen": 1000.0,
                    "second_location": 5000.0
                }
            },
            "difficulty": {
                "levels": {
                    "easy": {
                        "customer_frequency": 1.0,
                        "order_complexity": 0.7,
                        "profit": 1.0,
                        "event_frequency": 0.8
                    },
                    "normal": {
                        "customer_frequency": 1.3,
                        "order_complexity": 1.0,
                        "profit": 0.9,
                        "event_frequency": 1.3
                    },
                    "hard": {
                        "customer_frequency": 1.7,
                        "order_complexity": 1.6,
                        "profit": 0.7,
                        "event_frequency": 1.6
                    },
                    "ultimate": {
                        "customer_frequency": 2.2,
                        "order_complexity": 2.0,
                        "profit": 0.6,
                        "event_frequency": 1.9
                    },
                    "nightmare": {
                        "customer_frequency": 4.2,
                        "order_complexity": 3.7,
                        "profit": 0.5,
                        "event_frequency": 3.0
                    }   
                }
            }
        }
            
    def load_or_create_state(self, initial_balance: float) -> Dict[str, Any]:
        '''
        Come parametro riceve esplicitamente initial_balance (float) oltre a ricevere implicitamente l'istanza della classe Finance
        e ha tipo di ritorno Dict[str, Any].
        Tenta di caricare lo stato finanziario salvato da savestate.json.
        In particolare, se il file esiste, lo legge e converte eventuali datetime da stringa ISO inizializzando campi mancanti e
        in caso di errore (FileNotFoundError o JSONDecodeError) crea un nuovo stato con _create_new_state().
        '''
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                print(f'Stato caricato correttamente: {self.save_file}')
                
                if 'last_daily_charge' in state:
                    try:
                        state['last_daily_charge'] = datetime.fromisoformat(state['last_daily_charge'])
                    except (ValueError, TypeError):
                        state['last_daily_charge'] = datetime.now()
                
                if 'consecutive_negative_days' not in state:
                    state['consecutive_negative_days'] = 0
                
                return state
            else:
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Errore nel caricamento stato: {e}. Creando nuovo stato... ")
            return self._create_new_state(initial_balance)

    def _create_new_state(self, initial_balance: float) -> Dict[str, Any]:
        '''
        Funzione privata che come parametro riceve esplicitamente initial_balance (float) oltre a ricevere implicitamente l'istanza della classe Finance
        e ha tipo di ritorno Dict[str, Any].
        Crea un nuovo stato finanziario da zero per una nuova partita.
        In particolare, inizializza bilancio, upgrade sbloccati, statistiche giornaliere, contatori giorni e timestamp last_daily_charge.
        '''
        return {
            'balance': initial_balance,
            'unlocked_upgrades': [],
            'daily_stats': {
                'revenue': 0.0,
                'expenses': 0.0,
                'profit': 0.0,
                'orders_completed': 0
            },
            'days_in_operation': 0,
            'last_processed_game_day': 0,
            'consecutive_negative_days': 0,
            'last_daily_charge': datetime.now().isoformat()  
        }
            
    def _setup_daily_costs(self) -> None:
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno None (non restituisce nulla).
        Inizializza i costi giornalieri fissi (affitto, stipendi, utenze, ecc.) prelevandoli dalla configurazione.
        In particolare, crea il dizionario daily_costs, imposta il moltiplicatore di profitto in base alla difficoltà definita nella config (quella di default è "easy").
        '''
        economy_config = self.config.get('economy', {})
        
        self.daily_costs = {
            'rent': economy_config.get('rent', 20.0),
            'employee_salary': economy_config.get('employee_salary', 30.0),
            'utilities': economy_config.get('utility_price', 20.0),
            'tax': economy_config.get('daily_tax', 75.0),
            'insurance':  10.0,
            'waste_disposal': 5.0
        }
        
        difficulty =  self.config.get('gameplay', {}).get('starting_difficulty', 'easy')
        difficulty_settings = self.config.get('difficulty', {}).get('levels', {}).get(difficulty, {})
        self.profit_multiplier = difficulty_settings.get('profit', 1.0)
        
    def get_balance(self) -> float:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno float.
        Restituisce il bilancio corrente arrotondato a 2 decimali.
        In particolare è protetto da lock per thread-safety.
        '''
        with self.lock:
            return round(self.state['balance'], 2)
        
    def add_money(self, amount: float, description: str = 'Deposito') -> Tuple[bool, str]:
        '''
        Come parametro riceve esplicitamente amount (float) e description (stringa, con valore di default 'Deposito') oltre a ricevere implicitamente l'istanza della classe Finance
        e ha tipo di ritorno Tuple[bool, str].
        Aggiunge denaro al bilancio.
        In particolare verifica che amount sia positivo, entra in sezione protetta da lock, aggiorna il bilancio,
        registra la transazione, aggiorna statistiche giornaliere e globali, salva lo stato e restituisce successo con messaggio dettagliato.
        '''
        if amount <= 0:
            return False, "Errore: L'importo deve essere positivo!"
        
        with self.lock:
            old_balance = self.state['balance']
            self.state['balance'] += amount
            
            transaction = {
                'timestamp': datetime.now().isoformat(),
                'type': 'revenue',
                'amount': amount,
                'description':  description,
                'old_balance': old_balance,
                'new_balance': self.state['balance']
            }
            
            self.transactions.append(transaction)
            self.state['daily_stats']['revenue'] += amount
            self.state['daily_stats']['profit'] += amount
            self.stats['total_revenue'] += amount
            self.stats['total_profit'] += amount
            self._save_state()
        return True, f"+{amount:.2f}: {description}. Nuovo saldo: {self.state['balance']:.2f}"
    
    def subtract_money(self, amount: float, description: str = 'Pagamento') -> Tuple[bool, str]:
        '''
        Come parametro riceve esplicitamente amount (float) e description (stringa, con valore di default 'Pagamento') oltre a ricevere implicitamente l'istanza della classe Finance
        e ha tipo di ritorno Tuple[bool, str].
        Sottrae denaro dal bilancio.
        In particolare verifica che amount sia positivo e che ci siano fondi sufficienti, entra in sezione protetta da lock,
        aggiorna il bilancio, registra la transazione, aggiorna statistiche giornaliere e globali, salva lo stato e restituisce successo con messaggio dettagliato.
        '''
        if amount <= 0:
            return False, "Errore: L'importo deve essere positivo!"
        
        with self.lock:
            if self.state['balance'] < amount:
                return False, f"Errore: Fondi insufficienti. Richiesto: {amount:.2f}, Disponibile: {self.state['balance']:.2f}"
            
            old_balance = self.state['balance']
            self.state['balance'] -= amount         

            transaction = {
                'timestamp': datetime.now().isoformat(),
                'type': 'expense',
                'amount': amount,
                'description':  description,
                'old_balance': old_balance,
                'new_balance': self.state['balance']
            }
            
            self.transactions.append(transaction)
            self.state['daily_stats']['expenses'] += amount
            self.state['daily_stats']['profit'] -= amount
            self.stats['total_expenses'] += amount
            self.stats['total_profit'] -= amount
            
            self._save_state()
        return True, f"-{amount:.2f}: {description}. Nuovo saldo: {self.state['balance']:.2f}"
    
    def buy_ingredient(self, cost_total: float, name: str, qty: int):
        '''
        Come parametro riceve esplicitamente cost_total (float), name (str) e qty (int) oltre a ricevere implicitamente l'istanza della classe Finance.
        Sottrae il costo totale per l'acquisto di ingredienti chiamando subtract_money ed è utilizzato nell'acquisto degli ingredienti nello shop.
        '''
        success, _ = self.subtract_money(cost_total, f"Buy {name} x{qty}")
        return success

    
    def process_sale(self, recipe_price: float, ingredient_cost: float, recipe_name: str = "Vendita") -> Tuple[bool, str, Dict]:
        '''
        Come parametro riceve esplicitamente recipe_price (float), ingredient_cost (float) e recipe_name (stringa, valore di default "Vendita") oltre a ricevere implicitamente l'istanza della classe Finance
        e ha tipo di ritorno Tuple[bool, str, Dict].
        Gestisce la vendita di una ricetta calcolando profitto lordo e netto.
        In particolare applica il moltiplicatore di profitto della difficoltà, aggiunge o sottrae denaro in base al profitto netto e
        restituisce successo, messaggio e dettagli (ovvero profitti, margini, ecc...).
        '''
        if recipe_price < 0 or ingredient_cost < 0:
            return False, "Errore: Prezzo o costo non validi", {}
        
        gross_profit = recipe_price - ingredient_cost
        
        adjusted_revenue = recipe_price * self.profit_multiplier
        net_profit = adjusted_revenue - ingredient_cost
        
        if net_profit >= 0:
            success, msg = self.add_money(net_profit, f"Vendita: {recipe_name}")
        else:
            success, msg = self.subtract_money(abs(net_profit), f"Perdita: {recipe_name}")
        
        if success:
            details = {
                'gross_profit': round(gross_profit, 2),
                'net_profit': round(net_profit, 2),
                'profit_multiplier': self.profit_multiplier,
                'adjusted_revenue': round(adjusted_revenue, 2),
                'ingredient_cost': round(ingredient_cost, 2),
                'is_profitable': net_profit >= 0
            }
            return True, msg, details
        else:
            return False, msg, {}
        
    def apply_daily_costs(self) -> Tuple[bool, str, Dict]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno Tuple[bool, str, Dict].
        Applica i costi giornalieri fissi per i giorni trascorsi dall'ultimo processamento.
        In particolare, nella sezione protetta da lock calcola i giorni passati, verifica fondi per costi critici (affitto, utenze), applica tutti i costi possibili,
        gestisce fallimento se fondi insufficienti per critici, aggiorna statistiche e salva lo stato.
        Restituisce successo, messaggio e dettagli (cioè costi applicati, giorni passati, ecc...).
        '''
        with self.lock:
            total_daily_cost = sum(self.daily_costs.values())

            
            current_game_day = self.get_current_game_day()
            last_processed_day = self.state.get('last_processed_game_day', 0)
            days_passed = current_game_day - last_processed_day
            
            if days_passed <= 0:
                return True, "Costi giornalieri già applicati", {'total_cost': 0.0}
            
            total_cost_for_period = total_daily_cost * days_passed
            
            balance = self.state['balance']
            
            critical_costs = {'rent', 'utilities'}
            critical_total_per_day = sum(
                cost for name, cost in self.daily_costs.items() 
                if name in critical_costs
            )
            critical_total_for_period = critical_total_per_day * days_passed
            
            if balance < critical_total_for_period:
                self.state['game_over'] = True
                self.state['bankruptcy_day'] = current_game_day
                self.state['bankruptcy_reason'] = "Fondi insufficienti per costi critici"
                self._save_state()
                
                return False, f"FALLIMENTO: Ristorante fallito! Fondi insufficienti per i costi critici!", {
                    'total_cost': 0.0,
                    'days_passed': days_passed,
                    'cost_breakdown': {},
                    'failed_costs': list(critical_costs),
                    'game_over': True,
                    'bankruptcy': True
                }
            
            cost_details = {}
            total_cost = 0.0
            failed_costs = []
            
            for cost_name in critical_costs:
                if cost_name in self.daily_costs:
                    amount = self.daily_costs[cost_name] * days_passed
                    if balance >= amount:
                        self.state['balance'] -= amount
                        cost_details[cost_name] = amount
                        total_cost += amount
                        balance = self.state['balance']
                    else:
                        failed_costs.append(cost_name)
            
            for cost_name, daily_amount in self.daily_costs.items():
                if cost_name in critical_costs:
                    continue  
                    
                amount = daily_amount * days_passed
                if balance >= amount:
                    self.state['balance'] -= amount
                    cost_details[cost_name] = cost_details.get(cost_name, 0) + amount
                    total_cost += amount
                    balance = self.state['balance']
                else:
                    failed_costs.append(cost_name)
            
            self.state['daily_stats']['expenses'] += total_cost
            self.state['daily_stats']['profit'] -= total_cost
            self.stats['total_expenses'] += total_cost
            self.stats['total_profit'] -= total_cost
            
            self.state['days_in_operation'] += days_passed
            self.state['last_processed_game_day'] = current_game_day
            self.stats['days_in_business'] = self.state['days_in_operation']
            
            daily_profit = self.state['daily_stats']['profit']
            if daily_profit > self.stats['best_day_profit']:
                self.stats['best_day_profit'] = daily_profit
            if daily_profit < self.stats['worst_day_loss']:
                self.stats['worst_day_loss'] = daily_profit
            
            self.state['daily_stats'] = {
                'revenue': 0.0,
                'expenses': 0.0,
                'profit': 0.0,
                'orders_completed': 0
            }
            
            self._save_state()
            
            if failed_costs:
                message = f"⚠️ Fondi insufficienti per: {', '.join(failed_costs)}"
                success = False
            else:
                if days_passed == 1:
                    message = f"Costi giornalieri applicati: {total_cost:.2f}€"
                else:
                    message = f"Costi giornalieri applicati per {days_passed} giorni: {total_cost:.2f}€"
                success = True
            
            details = {
                'total_cost': total_cost,
                'days_passed': days_passed,
                'cost_breakdown': cost_details,
                'failed_costs': failed_costs,
                'new_balance': self.state['balance'],
                'day_number': self.state['days_in_operation']
            }
            
            return success, message, details
        
    def get_financial_report(self, period: str = 'daily') -> Dict[str, Any]:
        '''
        Come parametro riceve esplicitamente period (stringa, con valore di default 'daily') oltre all'istanza della classe Finance (self implicito)
        e ha tipo di ritorno Dict[str, Any].
        Genera un report finanziario completo.
        In particolare include bilancio corrente, giorni attività, statistiche giornaliere, metriche (margine profitto, valore medio ordine),
        statistiche globali e proiezioni (profitto medio giornaliero e settimanale).
        '''
        with self.lock:
            report = {
                'period': period,
                'generated_at': datetime.now().isoformat(),
                'current_balance': self.state['balance'],
                'days_in_operation': self.state['days_in_operation'],
                'daily_stats': self.state['daily_stats'].copy()
            }
            
            if self.state['daily_stats']['revenue'] > 0:
                profit_margin = (self.state['daily_stats']['profit'] / 
                                self.state['daily_stats']['revenue'] * 100)
            else:
                profit_margin = 0.0
            
            report['metrics'] = {
                'profit_margin_percent': round(profit_margin, 1),
                'avg_order_value': round(
                    self.state['daily_stats']['revenue'] / 
                    max(self.state['daily_stats']['orders_completed'], 1), 2
                ),
                'break_even_point': round(sum(self.daily_costs.values()) / max(profit_margin/100, 0.01), 2)
            }
            
            report['global_stats'] = {
                'total_revenue': self.stats['total_revenue'],
                'total_expenses': self.stats['total_expenses'],
                'total_profit': self.stats['total_profit'],
                'best_day_profit': self.stats['best_day_profit'],
                'worst_day_loss': self.stats['worst_day_loss']
            }
            
            if self.state['days_in_operation'] > 0:
                avg_daily_profit = self.stats['total_profit'] / self.state['days_in_operation']
                report['projections'] = {
                    'avg_daily_profit': round(avg_daily_profit, 2),
                    'weekly_projection': round(avg_daily_profit * 7, 2)
                }
            
            return report
    
    def get_unlocked_upgrades(self) -> List[str]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno List[str].
        Restituisce una copia della lista di upgrade sbloccati.
        '''
        return self.state['unlocked_upgrades'].copy()
    
    def _save_state(self) -> None:
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe Finance e ha tipo di ritorno None (non restituisce nulla).
        Salva lo stato finanziario su disco in savestate.json.
        In particolare converte eventuali datetime in stringa ISO, crea un dizionario con tutti i campi necessari,
        scrive il JSON con indentazione e aggiorna il timestamp delle statistiche e in caso di errore stampa il messaggio.
        '''
        try:
            last_daily = self.state.get('last_daily_charge')
            last_daily_str = last_daily.isoformat() if isinstance(last_daily, datetime) else last_daily

            save_state = {
                'balance': self.state.get('balance', 0.0),
                'unlocked_upgrades': self.state.get('unlocked_upgrades', []),
                'daily_stats': self.state.get('daily_stats', {
                    'revenue': 0.0,
                    'expenses': 0.0,
                    'profit': 0.0,
                    'orders_completed': 0
                }),
                'days_in_operation': self.state.get('days_in_operation', 0),
                'last_processed_game_day': self.state.get('last_processed_game_day', 0),
                'consecutive_negative_days': self.state.get('consecutive_negative_days', 0),
                'game_over': self.state.get('game_over', False),
                'bankruptcy_day': self.state.get('bankruptcy_day'),
                'bankruptcy_reason': self.state.get('bankruptcy_reason'),
                'last_daily_charge': last_daily_str  
            }

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_state, f, indent=2, ensure_ascii=False)

            self.stats['last_updated'] = datetime.now().isoformat()

        except Exception as e:
            print(f"Errore nel salvataggio stato finanziario: {e}")
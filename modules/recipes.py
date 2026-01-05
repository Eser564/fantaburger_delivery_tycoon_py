import json #importazione del modulo standard Python necessario per leggere, scrivere e manipolare dati in formato JSON (usato per caricare le ricette da recipes.json e la configurazione da config.json)
import threading #importazione del modulo necessario per gestire threading e concorrenza: fornisce Lock() per rendere thread-safe le operazioni sulle ricette
from typing import Optional, Any, List, Tuple, Dict #importazione di tipi avanzati per supportare controlli statici e rendere il codice più leggibile
'''
Tipi importati:
Optional corrisponde ad un valore che può essere None
Any corrisponde ad un tipo generico (cioè accetta qualsiasi valore)
List corrisponde ad una lista
Tuple corrisponde ad una tupla
Dict corrisponde ad un dizionario (struttura dati formata da una coppia chiave: valore)
'''
from datetime import datetime #classe datetime importata dal modulo datetime usata per salvare timestamp dell'ultimo aggiornamento delle statistiche ricette
from .inventory import Inventory #importazione della classe Inventory dal modulo locale per collegare la gestione ricette all'inventario reale (

class Recipe:
    def __init__(self, recipes_file: str = 'data/recipes.json', inventory: Optional[Inventory] = None, config_file: str = 'data/config.json'):
        '''
        Come parametro riceve esplicitamente recipes_file (stringa, con valore di default 'data/recipes.json'), inventory (Optional[Inventory], con None come valore di default) 
        e config_file (stringa, con 'data/config.json' come valore di default), oltre a ricevere implicitamente l'istanza della classe Recipe (self).
        Costruttore della classe Recipe che si occupa di inizializzare le strutture dati principali:
        In particolare, recipes_file e config_file: percorsi dei file JSON delle ricette e della configurazione, lock: threading.Lock() per garantire thread-safety, 
        inventory: riferimento all'istanza Inventory, recipes: carica le ricette dal file tramite load_recipes(), config: carica la configurazione tramite load_config(),
        recipe_cache e price_cache: cache per accesso rapido a ricette e costi, stats: dizionario con statistiche globali (preparazioni, incassi, ecc...)
        Alla fine chiama _build_cache() per costruire la cache delle ricette.
        '''
        self.recipes_file = recipes_file
        self.config_file = config_file
        self.lock = threading.Lock()
        self.inventory = inventory
        self.recipes = self.load_recipes()
        self.config = self.load_config()
        self.recipe_cache = {} 
        self.price_cache = {}
        self.stats = {
            'total_recipes': 0,
            'total_preparations': 0,
            'total_revenue': 0.0,
            'most_popular_recipe': None,
            'last_updated': datetime.now().isoformat()
        }
        self._build_cache()
        
    def load_recipes(self):
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Recipe.
        Carica le ricette dal file recipes.json.
        In particolare tenta di leggere e parsare il JSON in modalità lettura ('r') verificando che il contenuto sia un dizionario valido; in caso contrario stampa errore.
        In caso di eccezione (FileNotFoundError, JSONDecodeError, ecc...) stampa errore e restituisce dizionario vuoto.
        '''
        try:
            with open(self.recipes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("recipes.json non contiene un dict valido")
            print(f'Ricette caricate da {self.recipes_file}')
            return data
        except Exception as e:
            print(f'❌ ERRORE lettura ricette: {e}')
            return {}

            
    def load_config(self) -> Dict[str, Any]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Recipe.
        Carica la configurazione dal file config.json.
        In particolare tenta di leggere e parsare il JSON in modalità lettura ('r') ; in caso contrario stampa errore.
        In caso di eccezione (FileNotFoundError, JSONDecodeError, ecc...) stampa errore e utilizza una configurazione predefinita semplice.
        '''
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f'File {self.config_file} non trovato! Perciò sarà utilizzata una configurazione predefinita')
            return {'gameplay': {'max_burgers_per_order': 3}, 'difficulty': {'levels': {'easy': {'profit': 1.0}}}}
        except json.JSONDecodeError as e:
            print(f'Errore JSON in {self.config_file}: {e}')
            return {}
            
    def _build_cache(self) -> None:
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe Recipe e ha tipo di ritorno None (non restituisce nulla).
        Costruisce la cache delle ricette per accesso rapido.
        In particolare rimuove il contenuto precedente di recipe_cache e price_cache, verifica che self.recipes sia un dizionario valido e
        per ogni ricetta verifica che sia un dict e contenga 'name', aggiunge 'id' (la chiave esterna) ecopia i dati arricchiti in recipe_cache.
        Infinte, stampa il numero di ricette caricate con successo.
        '''
        self.recipe_cache.clear()
        self.price_cache.clear()

        if not isinstance(self.recipes, dict):
            print("❌ ERRORE: recipes.json non è un dict valido.")
            return

        for recipe_id, recipe_data in self.recipes.items():
            if not isinstance(recipe_data, dict):
                print(f"❌ Ricetta '{recipe_id}' non è un dict – ignorata")
                continue

            if 'name' not in recipe_data:
                print(f"❌ Ricetta '{recipe_id}' manca 'name' – ignorata")
                continue

            enriched = recipe_data.copy()
            enriched['id'] = recipe_id
            self.recipe_cache[recipe_id] = enriched

        print(f"✅ {len(self.recipe_cache)} ricette caricate in cache")
        
    def get_recipe(self, recipe_id: str) -> Optional[Dict]:
        '''
        Come parametro riceve esplicitamente l'id della ricetta (stringa) oltre all'istanza della classe Recipe (self implicito)
        e ha tipo di ritorno Optional[Dict].
        Restituisce i dati completi di una ricetta dato il suo id.
        In particolare cerca nella recipe_cache, verifica che il risultato sia un dict valido e in caso di cache corrotta ricostruisce la cache al volo e riprova.
        Restituisce None se non trovata o problema critico.
        '''
        if not isinstance(recipe_id, str) or not recipe_id:
            return None
        
        recipe = self.recipe_cache.get(recipe_id)
        
        if not isinstance(recipe, dict):
            print(f"Errore critico: cache corrotta per {recipe_id} – tipo: {type(recipe)}")
            self._build_cache()
            recipe = self.recipe_cache.get(recipe_id)
            if not isinstance(recipe, dict):
                return None
        
        return recipe
    
    def get_all_recipes(self) -> Dict[str, Dict]:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Recipe e ha tipo di ritorno Dict[str, Dict].
        Restituisce una copia completa di tutte le ricette presenti nella cache.
        '''
        return self.recipe_cache.copy()

    
    def can_prepare_recipe(self, recipe_id: str) -> Tuple[bool, str]:
        '''
        Come parametro riceve esplicitamente l'id della ricetta (stringa) oltre a ricevere implicitamente l'istanza della classe Recipe
        e ha tipo di ritorno Tuple[bool, str].
        Verifica se una ricetta è preparabile con gli ingredienti attualmente disponibili.
        In particolare se inventory è collegato usa inventory.check_availability(),
        altrimenti implementa un fallback manuale verificando quantità con get_ingredient_quantity().
        Restituisce True o False accompagnato da messaggio dettagliato.
        '''
        if not self.inventory:
            return False, 'Errore: Inventario non impostato!'
        
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return False, f'Ricetta {recipe_id} non trovata'
        ingredients = recipe.get('ingredients', {})
        
        if hasattr(self.inventory, 'check_availability'):
            return self.inventory.check_availability(ingredients)
        else:
            missing = []
            insufficient = []
            
            for ingredient_path, needed_quantity in ingredients.items():
                if hasattr(self.inventory, 'get_ingredient_quantity'):
                    available_quantity = self.inventory.get_ingredient_quantity(ingredient_path)
                    if available_quantity < needed_quantity:
                        insufficient.append(f'{ingredient_path} necessita di {needed_quantity}, attualmente disponibile {available_quantity}')
                else:
                    missing.append(ingredient_path)
            
            if missing or insufficient:
                error_message = ""
                if missing:
                    error_message += f"Ingredienti non trovati: {', '.join(missing)}\n"
                if insufficient:
                    error_message += f"Ingredienti insufficienti: {', '.join(insufficient)}"
                return False, error_message
            
            return True, 'Ricetta preparabile!'
        
    def calculate_recipe_cost(self, recipe_id: str) -> float:
        '''
        Come parametro riceve esplicitamente l'id della ricetta (stringa) oltre a ricevere implicitamente l'istanza della classe Recipe
        e ha tipo di ritorno float.
        Calcola il costo totale degli ingredienti per una ricetta.
        In particolare usa price_cache se disponibile, altrimenti calcola sommando (quantità × costo unitario) per ogni ingrediente.
        Se inventory collegato usa get_ingredient_cost(), altrimenti fallback con costi fissi predefiniti.
        Arrotonda a 2 decimali e salva in cache.
        '''
        if recipe_id in self.price_cache:
            return self.price_cache[recipe_id]
        
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return 0.0
        
        total_cost = 0.0
        ingredients = recipe.get('ingredients', {})
        
        if self.inventory and hasattr(self.inventory, 'get_ingredient_cost'):
            for ingredient_path, needed_quantity in ingredients.items():
                unit_cost = self.inventory.get_ingredient_cost(ingredient_path)
                total_cost += unit_cost * needed_quantity
        else:
            default_costs = {
                'hamburger': 1.5,
                'cheese': 0.8,
                'bread': 0.5,
                'lettuce': 0.3,
                'tomato': 0.4,
                'sauce': 0.1,
                'secret': 5.0  
            }
            for ingredient_path, needed_quantity in ingredients.items():
                base_cost = 0.1
                ingredient_name = ingredient_path.split('.')[-1].lower()
                
                for key, cost in default_costs.items():
                    if key in ingredient_name:
                        base_cost = cost
                        break
                
                total_cost += base_cost * needed_quantity
        
        total_cost = round(total_cost, 2)
        self.price_cache[recipe_id] = total_cost
        return total_cost
            
    def prepare_recipe(self, recipe_id: str, quantity: int = 1) -> Tuple[bool, str, Dict]:
        '''
        Come parametro riceve esplicitamente l'id della ricetta (str) e la quantità (int, default 1) oltre all'istanza della classe Recipe (self implicito)
        e ha tipo di ritorno Tuple[bool, str, Dict].
        Prepara una ricetta consumando gli ingredienti necessari.
        In particolare verifica l'inventaario, se ha quantità positiva, se la ricetta esiste, la disponibilità degli ingredienti (scalati per quantità).
        Consuma manualmente gli ingredienti, calcola costi, prezzi e profitti, aggiorna statistiche come preparazione, incassi e ricetta più popolare.
        Restituisce successo, messaggio e dettagli preparazione.
        '''
        if not self.inventory:
            return False, 'Inventario non impostato!', {}

        if quantity <= 0:
            return False, 'La quantità deve essere positiva', {}

        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return False, f'Errore: Ricetta {recipe_id} non trovata', {}

        ingredients = recipe.get('ingredients', {})
        scaled_ingredients = {k: v * quantity for k, v in ingredients.items()}

        can_prepare, message = self.inventory.check_availability(scaled_ingredients)
        if not can_prepare:
            return False, message, {}

        try:
            for path, qty in scaled_ingredients.items():
                current = self.inventory.get_ingredient_quantity(path)
                if current < qty:
                    return False, f'Ingredienti insufficienti per {path}', {}
                self.inventory.data["ingredients"][path.split('.')[0]][path.split('.')[1]]['current_quantity'] -= qty
        except Exception as e:
            return False, f"Errore consumo: {e}", {}

        cost_per_unit = recipe.get('cost', 0.0)
        price_per_unit = recipe.get('price', 0.0)
        total_cost = cost_per_unit * quantity
        total_price = price_per_unit * quantity
        profit = total_price - total_cost

        self.stats['total_preparations'] += quantity
        self.stats['total_revenue'] += total_price
        self.stats['last_updated'] = datetime.now().isoformat()

        if not hasattr(self, 'recipe_counts'):
            self.recipe_counts = {}

        self.recipe_counts[recipe_id] = self.recipe_counts.get(recipe_id, 0) + quantity

        if (not self.stats.get('most_popular_recipe') or 
            self.recipe_counts.get(recipe_id, 0) > self.recipe_counts.get(self.stats['most_popular_recipe'], 0)):
            self.stats['most_popular_recipe'] = recipe_id

        details = {
            'recipe_id': recipe_id,
            'recipe_name': recipe.get('name', recipe_id),
            'quantity': quantity,
            'total_cost': round(total_cost, 2),
            'total_price': round(total_price, 2),
            'total_profit': round(profit, 2),
            'profit_per_unit': round(profit / quantity, 2) if quantity > 0 else 0.0
        }

        return True, f"Preparati {quantity}x {recipe.get('name', recipe_id)}", details
    
    def get_secret_recipes(self) -> list:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Recipe e ha tipo di ritorno list.
        Restituisce la lista degli id delle ricette segrete.
        In particolare una ricetta è segreta se almeno uno dei suoi ingredienti ha percorso che inizia con "secret.".
        '''
        secrets = []
        for recipe_id, data in self.recipe_cache.items():
            ingredients = data.get("ingredients", {})
            if any(key.startswith("secret.") for key in ingredients.keys()):
                secrets.append(recipe_id)
        return secrets

    def get_recipe_profitability(self, recipe_id: str) -> Optional[Dict]:
        '''
        Come parametro riceve esplicitamente l'id della ricetta (str) oltre a ricevere implicitamente l'istanza della classe Recipe
        e ha tipo di ritorno Optional[Dict].
        Calcola la redditività di una singola ricetta.
        In particolare recupera ricetta, calcola costo ingredienti, prezzo vendita, profitto e margine percentuale e
        restituisce None se ricetta non trovata, altrimenti dizionario con tutti i dettagli.
        '''
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None
        
        cost = self.calculate_recipe_cost(recipe_id)
        price = recipe.get('price', 0.0)
        profit = price - cost
        margin = (profit / price * 100) if price > 0 else 0
        
        return {
            'recipe_id': recipe_id,
            'recipe_name': recipe.get('name', recipe_id),
            'ingredient_cost': cost,
            'selling_price': price,
            'profit': profit,
            'profit_margin_percent': round(margin, 1),
            'is_profitable': profit > 0,
            'ingredients_count': len(recipe.get('ingredients', {})),
            'preparation_time': recipe.get('preparation_time', 5.0)
        }
        
    def get_all_profitable_recipes(self, min_margin: float = 10.0) -> List[Dict]:
        '''
        Come parametro riceve esplicitamente min_margin (float, default 10.0) oltre a ricevere implicitamente l'istanza della classe Recipe
        e ha tipo di ritorno List[Dict].
        Restituisce la lista di tutte le ricette redditizie (profitto > 0 e margine ≥ min_margin) e
        in particolare analizza ogni ricetta con get_recipe_profitability() e ordina per margine decrescente.
        '''
        profitable = []
        
        for recipe_id in self.recipe_cache.keys():
            analysis = self.get_recipe_profitability(recipe_id)
            if analysis and analysis['is_profitable'] and analysis['profit_margin_percent'] >= min_margin:
                profitable.append(analysis)
        return sorted(profitable, key=lambda x: x['profit_margin_percent'], reverse=True)

    def is_producible(self, recipe_id: str) -> bool:
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return False

        for ing, qty in recipe["ingredients"].items():
            if self.inventory.get_quantity(ing) < qty:
                return False
        return True

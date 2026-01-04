import json #importazione del modulo standard Python necessario per leggere, scrivere e manipolare dati in formato JSON (usato per caricare o salvare l'inventario da ingredients.json)
import threading #importazione del modulo necessario per gestire threading e concorrenza: fornisce Lock() per rendere thread-safe le operazioni sull'inventario
from typing import Dict, Any, Optional, Tuple, List #importazione di tipi avanzati per supportare controlli statici e rendere il codice più leggibile
'''
Tipi importati:
Dict corrisponde ad un dizionario (struttura dati formata da una coppia chiave: valore)
Any corrisponde ad un tipo generico (cioè accetta qualsiasi valore)
Optional corrisponde ad un  valore che può essere None
Tuple corrisponde ad una tupla 
List corrisponde ad una lista
'''
from datetime import datetime # Classe datetime importata dal modulo datetime usata per salvare timestamp dell' ultimo salvataggio o aggiornamento 

class Inventory:
    def __init__(self, ingredients_file: str = 'data/ingredients.json', load_saved: bool = False):
        '''
        Come parametro riceve esplicitamente il file JSON su cui sono salvati gli ingredienti (stringa, con default 'data/ingredients.json') 
        e load_saved (bool, con False come valore di default), oltre a ricevere implicitamente l'stanza della classe Inventory (self).
        Costruttore della classe Inventory che si occupa di inizializzare le strutture dati principali:
        In particolare: ingredients_file: percorso del file JSON, data: dizionario che conterrà la struttura completa dell'inventario, flat_cache: cache piatta per 
        accesso rapido per nome, lock: threading.Lock() per garantire thread-safety, last_save_time: timestamp dell'ultimo salvataggio e stats: dizionario con statistiche 
        riassuntive (cioè totale ingredienti, valore, ultimo aggiornamento)        
        Infine, in base al valore di load_saved: se True: chiama load_data() (carica i dati salvati dalla partita precedente), invece
        se False: chiama load_default_data() (carica i valori di default e resetta le quantità)  
        Alla fine costruisce la cache piatta chiamando build_flat_cache().
        '''
        self.ingredients_file = ingredients_file
        self.data: Dict[str, Any] = {}
        self.flat_cache: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self.last_save_time = datetime.now()
        
        self.stats = {
            'total_ingredients': 0,
            'total_value': 0.0,
            'last_updated': datetime.now().isoformat()
        }
        
        if load_saved:
            self.load_data()
        else:
            self.load_default_data()
            
        self.build_flat_cache()
        
    def load_default_data(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Inventory e ha tipo di ritorno None (non restituisce nulla).
        Carica i dati dal file ingredients.json.
        In particolare: legge il JSON ('r') caricandone la struttura in self.data,
        se in self.data manca la chiave ingredients ne viene creata una vuota.
        Inoltre, resetta tutte le quantità ai valori iniziali solo agli ingredienti che
        dispongono di initial_quantity e i
        costi a base_cost dopo aver controllato se tipo di category e di item corrisponde
        ad un dizionario.
        In caso di FileNotFoundError viene creata una struttura vuota.    
        '''
        try:
            with open(self.ingredients_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Inventario iniziale caricato da {self.ingredients_file}")
            
            if "ingredients" not in self.data:
                print("⚠️ Struttura ingredienti non trovata, creando struttura vuota...")
                self.data = {"ingredients": {}}
                
            for category in self.data.get("ingredients", {}).values():
                if isinstance(category, dict):
                    for item in category.values():
                        if isinstance(item, dict) and "initial_quantity" in item:
                            item["current_quantity"] = item["initial_quantity"]
                            item["current_cost"] = item.get("base_cost", 1.0)
                
        except FileNotFoundError:
            print(f"❌ File {self.ingredients_file} non trovato!")
            self.data = {"ingredients": {}}
        
    def load_data(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Inventory e ha tipo di ritorno None (non restituisce nulla).
        Carica i dati dal file salvato, in particolare: legge il JSON ('r') caricandone la struttura in self.data,
        se in self.data manca la chiave ingredients ne viene creata una vuota.
        In caso di FileNotFoundError viene creata una struttura vuota.  
        '''
        try:
            with open(self.ingredients_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Inventario caricato da {self.ingredients_file}")
            
            if "ingredients" not in self.data:
                print(" Struttura ingredienti non trovata, creando struttura vuota...")
                self.data = {"ingredients": {}}
                
        except FileNotFoundError:
            print(f" File {self.ingredients_file} non trovato! Creando struttura vuota...")
            self.data = {"ingredients": {}}     
            self.save_data()         
            
    def save_data(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Inventory e ha tipo di ritorno None (non restituisce nulla).
        Salva l'intero inventario su disco.
        In particolare: aggiunge metadati (_metadata) contenente la data di salvataggio,
        il numero di ingredienti e il valore totale dell'inventario.
        Inoltre, viene scritto il json ('w') con identazione uguale a 4 spazi,
        aggiorna last_save_time e stampa conferma.
        In caso di eccezione stampa errore.
        '''
        with self.lock:
            try:
                self.data["_metadata"] = {
                    "last_saved": datetime.now().isoformat(),
                    "total_ingredients": self.stats['total_ingredients'],
                    "total_value": round(self.stats['total_value'], 2)
                } 
                
                with open(self.ingredients_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                    
                self.last_save_time = datetime.now()
                print(f'Inventario salvato alle {self.last_save_time.strftime("%H:%M:%S")}')
                
            except Exception as e:
                print(f"Errore nel salvataggio dell'inventario: {e}")
                    
    def build_flat_cache(self) -> None:
        '''
        Come parametro riceve implicitamente solo l'istanza della classe Inventory e ha tipo di ritorno None (non restituisce nulla).
        Costruisce una cache piatta per accesso rapido agli ingredienti,
        in particolare: prima viene cancellato il  contenuto precedente con .clear(),
        poi se manca la chiave ingredients in self.data l'esecuzione della funzione viene interrotta,
        altrimenti esplora ricorsivamente tutta la struttura gerarchica attraverso
        _explore_section (funzione interna ricorsiva che prende come parameteri:
        il dizionario che contiene i dati e il percorso corrente).
        e quando trova un dizionario con la chiave "display_name" (cioè un ingrediente vero e proprio),
        lo inserisce nella cache usando come chiave il nome dell'ingrediente.
        Altrimenti (è una categoria), continua la ricorsione aggiungendo il nome della categoria
        al percorso corrente (separato da punto).
        Infine, dopo aver completato la cache, chiama _update_stats() per ricalcolare le statistiche
        dell'inventario.
        '''
        self.flat_cache.clear()
        
        if "ingredients" not in self.data:
            return
        
        def _explore_section(section_data: Dict, current_path: str = '') -> None:
            for key, value in section_data.items():
                if isinstance(value, dict):
                    if "display_name" in value:
                        self.flat_cache[key] = {
                            "data": value,
                            "path": current_path + key if current_path else key
                        }
                    else:
                        new_path = f'{current_path}{key}.' if current_path else f'{key}.'
                        _explore_section(value, new_path)
        _explore_section(self.data['ingredients'])
        self._update_stats()
        
    def _update_stats(self) -> None:
        '''
        Funzione privata che come parametro riceve implicitamente solo l'istanza della classe Inventory e ha tipo di ritorno None (non restituisce nulla).
        Ricalcola e aggiorna le statistiche riassuntive, in particolare: scorre la cache piatta per accedere rapidamente a tutti gli ingredienti.
        che possiede sia "current_quantity" che "current_cost":
        Incrementa il contatore totale degli ingredienti (total_ingredients)
        Somma al valore totale il prodotto tra quantità corrente e costo unitario attuale 
        Infine, assegna i valori calcolati a:
        self.stats['total_ingredients']: numero totale di ingredienti presenti
        self.stats['total_value']: valore monetario totale dell'inventario (arrotondato a 2 decimali)
        self.stats['last_updated']: timestamp ISO dell'ultimo aggiornamento (datetime.now().isoformat())
        '''
        total_ingredients = 0
        total_value = 0.0
            
        for cache_item in self.flat_cache.values():
            ingredient = cache_item["data"]
            if "current_quantity" in ingredient and "current_cost" in ingredient:
                total_ingredients += 1
                total_value += ingredient['current_quantity'] * ingredient['current_cost']
                    
        self.stats['total_ingredients'] = total_ingredients
        self.stats['total_value'] = round(total_value, 2)
        self.stats['last_updated'] = datetime.now().isoformat()
            
    def get_ingredient(self, ingredient_path: str) -> Optional[Dict]:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, il percorso dell'ingrediente (stringa)
        e ha tipo di ritorno Optional[Dict] (restituisce dict oppure non restituisce nulla)
        Restituisce una copia dei dati di un ingrediente (dict) dato il suo percorso,
        oppure None se non trovato.
        Sono presenti due modalità di ricerca:
        Ricerca per nome semplice (senza punto): in cui controlla direttamente nella flat_cache ed è
        ideale quando si conosce solo il nome dell'ingrediente (es. "manzo")
        Ricerca per percorso completo (formato "categoria.ingrediente", supportando però solo percorsi a un livello di profondità): in cui il percorso è diviso in parti
        e se e sono esattamente 2 parti cerca direttamente nella categoria specificata, mentre se è 1 sola parte:
        cerca sequenzialmente in tutte le categorie fino a trovare una corrispondenza.
        In tutti i casi restituisce una copia (.copy()) dei dati per evitare modifiche accidentali
        alla struttura interna.   
        Se l'ingrediente non viene trovato, stampa un messaggio di warning e restituisce None
        '''
        if '.' not in ingredient_path: 
            if ingredient_path in self.flat_cache:
                return self.flat_cache[ingredient_path]['data'].copy()
                
        parts = ingredient_path.split('.')
            
        if len(parts) == 2:
            category, ingredient_name = parts
            if category in self.data.get('ingredients', {}):
                if ingredient_name in self.data['ingredients'][category]:
                    return self.data['ingredients'][category][ingredient_name].copy()
                    
        elif len(parts) == 1:
            ingredient_name = parts[0]
            for category in  self.data.get('ingredients', {}):
                if ingredient_name in self.data['ingredients'][category]:
                    return self.data['ingredients'][category][ingredient_name].copy()
                    
        print(f" Ingrediente non trovato: {ingredient_path}")
        return None
        
    def get_ingredient_quantity(self, ingredient_path: str) -> int:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, il percorso dell'ingrediente (stringa)
        e ha tipo di ritorno int
        Restituisce la quantità corrente di un ingrediente specificato dal percorso (ingredient_path). 
        In particolare, richiama get_ingredient per ottenere i dati dell'ingrediente; 
        se esiste e contiene la chiave "current_quantity", restituisce quel valore, altrimenti restituisce 0.
        '''
        ingredient = self.get_ingredient(ingredient_path)
        if ingredient and "current_quantity" in ingredient:
            return ingredient['current_quantity']
        return 0                
    
    def auto_restock_low_items(self, budget: float = 100.0) -> Tuple[bool,str,float]:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, il budget (float con 100.0 come valore di default)
        e ha tipo di ritorno Tuple[bool, str, float].
        Esegue il rifornimento automatico degli ingredienti con scorte basse rispettando un budget. 
        In particolare, ottiene la lista di ingredienti sotto soglia con get_low_stock_items. 
        Dopodichè, ottenuti già ordinati per criticità e quantità residua li ordina per quantità ascendente e, entro il budget, rifornisce la quantità necessaria (o restock_quantity). 
        Accumula costi e nomi riforniti e restituisce True/False, messaggio dettagliato e costo totale speso.
        '''
        low_items = self.get_low_stock_items()
        if not low_items:
            return True, "Nessun ingrediente da rifornire", 0.0
    
        total_cost = 0.0
        restocked_items = []
    
        for item in low_items:
            if total_cost >= budget:
                break
        
            ingredient = self.get_ingredient(item['path'])
            if not ingredient:
                continue
            
            needed_quantity = max(item['reorder_point'] - item['current_quantity'], 0)
            if needed_quantity <= 0:
                continue
            
            restock_quantity = ingredient.get('restock_quantity', needed_quantity)
            quantity_order = min(needed_quantity, restock_quantity)
        
            item_cost = ingredient.get('current_cost', 0) * quantity_order
        
            if total_cost + item_cost <= budget:
                success = self.add_ingredient(item['path'], quantity_order)
                if success:
                    cost = ingredient.get('current_cost', 0) * quantity_order
                    total_cost += cost
                    restocked_items.append(item['name'])
    
        if restocked_items:
            message = f"Riforniti: {', '.join(restocked_items)}\nCosto totale: {total_cost:.2f}€"
            return True, message, round(total_cost, 2)
        else:
            return False, "Nessun riordine possibile con il budget disponibile", 0.0
            
    def get_low_stock_items(self) -> List[Dict]:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory e ha tipo di ritorno List[Dict].
        Restituisce una lista ordinata di ingredienti con scorte basse o critiche. 
        In particolare, scorre la flat_cache, confronta current_quantity con reorder_point e 
        crea un dizionario per ogni ingrediente con nome, percorso, quantità attuale, soglia, categoria e flag critical. 
        Dopodichè ordina prima per criticità (desc), poi per quantità rimanente (asc).
        '''
        low_items = []
        
        for ingredient_name, cache_item in self.flat_cache.items():
            ingredient = cache_item['data']
            current_quantity =  ingredient.get('current_quantity', 0)
            reorder_point = ingredient.get('reorder_point', 0)
            
            if current_quantity <= reorder_point:
                low_items.append({'name': ingredient.get('display_name', ingredient_name),'path': cache_item['path'], 'current_quantity': current_quantity,'reorder_point': reorder_point, 'category': ingredient.get('category', 'unknown'), 'critical': ingredient.get('critical', False)})
                
        return sorted(low_items, key=lambda x: (x['critical'], x['current_quantity']))
        
    def get_inventory_value(self) -> float:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory e ha tipo di ritorno float.
        Restituisce il valore monetario totale dell'intero inventario, preso direttamente dalle statistiche aggiornate (self.stats['total_value']).
        '''
        return self.stats['total_value']
    
    def get_ingredient_cost(self, ingredient_path: str) -> float: 
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, il percorso dell'ingrediente (str) e ha tipo di ritorno float.
        Restituisce il costo unitario attuale (current_cost) di un ingrediente dato il percorso richiamando get_ingredient; se non trovato o chiave mancante restituisce 0.0.
        '''
        ingredient = self.get_ingredient(ingredient_path)
        if ingredient:
            return ingredient.get('current_cost', 0.0)
        return 0.0
    
    def get_unit_cost(self, path: str) -> float:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, il percorso dell'ingrediente (str) e ha tipo di ritorno float.
        Restituisce il costo base (base_cost) di un ingrediente dato il percorso (formato "categoria.ingrediente") accedendo direttamente alla struttura gerarchica; 
        in caso di errore (percorso invalido o chiave mancante) restituisce 0.0.
        '''
        try:
            cat, item = path.split(".")
            return self.data["ingredients"][cat][item].get("base_cost", 0.0)
        except:
            return 0.0
    
    
    def check_availability(self, recipe_ingredients: Dict[str, int]) -> Tuple[bool, str]:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, gli ingredienti di una ricetta (contenuti in Dict[str, int]) e ha tipo di ritorno Tuple[bool, str]].
        Controlla se tutti gli ingredienti richiesti da una ricetta sono disponibili in quantità sufficiente. 
        In particolare, scorre recipe_ingredients, verifica esistenza e quantità, in caso sia necessario ostruisce un messaggio di errore dettagliato per ingredienti mancanti o insufficienti 
        e restituisce (True, messaggio_ok) o (False, messaggio_errore).
        '''
        missing = []
        insufficient = []
        
        for ingredient_path, needed_quantity in recipe_ingredients.items():
            ingredient = self.get_ingredient(ingredient_path)
            
            if not ingredient:
                missing.append(ingredient_path)
            elif ingredient.get('current_quantity', 0) < needed_quantity:
                insufficient.append({'name': ingredient.get('display_name', ingredient_path), 'needed': needed_quantity, 'available': ingredient.get('current_quantity', 0)})
                
        error_message = ''
        if missing:
            error_message += f' Ingredienti non trovati:\n'
            for item in missing:
                error_message += f'    .{item}\n'
                    
        if insufficient:
            error_message += f" Ingredienti insufficienti: \n"
            for item in insufficient:
                error_message += f"    .{item['name']}: bisogno {item['needed']}, disponibile {item['available']}"

        if error_message:
            return False, error_message.strip()
            
        return True, 'Tutti gli ingredienti sono disponibili'
                
    def add_ingredient(self, ingredient_path: str, quantity: int) -> bool:
        '''
        Funzione che come parametro riceve implicitamente l'istanza della classe Inventory, il percorso dell'ingrediente (str), la quantità (int) e ha tipo di ritorno bool.
        Aggiunge una quantità specifica a un ingrediente. 
        In particolare, verifica quantità positiva e esistenza ingrediente. 
        Successivamente, entra in sezione protetta da lock: aumenta current_quantity, salva su disco, aggiorna statistiche e 
        restituisce True se l'operazione è riuscita, altrimenti False.
        '''
        if quantity <= 0:
            return False
        
        ingredient = self.get_ingredient(ingredient_path)
        if not ingredient:
            return False
                
        with self.lock:
            try:
                parts = ingredient_path.split('.')
                        
                if len(parts) == 2:
                    category, ingredient_name = parts
                            
                    if (category in self.data['ingredients'] and ingredient_name in self.data['ingredients'][category]):
                        self.data['ingredients'][category][ingredient_name]['current_quantity'] += quantity
                    
                        self.save_data()
                        self._update_stats()
                        
                        display_name = ingredient.get('display_name', ingredient_path)
                    
                        return True
                
            except Exception as e:
                return False
                
        return False

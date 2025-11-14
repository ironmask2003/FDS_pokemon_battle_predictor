import numpy as np
import pandas as pd
from tqdm import tqdm

# Mappatura dei tipi delle mosse in relazione con i tipi dei pokemon, che sottolinea le loro debolezze e punti di forza
TYPE_CHART = {
        'NORMAL': {
            'ROCK': 0.5, 'GHOST': 0, 'STEEL': 0.5
        },
        'FIRE': {
            'FIRE': 0.5, 'WATER': 0.5, 'GRASS': 2, 'ICE': 2, 'BUG': 2, 'ROCK': 0.5, 'DRAGON': 0.5, 'STEEL': 2
        },
        'WATER': {
            'FIRE': 2, 'WATER': 0.5, 'GRASS': 0.5, 'GROUND': 2, 'ROCK': 2, 'DRAGON': 0.5
        },
        'GRASS': {
            'FIRE': 0.5, 'WATER': 2, 'GRASS': 0.5, 'POISON': 0.5, 'GROUND': 2, 'FLYING': 0.5, 'BUG': 0.5, 'ROCK': 2, 'DRAGON': 0.5, 'STEEL': 0.5
        },
        'ELECTRIC': {
            'WATER': 2, 'GRASS': 0.5, 'ELECTRIC': 0.5, 'GROUND': 0, 'FLYING': 2, 'DRAGON': 0.5
        },
        'ICE': {
            'FIRE': 0.5, 'WATER': 0.5, 'GRASS': 2, 'ICE': 0.5, 'GROUND': 2, 'FLYING': 2, 'DRAGON': 2, 'STEEL': 0.5
        },
        'FIGHTING': {
            'NORMAL': 2, 'ICE': 2, 'POISON': 0.5, 'FLYING': 0.5, 'PSYCHIC': 0.5, 'BUG': 0.5, 'ROCK': 2, 'GHOST': 0, 'DARK': 2, 'STEEL': 2, 'FAIRY': 0.5
        },
        'POISON': {
            'GRASS': 2, 'POISON': 0.5, 'GROUND': 0.5, 'ROCK': 0.5, 'GHOST': 0.5, 'STEEL': 0, 'FAIRY': 2
        },
        'GROUND': {
            'FIRE': 2, 'ELECTRIC': 2, 'GRASS': 0.5, 'POISON': 2, 'FLYING': 0, 'BUG': 0.5, 'ROCK': 2, 'STEEL': 2
        },
        'FLYING': {
            'GRASS': 2, 'ELECTRIC': 0.5, 'FIGHTING': 2, 'BUG': 2, 'ROCK': 0.5, 'STEEL': 0.5
        },
        'PSYCHIC': {
            'FIGHTING': 2, 'POISON': 2, 'PSYCHIC': 0.5, 'DARK': 0, 'STEEL': 0.5
        },
        'BUG': {
            'FIRE': 0.5, 'GRASS': 2, 'FIGHTING': 0.5, 'POISON': 0.5, 'FLYING': 0.5, 'PSYCHIC': 2, 'GHOST': 0.5, 'DARK': 2, 'STEEL': 0.5, 'FAIRY': 0.5
        },
        'ROCK': {
            'FIRE': 2, 'ICE': 2, 'FIGHTING': 0.5, 'GROUND': 0.5, 'FLYING': 2, 'BUG': 2, 'STEEL': 0.5
        },
        'GHOST': {
            'NORMAL': 0, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': 0.5
        },
        'DRAGON': {
            'DRAGON': 2, 'STEEL': 0.5, 'FAIRY': 0
        },
        'DARK': {
            'FIGHTING': 0.5, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': 0.5, 'FAIRY': 0.5
        },
        'STEEL': {
            'FIRE': 0.5, 'WATER': 0.5, 'ELECTRIC': 0.5, 'ICE': 2, 'ROCK': 2, 'STEEL': 0.5, 'FAIRY': 2
        },
        'FAIRY': {
            'FIRE': 0.5, 'FIGHTING': 2, 'POISON': 0.5, 'DRAGON': 2, 'DARK': 2, 'STEEL': 0.5
        }
    }

POSITIVE_EFFECTS = {
    "reflect",          # dimezza i danni fisici
    "lightscreen",      # dimezza i danni speciali
    "auroraveil",       # dimezza entrambi i tipi di danni (se è grandine)
    "substitute",       # crea un scudo temporaneo
    "tailwind",         # raddoppia la Speed
    "focusenergy",      # aumenta la probabilità di critico
    "safeguard",        # previene status alterati
    "aqua_ring",        # recupera HP ogni turno
    "ingrain",          # recupera HP ogni turno ma blocca lo switch
    "leechseed" ,       # (solo se usato sull’avversario) drena HP ogni turno
    "wish",             # cura in un turno futuro
    "protect",          # blocca i danni per un turno
    "detect",           # come protect
    "spikes",           # piazza trappole sul campo avversario
    "toxicspikes",      # avvelena chi entra
    "stealthrock",      # danneggia chi entra
    "stickyweb",        # riduce la Speed di chi entra
    "trickroom",        # inverte le priorità di velocità
    "psychicterrain", "mistyterrain", "grassyterrain", "electricterrain",  # terreni vantaggiosi
    "rain", "sun", "sandstorm", "hail",  # meteo, vantaggiosi per certi team
}

NEGATIVE_EFFECTS = {
    "leechseed",        # se subito (drain ogni turno)
    "confusion",        # può auto-danneggiarsi
    "curse",            # subisce danni ogni turno (se colpito da Ghost)
    "bind", "wrap", "fire_spin", "clamp", "whirlpool",  # intrappolato e subisce danni
    "infestation", "sand_tomb", "magma_storm",          # versioni moderne dei binding
    "encore",           # costretto a ripetere una mossa
    "taunt",            # può usare solo mosse offensive
    "torment",          # non può usare la stessa mossa consecutivamente
    "infatuation",      # può non attaccare
    "disable",          # disabilita una mossa
    "yawn",             # si addormenterà al turno successivo
    "perishsong",       # KO dopo 3 turni
    "embargo",          # non può usare strumenti
    "healblock",        # non può curarsi
    "nightmare",        # subisce danni durante il sonno
    "partiallytrapped", # generico: intrappolato
}

def calculate_moves_effectiveness(move_type: str, defender_types: list) -> float:
        """
        Calcola l'efficacia di una mossa contro un Pokémon.
        """
        if not move_type or not defender_types:
            return 1.0
        
        effectiveness = 1.0
        
        # Per ogni tipo del difensore, moltiplica l'efficacia
        for def_type in defender_types:
            if move_type in TYPE_CHART:
                multiplier = TYPE_CHART[move_type].get(def_type, 1.0)
                effectiveness *= multiplier
        
        return effectiveness

def calculate_effectiveness(effects, positive, negative):
    for e in effects:
        if e in POSITIVE_EFFECTS:
            positive += 1
        elif e in NEGATIVE_EFFECTS:
            negative += 1
    return positive, negative
            
def extract_pokemon_p1(p1_team):
    pokemon_types = {}
    
    team_size = len(p1_team)
    for pokemon in p1_team:
        name = pokemon.get('name', '').lower()
        types = [t.upper() for t in pokemon.get('types', [])]
        
        # Delete "notype"
        types = [t for t in types if t != 'NOTYPE']
        if name and types:
            pokemon_types[name] = types
    return pokemon_types

def moves_analyze(number: str, p_move, p_state, p_other_state, p_state_before, p_name_pok, pokemon_types, variables: dict) -> dict:
    move_type = p_move.get('type', '').upper()
    base_p = p_move.get('base_power', 0)
    category = p_move.get('category', '').upper()
    
    variables[f"p{number}_base_powers"].append(base_p)
    
    if category == 'SPECIAL':
        variables[f"p{number}_special_moves"] += 1
    elif category == 'PHYSICAL':
        variables[f"p{number}_physical_moves"] += 1

    
    if p_state_before and category in ['SPECIAL', 'PHYSICAL'] and base_p > 0:
        # Calcola danno osservato
        hp_before = p_state_before.get('hp_pct', 1.0)
        hp_after = p_other_state.get('hp_pct', 1.0)
        
        # Controlla se è lo stesso pokemon
        if p_state_before.get('name') == p_name_pok:
            damage_dealt = hp_before - hp_after
            
            # Solo se c'è stato danno positivo
            if damage_dealt > 0:
                variables[f"p{number}_damages"].append(damage_dealt)
            elif damage_dealt == 0:
                variables[f"p{number}_no_attack"] += 1
            else:
                variables[f"p{1 if number == 2 else 2}_heal"] += 1
        else:
            variables[f"p{number}_num_change"] += 1

    if number == 2:
        if category != 'STATUS' and base_p > 0:
            defender_name = p_state.get('name', '').lower()
            defender_types = pokemon_types.get(defender_name, [])
            
            if defender_types:
                effectiveness = calculate_moves_effectiveness(move_type, defender_types)
                if effectiveness >= 2.0:
                    variables[f"p{number}_super_effective"] += 1
                else:
                    variables[f"p{number}_no_effective"] += 1
    return variables

def analyze_timeline(timeline, pokemon_types, variables: dict) -> dict:

    for i in range(len(timeline)):
        turn = timeline[i]

        # Move details for turn i of p1
        p1_move = turn.get('p1_move_details')
        p1_state = turn.get('p1_pokemon_state', {})
        p1_boosts = p1_state.get('boosts', {})
        p1_name_pok = p1_state.get("name")
        p1_state_before = timeline[i-1].get('p1_pokemon_state', {}) if i > 0 else None
        effects_p1 = p1_state.get('effects', [])
        
        variables["p1_list_hp"].append(p1_state.get('hp_pct', 0))

        # Move details for turn i of p2
        p2_move = turn.get('p2_move_details')
        p2_state = turn.get('p2_pokemon_state', {})
        p2_boosts = p2_state.get('boosts', {})
        p2_name_pok = p2_state.get("name")
        p2_state_before = timeline[i-1].get('p2_pokemon_state', {}) if i > 0 else None
        effects_p2 = p2_state.get('effects', [])
        
        variables["p2_list_hp"].append(p2_state.get('hp_pct', 0))

        if p1_move:
            variables = moves_analyze(1, p1_move, p1_state, p2_state, p2_state_before, p2_name_pok, pokemon_types, variables)

        if p1_boosts:
            total_boost = sum(p1_boosts.values())

            variables["p1_atk_boosts"].append(p1_boosts.get('atk', 0))
            variables["p1_def_boosts"].append(p1_boosts.get('def', 0))
            variables["p1_spa_boosts"].append(p1_boosts.get('spa', 0))
            variables["p1_spd_boosts"].append(p1_boosts.get('spd', 0))
            variables["p1_spe_boosts"].append(p1_boosts.get('spe', 0))
            
            if total_boost < 0:
                variables["p1_negative_boost_turns"] += 1

        if p2_move:
            variables = moves_analyze(2, p2_move, p2_state, p1_state, p1_state_before, p1_name_pok, pokemon_types, variables)

        if p2_boosts:
            # Conta turni con boost totale positivo/negativo
            total_boost = sum(p2_boosts.values())

            variables["p2_atk_boosts"].append(p2_boosts.get('atk', 0))
            variables["p2_def_boosts"].append(p2_boosts.get('def', 0))
            variables["p2_spa_boosts"].append(p2_boosts.get('spa', 0))
            variables["p2_spd_boosts"].append(p2_boosts.get('spd', 0))
            variables["p2_spe_boosts"].append(p2_boosts.get('spe', 0))
            
            if total_boost < 0:
                variables["p2_negative_boost_turns"] += 1

        # Calcolo delle features combinate tra p1 e p2

        variables["rem_pok_p1"][p1_name_pok] = p1_state.get('hp_pct', 1.0)
        variables["rem_pok_p2"][p2_name_pok] = p2_state.get('hp_pct', 1.0)

        if p1_name_pok not in variables["pokemon_p1"]:
            variables["pokemon_p1"].append(p1_name_pok)

        if p2_name_pok not in variables["pokemon_p2"]:
            variables["pokemon_p2"].append(p2_name_pok)

        if p1_state.get("status", "nostatus") == "fnt":
            del variables["rem_pok_p1"][p1_name_pok]

        if p2_state.get("status", "nostatus") == "fnt":
            del variables["rem_pok_p2"][p2_name_pok]

        variables["p1_number_effective_pos"], variables["p1_number_effective_neg"] = calculate_effectiveness(effects_p1, variables["p1_number_effective_pos"], variables["p1_number_effective_neg"])
        variables["p2_number_effective_pos"], variables["p2_number_effective_neg"] = calculate_effectiveness(effects_p2, variables["p2_number_effective_pos"], variables["p2_number_effective_neg"])

    return variables

def create_simple_features(data: list[dict]) -> pd.DataFrame:
    """
    Feature extraction function based on correlation analysis with player victory.
    """
    feature_list = []

    for battle in tqdm(data, desc="Extracting features"):
        features = {}

        # --- P1 Team ---
        p1_team = battle.get('p1_team_details', [])
        team_size = len(p1_team)
        pokemon_types = extract_pokemon_p1(p1_team)

        # --- Battle Timeline Features ---
        timeline = battle.get('battle_timeline', [])

        variables = {
            # Lista dei base_power durante la battaglia
            "p1_base_powers": [],
            "p2_base_powers": [],
            # Contatori per mosse speciali e fisiche di p1 e p2
            "p1_special_moves": 0,
            "p1_physical_moves": 0,
            "p2_special_moves": 0,
            "p2_physical_moves": 0,
            # Contatori dei boost totali negativi
            "p1_negative_boost_turns": 0,
            "p2_negative_boost_turns": 0,
            # Contatore delle mosse di p2 super efficaci contro p1
            "p2_super_effective":0,
            # Contatore delle mosse di p2 non super efficaci contro p1
            "p2_no_effective": 0,
            # Lista dei danni recati
            "p1_damages": [],
            "p2_damages": [],
            # Lista degli HP durante la partita
            "p1_list_hp": [],
            "p2_list_hp": [],
            # Contatore degli effetti positivi 
            "p1_number_effective_pos": 0,
            "p2_number_effective_pos": 0,
            # Contatore degli effetti negativi 
            "p1_number_effective_neg": 0,
            "p2_number_effective_neg": 0,
            # Lista dei boost per tipo di P1
            "p1_atk_boosts": [],
            "p1_def_boosts": [],
            "p1_spa_boosts": [],
            "p1_spd_boosts": [],
            "p1_spe_boosts": [],
            # Lista dei boost per tipo di P2
            "p2_atk_boosts": [],
            "p2_def_boosts": [],
            "p2_spa_boosts": [],
            "p2_spd_boosts": [],
            "p2_spe_boosts": [],
            # Contatore dei cambi durante la battaglia
            "p1_num_change": 0,
            "p2_num_change": 0,
            # Lista dei pokemon spuntati durante la partita
            "pokemon_p1": [],
            "pokemon_p2": [],
            # Contatore delle guarigioni durante la battaglia
            "p1_heal": 0,
            "p2_heal": 0,
            # Pokemon rimasti al 30 turno
            "rem_pok_p1": {},
            "rem_pok_p2": {},
            # Lista degli attacchi non andati a buon fine
            "p1_no_attack": 0,
            "p2_no_attack": 0,
         }

        
        if timeline:

            variables = analyze_timeline(timeline, pokemon_types, variables)
            features['damage_advantage'] = sum(variables["p1_damages"]) - sum(variables["p2_damages"])
            features['var_pok'] = len(variables["pokemon_p1"]) - len(variables["pokemon_p2"])
            
            # Numero di turni in i pokemon di p1 sono in fnt (battuti)
            ko_p1 = sum(
                1 for turn in timeline 
                if turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'fnt' # or turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'slp' or turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'frz' or turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'fnt'
            )

            # Numero di turni in i pokemon di p2 sono in fnt (battuti)
            ko_p2 = sum(
                1 for turn in timeline 
                if turn.get('p2_pokemon_state', {}).get('status', 'nostatus') == 'fnt' # or turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'slp' or turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'frz' or turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'fnt'
            )
            
            features["ko_adv"] = ko_p1 - ko_p2

            # Assegnazione delle features
            features['negative_adv'] = variables["p1_negative_boost_turns"] - variables["p2_negative_boost_turns"]

            p1_rem_hp = np.mean([hp for hp in variables["rem_pok_p1"].values()]) if variables["rem_pok_p1"].values() else 0
            p2_rem_hp = np.mean([hp for hp in variables["rem_pok_p2"].values()]) if variables["rem_pok_p2"].values() else 0
            features["rem_hp_adv"] = p1_rem_hp - p2_rem_hp

            features['number_change'] = variables["p1_num_change"] - variables["p2_num_change"]

            features['heal_adv'] = variables["p1_heal"] - variables["p2_heal"]

            p1_effect_score = variables["p1_number_effective_pos"] - variables["p1_number_effective_neg"]
            p2_effect_score = variables["p2_number_effective_pos"] - variables["p2_number_effective_neg"]
            features['score_adv'] = p1_effect_score - p2_effect_score

            features['no_atk_adv'] = variables["p2_no_attack"] - variables["p1_no_attack"]
            

            # Calcolo delle mosse totali con un base_power maggiore di 0 per entrambi
            p1_total_moves = len([m for m in variables["p1_base_powers"] if m > 0])
            p2_total_moves = len([m for m in variables["p2_base_powers"] if m > 0])
            features['p1_moves_advantage'] = p1_total_moves - p2_total_moves

            p1_high_damage_moves = sum(1 for d in variables["p1_damages"] if d > 0.3)  # >30% HP
            p2_high_damage_moves = sum(1 for d in variables["p2_damages"] if d > 0.3)  # >30% HP
            features['p1_high_damage_moves'] = p1_high_damage_moves
            features['p2_high_damage_moves'] = p2_high_damage_moves

            # Numero di tutte le mosse da p1
            p1_moves_used = sum(1 for turn in timeline if turn.get('p1_move_details') is not None)
            # Numero di tutte le mosse da p2
            p2_moves_used = sum(1 for turn in timeline if turn.get('p2_move_details') is not None)         
            features['moves_adv'] = p1_moves_used - p2_moves_used

            # Calcolo della percentuale delle mosse speciali e fisiche in tutte le mosse usate
            p2_ratio = (variables["p2_special_moves"] + variables["p2_physical_moves"]) / p2_moves_used if p2_moves_used > 0 else 0
            p1_ratio = (variables["p1_special_moves"] + variables["p1_physical_moves"]) / p1_moves_used if p1_moves_used > 0 else 0
            # Differenza tra le percentuali di p1 e p2
            features['offensive_advantage'] = p1_ratio - p2_ratio

            features['p1_team_rm'] = team_size - ko_p1

            no_status_p1 = sum(
                1 for turn in timeline
                if turn.get('p1_pokemon_state', {}).get('status', 'nostatus') == 'nostatus'
            )
            no_status_p2 = sum(
                1 for turn in timeline
                if turn.get('p2_pokemon_state', {}).get('status', 'nostatus') == 'nostatus'
            )
            features["no_status_adv"] = no_status_p1 - no_status_p2

            status_p1 = sum(
                1 for turn in timeline
                if turn.get('p1_pokemon_state', {}).get('status', 'nostatus') != 'nostatus'
            )
            status_p2 = sum(
                1 for turn in timeline
                if turn.get('p2_pokemon_state', {}).get('status', 'nostatus') != 'nostatus'
            )

            features["status_adv"] = status_p1 - status_p2

            p1_total_boosts = [sum([variables["p1_atk_boosts"][i], variables["p1_def_boosts"][i], variables["p1_spa_boosts"][i], 
                                variables["p1_spd_boosts"][i], variables["p1_spe_boosts"][i]]) 
                          for i in range(len(variables["p1_atk_boosts"]))]
            p1_std_total_boost = np.std(p1_total_boosts) if p1_total_boosts else 0

            p2_total_boosts = [sum([variables["p2_atk_boosts"][i], variables["p2_def_boosts"][i], variables["p2_spa_boosts"][i], 
                                variables["p2_spd_boosts"][i], variables["p2_spe_boosts"][i]]) 
                          for i in range(len(variables["p2_atk_boosts"]))]
            p2_std_total_boost = np.std(p2_total_boosts) if p2_total_boosts else 0

            features["std_total_boost_adv"] = p1_std_total_boost - p2_std_total_boost

            # Differenza tra il numero di posse super efficaci di p1 con le mosse super efficaci di p2
            features['p2_super_effective'] =  variables["p2_super_effective"]
            features['p2_no_effective'] = variables["p2_no_effective"]
            
            # p1_final_hp: HP percentuale di P1 nell'ultimo turno
            final_turn = timeline[-1]
            p1_final_hp = final_turn.get('p1_pokemon_state', {}).get('hp_pct', 0)
            p2_final_hp = final_turn.get('p2_pokemon_state', {}).get('hp_pct', 0)
            features['final_hp_adv'] = p1_final_hp - p2_final_hp

            p1_avg_hp = np.std(variables["p1_list_hp"]) if variables["p1_list_hp"] else 0
            p2_avg_hp = np.std(variables["p2_list_hp"]) if variables["p2_list_hp"] else 0
            features['p1_std_hp_advantage'] = p1_avg_hp - p2_avg_hp
    
            # Battle ID e target variable
            features['battle_id'] = battle.get('battle_id')
            if 'player_won' in battle:
                features['player_won'] = int(battle['player_won'])
            
        feature_list.append(features)
    return pd.DataFrame(feature_list).fillna(0)
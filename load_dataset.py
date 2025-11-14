import json
import pandas as pd
import os

def gen_path(kaggle):
    if kaggle:
        # --- Define the path to our data ---
        COMPETITION_NAME = 'fds-pokemon-battles-prediction-2025'
        DATA_PATH = os.path.join('../input', COMPETITION_NAME)

        train_file_path = os.path.join(DATA_PATH, 'train.jsonl')
        test_file_path = os.path.join(DATA_PATH, 'test.jsonl')
    else:
        train_file_path = 'data/train.jsonl'
        test_file_path = 'data/test.jsonl'
    return train_file_path, test_file_path

def load_data(path, idx_view = 0, n_turns = 2, show=False):
    data = []

    # Read the file line by line
    print(f"Loading data from '{path}'...")
    try:
        with open(path, 'r') as f:
            cont = 0
            for line in f:
                if cont == 4877:
                    cont += 1
                    continue
                cont += 1
                # json.loads() parses one line (one JSON object) into a Python dictionary
                data.append(json.loads(line))

        print(f"Successfully loaded {len(data)} battles.")

        # Let's inspect the first battle to see its structure
        print("\n--- Structure of the first train battle: ---")
        if data:
            first_battle = data[idx_view]
            
            # To keep the output clean, we can create a copy and truncate the timeline
            battle_for_display = first_battle.copy()
            battle_for_display['battle_timeline'] = battle_for_display.get('battle_timeline', [])[:n_turns] # Show first n_turns
            
            # Use json.dumps for pretty-printing the dictionary
            if show:
                print(json.dumps(battle_for_display, indent=4))

        return data

    except FileNotFoundError:
        print(f"ERROR: Could not find the training file at '{path}'.")
        print("Please make sure you have added the competition data to this notebook.")
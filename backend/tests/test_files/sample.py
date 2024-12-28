import os
import subprocess
import pickle

def unsafe_command(cmd):
    # Vulnérabilité: Exécution de commande shell non sécurisée
    os.system(cmd)

def unsafe_deserialization(data):
    # Vulnérabilité: Désérialisation non sécurisée
    return pickle.loads(data)

def sql_query(user_input):
    # Vulnérabilité: Injection SQL potentielle
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return query

def write_file(filename, content):
    # Vulnérabilité: Path traversal potentiel
    with open(filename, 'w') as f:
        f.write(content)

class ComplexClass:
    def __init__(self):
        self.data = []
    
    def process_data(self, input_data):
        # Complexité cyclomatique élevée
        if isinstance(input_data, list):
            for item in input_data:
                if isinstance(item, dict):
                    if 'value' in item:
                        if item['value'] > 0:
                            if 'type' in item:
                                if item['type'] == 'special':
                                    self.data.append(item['value'] * 2)
                                else:
                                    self.data.append(item['value'])
                            else:
                                self.data.append(item['value'])
        return self.data

# Code mort
def unused_function():
    pass

# Variables non utilisées
UNUSED_CONSTANT = 42

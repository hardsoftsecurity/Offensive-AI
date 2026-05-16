import re
import pickle
import hashlib
import os, glob, random
import re
import json
from typing import Any, Dict, Union

# Define what we consider a “simple” / primitive JSON-safe type
Primitive = Union[str, int, float, bool, None]


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        ...

def _hash(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
    integer_hash = int(sha256_hash, 16)
    return integer_hash

def read_pickle(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data

def write_pickle(path, data):
    with open(path, 'wb') as f:
        data = pickle.dump(data, f)

def sample_from_multi_universe(universe):
    sample = {}
    for k, u in universe.items():
        sample[k] = random.sample(u, 1)[0]
    return sample


def read_conf_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_conf_file(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

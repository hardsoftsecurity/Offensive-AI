import json
import random 

from .utility import *

_TRAIN_STR = 'train'
_TEST_STR = 'test'

def read_dataset(
    path,
    encoding='utf-8',
    shuffle=True
):
    train, test = [], []
    
    with open(path, 'r', encoding=encoding) as f:
        for line in f:
            entry = json.loads(line)
            if entry['dataset'] == _TRAIN_STR:
                dest = train
            elif entry['dataset'] == _TEST_STR:
                dest = test

            entry.pop('dataset')
            dest.append(entry)
            
    if shuffle:
        random.shuffle(train)
        random.shuffle(test)
    return train, test

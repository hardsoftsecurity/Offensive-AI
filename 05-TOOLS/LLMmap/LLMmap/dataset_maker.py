import tqdm
import json
import random 

from .llm import load_llm
from .prompt_configuration import TRAIN, TEST

def read_dataset(
    path,
    encoding='utf-8',
    shuffle=True
):
    train, test = [], []
    
    with open(path, 'r', encoding=encoding) as f:
        for line in f:
            entry = json.loads(line)
            if entry['dataset'] == TRAIN:
                dest = train
            elif entry['dataset'] == TEST:
                dest = test

            entry.pop('dataset')
            dest.append(entry)
            
    if shuffle:
        random.shuffle(train)
        random.shuffle(test)
    return train, test


def make_dataset_entries_for_new_llm(llm, queries, prompt_confs, pool=TRAIN):
    entries = []
    for prompt_conf in tqdm.tqdm(prompt_confs):
        entry = {'dataset':pool, 'llm': llm.llm_name, 'traces': [], 'prompt_conf': prompt_conf.to_dict()}
        for query in queries:
            prompt, sample_params = prompt_conf(query, llm)
            o = llm.generate(prompt, sample_params)[0]
            entry['traces'].append((query, o))
        entries.append(entry)
    return entries

class DatasetMaker:

    def __init__(self, pc, llms, queries, num_prompt_conf_train, num_prompt_conf_test, output_path, encoding='utf8'):
        self.pc = pc
        self.llms = llms
        self.queries = queries
        self.num_prompt_conf_train = num_prompt_conf_train
        self.num_prompt_conf_test = num_prompt_conf_test
        self.output_path = output_path

        self.encoding = encoding
    
        self.train = []
        self.test = []

    def run_on_an_llm(self, llm_name, llm_type):

        train_prompt_conf = self.pc.sample(self.num_prompt_conf_train, pool=TRAIN)
        test_prompt_conf = self.pc.sample(self.num_prompt_conf_test, pool=TEST)
        
        print(f"Loading {llm_name}...")
        llm = load_llm(llm_name, llm_type)
        print(f"\tRunning on {llm_name} train...")
        _train = make_dataset_entries_for_new_llm(llm, self.queries, train_prompt_conf, pool=TRAIN)
        self.dump(_train)
        self.train += _train
        print(f"\tRunning on {llm_name} test...")
        _test = make_dataset_entries_for_new_llm(llm, self.queries, test_prompt_conf, pool=TEST)
        self.dump(_test)
        self.test += _test

    def __call__(self):
        for llm_name, llm_type in self.llms:
            self.run_on_an_llm(llm_name, llm_type)

    def dump(self, entries):
        with open(self.output_path, 'a', encoding=self.encoding) as f:
            for entry in entries:
                print(json.dumps(entry), file=f)

import torch
import tqdm
import random
from torch.utils.data import Dataset, DataLoader, get_worker_info
from typing import Iterable, Dict, List, Any
from torch.utils.data import DataLoader

from .dataset_maker import read_dataset
from .embedding_model import load_model, EMBEDDING_MODELS

class EmbeddingCache:
    def __init__(self, emb_model, batch_size: int = 128) -> None:
        self.batch_size = max(1, batch_size)
        self._cache = {}
        self.emb_model = emb_model
        self.llms_map = None

        self.queries = None

        self.embedding_size = None

        self.llms = set()

    def get_embedding(self, texts: List[str]) -> List[Any]:
        emb = self.emb_model.get_embedding(texts)
        if self.embedding_size  is None:
            self.embedding_size = emb.shape[-1]
        return emb

    def precompute(self, dataset) -> Dict[str, Any]:
        pending: List[str] = []

        def flush() -> None:
            """Send the current batch to the model and clear `pending`."""
            if pending:
                embs = self.get_embedding(pending)
                self._cache.update(zip(pending, embs))
                pending.clear()

        # ---------------------------------------------------------------------
        def handle_one(t: str) -> None:
            """
            Process a *single* string:
              • skip if already cached
              • skip duplicates within the current batch
              • queue it, and flush when the batch fills up
            """
            if t in self._cache or t in pending:
                return
            pending.append(t)
            if len(pending) >= self.batch_size:
                flush()

        for entry in tqdm.tqdm(dataset):
            self.add_llm(entry['llm'])

            queries = [t[0] for t in entry['traces']]
            if self.queries is None:
                self.queries = queries
            else:
                # check if queries are consistent
                assert self.queries == queries
                
            for query, resp in entry['traces']:
                handle_one(query)
                handle_one(resp)

        flush()                       # last (possibly small) batch
        self.set_llms_map()
        
    def add_llm(self, llm):
        if not llm in self.llms:
            self.llms.add(llm)

    def __call__(self, key):
        return self._cache[key]

    def set_llms_map(self):
        llms = sorted(self.llms)
        self.llms_map = dict(zip(llms, range(len(self.llms))))


# ---------------------------------------------------------------------

class DatasetFactory(Dataset):
    def __init__(self, dataset_raw, cache, *args, **k):
        self.dataset_raw = dataset_raw
        self.cache = cache
        self.num_labels = len(self.cache.llms_map)

    def __len__(self):
        return len(self.dataset_raw)

    def pack_traces(self, traces):
        traces_emb = []
        for q, o in traces:
            q_emb = self.cache(q)
            o_emb = self.cache(o)
            emb = torch.concat([q_emb, o_emb])[None,:]
            traces_emb.append(emb)
        return torch.concat(traces_emb, dim=0)

    def __getitem__(self, idx):
        entry = self.dataset_raw[idx]
        traces_emb = self.pack_traces(entry['traces'])
        label_id = self.cache.llms_map[entry['llm']]
        return traces_emb, label_id

# ---------------------------------------------------------------------

class DatasetFactorySiamese(DatasetFactory):
    def __init__(self, dataset_raw, cache, num_pairs_per_epoch, *args, **kargs):
        super().__init__(dataset_raw, cache, *args, **kargs)
        
        self.num_pairs_per_epoch = num_pairs_per_epoch
        self.traces_per_llm = [[] for _ in range(self.num_labels)]
        self.fill_traces_per_llm()

    def fill_traces_per_llm(self):
        for i, entry in enumerate(self.dataset_raw):
            label_id = self.cache.llms_map[entry['llm']]
            self.traces_per_llm[label_id].append(i)

    def __len__(self):
        return self.num_pairs_per_epoch

    @staticmethod
    def _sample_but_x(population, x):
        pool = [i for i in population if i != x]
        if not pool:
            raise ValueError("No alternative element available")
        return random.choice(pool)

    @staticmethod
    def get_worker_id():
        winfo = get_worker_info()         
        if winfo is None:
            worker_id = 0
        else:
            worker_id = winfo.id
        return worker_id

    def __getitem__(self, idx):
        random.seed(idx+self.get_worker_id())

        llm_a = random.randrange(0, self.num_labels)
        trace_a_id = random.choice(self.traces_per_llm[llm_a])

        if random.choice([True, False]):
            # positive pair
            llm_b = llm_a
            trace_b_id = self._sample_but_x(self.traces_per_llm[llm_a], trace_a_id)
            label = 1
        else:
            # negative pair
            llm_b = self._sample_but_x(range(self.num_labels), llm_a)
            trace_b_id = random.choice(self.traces_per_llm[llm_b])
            label = 0
            
        trace_a = self.pack_traces(self.dataset_raw[trace_a_id]['traces'])
        trace_b = self.pack_traces(self.dataset_raw[trace_b_id]['traces'])

        pair = torch.concat([trace_a[None,:], trace_b[None,:]])

        return pair, label

# ---------------------------------------------------------------------

def load_datasets(conf, siamese=True, ks=None):
    # load db
    train, test = read_dataset(conf['dataset_path'])

    if ks:
        train, test = train[:ks[0]], test[:ks[1]]
    # load emb_model
    emb_model = load_model(conf['embedding_model_id'])

    # compute embeddings in db
    cache = EmbeddingCache(emb_model, conf['embedding_batch_size'])
    cache.precompute(train + test)

    if siamese:
        data_factory_class = DatasetFactorySiamese
    else:
        data_factory_class = DatasetFactory
    
    dataset_train = data_factory_class(train, cache, conf['num_pairs_per_epoch'])
    dataset_test = data_factory_class(test, cache, conf['num_pairs_per_eval'])

    conf['llms_map'] = cache.llms_map
    conf['queries'] = cache.queries

    conf['inference_model']['num_classes'] = dataset_train.num_labels
    conf['inference_model']['num_queries'] = len(cache.queries)
    conf['inference_model']['emb_size'] = cache.embedding_size
    
    
    loader_train = DataLoader(dataset_train, batch_size=conf['batch_size'], shuffle=True)
    loader_test = DataLoader(dataset_test, batch_size=conf['batch_size'], shuffle=False)

    return (loader_train, loader_test), cache, (dataset_train, dataset_test)
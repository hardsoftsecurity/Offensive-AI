import os
import json
import torch
import torch.nn.functional as F
import numpy as np
from scipy.spatial.distance import cdist
import shutil
from pathlib import Path


from . import CONF_NAME, MODEL_NAME, TEMPLATE_NAME
from .utility import read_conf_file
from .embedding_model import load_model as load_model_emb
from .inference_model_archs import InferenceModelLLMmap

def read_templates(templates_path):
    with open(templates_path) as f:
        templates = json.load(f)
    templates = {k:np.array(v) for (k,v) in templates.items()}
    return templates

def write_templates(templates_path, templates):
    templates = {k:v.tolist() for (k,v) in templates.items()}
    with open(templates_path, 'w') as f:
        json.dump(templates, f, indent=4)

def load_LLMmap(model_home_dir, device='cpu', **kargs):
    if not os.path.isdir(model_home_dir):
        raise FileNotFoundError(f"Model directory not found: {model_home_dir}")

    conf_path = os.path.join(model_home_dir, CONF_NAME)
    if not os.path.isfile(conf_path):
        raise FileNotFoundError(f"Configuration file not found: {conf_path}")
    
    conf = read_conf_file(conf_path)

    if 'is_open' not in conf:
        raise KeyError("'is_open' key missing in configuration file")

    siamese = conf['is_open']

    model_path = os.path.join(model_home_dir, MODEL_NAME)
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    if siamese:
        templates_path = os.path.join(model_home_dir, TEMPLATE_NAME)
        if os.path.isfile(templates_path):
            templates = read_templates(templates_path)
            conf['templates'] = templates
            conf['template_file_path'] = templates_path


    if 'inference_model' not in conf:
        raise KeyError("'inference_model' key missing in configuration file")

    hp = conf['inference_model']

    try:
        net = InferenceModelLLMmap(hp, is_for_siamese=siamese)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize InferenceModelLLMmap: {e}")

    try:
        net.load_state_dict(torch.load(model_path))
    except Exception as e:
        raise RuntimeError(f"Failed to load model state from {model_path}: {e}")

    inf_class = InferenceModel_open if siamese else InferenceModel_closed
    inf = inf_class(conf, net, device=device, **kargs)

    return conf, inf

class InferenceModel:

    def print(self, *args, **kargs):
        if self.verbose:
            print(*args, **kargs)
            
    def __init__(self, conf, model, device, verbose=True):

        self.conf = conf
        self.model = model
        self.verbose = verbose
        self.device = device
        
        self.model = self.model.eval().to(self.device)
        self.is_open = self.conf['is_open']

        self.label_map = {v:k for (k,v) in self.conf['llms_map'].items()}
        
        self.queries = self.conf['queries']
                
        self.print("\tLoading Embedding Model...")
        self.emb_model_id = self.conf.get('emb_model_id', 0)
        self.emb_model = load_model_emb(self.emb_model_id, self.device)
        
        self.print("\tPre-comupting Queries embeddings...")
        self.emb_queries = self.emb_model.get_embedding(self.queries) 
        self.print("Model ready for inference.")

        self.ready = False
        
        
    def __call__(self, answers):
        if len(answers) != len(self.queries):
            raise Exeception(f"Model supports {self.queries} queries, {len(answers)} answers provided")
        answers = [self._preprocess_answers(answer) for answer in answers]

        with torch.no_grad():
            emb_outs = self.emb_model.get_embedding(answers)
            traces = torch.cat((self.emb_queries, emb_outs), dim=1)
            traces = traces.unsqueeze(0)
            output = self.model(traces)
        return output
        
    def _preprocess_answers(self, out):
        return out[:self.conf['max_number_chars_response']]
                
class InferenceModel_closed(InferenceModel):
    
    def __call__(self, answers):
        logits = super().__call__(answers)
        with torch.no_grad():
            p = F.softmax(logits, dim=-1).cpu().numpy()[0]
        return p
    
    def print_result(self, probabilities, k=5):
        if k < 1:
            raise ValueError("k must be at least 1")
        if k > len(probabilities):
            raise ValueError("k cannot be greater than the number of classes")

        sorted_indices = np.argsort(probabilities)[::-1]
        top_k_indices = sorted_indices[:k]
        top_k_probs = probabilities[top_k_indices]

        print("Prediction:\n")
        for i, (index, prob) in enumerate(zip(top_k_indices, top_k_probs)):
            if prob < 0.001:
                prob_str = f"{prob:.1e}"
            else:
                prob_str = f"{prob:.4f}"

            if i == 0:  # Top-1 class
                print(f"\t[Pr: {prob_str}] \t--> {self.label_map[index]} <--")
            else:
                print(f"\t[Pr: {prob_str}] \t{self.label_map[index]}")
                
class InferenceModel_open(InferenceModel):

    _precision_print_ths = 0.001
        
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        if 'templates' in self.conf:
            self.templates_map = self.conf['templates']

            self.llms_supported = sorted(self.templates_map.keys())
            self.label_map = {i:llm for (i,llm) in enumerate(self.llms_supported)} 
            # templates matrix
            self.DB = np.concatenate([self.templates_map[llm][np.newaxis,:] for llm in self.llms_supported])
            self.distance_fn = self.conf.get('distance_fn', 'euclidean')
            self.ready = True
            
        else:
            self.templates_map = None
            self.DB = None
            print(f'[WARNING] No template file found for the model.')
            
    def __call__(self, answers):
        emb = super().__call__(answers).cpu().numpy()

        if self.templates_map is None:
            raise Exception("No templates provided upon model creation.")
        
        distances = cdist(emb, self.DB, metric=self.distance_fn)[0]
        return distances

    def compute_template(self, entries):
        es = self.conf['inference_model']['feature_size']
        _template = np.zeros((len(entries), es))
        for i, entry in enumerate(entries):
            answers = [t[1] for t in entry['traces']]
            emb = super().__call__(answers)
            _template[i] = emb.cpu().numpy()
        return _template.mean(0)

    def print_result(self, distances, k=5):
        if k < 1:
            raise ValueError("k must be at least 1")
        if k > len(distances):
            raise ValueError("k cannot be greater than the number of classes")

        sorted_indices = np.argsort(distances)
        top_k_indices = sorted_indices[:k]
        top_k_probs = distances[top_k_indices]

        print("Prediction:\n")
        for i, (index, dist) in enumerate(zip(top_k_indices, top_k_probs)):
            if dist < self._precision_print_ths:
                dist_str = f"{dist:.1e}"
            else:
                dist_str = f"{dist:.4f}"

            if i == 0:  # Top-1 class
                print(f"\t[Distance: {dist_str}] \t--> {self.label_map[index]} <--")
            else:
                print(f"\t[Distance: {dist_str}] \t{self.label_map[index]}")


    def add_entry_and_save_templates(self, new_llm, new_template):
        templates_path = Path(self.conf['template_file_path'])
        
        # Load the original data
        data = read_templates(templates_path)
        
        self.templates_map[new_llm] = new_template
        self.label_map = {i:llm for (i,llm) in enumerate(sorted(self.templates_map.keys()))}
    
        # Backup the original file
        backup_path = templates_path.with_suffix(templates_path.suffix + '.previous')
        shutil.copy(templates_path, backup_path)
    
        write_templates(templates_path, self.templates_map)
    
        print(f"Updated file saved to: {templates_path}")
        print(f"Backup saved to: {backup_path}")
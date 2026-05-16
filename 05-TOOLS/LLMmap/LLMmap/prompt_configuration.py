import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

TRAIN, TEST = 'train', 'test'

def sample_from_multi_universe(universe):
    sample = {}
    for k, u in universe.items():
        sample[k] = random.sample(u, 1)[0]
    return sample

###############################################################################
# Data classes                                                               #
###############################################################################

class PromptConf:
    """A concrete prompt + decoding‑parameters bundle.

    Calling a *PromptConf* with a *query* returns a ready‑to‑feed prompt string
    and the corresponding sampling hyper‑parameters.
    """

    def __init__(
        self,
        sampling_hparams: Dict[str, Any],
        system_prompt: Optional[str],
        cot_prompt: Optional[str] = None,
        rag_prompt: Optional[str] = None,
        raw: Sequence[Any] | None = None,
    ) -> None:
        self.sampling_hparams = sampling_hparams
        self.system_prompt = system_prompt or ""
        self.cot_prompt = cot_prompt
        self.rag_prompt = rag_prompt
        self.raw = raw or []

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    def __call__(self, query: str, llm, apply_template: bool = True):
        """Materialise the prompt and return *(prompt, sampling_hparams)*."""
        # Chain‑of‑thought augmentation ------------------------------------------------
        if self.cot_prompt:
            query = self.cot_prompt % query

        # Retrieval‑augmented generation augmentation ---------------------------------
        if self.rag_prompt:
            query = self.rag_prompt % query

        # Final assembly --------------------------------------------------------------
        if apply_template:
            prompt_str = llm.make_prompt(self.system_prompt, query)
        else:
            prompt_str = (query, self.system_prompt)

        return prompt_str, self.sampling_hparams

    # ---------------------------------------------------------------------

    def __str__(self) -> str:
        raw_str = " ".join(map(str, self.raw))
        return raw_str


    def to_dict(self) -> Dict[str, Any]:
        return {
            "sampling_hparams": self.sampling_hparams,
            "system_prompt": self.system_prompt,
            "cot_prompt": self.cot_prompt,
            "rag_prompt": self.rag_prompt,
            "raw": self.raw,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptConf":
        return cls(
            sampling_hparams=data.get("sampling_hparams", {}),
            system_prompt=data.get("system_prompt", ""),
            cot_prompt=data.get("cot_prompt"),
            rag_prompt=data.get("rag_prompt"),
            raw=data.get("raw", []),
        )

###############################################################################
# JSON‑driven factory                                                         #
###############################################################################

class _ConfigLoader:
    """Utility class that lazily loads JSON config files from disk.

    Attributes from *general.json* act as a global fallback whenever the
    dedicated file is missing or a key cannot be resolved.
    """

    def __init__(self, home_dir: Union[str, Path]):
        self._root = Path(home_dir).expanduser().resolve()
        if not self._root.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self._root}")

        # *general.json* is mandatory because it holds fallbacks & constants.
        self._general: Dict[str, Any] = self._read_json("general.json", required=True)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def load(self, filename: str, fallback_key: str, default: Any) -> Any:
        """Return JSON content or a fallback from *general.json*.

        If *filename* is missing or returns an empty structure, the value of
        *fallback_key* inside *general.json* is returned instead. If that key
        is also absent, *default* is returned.
        """
        data = self._read_json(filename, required=False)
        if data:
            return data
        return self._general.get(fallback_key, default)

    def constant(self, key: str, default: Any = None) -> Any:
        """Read a scalar constant from *general.json* (with optional default)."""
        return self._general.get(key, default)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _read_json(self, filename: str, *, required: bool) -> Any:

        path = self._root / filename
        if not path.exists():
            if required:
                raise FileNotFoundError(f"Required configuration file missing: {path}")
            return None

        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)

        return data

###############################################################################
# The main factory                                                            #
###############################################################################

class PromptConfFactory:
    """Sample *PromptConf* objects based on JSON configuration files.

    Parameters
    ----------
    home_dir:
        Path to the project root. The actual JSON files are expected under –
        ``{home_dir}/confs/prompt_configurations``.
    """

    def __init__(self, home_dir: Union[str, Path]):
        self._cfg = _ConfigLoader(home_dir)

        # Collections ------------------------------------------------------
        self.sampling_universe: Dict[str, Any] = self._cfg.constant("sampling_universe", {})

        self.params = {
            'systems' :  self._cfg.load("systems.json", "system_prompts", []),
            'cot_prompts' : self._cfg.load("cot_prompts.json", "cot_prompts", []),
            'rag_prompts' : self._cfg.load("rag_prompts.json", "rag_templates", []),
        }
       
        self.documents_rag: List[Tuple[Any, Any, List[str]]] = self._cfg.load("rag_context.json", "documents_rag", [])

        self.train_test_split: List[Tuple[Any, Any, List[str]]] = self._cfg.load("train_test_split.json", "train_test_split", {})
        
        # Scalars / probabilities -----------------------------------------
        self.COT_P: float = self._cfg.constant("COT_P", 0.0)
        self.RAG_P: float = self._cfg.constant("RAG_P", 0.0)
        self.MIN_CHUNKS_RAG: int = self._cfg.constant("MIN_CHUNKS_RAG", 1)
        self.MAX_CHUNKS_RAG: int = self._cfg.constant("MAX_CHUNKS_RAG", 2)

        self.WITH_SYSTEM_P: int = self._cfg.constant("WITH_SYSTEM_P", 1)

    # ------------------------------------------------------------------
    # Sampling helpers
    # ------------------------------------------------------------------

    def _generate_rag_prompt(self, rag_template: Tuple[str, str]) -> Optional[str]:
        t_body, t_chunk = rag_template

        # Pick a random document from the retrieval corpus --------------
        if not self.documents_rag:
            return None

        _, _, background_texts = random.choice(self.documents_rag)
        random.shuffle(background_texts)

        n_chunks = random.randint(self.MIN_CHUNKS_RAG, self.MAX_CHUNKS_RAG)
        chunks = background_texts[:n_chunks]
        chunks_text = "".join(t_chunk % c for c in chunks)

        # Guard: template placeholders should be fully resolved ---------
        if "%" in chunks_text:
            return None

        return t_body.format(retrieved_chunk=chunks_text)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sample_one(self, pool=TRAIN) -> PromptConf:
        """Return a freshly sampled *PromptConf* instance."""
        sampling_hparams = sample_from_multi_universe(self.sampling_universe)
        
        system_prompt = self._cond_choice("systems", self.WITH_SYSTEM_P, pool)
        cot_prompt = self._cond_choice("cot_prompts", self.COT_P, pool)
        rag_template = self._cond_choice("rag_prompts", self.RAG_P, pool)

        rag_prompt = self._generate_rag_prompt(rag_template) if rag_template else None

        raw = (system_prompt, cot_prompt, rag_template)
        return PromptConf(
            sampling_hparams=sampling_hparams,
            system_prompt=system_prompt,
            cot_prompt=cot_prompt,
            rag_prompt=rag_prompt,
            raw=raw,
        )
    
    def _cond_choice(self, collection_name, p, pool):
        collection = self.params[collection_name]
        avaliable = self.train_test_split[pool][collection_name]
        idx = random.choice(avaliable) if avaliable and random.random() < p else None
        return None if idx is None else collection[idx]

    def sample(self, n, pool=TRAIN):
        """Sample n unique confs"""
        assert n > 0
        s = set()
        while len(s) != n:
            s.add(self.sample_one())
        return list(s)
            


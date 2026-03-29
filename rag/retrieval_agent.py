import json
import os
import faiss
import numpy as np
import logging
import warnings
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

try:
    from huggingface_hub.utils import disable_progress_bars
    disable_progress_bars()
except ImportError:
    pass

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class RetrievalAgent:
    def __init__(self, data_path: str = None, model_name: str = 'all-MiniLM-L6-v2'):
        if data_path is None:
            # Default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, 'data', 'fraud_examples.json')
            
        self.data_path = data_path
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.examples = []
        self._load_and_index_data()

    def _load_and_index_data(self):
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.examples = json.load(f)
        except Exception as e:
            logger.error(f"Cannot load data from {self.data_path}. Error: {e}")
            self.examples = []

        if not self.examples:
            logger.warning("No examples found. Vector index will be empty.")
            return

        texts = [ex['text'] for ex in self.examples]
        embeddings = self.model.encode(texts)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        # Required for fast retrieval
        self.index.add(np.array(embeddings).astype('float32'))
        logger.info(f"Loaded and indexed {len(self.examples)} examples.")

    def retrieve_similar_cases(self, query: str, top_k: int = 3) -> list:
        if not self.index or not self.examples:
            return []

        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.examples):
                match = self.examples[idx]
                results.append({
                    "text": match['text'],
                    "label": match['label'],
                    "explanation": match['explanation'],
                    "distance": float(distances[0][i])
                })
        return results

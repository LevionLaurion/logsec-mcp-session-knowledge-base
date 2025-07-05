"""
🧠 LogSec 2.0 - Embedding Engine
Semantic understanding for every session using sentence-transformers
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, Dict, List

class EmbeddingEngine:
    """Generate and manage semantic embeddings for LogSec sessions"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize embedding engine with specified model
        
        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2, 384 dims)
        """
        self.logger = logging.getLogger('EmbeddingEngine')
        self.logger.info(f"Initializing EmbeddingEngine with model: {model_name}")
        
        # Load the model (will download on first run ~90MB)
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
        
        # Setup paths
        self.embeddings_path = Path(r"C:\LogSec\knowledge\shared\embeddings")
        self.embeddings_path.mkdir(parents=True, exist_ok=True)
        
        # Create monthly subdirectories
        self.current_month_path = self.embeddings_path / datetime.now().strftime("%Y-%m")
        self.current_month_path.mkdir(exist_ok=True)        
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding vector for given text
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of shape (dimension,)
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided for embedding")
            return np.zeros(self.dimension)
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            self.logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return np.zeros(self.dimension)
    
    def save_embedding(self, session_id: str, embedding: np.ndarray, metadata: Optional[Dict] = None):
        """Save embedding to disk with metadata
        
        Args:
            session_id: Unique session identifier
            embedding: Numpy array with embedding
            metadata: Optional metadata (timestamp, text_length, etc.)
        """        # Determine path based on session date
        month_path = self.current_month_path
        if metadata and 'timestamp' in metadata:
            timestamp = datetime.fromisoformat(metadata['timestamp'])
            month_path = self.embeddings_path / timestamp.strftime("%Y-%m")
            month_path.mkdir(exist_ok=True)
        
        # Save embedding as .npy file
        embedding_file = month_path / f"{session_id}.npy"
        np.save(embedding_file, embedding)
        
        # Save metadata if provided
        if metadata:
            metadata_file = month_path / f"{session_id}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Saved embedding for session {session_id}")
    
    def load_embedding(self, session_id: str) -> Optional[np.ndarray]:
        """Load embedding from disk
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Embedding array or None if not found
        """        # Search in all month directories
        for month_dir in self.embeddings_path.glob("*/"):
            if not month_dir.is_dir():
                continue
            
            embedding_file = month_dir / f"{session_id}.npy"
            if embedding_file.exists():
                try:
                    embedding = np.load(embedding_file)
                    self.logger.debug(f"Loaded embedding for {session_id}")
                    return embedding
                except Exception as e:
                    self.logger.error(f"Error loading embedding {session_id}: {e}")
                    return None
        
        self.logger.warning(f"Embedding not found for session {session_id}")
        return None
    
    def load_metadata(self, session_id: str) -> Optional[Dict]:
        """Load metadata for a session embedding"""
        for month_dir in self.embeddings_path.glob("*/"):
            if not month_dir.is_dir():
                continue
            
            metadata_file = month_dir / f"{session_id}.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading metadata {session_id}: {e}")
        return None    
    def batch_generate_embeddings(self, texts: List[str], batch_size: int = 10) -> List[np.ndarray]:
        """Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of texts to embed
            batch_size: Process texts in batches for memory efficiency
            
        Returns:
            List of embedding arrays
        """
        embeddings = []
        total = len(texts)
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            try:
                batch_embeddings = self.model.encode(batch, convert_to_numpy=True)
                embeddings.extend(batch_embeddings)
            except Exception as e:
                self.logger.error(f"Error in batch {i//batch_size + 1}: {e}")
                # Add zero embeddings for failed batch
                embeddings.extend([np.zeros(self.dimension) for _ in batch])
        
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings
        
        Returns:
            Similarity score between 0 and 1
        """        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Convert to 0-1 range
        return float((similarity + 1) / 2)
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored embeddings"""
        stats = {
            'total_embeddings': 0,
            'by_month': {},
            'total_size_mb': 0
        }
        
        for month_dir in self.embeddings_path.glob("*/"):
            if not month_dir.is_dir() or month_dir.name == 'index':
                continue
            
            month_embeddings = list(month_dir.glob("*.npy"))
            count = len(month_embeddings)
            size_mb = sum(f.stat().st_size for f in month_embeddings) / (1024 * 1024)
            
            stats['by_month'][month_dir.name] = count
            stats['total_embeddings'] += count
            stats['total_size_mb'] += size_mb
        
        return stats

# Example usage and testing
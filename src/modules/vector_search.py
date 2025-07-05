"""
🔍 LogSec 2.0 - Vector Search Engine
Semantic similarity search using FAISS for intelligent session discovery
"""

import faiss
import numpy as np
import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import sqlite3

from .embedding_engine import EmbeddingEngine

class VectorSearchEngine:
    """FAISS-based semantic search for LogSec sessions"""
    
    def __init__(self, dimension: int = 384):
        """Initialize vector search engine
        
        Args:
            dimension: Embedding dimension (must match EmbeddingEngine)
        """
        self.logger = logging.getLogger('VectorSearchEngine')
        self.dimension = dimension
        
        # Initialize FAISS index (start with Flat L2 for accuracy)
        self.index = faiss.IndexFlatL2(dimension)
        self.logger.info(f"Initialized FAISS IndexFlatL2 with dimension {dimension}")
        
        # Session ID mapping (FAISS index position -> session_id)
        self.id_map = []
        self.session_metadata = {}
        
        # Paths
        self.index_path = Path(r"C:\LogSec\knowledge\embeddings\index\faiss.index")
        self.metadata_path = Path(r"C:\LogSec\knowledge\embeddings\index\metadata.json")
        self.graph_db_path = Path(r"C:\LogSec\knowledge\graph_memory\knowledge_graph.db")
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata from disk"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_path))
                
                # Load metadata
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.id_map = data['id_map']
                    self.session_metadata = data['session_metadata']
                
                self.logger.info(f"Loaded index with {len(self.id_map)} vectors")
            except Exception as e:
                self.logger.error(f"Error loading index: {e}")
                self.index = faiss.IndexFlatL2(self.dimension)
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Ensure directory exists
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            metadata = {
                'id_map': self.id_map,
                'session_metadata': self.session_metadata,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Saved index with {len(self.id_map)} vectors")
        except Exception as e:
            self.logger.error(f"Error saving index: {e}")
    
    def add_vector(self, session_id: str, embedding: np.ndarray, metadata: Optional[Dict] = None):
        """Add a single vector to the index
        
        Args:
            session_id: Unique session identifier
            embedding: Embedding vector
            metadata: Optional metadata for the session
        """        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))
        
        # Update mappings
        self.id_map.append(session_id)
        if metadata:
            self.session_metadata[session_id] = metadata
        
        self.logger.debug(f"Added vector for session {session_id}")
    
    def add_vectors(self, embeddings: List[Tuple[str, np.ndarray]], metadata_dict: Optional[Dict[str, Dict]] = None):
        """Add multiple vectors to the index in batch
        
        Args:
            embeddings: List of (session_id, embedding) tuples
            metadata_dict: Optional dict of session_id -> metadata
        """
        if not embeddings:
            return
        
        # Prepare batch
        vectors = np.array([emb[1] for emb in embeddings])
        session_ids = [emb[0] for emb in embeddings]
        
        # Add to FAISS
        self.index.add(vectors)
        
        # Update mappings
        self.id_map.extend(session_ids)
        if metadata_dict:
            self.session_metadata.update(metadata_dict)
        
        self.logger.info(f"Added {len(embeddings)} vectors to index")
    
    def update_vector(self, session_id: str, new_embedding: np.ndarray, metadata: Optional[Dict] = None):
        """Update an existing vector in the index
        
        For FAISS Flat index, we need to rebuild since there's no direct update.
        This is fine for small-medium datasets.
        """
        try:
            if session_id in self.id_map:
                # Find index
                idx = self.id_map.index(session_id)
                
                # For larger datasets, consider using IndexIDMap for direct updates
                # For now, we'll mark for rebuild
                self.logger.info(f"Vector update for {session_id} - marking for rebuild")
                
                # Update metadata immediately
                if metadata:
                    self.session_metadata[session_id] = metadata
                
                # For immediate effect, rebuild index
                # In production, this could be batched
                self.rebuild_index_from_embeddings()
            else:
                # Not in index, just add it
                self.add_vector(session_id, new_embedding, metadata)
                
        except Exception as e:
            self.logger.error(f"Error updating vector: {e}")
    
    def search_similar(self, query_embedding: np.ndarray, k: int = 5, threshold: float = 0.0) -> List[Tuple[str, float, Dict]]:
        """Find k most similar sessions to query
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            threshold: Minimum similarity threshold (0-1, higher = more similar)
            
        Returns:
            List of (session_id, similarity_score, metadata) tuples
        """
        if self.index.ntotal == 0:
            self.logger.warning("Index is empty")
            return []
        
        # Search in FAISS (returns L2 distances)
        distances, indices = self.index.search(query_embedding.reshape(1, -1), min(k, self.index.ntotal))
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for not found
                continue
            
            # Convert L2 distance to similarity score (0-1)
            # Lower distance = higher similarity
            similarity = 1 / (1 + dist)
            
            if similarity >= threshold:
                session_id = self.id_map[idx]
                metadata = self.session_metadata.get(session_id, {})
                results.append((session_id, similarity, metadata))
        
        return results
    
    def search_by_session_id(self, session_id: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Find sessions similar to a given session ID
        
        Args:
            session_id: Source session ID
            k: Number of similar sessions to find
            
        Returns:
            List of similar sessions (excluding the source)
        """
        # Load embedding for session
        engine = EmbeddingEngine()
        embedding = engine.load_embedding(session_id)
        
        if embedding is None:
            self.logger.error(f"No embedding found for session {session_id}")
            return []
        
        # Search for similar
        results = self.search_similar(embedding, k + 1)  # +1 to exclude self
        
        # Filter out the source session
        return [(sid, score, meta) for sid, score, meta in results if sid != session_id]    
    def rebuild_index_from_embeddings(self):
        """Rebuild the entire index from stored embeddings"""
        self.logger.info("Rebuilding index from embeddings...")
        
        # Clear current index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = []
        self.session_metadata = {}
        
        # Load all embeddings
        engine = EmbeddingEngine()
        embeddings_path = Path(r"C:\LogSec\knowledge\embeddings")
        
        embeddings_to_add = []
        metadata_dict = {}
        
        for month_dir in embeddings_path.glob("*/"):
            if not month_dir.is_dir() or month_dir.name == 'index':
                continue
            
            for embedding_file in month_dir.glob("*.npy"):
                session_id = embedding_file.stem
                try:
                    # Load embedding
                    embedding = np.load(embedding_file)
                    embeddings_to_add.append((session_id, embedding))
                    
                    # Load metadata if exists
                    metadata_file = embedding_file.with_suffix('.json')
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata_dict[session_id] = json.load(f)
                    
                except Exception as e:
                    self.logger.error(f"Error loading {session_id}: {e}")
        
        # Add all to index
        if embeddings_to_add:
            self.add_vectors(embeddings_to_add, metadata_dict)
            self._save_index()
            self.logger.info(f"Rebuilt index with {len(embeddings_to_add)} vectors")
        else:
            self.logger.warning("No embeddings found to rebuild index")
    
    def get_statistics(self) -> Dict:
        """Get search index statistics"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': 'IndexFlatL2',
            'memory_usage_mb': (self.index.ntotal * self.dimension * 4) / (1024 * 1024),
            'sessions_indexed': len(self.id_map),
            'has_metadata': len(self.session_metadata)
        }
    
    def auto_link_similar_sessions(self, session_id: str, similarity_threshold: float = 0.75):
        """Automatically create relationships in graph DB for similar sessions
        
        Args:
            session_id: Session to find links for
            similarity_threshold: Minimum similarity to create link
        """
        similar = self.search_by_session_id(session_id, k=10)
        
        if not similar:
            return 0
        
        # Connect to graph database
        conn = sqlite3.connect(str(self.graph_db_path))
        cursor = conn.cursor()
        
        links_created = 0
        for similar_id, similarity, _ in similar:
            if similarity >= similarity_threshold:
                try:
                    # Get entity IDs for both sessions
                    cursor.execute('SELECT id FROM entities WHERE metadata LIKE ?', (f'%"{session_id}"%',))
                    source_entities = cursor.fetchall()
                    
                    cursor.execute('SELECT id FROM entities WHERE metadata LIKE ?', (f'%"{similar_id}"%',))
                    target_entities = cursor.fetchall()
                    
                    # Create similarity relationships
                    for source in source_entities:
                        for target in target_entities:
                            cursor.execute('''
                                INSERT OR IGNORE INTO relationships 
                                (source_id, target_id, relationship_type, strength)
                                VALUES (?, ?, 'similarity', ?)
                            ''', (source[0], target[0], similarity))
                            links_created += 1
                    
                except Exception as e:
                    self.logger.error(f"Error creating link: {e}")
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Created {links_created} similarity links for session {session_id}")
        return links_created

# Example usage and testing
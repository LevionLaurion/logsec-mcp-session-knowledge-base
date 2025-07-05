"""
🏷️ Extended Auto-Tagger for LogSec 3.0
Integrates Knowledge Type Classification with existing auto-tagging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auto_tagger import AutoTagger
from modules.knowledge_type_classifier import KnowledgeTypeClassifier
from typing import List, Tuple, Dict
import sqlite3
import logging

logger = logging.getLogger(__name__)

class ExtendedAutoTagger(AutoTagger):
    """Extended auto-tagger with Knowledge Type Classification"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.knowledge_classifier = KnowledgeTypeClassifier()
        self._update_database_schema()
    
    def _update_database_schema(self):
        """Update database schema for knowledge types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Add knowledge_type column to session_metadata if not exists
            cursor.execute('''
                PRAGMA table_info(session_metadata)
            ''')
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'knowledge_type' not in columns:
                cursor.execute('''
                    ALTER TABLE session_metadata 
                    ADD COLUMN knowledge_type TEXT DEFAULT 'implementation'
                ''')
                logger.info("Added knowledge_type column to session_metadata")
            
            # Create knowledge_types table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default knowledge types
            for k_type in self.knowledge_classifier.get_knowledge_types():
                cursor.execute('''
                    INSERT OR IGNORE INTO knowledge_types (type_name, description)
                    VALUES (?, ?)
                ''', (k_type, self.knowledge_classifier.get_type_description(k_type)))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating database schema: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def classify_and_tag(self, session_id: str, content: str, max_tags: int = 5) -> Dict[str, any]:
        """
        Classify knowledge type and generate tags
        Returns dict with knowledge_type, tags, and metadata
        """
        # Get knowledge type classification
        knowledge_type, confidence = self.knowledge_classifier.classify_knowledge_type(content)
        
        # Get regular tags
        tags_with_scores = self.generate_tags(content, max_tags)
        
        # Save to database
        self._save_knowledge_type(session_id, knowledge_type, confidence)
        self.save_tags(session_id, tags_with_scores)
        
        return {
            'knowledge_type': knowledge_type,
            'type_confidence': confidence,
            'tags': tags_with_scores,
            'analysis': self.knowledge_classifier.analyze_content_structure(content)
        }
    
    def _save_knowledge_type(self, session_id: str, knowledge_type: str, confidence: float):
        """Save knowledge type classification to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update session metadata
            cursor.execute('''
                UPDATE session_metadata
                SET knowledge_type = ?
                WHERE id = ?
            ''', (knowledge_type, session_id))
            
            # Update usage count
            cursor.execute('''
                UPDATE knowledge_types
                SET usage_count = usage_count + 1
                WHERE type_name = ?
            ''', (knowledge_type,))
            
            conn.commit()
            logger.info(f"Saved knowledge type '{knowledge_type}' for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving knowledge type: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_sessions_by_type(self, knowledge_type: str, limit: int = 10) -> List[Dict]:
        """Get sessions by knowledge type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, project, timestamp, summary
            FROM session_metadata
            WHERE knowledge_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (knowledge_type, limit))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'project': row[1],
                'timestamp': row[2],
                'summary': row[3]
            })
        
        conn.close()
        return sessions
    
    def get_knowledge_type_stats(self) -> List[Dict]:
        """Get statistics for all knowledge types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT kt.type_name, kt.description, kt.usage_count,
                   COUNT(sm.id) as session_count
            FROM knowledge_types kt
            LEFT JOIN session_metadata sm ON kt.type_name = sm.knowledge_type
            GROUP BY kt.type_name
            ORDER BY session_count DESC
        ''')
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                'type': row[0],
                'description': row[1],
                'usage_count': row[2],
                'session_count': row[3]
            })
        
        conn.close()
        return stats


# Integration function for logsec_core_v3.py
def classify_and_tag_session(session_id: str, content: str, project: str = None) -> Dict[str, any]:
    """
    Classify knowledge type and auto-tag a session
    This is the main integration point for lo_save
    """
    tagger = ExtendedAutoTagger()
    result = tagger.classify_and_tag(session_id, content)
    
    # Log the classification
    logger.info(f"Session {session_id} classified as '{result['knowledge_type']}' "
                f"with confidence {result['type_confidence']:.2f}")
    
    return result
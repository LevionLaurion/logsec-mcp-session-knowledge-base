"""
🏷️ LogSec 2.0 Auto-Tagging Engine
Automatically generates relevant tags for sessions using ML
"""

import numpy as np
from typing import List, Dict, Set, Tuple
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import sqlite3
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoTagger:
    """Intelligent auto-tagging for LogSec sessions"""
    
    def __init__(self, db_path: str = r"C:\LogSec\logsec_brain.db", graph_db_path: str = r"C:\LogSec\knowledge\graph_memory\knowledge_graph.db"):
        self.db_path = db_path
        self.graph_db_path = graph_db_path
        self.tfidf = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.lda = LatentDirichletAllocation(
            n_components=10,
            random_state=42
        )
        self.tag_patterns = self._initialize_tag_patterns()
        self.existing_tags = self._load_existing_tags()
        
    def _initialize_tag_patterns(self) -> Dict[str, List[str]]:
        """Initialize pattern-based tag detection"""
        return {
            # Technology tags
            'python': [r'\bpython\b', r'\.py\b', r'\bpip\b', r'\bdjango\b', r'\bflask\b'],
            'javascript': [r'\bjavascript\b', r'\.js\b', r'\bnode\b', r'\breact\b', r'\bvue\b'],
            'database': [r'\bsql\b', r'\bdatabase\b', r'\bpostgres\b', r'\bmysql\b', r'\bsqlite\b'],
            'ml': [r'\bmachine learning\b', r'\bml\b', r'\bneural\b', r'\bmodel\b', r'\btraining\b'],
            'ai': [r'\bai\b', r'\bartificial intelligence\b', r'\bgpt\b', r'\bllm\b', r'\bclaude\b'],
            'logsec': [r'\blogsec\b', r'\blaurion\b', r'\bknowledge\b', r'\bgraph\b'],
            
            # Project phases
            'planning': [r'\bplan\b', r'\broadmap\b', r'\bstrategy\b', r'\bdesign\b'],
            'implementation': [r'\bimplement\b', r'\bcoding\b', r'\bdevelop\b', r'\bbuild\b'],
            'testing': [r'\btest\b', r'\bdebug\b', r'\bfix\b', r'\bqa\b'],
            'deployment': [r'\bdeploy\b', r'\brelease\b', r'\bproduction\b', r'\blive\b'],
            
            # Importance indicators
            'breakthrough': [r'\bbreakthrough\b', r'\bmajor\b', r'\bsuccess\b', r'\bachieved\b'],
            'issue': [r'\bissue\b', r'\bproblem\b', r'\berror\b', r'\bbug\b', r'\bfail\b'],
            'todo': [r'\btodo\b', r'\bnext\b', r'\bupcoming\b', r'\bplan to\b'],
            
            # LogSec specific
            'embedding': [r'\bembedding\b', r'\bvector\b', r'\bsemantic\b'],
            'search': [r'\bsearch\b', r'\bfaiss\b', r'\bsimilarity\b'],
            'analytics': [r'\banalytics\b', r'\bmetrics\b', r'\bdashboard\b'],
        }
    
    def _load_existing_tags(self) -> Set[str]:
        """Load all existing tags from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tags table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag TEXT UNIQUE NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create session_tags junction table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_tags (
                    session_id TEXT NOT NULL,
                    tag_id INTEGER NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    FOREIGN KEY (session_id) REFERENCES sessions(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id),
                    PRIMARY KEY (session_id, tag_id)
                )
            ''')
            
            cursor.execute("SELECT tag FROM tags")
            tags = {row[0] for row in cursor.fetchall()}
            conn.close()
            return tags
        except Exception as e:
            logger.error(f"Error loading tags: {e}")
            return set()
    
    def generate_tags(self, text: str, max_tags: int = 5) -> List[Tuple[str, float]]:
        """Generate tags for a session with confidence scores"""
        tags_with_scores = []
        
        # 1. Pattern-based tags
        pattern_tags = self._extract_pattern_tags(text)
        tags_with_scores.extend(pattern_tags)
        
        # 2. Entity extraction tags (simplified without spaCy)
        entity_tags = self._extract_entity_tags(text)
        tags_with_scores.extend(entity_tags)
        
        # 3. Topic modeling tags
        topic_tags = self._extract_topic_tags(text)
        tags_with_scores.extend(topic_tags)
        
        # 4. Keyword extraction tags
        keyword_tags = self._extract_keyword_tags(text)
        tags_with_scores.extend(keyword_tags)
        
        # Combine and rank tags
        tag_scores = {}
        for tag, score in tags_with_scores:
            if tag in tag_scores:
                tag_scores[tag] = max(tag_scores[tag], score)
            else:
                tag_scores[tag] = score
        
        # Sort by score and return top tags
        sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:max_tags]
    
    def _extract_pattern_tags(self, text: str) -> List[Tuple[str, float]]:
        """Extract tags based on regex patterns"""
        tags = []
        text_lower = text.lower()
        
        for tag, patterns in self.tag_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    tags.append((tag, 0.8))
                    break
        
        return tags
    
    def _extract_entity_tags(self, text: str) -> List[Tuple[str, float]]:
        """Extract entity tags without spaCy"""
        tags = []
        
        # Extract file names
        file_pattern = r'([A-Za-z_]+\.(py|js|cs|md|txt|json|yaml|yml))'
        files = re.findall(file_pattern, text)
        for file, _ in files[:3]:  # Limit to 3 files
            tags.append((file.lower().replace('.', '_'), 0.7))
        
        # Extract version numbers
        version_pattern = r'v(\d+\.\d+(?:\.\d+)?)'
        versions = re.findall(version_pattern, text.lower())
        for version in versions[:2]:
            tags.append((f'v{version}', 0.6))
        
        # Extract uppercase acronyms
        acronym_pattern = r'\b([A-Z]{2,})\b'
        acronyms = re.findall(acronym_pattern, text)
        for acronym in acronyms[:3]:
            if len(acronym) <= 5:  # Reasonable acronym length
                tags.append((acronym.lower(), 0.5))
        
        return tags
    
    def _extract_topic_tags(self, text: str) -> List[Tuple[str, float]]:
        """Extract tags using topic modeling"""
        try:
            # Simple keyword frequency approach
            words = re.findall(r'\b[a-z]{4,}\b', text.lower())
            word_freq = Counter(words)
            
            # Filter common words
            common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'will', 'what', 'when', 'where', 'which', 'their', 'there', 'these', 'those'}
            
            tags = []
            for word, count in word_freq.most_common(10):
                if word not in common_words and count > 1:
                    tags.append((word, 0.5))
            
            return tags[:3]
        except:
            return []
    
    def _extract_keyword_tags(self, text: str) -> List[Tuple[str, float]]:
        """Extract keywords using simple heuristics"""
        try:
            # Extract compound terms
            compound_pattern = r'\b([a-z]+[-_][a-z]+)\b'
            compounds = re.findall(compound_pattern, text.lower())
            
            tags = []
            for compound in compounds[:5]:
                if len(compound) > 3:
                    tags.append((compound.replace('-', '_'), 0.6))
            
            return tags
        except:
            return []
    
    def save_tags(self, session_id: str, tags: List[Tuple[str, float]]):
        """Save tags to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for tag, confidence in tags:
                # Insert or update tag
                cursor.execute('''
                    INSERT INTO tags (tag) VALUES (?)
                    ON CONFLICT(tag) DO UPDATE SET usage_count = usage_count + 1
                ''', (tag,))
                
                # Get tag ID
                cursor.execute("SELECT id FROM tags WHERE tag = ?", (tag,))
                tag_id = cursor.fetchone()[0]
                
                # Link tag to session
                cursor.execute('''
                    INSERT OR REPLACE INTO session_tags (session_id, tag_id, confidence)
                    VALUES (?, ?, ?)
                ''', (session_id, tag_id, confidence))
            
            conn.commit()
            logger.info(f"Saved {len(tags)} tags for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving tags: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_session_tags(self, session_id: str) -> List[Dict[str, any]]:
        """Get all tags for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.tag, st.confidence
            FROM session_tags st
            JOIN tags t ON st.tag_id = t.id
            WHERE st.session_id = ?
            ORDER BY st.confidence DESC
        ''', (session_id,))
        
        tags = [{'tag': row[0], 'confidence': row[1]} for row in cursor.fetchall()]
        conn.close()
        return tags
    
    def retag_all_sessions(self):
        """Retag all existing sessions"""
        conn = sqlite3.connect(self.graph_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT session_id, summary FROM sessions")
        sessions = cursor.fetchall()
        conn.close()
        
        logger.info(f"Retagging {len(sessions)} sessions...")
        
        for session_id, content in sessions:
            tags = self.generate_tags(content)
            self.save_tags(session_id, tags)
        
        logger.info("Retagging complete!")
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, any]]:
        """Get most popular tags"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tag, usage_count
            FROM tags
            ORDER BY usage_count DESC
            LIMIT ?
        ''', (limit,))
        
        tags = [{'tag': row[0], 'count': row[1]} for row in cursor.fetchall()]
        conn.close()
        return tags


# Integration function for logsec_core.py
def auto_tag_session(session_id: str, content: str) -> List[str]:
    """Auto-tag a session and return tag list"""
    tagger = AutoTagger()
    tags_with_scores = tagger.generate_tags(content)
    tagger.save_tags(session_id, tags_with_scores)
    return [tag for tag, _ in tags_with_scores]
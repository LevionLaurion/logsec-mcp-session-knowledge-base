"""
ML Analytics Engine for LogSec 2.0
Provides clustering, productivity analysis, and knowledge gap detection

Created: 2025-07-04
Author: Felix (via Claude Opus 4)
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import os
from pathlib import Path
import sqlite3
from collections import defaultdict, Counter

from .embedding_engine import EmbeddingEngine


class MLAnalytics:
    """Machine Learning Analytics for LogSec sessions"""
    
    def __init__(self, db_path: str = r"C:\LogSec\knowledge\graph_memory\knowledge_graph.db"):
        self.db_path = db_path
        self.embedding_engine = EmbeddingEngine()
        self.clustering_model = None
        self.productivity_model = None
        self.cache_dir = Path(r"C:\LogSec\knowledge\ml_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Analytics results cache
        self.cluster_cache = None
        self.last_cluster_update = None
        
    def cluster_sessions(self, n_clusters: int = 5, force_update: bool = False) -> Dict[str, int]:
        """
        Cluster all sessions into knowledge domains
        Returns mapping of session_id -> cluster_id
        """
        # Check cache first
        cache_file = self.cache_dir / "clusters.json"
        if not force_update and cache_file.exists():
            # Check if cache is less than 24 hours old
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=24):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        print(f"[ML Analytics] Clustering sessions into {n_clusters} domains...")
        
        # Get all embeddings
        embeddings, session_ids = self._load_all_embeddings()
        
        if len(embeddings) < n_clusters:
            print(f"[ML Analytics] Not enough sessions ({len(embeddings)}) for {n_clusters} clusters")
            n_clusters = max(2, len(embeddings) // 2)
        
        # Perform clustering
        self.clustering_model = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = self.clustering_model.fit_predict(embeddings)
        
        # Create mapping
        cluster_map = {session_ids[i]: int(cluster_labels[i]) 
                      for i in range(len(session_ids))}
        
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(cluster_map, f)        
        # Analyze cluster characteristics
        self._analyze_clusters(embeddings, cluster_labels, session_ids)
        
        print(f"[ML Analytics] Clustered {len(session_ids)} sessions into {n_clusters} domains")
        return cluster_map
    
    def _load_all_embeddings(self) -> Tuple[np.ndarray, List[str]]:
        """Load all embeddings from file system"""
        embeddings = []
        session_ids = []
        
        # Get embeddings directory
        embeddings_dir = Path(r"C:\LogSec\knowledge\embeddings")
        
        if not embeddings_dir.exists():
            print("[ML Analytics] No embeddings directory found")
            return np.array([]), []
        
        # Walk through all .npy files
        for year_month_dir in embeddings_dir.iterdir():
            if year_month_dir.is_dir():
                for embedding_file in year_month_dir.glob("*.npy"):
                    try:
                        # Load embedding
                        embedding = np.load(embedding_file)
                        embeddings.append(embedding)
                        # Extract session_id from filename
                        session_id = embedding_file.stem  # Remove .npy extension
                        session_ids.append(session_id)
                    except Exception as e:
                        print(f"[ML Analytics] Failed to load {embedding_file}: {e}")
        
        if not embeddings:
            print("[ML Analytics] No embeddings found in file system")
            return np.array([]), []
            
        return np.array(embeddings), session_ids
    
    def _analyze_clusters(self, embeddings: np.ndarray, labels: np.ndarray, session_ids: List[str]):
        """Analyze and name clusters based on content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cluster_info = defaultdict(lambda: {"sessions": [], "keywords": []})
        
        for i, (session_id, label) in enumerate(zip(session_ids, labels)):
            # Get session content
            cursor.execute("SELECT summary FROM sessions WHERE session_id = ?", (session_id,))
            result = cursor.fetchone()
            if result:
                summary = result[0]
                cluster_info[int(label)]["sessions"].append(session_id)
                # Extract keywords (simple approach - could be improved)
                words = summary.lower().split()
                cluster_info[int(label)]["keywords"].extend(words)
        
        # Analyze each cluster
        cluster_analysis = {}
        for cluster_id, info in cluster_info.items():
            # Find most common keywords
            word_freq = Counter(info["keywords"])
            # Filter out common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            top_keywords = [word for word, _ in word_freq.most_common(10) 
                          if word not in stop_words and len(word) > 3]            
            cluster_analysis[cluster_id] = {
                "size": len(info["sessions"]),
                "top_keywords": top_keywords[:5],
                "sample_sessions": info["sessions"][:3]
            }
        
        # Save cluster analysis
        analysis_file = self.cache_dir / "cluster_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(cluster_analysis, f, indent=2)
        
        conn.close()
    
    def predict_productivity(self, time_of_day: Optional[int] = None, 
                           day_of_week: Optional[int] = None) -> Dict[str, float]:
        """
        Predict productivity based on time patterns
        Returns productivity score and insights
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session data with timestamps
        cursor.execute("""
            SELECT timestamp, summary, LENGTH(summary) as length
            FROM sessions
            ORDER BY timestamp DESC
            LIMIT 1000
        """)
        
        data = []
        for timestamp, summary, length in cursor.fetchall():
            dt = datetime.fromisoformat(timestamp)
            data.append({
                'hour': dt.hour,
                'weekday': dt.weekday(),
                'length': length,
                'timestamp': timestamp
            })
        
        conn.close()
        
        if not data:
            return {"score": 0.5, "confidence": "low", "insights": "No data available"}
        
        df = pd.DataFrame(data)
        
        # Analyze productivity patterns
        hourly_avg = df.groupby('hour')['length'].mean()
        daily_avg = df.groupby('weekday')['length'].mean()
        
        # Normalize scores
        hourly_scores = (hourly_avg - hourly_avg.min()) / (hourly_avg.max() - hourly_avg.min() + 1)
        daily_scores = (daily_avg - daily_avg.min()) / (daily_avg.max() - daily_avg.min() + 1)        
        # Get current or specified time
        if time_of_day is None:
            time_of_day = datetime.now().hour
        if day_of_week is None:
            day_of_week = datetime.now().weekday()
        
        # Calculate productivity score
        hour_score = hourly_scores.get(time_of_day, 0.5)
        day_score = daily_scores.get(day_of_week, 0.5)
        combined_score = (hour_score + day_score) / 2
        
        # Generate insights
        best_hour = hourly_avg.idxmax()
        best_day = daily_avg.idxmax()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        insights = f"Your most productive time is {best_hour}:00 on {days[best_day]}s. "
        
        if combined_score > 0.7:
            insights += "This is one of your peak productivity periods!"
        elif combined_score < 0.3:
            insights += "This tends to be a lower productivity period for you."
        
        return {
            "score": float(combined_score),
            "hour_score": float(hour_score),
            "day_score": float(day_score),
            "confidence": "high" if len(data) > 100 else "medium" if len(data) > 30 else "low",
            "insights": insights,
            "best_hour": int(best_hour),
            "best_day": days[best_day],
            "data_points": len(data)
        }
    
    def detect_knowledge_gaps(self, min_sessions: int = 3) -> List[Dict[str, any]]:
        """
        Detect areas with low coverage or stale knowledge
        Returns list of potential knowledge gaps
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get project activity
        cursor.execute("""
            SELECT project, COUNT(*) as count, MAX(timestamp) as last_update
            FROM sessions
            GROUP BY project
        """)
        
        project_data = cursor.fetchall()
        
        # Get entity activity (simplified without entity_facts)
        cursor.execute("""
            SELECT e.name, e.type, COUNT(DISTINCT e.id) as mentions
            FROM entities e
            GROUP BY e.name, e.type
        """)
        
        entity_data = cursor.fetchall()
        
        conn.close()
        
        gaps = []
        now = datetime.now()
        
        # Analyze projects
        for project, count, last_update in project_data:
            if last_update:
                days_since = (now - datetime.fromisoformat(last_update)).days
                if days_since > 14:  # No activity in 2 weeks
                    gaps.append({
                        "type": "stale_project",
                        "name": project,
                        "severity": "high" if days_since > 30 else "medium",
                        "days_inactive": days_since,
                        "session_count": count,
                        "recommendation": f"Project '{project}' hasn't been updated in {days_since} days"
                    })
        
        # Analyze entities
        entity_gaps = defaultdict(int)
        for name, entity_type, mentions in entity_data:
            if mentions and mentions < min_sessions:
                entity_gaps[entity_type] += 1
        
        # Report entity type gaps
        for entity_type, count in entity_gaps.items():
            if count > 3:  # Multiple entities of same type have low coverage
                gaps.append({
                    "type": "low_coverage",
                    "name": f"{entity_type} entities",
                    "severity": "medium",
                    "count": count,
                    "recommendation": f"{count} {entity_type} entities have less than {min_sessions} sessions"
                })
        
        # Check for imbalanced clusters
        cluster_map = self.cluster_sessions(force_update=False)
        if cluster_map:
            cluster_sizes = Counter(cluster_map.values())
            avg_size = sum(cluster_sizes.values()) / len(cluster_sizes)
            
            for cluster_id, size in cluster_sizes.items():
                if size < avg_size * 0.3:  # Cluster is less than 30% of average
                    gaps.append({                        "type": "small_cluster",
                        "name": f"Knowledge cluster {cluster_id}",
                        "severity": "low",
                        "size": size,
                        "recommendation": f"Cluster {cluster_id} has only {size} sessions (avg: {avg_size:.1f})"
                    })
        
        return sorted(gaps, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])
    
    def get_analytics_dashboard(self) -> Dict[str, any]:
        """
        Get comprehensive analytics dashboard data
        """
        print("[ML Analytics] Generating analytics dashboard...")
        
        # Get productivity analysis
        productivity = self.predict_productivity()
        
        # Get knowledge gaps
        gaps = self.detect_knowledge_gaps()
        
        # Get cluster information
        cluster_map = self.cluster_sessions(force_update=False)
        cluster_stats = {}
        
        if cluster_map:
            cluster_counts = Counter(cluster_map.values())
            
            # Load cluster analysis if available
            analysis_file = self.cache_dir / "cluster_analysis.json"
            if analysis_file.exists():
                with open(analysis_file, 'r') as f:
                    cluster_analysis = json.load(f)
                
                for cluster_id, count in cluster_counts.items():
                    cluster_info = cluster_analysis.get(str(cluster_id), {})
                    cluster_stats[f"Cluster {cluster_id}"] = {
                        "size": count,
                        "keywords": cluster_info.get("top_keywords", []),
                        "percentage": f"{(count / len(cluster_map)) * 100:.1f}%"
                    }
        
        # Get recent trends
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions per day for last 30 days
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM sessions
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        """)
        
        daily_activity = {row[0]: row[1] for row in cursor.fetchall()}        
        # Get total statistics
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        total_entities = cursor.fetchone()[0]
        
        # Count embeddings from file system
        embeddings_dir = Path(r"C:\LogSec\knowledge\embeddings")
        total_embeddings = 0
        if embeddings_dir.exists():
            for year_month_dir in embeddings_dir.iterdir():
                if year_month_dir.is_dir():
                    total_embeddings += len(list(year_month_dir.glob("*.npy")))
        
        conn.close()
        
        dashboard = {
            "overview": {
                "total_sessions": total_sessions,
                "total_entities": total_entities,
                "total_embeddings": total_embeddings,
                "embedding_coverage": f"{(total_embeddings / total_sessions * 100):.1f}%" if total_sessions > 0 else "0%"
            },
            "productivity": productivity,
            "knowledge_gaps": gaps[:5],  # Top 5 gaps
            "clusters": cluster_stats,
            "daily_activity": daily_activity,
            "insights": self._generate_insights(productivity, gaps, cluster_stats)
        }
        
        return dashboard
    
    def _generate_insights(self, productivity: Dict, gaps: List[Dict], clusters: Dict) -> List[str]:
        """Generate actionable insights from analytics"""
        insights = []
        
        # Productivity insights
        if productivity["score"] > 0.7:
            insights.append(f"You're in a high productivity period! Best time: {productivity['best_hour']}:00")
        
        # Gap insights
        if gaps:
            high_severity = [g for g in gaps if g["severity"] == "high"]
            if high_severity:
                insights.append(f"⚠️ {len(high_severity)} critical knowledge gaps detected")
        
        # Cluster insights
        if clusters:
            sizes = [c["size"] for c in clusters.values()]
            if sizes:
                largest = max(sizes)
                smallest = min(sizes)
                if largest > smallest * 5:
                    insights.append("Knowledge distribution is unbalanced - consider exploring underrepresented areas")
        
        # Time-based insight
        hour = datetime.now().hour
        if 22 <= hour or hour <= 2:
            insights.append("Late night session - remember to maintain healthy work-life balance")
        elif 5 <= hour <= 7:
            insights.append("Early bird! Morning sessions often lead to clearer thinking")
        
        return insights


# Test function
# LogSec 3.0 - Minimalistisches Tier System Konzept

## Vision
Transformation von LogSec zu einem fokussierten 3-Tier Knowledge System mit nur den essentiellen Features.

## Architektur

### Tier-System
```
Tier 1 (Working Memory): Letzte Session für nahtlose Fortsetzung
Tier 2 (Project Context): Persistente Projekt-Dokumentation (IMMER dabei)
Tier 3 (Knowledge Base): Strukturiertes Fachwissen (Vector Search in DB)
  └── Intelligente Suche statt manuelle Subtiers
```

## Kern-Befehle

### 1. lo_load - Intelligentes Laden (für Claude)
```bash
lo_load project         # Tier 2 + Tier 1 Summary
lo_load project "query" # Tier 2 + semantische Suche in Tier 3 (Vector DB)
```

**Zwei Modi:**
- **Modus 1**: `lo_load logsec` → Tier 2 (Projekt-Kontext) + Tier 1 (Recent Sessions)
- **Modus 2**: `lo_load logsec "API"` → Tier 2 (Projekt-Kontext) + Tier 3 (Vector Search)

### 2. lo_start - Session Fortsetzen  
```bash
lo_start [project]      # Lädt nur Tier 1, öffnet Files, zeigt Status
```

### 3. lo_save vs lo_cont
```bash
lo_save "content"       # Extrahiert Wissen für Tier 3
lo_cont "content"       # Speichert Arbeitskontext für Fortsetzung
```

## Implementierungsplan

### Phase 1: Core Refactoring
- [ ] Tier 2 README System implementieren
- [ ] lo_cont mit strukturiertem Format
- [ ] Knowledge Type Classification

### Phase 2: Feature Integration
- [ ] Session Handoff erweitern
- [ ] Auto-Tagger für Knowledge Types
- [ ] Vereinfachte lo_load Logic

### Phase 3: Migration
- [ ] Bestehende Sessions klassifizieren
- [ ] README Generation aus alten Daten
- [ ] Cleanup alter Features

## Technische Details

### lo_cont Format
```
STATUS: Aktuelle Aufgabe
POSITION: file.py:line - method()
PROBLEM: Was blockiert
TRIED: Bisherige Versuche
NEXT: Nächste Schritte
TODO: Offene Punkte
CONTEXT: Zusätzlicher Kontext
```

### Neue Datenbank-Struktur
```sql
-- Tier 2 Storage
CREATE TABLE project_readme (
    project TEXT PRIMARY KEY,
    content TEXT,
    last_updated TIMESTAMP,
    version TEXT
);

-- Session Metadata erweitern
ALTER TABLE session_metadata ADD COLUMN knowledge_type TEXT;
-- Werte: 'continuation', 'api_doc', 'schema', 'implementation', 'milestone'
```

### Module-Nutzung
- **BEHALTEN**: Embedding, Vector Search, Handoff, Path Tracker
- **ANPASSEN**: Auto-Tagger für Knowledge Types
- **ENTFERNEN**: ML Analytics, Cross-lingual (vorerst)

## Migration Strategy
1. Feature Branch für LogSec 3.0
2. Schrittweise Implementation
3. Backward Compatibility während Übergang
4. Testing mit echten Projekten (LynnVest ideal)

## Erfolgs-Kriterien
- `lo_start` lädt in <1 Sekunde
- `lo_cont` erfasst alle relevanten Fortsetzungs-Infos
- Tier 2 bleibt stabil über Sessions
- Tier 3 ist suchbar und strukturiert

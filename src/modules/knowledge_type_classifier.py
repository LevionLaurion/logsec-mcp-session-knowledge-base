"""
🏷️ Knowledge Type Classifier for LogSec 3.0
Extension module for Issue #3 - Knowledge Type Classification
"""

from typing import Dict, Tuple, List
import re
import logging

logger = logging.getLogger(__name__)

class KnowledgeTypeClassifier:
    """Classifies content into knowledge types for Tier 3 organization"""
    
    def __init__(self):
        self.knowledge_type_patterns = self._initialize_knowledge_type_patterns()
        
    def _initialize_knowledge_type_patterns(self) -> Dict[str, Dict[str, any]]:
        """Initialize patterns for Knowledge Type Classification"""
        return {
            'continuation': {
                'patterns': [
                    r'\bSTATUS:\s*', r'\bPOSITION:\s*', r'\bNEXT:\s*', 
                    r'\bTODO:\s*', r'\bCONTEXT:\s*', r'\bPROBLEM:\s*',
                    r'\bTRIED:\s*', r'\bcontinue\s+with\b',
                    r'\bresume\s+from\b', r'\bleft\s+off\b'
                ],
                'weight': 1.0,
                'indicators': ['STATUS:', 'POSITION:', 'NEXT:', 'TODO:', 'PROBLEM:', 'TRIED:'],
                'description': 'Session continuation context for seamless handoff'
            },
            
            'api_doc': {
                'patterns': [
                    r'\bAPI\s+endpoint\b', r'\bREST\s+API\b', r'\bendpoint:\s*',
                    r'\bGET\s+/\w+', r'\bPOST\s+/\w+', r'\bPUT\s+/\w+', r'\bDELETE\s+/\w+',
                    r'\brequest\s+body\b', r'\bresponse\s+format\b', r'\bstatus\s+code\b',
                    r'\bauthentication\b', r'\bheaders:\s*', r'\bparameters:\s*',
                    r'\bOpenAPI\b', r'\bSwagger\b', r'\bGraphQL\b'
                ],
                'weight': 0.9,
                'indicators': ['endpoint:', 'request:', 'response:', 'authentication:', 'parameters:'],
                'description': 'API documentation and endpoint specifications'
            },
            
            'schema': {
                'patterns': [
                    r'\bschema\b', r'\bdata\s+structure\b', r'\btable\s+definition\b',
                    r'\bCREATE\s+TABLE\b', r'\binterface\s+\w+\s*{', r'\bclass\s+\w+:',
                    r'\btype\s+\w+\s*=', r'\bmodel\s+\w+\b', r'\bentity\s+\w+\b',
                    r'\bfields?:\s*', r'\bproperties:\s*', r'\battributes?:\s*',
                    r'\bJSON\s+schema\b', r'\bXML\s+schema\b', r'\bprotobuf\b'
                ],
                'weight': 0.9,
                'indicators': ['CREATE TABLE', 'interface ', 'class ', 'fields:', 'properties:', 'schema'],
                'description': 'Data structures, schemas, and type definitions'
            },
            
            'implementation': {
                'patterns': [
                    r'\bdef\s+\w+\(', r'\bfunction\s+\w+\(', r'\bclass\s+\w+[:\(]',
                    r'\bimplemented\s+\w+', r'\bcode\s+implementation\b',
                    r'\bmethod\s+\w+\b', r'\balgorithm\b', r'\bsolution:\s*',
                    r'```\w*\n', r'\bimport\s+\w+', r'\bfrom\s+\w+\s+import\b',
                    r'\bif\s+__name__\s*==\s*["\']__main__["\']'
                ],
                'weight': 0.8,
                'indicators': ['def ', 'function ', 'class ', 'import ', '```'],
                'description': 'Code implementations and algorithms'
            },
            
            'architecture': {
                'patterns': [
                    r'\barchitecture\b', r'\bsystem\s+design\b', r'\bcomponent\s+diagram\b',
                    r'\btier\s+\d+\b', r'\blayer\s+\w+\b', r'\bmodule\s+structure\b',
                    r'\bworkflow\b', r'\bdata\s+flow\b', r'\bintegration\s+points?\b',
                    r'\bdependencies:\s*', r'\binterfaces?\b', r'\bmicroservices?\b',
                    r'\bdesign\s+pattern\b', r'\bUML\b', r'\bdiagram\b'
                ],
                'weight': 0.85,
                'indicators': ['architecture', 'tier ', 'layer ', 'component', 'workflow', 'design'],
                'description': 'System architecture and design documents'
            },
            
            'milestone': {
                'patterns': [
                    r'\bmilestone\b', r'\bachieved\b', r'\bcompleted?\b',
                    r'\brelease\s+v?\d+', r'\bdeployed\b', r'\blaunched\b',
                    r'\bmajor\s+breakthrough\b', r'\bfinished\s+\w+\b',
                    r'\b✅\s*\w+', r'\bDONE:\s*', r'\bsuccess\w*\b',
                    r'\bdelivered\b', r'\bshipped\b', r'\baccomplished\b'
                ],
                'weight': 0.85,
                'indicators': ['milestone', 'completed', 'achieved', '✅', 'release', 'DONE:'],
                'description': 'Project milestones and achievements'
            },
            
            'error_solution': {
                'patterns': [
                    r'\berror:\s*', r'\bexception:\s*', r'\bfixed\s+\w+\b',
                    r'\bsolved\s+\w+\b', r'\bworkaround\b', r'\bbugfix\b',
                    r'\bissue\s+#\d+', r'\bproblem:\s*', r'\bsolution:\s*',
                    r'\btroubleshooting\b', r'\bdebug\w*\b', r'\bresolved\b',
                    r'\bstack\s+trace\b', r'\btraceback\b', r'\bfix:\s*'
                ],
                'weight': 0.8,
                'indicators': ['error:', 'exception:', 'fixed', 'solution:', 'resolved', 'traceback'],
                'description': 'Error messages and their solutions'
            },
            
            'research': {
                'patterns': [
                    r'\bresearch\b', r'\banalysis\b', r'\bfindings?\b',
                    r'\bexperiment\w*\b', r'\btest\s+results?\b', r'\bcomparison\b',
                    r'\bevaluation\b', r'\bbenchmark\w*\b', r'\bmetrics?\b',
                    r'\bconclusions?\b', r'\bobservations?\b', r'\bhypothesis\b',
                    r'\bstudy\b', r'\binvestigation\b', r'\bexploration\b'
                ],
                'weight': 0.75,
                'indicators': ['research', 'analysis', 'findings', 'results', 'conclusion', 'experiment'],
                'description': 'Research findings and analysis results'
            }
        }
    
    def classify_knowledge_type(self, text: str) -> Tuple[str, float]:
        """
        Classify the knowledge type of the content
        Returns: (knowledge_type, confidence_score)
        """
        scores = {}
        text_lower = text.lower()
        
        # Check each knowledge type
        for k_type, config in self.knowledge_type_patterns.items():
            score = 0.0
            matches = 0
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    matches += 1
                    
            # Check specific indicators (higher weight)
            indicator_matches = 0
            for indicator in config['indicators']:
                if indicator.lower() in text_lower:
                    indicator_matches += 1
            
            # Calculate score
            if matches > 0 or indicator_matches > 0:
                pattern_score = min(matches / len(config['patterns']), 1.0)
                indicator_score = min(indicator_matches / len(config['indicators']), 1.0)
                
                # Indicators have higher weight
                score = (pattern_score * 0.3 + indicator_score * 0.7) * config['weight']
                scores[k_type] = score
        
        # Return the highest scoring type, default to 'implementation' if unclear
        if not scores:
            return ('implementation', 0.5)
            
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type
    
    def get_knowledge_types(self) -> List[str]:
        """Get list of all available knowledge types"""
        return list(self.knowledge_type_patterns.keys())
    
    def get_type_description(self, knowledge_type: str) -> str:
        """Get description for a knowledge type"""
        if knowledge_type in self.knowledge_type_patterns:
            return self.knowledge_type_patterns[knowledge_type]['description']
        return "Unknown knowledge type"
    
    def analyze_content_structure(self, text: str) -> Dict[str, any]:
        """
        Analyze content and return detailed classification info
        """
        primary_type, confidence = self.classify_knowledge_type(text)
        
        # Get all scores for transparency
        all_scores = {}
        text_lower = text.lower()
        
        for k_type, config in self.knowledge_type_patterns.items():
            matches = sum(1 for pattern in config['patterns'] 
                         if re.search(pattern, text_lower))
            indicator_matches = sum(1 for indicator in config['indicators'] 
                                  if indicator.lower() in text_lower)
            
            all_scores[k_type] = {
                'pattern_matches': matches,
                'indicator_matches': indicator_matches,
                'total_patterns': len(config['patterns']),
                'total_indicators': len(config['indicators'])
            }
        
        return {
            'primary_type': primary_type,
            'confidence': confidence,
            'description': self.get_type_description(primary_type),
            'all_scores': all_scores,
            'content_length': len(text),
            'line_count': text.count('\n') + 1
        }


# Test the classifier
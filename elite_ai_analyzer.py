#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Elite AI Intelligence Analyzer
NLP | Facial Recognition | Entity Extraction | Relationship Mapping | Sentiment Analysis
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForTokenClassification,
    pipeline, AutoModelForSequenceClassification
)
import spacy
from spacy import displacy
import cv2
import face_recognition
import numpy as np
from PIL import Image
import io
import base64
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
import json
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import re
from neo4j import GraphDatabase
import asyncio
import aiohttp
from anthropic import Anthropic
from openai import AsyncOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Container for analysis results"""
    entities: List[Dict] = field(default_factory=list)
    relationships: List[Dict] = field(default_factory=list)
    sentiment: Dict = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    summary: str = ""
    key_phrases: List[str] = field(default_factory=list)
    language: str = "en"
    confidence: float = 0.0


class AdvancedNLPEngine:
    """Elite NLP processing with multiple models"""
    
    def __init__(self, model_name: str = "bert-base-cased"):
        logger.info("[*] Initializing Advanced NLP Engine...")
        
        # Load spaCy model
        self.nlp = spacy.load('en_core_web_lg')
        
        # Load transformer models
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # NER pipeline
        self.ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        
        # Sentiment analysis
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        
        # Zero-shot classification
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Relationship extraction model
        self.relation_extractor = pipeline(
            "text2text-generation",
            model="Babelscape/rebel-large"
        )
        
        logger.info("[+] NLP Engine initialized")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities with multiple methods"""
        entities = []
        
        # Method 1: spaCy
        doc = self.nlp(text)
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'method': 'spacy'
            })
        
        # Method 2: Transformer NER
        ner_results = self.ner_pipeline(text)
        for ent in ner_results:
            entities.append({
                'text': ent['word'],
                'label': ent['entity_group'],
                'score': ent['score'],
                'method': 'transformer'
            })
        
        # Deduplicate and merge
        return self.merge_entities(entities)
    
    def merge_entities(self, entities: List[Dict]) -> List[Dict]:
        """Merge overlapping entities from different methods"""
        merged = {}
        
        for ent in entities:
            key = ent['text'].lower()
            if key not in merged:
                merged[key] = ent
            else:
                # Update with higher confidence
                if 'score' in ent and ent['score'] > merged[key].get('score', 0):
                    merged[key] = ent
        
        return list(merged.values())
    
    def extract_relationships(self, text: str) -> List[Dict]:
        """Extract entity relationships using REBEL model"""
        try:
            # Generate relationship triples
            results = self.relation_extractor(
                text,
                max_length=512,
                num_beams=3,
                num_return_sequences=1
            )
            
            relationships = []
            
            for result in results:
                # Parse the generated text for relationship triples
                triples_text = result['generated_text']
                
                # Extract triples (subject, predicate, object)
                triple_pattern = r'\(([^,]+),\s*([^,]+),\s*([^)]+)\)'
                matches = re.findall(triple_pattern, triples_text)
                
                for subject, predicate, obj in matches:
                    relationships.append({
                        'subject': subject.strip(),
                        'predicate': predicate.strip(),
                        'object': obj.strip(),
                        'source': 'rebel'
                    })
            
            return relationships
            
        except Exception as e:
            logger.error(f"[!] Relationship extraction error: {str(e)}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Multi-level sentiment analysis"""
        
        # Overall sentiment
        overall = self.sentiment_pipeline(text[:512])[0]
        
        # Sentence-level sentiment
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        sentence_sentiments = []
        
        for sent in sentences[:20]:  # Limit to 20 sentences
            if len(sent) > 10:  # Skip very short sentences
                sent_result = self.sentiment_pipeline(sent[:512])[0]
                sentence_sentiments.append({
                    'text': sent,
                    'sentiment': sent_result['label'],
                    'score': sent_result['score']
                })
        
        # Calculate emotion distribution
        emotion_counts = Counter([s['sentiment'] for s in sentence_sentiments])
        
        return {
            'overall': overall,
            'sentences': sentence_sentiments,
            'distribution': dict(emotion_counts),
            'average_score': np.mean([s['score'] for s in sentence_sentiments]) if sentence_sentiments else 0
        }
    
    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """Extract key phrases using TF-IDF and NER"""
        doc = self.nlp(text)
        
        # Extract noun phrases
        noun_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 4:  # Max 4 words
                noun_phrases.append(chunk.text.lower())
        
        # Count frequencies
        phrase_counts = Counter(noun_phrases)
        
        # Get top phrases
        top_phrases = phrase_counts.most_common(top_n)
        
        return top_phrases
    
    def classify_text(self, text: str, candidate_labels: List[str]) -> Dict:
        """Zero-shot text classification"""
        result = self.classifier(
            text,
            candidate_labels,
            multi_label=True
        )
        
        return {
            'labels': result['labels'],
            'scores': result['scores']
        }
    
    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Extract summarization using extractive method"""
        doc = self.nlp(text)
        
        # Score sentences based on importance
        sentence_scores = {}
        
        for sent in doc.sents:
            score = 0
            for token in sent:
                if token.is_stop:
                    continue
                if token.pos_ in ['NOUN', 'PROPN', 'VERB']:
                    score += 1
            
            sentence_scores[sent.text] = score / len(sent) if len(sent) > 0 else 0
        
        # Get top 3 sentences
        top_sentences = sorted(
            sentence_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        summary = ' '.join([sent[0] for sent in top_sentences])
        return summary[:max_length]


class FacialRecognitionEngine:
    """Advanced facial recognition and analysis"""
    
    def __init__(self):
        logger.info("[*] Initializing Facial Recognition Engine...")
        self.known_faces = {}
        self.face_encodings_cache = {}
        logger.info("[+] Facial Recognition Engine initialized")
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """Detect and analyze faces in image"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations
            face_locations = face_recognition.face_locations(image, model='hog')
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces = []
            
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                # Extract face for additional analysis
                face_image = image[top:bottom, left:right]
                
                face_data = {
                    'location': {
                        'top': int(top),
                        'right': int(right),
                        'bottom': int(bottom),
                        'left': int(left)
                    },
                    'encoding': encoding.tolist(),
                    'dimensions': {
                        'width': right - left,
                        'height': bottom - top
                    }
                }
                
                # Check against known faces
                matches = self.match_known_faces(encoding)
                if matches:
                    face_data['matches'] = matches
                
                faces.append(face_data)
            
            return faces
            
        except Exception as e:
            logger.error(f"[!] Face detection error: {str(e)}")
            return []
    
    def match_known_faces(self, encoding: np.ndarray, tolerance: float = 0.6) -> List[Dict]:
        """Match face against known faces"""
        matches = []
        
        for name, known_encoding in self.known_faces.items():
            distance = face_recognition.face_distance([known_encoding], encoding)[0]
            
            if distance < tolerance:
                matches.append({
                    'name': name,
                    'confidence': 1 - distance,
                    'distance': float(distance)
                })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    def add_known_face(self, name: str, image_path: str):
        """Add a face to the known faces database"""
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                self.known_faces[name] = encodings[0]
                logger.info(f"[+] Added {name} to known faces")
                return True
            else:
                logger.warning(f"[!] No face found in image for {name}")
                return False
                
        except Exception as e:
            logger.error(f"[!] Error adding known face: {str(e)}")
            return False
    
    def compare_faces(self, image1_path: str, image2_path: str) -> Dict:
        """Compare two faces for similarity"""
        try:
            image1 = face_recognition.load_image_file(image1_path)
            image2 = face_recognition.load_image_file(image2_path)
            
            encoding1 = face_recognition.face_encodings(image1)[0]
            encoding2 = face_recognition.face_encodings(image2)[0]
            
            distance = face_recognition.face_distance([encoding1], encoding2)[0]
            is_same = distance < 0.6
            
            return {
                'is_same_person': bool(is_same),
                'distance': float(distance),
                'confidence': float(1 - distance),
                'threshold': 0.6
            }
            
        except Exception as e:
            logger.error(f"[!] Face comparison error: {str(e)}")
            return {'error': str(e)}


class GraphIntelligenceEngine:
    """Build and analyze relationship graphs"""
    
    def __init__(self, neo4j_uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        logger.info("[*] Initializing Graph Intelligence Engine...")
        
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
            self.graph = nx.DiGraph()
            logger.info("[+] Connected to Neo4j database")
        except Exception as e:
            logger.warning(f"[!] Neo4j connection failed: {str(e)}")
            self.driver = None
        
        logger.info("[+] Graph Intelligence Engine initialized")
    
    def add_entity(self, entity: Dict):
        """Add entity to graph"""
        entity_id = entity.get('text', str(hash(str(entity))))
        entity_type = entity.get('label', 'UNKNOWN')
        
        self.graph.add_node(
            entity_id,
            type=entity_type,
            data=entity
        )
        
        # Add to Neo4j if available
        if self.driver:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (e:Entity {id: $id})
                    SET e.type = $type, e.data = $data
                    """,
                    id=entity_id,
                    type=entity_type,
                    data=json.dumps(entity)
                )
    
    def add_relationship(self, source: str, target: str, rel_type: str, properties: Dict = None):
        """Add relationship to graph"""
        self.graph.add_edge(
            source,
            target,
            type=rel_type,
            properties=properties or {}
        )
        
        # Add to Neo4j
        if self.driver:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (s:Entity {id: $source})
                    MATCH (t:Entity {id: $target})
                    MERGE (s)-[r:RELATED {type: $rel_type}]->(t)
                    SET r.properties = $props
                    """,
                    source=source,
                    target=target,
                    rel_type=rel_type,
                    props=json.dumps(properties or {})
                )
    
    def find_shortest_path(self, source: str, target: str) -> List[str]:
        """Find shortest path between two entities"""
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def get_central_entities(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Find most central/important entities"""
        try:
            centrality = nx.betweenness_centrality(self.graph)
            top_entities = sorted(
                centrality.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
            return top_entities
        except:
            return []
    
    def detect_communities(self) -> List[Set[str]]:
        """Detect communities/clusters in the graph"""
        try:
            undirected = self.graph.to_undirected()
            communities = list(nx.community.greedy_modularity_communities(undirected))
            return communities
        except:
            return []
    
    def visualize_graph(self, output_file: str = "graph.png"):
        """Visualize the relationship graph"""
        plt.figure(figsize=(20, 20))
        
        # Layout
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_size=500,
            node_color='lightblue',
            alpha=0.8
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            alpha=0.5
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.graph,
            pos,
            font_size=8,
            font_weight='bold'
        )
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"[+] Graph visualization saved to {output_file}")
    
    def export_for_neo4j(self, filename: str = "graph_import.cypher"):
        """Export graph as Cypher queries for Neo4j"""
        with open(filename, 'w') as f:
            # Export nodes
            for node, data in self.graph.nodes(data=True):
                f.write(f"CREATE (n:Entity {{id: '{node}', type: '{data.get('type', 'UNKNOWN')}'}});\n")
            
            # Export relationships
            for source, target, data in self.graph.edges(data=True):
                rel_type = data.get('type', 'RELATED')
                f.write(f"MATCH (s:Entity {{id: '{source}'}}), (t:Entity {{id: '{target}'}}) CREATE (s)-[:{rel_type}]->(t);\n")
        
        logger.info(f"[+] Graph exported to {filename}")
    
    def close(self):
        """Close database connections"""
        if self.driver:
            self.driver.close()


class EliteAIAnalyzer:
    """Master AI analysis orchestrator"""
    
    def __init__(self):
        self.nlp_engine = AdvancedNLPEngine()
        self.face_engine = FacialRecognitionEngine()
        self.graph_engine = GraphIntelligenceEngine()
        
        # LLM clients for advanced analysis
        self.openai_client = None
        self.anthropic_client = None
    
    def configure_llm_apis(self, openai_key: str = None, anthropic_key: str = None):
        """Configure LLM API clients"""
        if openai_key:
            self.openai_client = AsyncOpenAI(api_key=openai_key)
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
    
    async def analyze_text_comprehensive(self, text: str) -> AnalysisResult:
        """Comprehensive text analysis"""
        logger.info("[*] Starting comprehensive text analysis...")
        
        result = AnalysisResult()
        
        # Extract entities
        result.entities = self.nlp_engine.extract_entities(text)
        logger.info(f"[+] Extracted {len(result.entities)} entities")
        
        # Extract relationships
        result.relationships = self.nlp_engine.extract_relationships(text)
        logger.info(f"[+] Extracted {len(result.relationships)} relationships")
        
        # Sentiment analysis
        result.sentiment = self.nlp_engine.analyze_sentiment(text)
        logger.info(f"[+] Sentiment: {result.sentiment['overall']['label']}")
        
        # Key phrases
        result.key_phrases = [phrase for phrase, count in self.nlp_engine.extract_key_phrases(text)]
        logger.info(f"[+] Extracted {len(result.key_phrases)} key phrases")
        
        # Generate summary
        result.summary = self.nlp_engine.generate_summary(text)
        
        # Build graph
        for entity in result.entities:
            self.graph_engine.add_entity(entity)
        
        for rel in result.relationships:
            self.graph_engine.add_relationship(
                rel['subject'],
                rel['object'],
                rel['predicate']
            )
        
        logger.info("[+] Comprehensive analysis complete")
        
        return result
    
    def analyze_image(self, image_path: str) -> Dict:
        """Comprehensive image analysis"""
        logger.info(f"[*] Analyzing image: {image_path}")
        
        # Detect faces
        faces = self.face_engine.detect_faces(image_path)
        
        # Additional CV analysis could be added here
        # - Object detection
        # - OCR text extraction
        # - Scene classification
        
        return {
            'faces': faces,
            'face_count': len(faces),
            'timestamp': datetime.now().isoformat()
        }
    
    async def deep_llm_analysis(self, text: str, prompt: str = None) -> str:
        """Use LLMs for deep analysis"""
        if not self.anthropic_client:
            return "LLM API not configured"
        
        if not prompt:
            prompt = f"""Analyze this intelligence data and provide:
            1. Key insights
            2. Risk assessment
            3. Recommended actions
            4. Related entities to investigate
            
            Data:
            {text[:4000]}"""
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"[!] LLM analysis error: {str(e)}")
            return f"Error: {str(e)}"
    
    def export_analysis_report(self, result: AnalysisResult, filename: str = None):
        """Export comprehensive analysis report"""
        if filename is None:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'entities': result.entities,
            'relationships': result.relationships,
            'sentiment': result.sentiment,
            'key_phrases': result.key_phrases,
            'summary': result.summary,
            'graph_stats': {
                'node_count': self.graph_engine.graph.number_of_nodes(),
                'edge_count': self.graph_engine.graph.number_of_edges(),
                'central_entities': self.graph_engine.get_central_entities()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"[+] Analysis report exported to {filename}")
        return filename


async def main():
    """Demo execution"""
    analyzer = EliteAIAnalyzer()
    
    # Example text analysis
    sample_text = """
    John Smith, CEO of TechCorp, announced a partnership with DataSystems Inc. 
    The deal, valued at $50 million, will revolutionize data analytics in the healthcare sector.
    Smith stated that this collaboration represents a major milestone for both companies.
    """
    
    result = await analyzer.analyze_text_comprehensive(sample_text)
    
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS")
    print(f"{'='*60}\n")
    print(f"Entities found: {len(result.entities)}")
    print(f"Relationships: {len(result.relationships)}")
    print(f"Sentiment: {result.sentiment['overall']['label']}")
    print(f"\nSummary: {result.summary}")
    
    # Generate visualization
    analyzer.graph_engine.visualize_graph("intelligence_graph.png")
    
    # Export report
    analyzer.export_analysis_report(result)


if __name__ == '__main__':
    asyncio.run(main())

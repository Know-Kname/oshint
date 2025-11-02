#!/usr/bin/env python3
"""
Advanced Data Analysis Module for Hughes Clues
Implements pattern recognition, anomaly detection, and threat scoring
"""

import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass
import json

@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters"""
    anomaly_threshold: float = 0.95
    correlation_threshold: float = 0.7
    risk_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.risk_weights is None:
            self.risk_weights = {
                'vulnerabilities': 0.3,
                'exposures': 0.25,
                'breaches': 0.2,
                'infrastructure': 0.15,
                'reconnaissance': 0.1
            }

class AdvancedAnalyzer:
    """Enhanced analysis capabilities for intelligence data"""
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        
    def analyze_patterns(self, data: List[Dict]) -> Dict[str, Any]:
        """Identify patterns and correlations in data"""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Text feature extraction
            text_columns = df.select_dtypes(include=['object']).columns
            text_features = {}
            for col in text_columns:
                if df[col].notna().any():
                    text_features[col] = self.vectorizer.fit_transform(df[col].fillna(''))
            
            # Numerical analysis
            num_df = df.select_dtypes(include=[np.number])
            if not num_df.empty:
                correlations = num_df.corr()
                strong_correlations = correlations[abs(correlations) > self.config.correlation_threshold]
            else:
                strong_correlations = pd.DataFrame()
            
            # Pattern detection
            patterns = {
                'correlations': strong_correlations.to_dict(),
                'text_patterns': {
                    col: self._extract_text_patterns(features)
                    for col, features in text_features.items()
                },
                'numerical_patterns': self._analyze_numerical_patterns(num_df)
            }
            
            return patterns
            
        except Exception as e:
            logging.error(f"Pattern analysis failed: {str(e)}")
            return {}
    
    def detect_anomalies(self, data: List[Dict]) -> Tuple[List[int], Dict[str, Any]]:
        """Detect anomalies in the dataset"""
        try:
            # Prepare data
            df = pd.DataFrame(data)
            numerical_data = df.select_dtypes(include=[np.number]).fillna(0)
            
            if numerical_data.empty:
                return [], {}
            
            # Scale data
            scaled_data = self.scaler.fit_transform(numerical_data)
            
            # Isolation Forest for anomaly detection
            anomalies = self.isolation_forest.fit_predict(scaled_data)
            anomaly_indices = np.where(anomalies == -1)[0]
            
            # Calculate anomaly scores
            anomaly_scores = {}
            for idx in anomaly_indices:
                anomaly_scores[idx] = {
                    'score': float(np.mean(abs(scaled_data[idx]))),
                    'features': numerical_data.columns[
                        abs(scaled_data[idx]) > self.config.anomaly_threshold
                    ].tolist()
                }
            
            return anomaly_indices.tolist(), anomaly_scores
            
        except Exception as e:
            logging.error(f"Anomaly detection failed: {str(e)}")
            return [], {}
    
    def calculate_advanced_risk_score(self, intel_data: Dict) -> Dict[str, Any]:
        """Calculate detailed risk score with contributing factors"""
        risk_components = {
            'vulnerabilities': self._assess_vulnerabilities(intel_data),
            'exposures': self._assess_exposures(intel_data),
            'breaches': self._assess_breaches(intel_data),
            'infrastructure': self._assess_infrastructure(intel_data),
            'reconnaissance': self._assess_reconnaissance(intel_data)
        }
        
        # Calculate weighted score
        total_score = sum(
            score * self.config.risk_weights[component]
            for component, score in risk_components.items()
        )
        
        # Normalize to 0-100
        normalized_score = min(max(total_score * 100, 0), 100)
        
        return {
            'total_score': round(normalized_score, 2),
            'components': risk_components,
            'risk_level': self._determine_risk_level(normalized_score),
            'contributing_factors': self._identify_contributing_factors(risk_components)
        }
    
    def _extract_text_patterns(self, features) -> Dict[str, Any]:
        """Extract patterns from text features"""
        # Convert sparse matrix to dense for processing
        dense_features = features.toarray()
        
        # Find common patterns
        feature_freq = np.sum(dense_features > 0, axis=0)
        significant_features = np.where(feature_freq > len(dense_features) * 0.1)[0]
        
        return {
            'common_features': significant_features.tolist(),
            'feature_frequencies': feature_freq[significant_features].tolist()
        }
    
    def _analyze_numerical_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in numerical data"""
        if df.empty:
            return {}
        
        patterns = {}
        for column in df.columns:
            column_data = df[column].dropna()
            if len(column_data) > 0:
                patterns[column] = {
                    'mean': float(column_data.mean()),
                    'std': float(column_data.std()),
                    'quartiles': column_data.quantile([0.25, 0.5, 0.75]).tolist(),
                    'is_normal': stats.normaltest(column_data)[1] > 0.05
                }
        
        return patterns
    
    def _assess_vulnerabilities(self, intel_data: Dict) -> float:
        """Assess vulnerability risk score"""
        score = 0.0
        vulns = intel_data.get('shodan', {}).get('vulnerabilities', [])
        
        if vulns:
            # Weight by CVSS if available
            cvss_scores = [v.get('cvss', 5.0) for v in vulns]
            score = np.mean(cvss_scores) / 10.0  # Normalize to 0-1
        
        return score
    
    def _assess_exposures(self, intel_data: Dict) -> float:
        """Assess exposure risk score"""
        score = 0.0
        github_exposure = intel_data.get('github_exposure', {}).get('total_findings', 0)
        cloud_exposure = intel_data.get('cloud_assets', {}).get('public_buckets', 0)
        
        # Normalize and combine scores
        score = min((github_exposure * 0.1 + cloud_exposure * 0.2), 1.0)
        return score
    
    def _assess_breaches(self, intel_data: Dict) -> float:
        """Assess breach risk score"""
        score = 0.0
        breaches = intel_data.get('breaches', {})
        
        if isinstance(breaches, dict):
            total_breaches = sum(
                1 for v in breaches.values()
                if isinstance(v, dict) and v.get('breached', False)
            )
            score = min(total_breaches * 0.2, 1.0)
        
        return score
    
    def _assess_infrastructure(self, intel_data: Dict) -> float:
        """Assess infrastructure risk score"""
        score = 0.0
        
        # Check for open ports
        ports = intel_data.get('ports', {})
        if ports:
            score += min(len(ports) * 0.05, 0.5)
        
        # Check for outdated technologies
        tech = intel_data.get('technologies', {})
        if tech:
            if tech.get('web_server') == 'Unknown':
                score += 0.2
            if tech.get('powered_by') == 'Unknown':
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_reconnaissance(self, intel_data: Dict) -> float:
        """Assess reconnaissance risk score"""
        score = 0.0
        
        # Check DNS security
        dns = intel_data.get('dns', {})
        if dns:
            if not dns.get('dnssec_enabled'):
                score += 0.3
            if dns.get('zone_transfer'):
                score += 0.7
        
        return min(score, 1.0)
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 20:
            return 'LOW'
        return 'MINIMAL'
    
    def _identify_contributing_factors(self, components: Dict[str, float]) -> List[str]:
        """Identify main factors contributing to risk"""
        factors = []
        for component, score in components.items():
            if score > 0.6:
                factors.append(f'HIGH {component.upper()} RISK')
            elif score > 0.3:
                factors.append(f'MODERATE {component.upper()} RISK')
        return factors

    def export_analysis(self, analysis_data: Dict, filepath: str):
        """Export analysis results to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            logging.info(f"Analysis exported to {filepath}")
        except Exception as e:
            logging.error(f"Failed to export analysis: {str(e)}")
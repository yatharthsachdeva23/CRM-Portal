"""
AI Service
Natural Language Processing and Computer Vision services for Smart PS-CRM.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_NLP_LIBS = True
except ImportError:
    HAS_NLP_LIBS = False
    print("WARNING: NLP libraries (sentence-transformers, sklearn) not found. Semantic classification will be disabled.")

import re
from datetime import datetime
import cv2
from PIL import Image
import imagehash
import io
import base64
import httpx

from app.core.config import settings
from app.models.schemas import ClassificationResult, SimilarityCheckResult


class NLPClassifier:
    """
    AI-powered complaint classifier using Sentence Transformers.
    Classifies complaints into categories: Electricity, Water, Roads, Sanitation.
    """
    
    # Category-specific keywords for enhanced classification
    CATEGORY_KEYWORDS = {
        "Electricity": [
            "power", "electric", "electricity", "light", "bulb", "transformer",
            "wire", "wires", "sparking", "spark", "fuse", "meter", "voltage",
            "outage", "blackout", "current", "short circuit", "pole", "street light",
            "led", "fan", "ac", "refrigerator", "generator", "inverter", "billing"
        ],
        "Water": [
            "water", "leak", "leakage", "pipe", "pipeline", "tap", "faucet",
            "supply", "tank", "reservoir", "drainage", "sewage", "sewer",
            "contaminated", "dirty water", "pressure", "pump", "borewell",
            "handpump", "tubewell", "storm water", "clogged", "overflow"
        ],
        "Roads": [
            "road", "street", "pothole", "potholes", "patch", "damage",
            "construction", "repair", "maintenance", "traffic", "signal",
            "signboard", "street light", "footpath", "sidewalk", "bridge",
            "flyover", "underpass", "manhole", "drain", "gravel", "asphalt"
        ],
        "Sanitation": [
            "garbage", "trash", "waste", "dump", "dumping", "cleaning",
            "sweeping", "toilet", "public toilet", "urinal", "hygiene",
            "mosquito", "pest", "rodent", "dead animal", "sewage", "smell",
            "odor", "stench", "litter", "debris", "construction waste"
        ]
    }
    
    # Urgency indicators that boost priority
    URGENCY_KEYWORDS = [
        "urgent", "emergency", "dangerous", "hazard", "accident", "injured",
        "fire", "sparking", "electrocution", "flood", "burst", "collapsed",
        "broken", "fallen", "immediate", "asap", "hospital", "school",
        "children", "elderly", "main road", "highway", "busy", "crowded"
    ]
    
    def __init__(self):
        """Initialize the NLP classifier with sentence transformer model."""
        if not HAS_NLP_LIBS:
            print("WARNING: Falling back to keyword-based classification (libraries missing)")
            self.model = None
            return

        try:
            self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
            self._precompute_category_embeddings()
            print(f"NLP Classifier loaded: {settings.SENTENCE_TRANSFORMER_MODEL}")
        except Exception as e:
            print(f"WARNING: Could not load transformer model: {e}")
            print("Falling back to keyword-based classification")
            self.model = None
    
    def _precompute_category_embeddings(self):
        """Precompute embeddings for category descriptions."""
        category_descriptions = {
            "Electricity": "Electrical power supply issues, transformer problems, sparking wires, voltage fluctuations, street lights not working, power outages, electrical hazards",
            "Water": "Water supply problems, pipe leaks, contaminated water, low water pressure, drainage issues, sewage overflow, water tank problems",
            "Roads": "Road damage, potholes, street repairs, traffic signal issues, road construction, footpath problems, manhole covers, road safety",
            "Sanitation": "Garbage collection, waste management, public toilets, cleanliness issues, mosquito breeding, dead animals, sewage smell, littering"
        }
        
        self.category_embeddings = {}
        for category, description in category_descriptions.items():
            self.category_embeddings[category] = self.model.encode(description)
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify complaint text into a category.
        
        Args:
            text: The complaint description
            
        Returns:
            ClassificationResult with category, confidence, and detected keywords
        """
        text_lower = text.lower()
        
        # Keyword-based scoring
        keyword_scores = {}
        detected_keywords = []
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
                    if keyword not in detected_keywords:
                        detected_keywords.append(keyword)
            keyword_scores[category] = score
        
        # Transformer-based classification (if available)
        if HAS_NLP_LIBS and self.model:
            text_embedding = self.model.encode(text)
            similarities = {}
            
            for category, cat_embedding in self.category_embeddings.items():
                if HAS_NLP_LIBS:
                    similarity = cosine_similarity(
                        [text_embedding], [cat_embedding]
                    )[0][0]
                else:
                    similarity = 0.0
                similarities[category] = similarity
            
            # Combine keyword and semantic scores
            combined_scores = {}
            for category in settings.CLASSIFICATION_CATEGORIES:
                keyword_weight = 0.3
                semantic_weight = 0.7
                combined_scores[category] = (
                    keyword_scores.get(category, 0) * keyword_weight +
                    similarities.get(category, 0) * semantic_weight
                )
            
            best_category = max(combined_scores, key=combined_scores.get)
            confidence = combined_scores[best_category]
        else:
            # Fallback to keyword-only
            best_category = max(keyword_scores, key=keyword_scores.get)
            confidence = min(keyword_scores[best_category] / 3, 1.0)
        
        # Detect urgency indicators
        urgency_indicators = [
            kw for kw in self.URGENCY_KEYWORDS if kw in text_lower
        ]
        
        return ClassificationResult(
            category=best_category,
            confidence=round(float(confidence), 3),
            keywords_detected=detected_keywords[:5],
            urgency_indicators=urgency_indicators
        )
    
    def calculate_urgency_score(
        self,
        text: str,
        classification: ClassificationResult,
        report_count: int = 1
    ) -> float:
        """
        Calculate urgency score (1-10) based on multiple factors.
        
        Args:
            text: Complaint text
            classification: Classification result
            report_count: Number of similar reports
            
        Returns:
            Urgency score from 1-10
        """
        score = 5.0  # Base score
        
        # Urgency keywords boost
        urgency_count = len(classification.urgency_indicators)
        score += urgency_count * 0.8
        
        # Category-based adjustments
        if classification.category == "Electricity":
            if any(kw in text.lower() for kw in ["sparking", "fire", "electrocution"]):
                score += 3
            elif "transformer" in text.lower():
                score += 1.5
        
        elif classification.category == "Water":
            if any(kw in text.lower() for kw in ["contaminated", "sewage", "burst"]):
                score += 2
        
        elif classification.category == "Roads":
            if any(kw in text.lower() for kw in ["accident", "collapsed", "main road"]):
                score += 2
        
        # Community corroboration boost
        if report_count >= 10:
            score += 2
        elif report_count >= 5:
            score += 1
        elif report_count >= 3:
            score += 0.5
        
        # Sentiment analysis (negative sentiment = higher urgency)
        # This would normally use a sentiment model
        negative_words = ["very", "extremely", "dangerous", "severe", "critical"]
        sentiment_boost = sum(0.5 for word in negative_words if word in text.lower())
        score += sentiment_boost
        
        return min(round(score, 1), 10.0)
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract location entities and other metadata from text.
        
        Args:
            text: Complaint text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            "locations": [],
            "landmarks": [],
            "dates": [],
            "times": []
        }
        
        # Common landmark patterns
        landmark_patterns = [
            r"near\s+([\w\s]+?)(?:,|\.|$)",
            r"at\s+([\w\s]+?)(?:,|\.|$)",
            r"opposite\s+([\w\s]+?)(?:,|\.|$)",
            r"beside\s+([\w\s]+?)(?:,|\.|$)"
        ]
        
        for pattern in landmark_patterns:
            matches = re.findall(pattern, text.lower())
            entities["landmarks"].extend([m.strip() for m in matches])
        
        return entities


class ImageSimilarityChecker:
    """
    Computer Vision service for corruption-proof proof of work.
    Compares 'before' and 'after' images to verify work was done at the same location.
    """
    
    def __init__(self, threshold: float = 0.75):
        """
        Initialize the similarity checker.
        
        Args:
            threshold: Minimum similarity score to pass verification
        """
        self.threshold = threshold
        self.orb = cv2.ORB_create(nfeatures=1000)
    
    async def download_image(self, url: str) -> Optional[np.ndarray]:
        """Download image from URL and convert to OpenCV format."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                # Convert to numpy array
                image_array = np.frombuffer(response.content, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                return image
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
            return None
    
    def compute_hash_similarity(
        self,
        img1: np.ndarray,
        img2: np.ndarray
    ) -> float:
        """
        Compute perceptual hash similarity between two images.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Similarity score (0-1)
        """
        # Convert to PIL Images
        img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        
        pil1 = Image.fromarray(img1_rgb)
        pil2 = Image.fromarray(img2_rgb)
        
        # Compute perceptual hashes
        hash1 = imagehash.phash(pil1)
        hash2 = imagehash.phash(pil2)
        
        # Calculate similarity (1 - normalized hamming distance)
        hash_diff = hash1 - hash2
        max_diff = 64.0  # Maximum possible difference for phash
        similarity = 1 - (hash_diff / max_diff)
        
        return max(0, similarity)
    
    def compute_feature_similarity(
        self,
        img1: np.ndarray,
        img2: np.ndarray
    ) -> float:
        """
        Compute ORB feature-based similarity.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Similarity score (0-1)
        """
        # Resize for consistency
        target_size = (400, 400)
        img1_resized = cv2.resize(img1, target_size)
        img2_resized = cv2.resize(img2, target_size)
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
        
        # Detect keypoints and compute descriptors
        kp1, des1 = self.orb.detectAndCompute(gray1, None)
        kp2, des2 = self.orb.detectAndCompute(gray2, None)
        
        if des1 is None or des2 is None:
            return 0.0
        
        # Match features using BFMatcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        # Sort matches by distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Calculate similarity based on good matches
        good_matches = [m for m in matches if m.distance < 50]
        
        if len(matches) == 0:
            return 0.0
        
        # Similarity based on ratio of good matches
        similarity = len(good_matches) / max(len(kp1), len(kp2))
        
        return min(similarity, 1.0)
    
    def compute_color_histogram_similarity(
        self,
        img1: np.ndarray,
        img2: np.ndarray
    ) -> float:
        """
        Compute color histogram similarity.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Similarity score (0-1)
        """
        # Resize for consistency
        target_size = (200, 200)
        img1_resized = cv2.resize(img1, target_size)
        img2_resized = cv2.resize(img2, target_size)
        
        # Convert to HSV for better color comparison
        hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2HSV)
        
        # Calculate histograms
        hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256])
        
        # Normalize histograms
        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
        
        # Compare using correlation
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        return max(0, similarity)
    
    async def check_similarity(
        self,
        before_url: str,
        after_url: str
    ) -> SimilarityCheckResult:
        """
        Perform comprehensive similarity check between two images.
        
        Args:
            before_url: URL to 'before' image
            after_url: URL to 'after' image
            
        Returns:
            SimilarityCheckResult with score and pass/fail status
        """
        # Download images
        before_img = await self.download_image(before_url)
        after_img = await self.download_image(after_url)
        
        if before_img is None or after_img is None:
            return SimilarityCheckResult(
                similarity_score=0.0,
                passed=False,
                details={"error": "Could not download one or both images"}
            )
        
        # Compute multiple similarity metrics
        hash_sim = self.compute_hash_similarity(before_img, after_img)
        feature_sim = self.compute_feature_similarity(before_img, after_img)
        color_sim = self.compute_color_histogram_similarity(before_img, after_img)
        
        # Weighted combination
        # Hash similarity is most reliable for location verification
        # Feature similarity captures structural elements
        # Color similarity captures lighting/environment
        final_score = (
            hash_sim * 0.5 +
            feature_sim * 0.3 +
            color_sim * 0.2
        )
        
        passed = final_score >= self.threshold
        
        return SimilarityCheckResult(
            similarity_score=round(final_score, 3),
            passed=passed,
            details={
                "hash_similarity": round(hash_sim, 3),
                "feature_similarity": round(feature_sim, 3),
                "color_similarity": round(color_sim, 3),
                "threshold": self.threshold,
                "images_loaded": True
            }
        )


# Global service instances
nlp_classifier = NLPClassifier()
image_checker = ImageSimilarityChecker(threshold=settings.IMAGE_SIMILARITY_THRESHOLD)

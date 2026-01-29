"""
Module for sentiment analysis using Gemini API.
Handles AI interactions and sentiment processing.
"""

import google.generativeai as genai
import json
from typing import List, Dict, Any
import re
from collections import Counter


class SentimentAnalyzer:
    """Handles sentiment analysis using Gemini AI."""
    
    def __init__(self, config):
        """
        Initialize Gemini AI client.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.client = self._initialize_gemini_client()
        self.model_name = "gemini-2.0-flash-exp"
    
    def _initialize_gemini_client(self):
        """Initialize and return Gemini AI client."""
        try:
            api_key = self.config.get('GEMINI_API_KEY')
            if api_key and api_key != 'YOUR_GEMINI_API_KEY':
                genai.configure(api_key=api_key)
                return genai
            return None
        except Exception as e:
            print(f"Warning: Could not initialize Gemini client: {e}")
            return None
    
    def analyze_sentiment_batch(self, tweets: List[Dict]) -> Dict[str, Any]:
        """
        Analyze sentiment for a batch of tweets.
        
        Args:
            tweets (List[Dict]): List of tweet dictionaries
            
        Returns:
            Dict: Sentiment analysis results
        """
        if not tweets:
            return self._get_default_sentiment()
        
        # If no Gemini client, use rule-based fallback
        if not self.client:
            return self._rule_based_sentiment_analysis(tweets)
        
        try:
            # Prepare tweets for analysis
            tweet_texts = [tweet['text'] for tweet in tweets[:10]]
            analysis_prompt = self._create_analysis_prompt(tweet_texts)
            
            # Call Gemini API
            model = self.client.GenerativeModel(self.model_name)
            response = model.generate_content(analysis_prompt)
            
            # Parse response
            return self._parse_ai_response(response.text, tweets)
            
        except Exception as e:
            print(f"Error in AI sentiment analysis: {e}")
            return self._rule_based_sentiment_analysis(tweets)
    
    def _create_analysis_prompt(self, tweet_texts: List[str]) -> str:
        """Create prompt for sentiment analysis."""
        tweets_str = "\n".join([f"{i+1}. {text}" for i, text in enumerate(tweet_texts)])
        
        prompt = f"""
        Analyze the sentiment of these business-related tweets and provide insights.
        
        Tweets:
        {tweets_str}
        
        Please provide a JSON response with the following structure:
        {{
            "overall_sentiment": float (-1.0 to 1.0),
            "sentiment_distribution": {{
                "positive": float (0.0 to 1.0),
                "neutral": float (0.0 to 1.0),
                "negative": float (0.0 to 1.0)
            }},
            "positive_topics": ["topic1", "topic2", "topic3"],
            "negative_topics": ["topic1", "topic2"],
            "key_insights": ["insight1", "insight2", "insight3"]
        }}
        
        Return ONLY valid JSON, no additional text.
        """
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, tweets: List[Dict]) -> Dict[str, Any]:
        """Parse AI response and combine with tweet data."""
        try:
            # Extract JSON from response
            json_str = response_text
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0]
            
            ai_result = json.loads(json_str)
            
            # Enhance with engagement data
            avg_engagement = sum(t.get('engagement_score', 0) for t in tweets) / len(tweets) if tweets else 0
            ai_result['average_engagement'] = avg_engagement
            ai_result['tweets_analyzed'] = len(tweets)
            
            return ai_result
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {e}")
            return self._rule_based_sentiment_analysis(tweets)
    
    def _rule_based_sentiment_analysis(self, tweets: List[Dict]) -> Dict[str, Any]:
        """Fallback sentiment analysis using rule-based approach."""
        if not tweets:
            return self._get_default_sentiment()
        
        # Define sentiment keywords
        positive_words = [
            'great', 'excellent', 'good', 'positive', 'success', 'growth',
            'profit', 'innovation', 'opportunity', 'improve', 'increase'
        ]
        
        negative_words = [
            'bad', 'poor', 'negative', 'failure', 'decline', 'loss',
            'problem', 'issue', 'challenge', 'difficult', 'risk'
        ]
        
        # Analyze each tweet
        sentiments = []
        all_words = []
        
        for tweet in tweets:
            text = tweet['text'].lower()
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                sentiments.append(1.0)
            elif neg_count > pos_count:
                sentiments.append(-1.0)
            else:
                sentiments.append(0.0)
            
            all_words.extend(text.split())
        
        # Calculate overall sentiment
        if sentiments:
            overall = sum(sentiments) / len(sentiments)
            
            # Calculate distribution
            pos_count = sum(1 for s in sentiments if s > 0)
            neu_count = sum(1 for s in sentiments if s == 0)
            neg_count = sum(1 for s in sentiments if s < 0)
            total = len(sentiments)
            
            return {
                'overall_sentiment': overall,
                'sentiment_distribution': {
                    'positive': pos_count / total,
                    'neutral': neu_count / total,
                    'negative': neg_count / total
                },
                'positive_topics': self._extract_topics(all_words, positive_words)[:3],
                'negative_topics': self._extract_topics(all_words, negative_words)[:2],
                'key_insights': [
                    "Consider timing posts around positive trend discussions",
                    "Monitor mentions of challenges for proactive responses"
                ],
                'average_engagement': sum(t.get('engagement_score', 0) for t in tweets) / len(tweets),
                'tweets_analyzed': len(tweets)
            }
        
        return self._get_default_sentiment()
    
    def _extract_topics(self, words: List[str], sentiment_words: List[str]) -> List[str]:
        """Extract common topics from words."""
        # Filter for meaningful words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'are', 'was'}
        meaningful = [w for w in words if len(w) > 3 and w not in stop_words and w in sentiment_words]
        
        # Count occurrences
        word_counts = Counter(meaningful)
        return [word for word, count in word_counts.most_common(5)]
    
    def generate_content_ideas(self, sentiment_results: Dict, hashtag: str) -> List[str]:
        """Generate content ideas based on sentiment analysis."""
        ideas = []
        positive_topics = sentiment_results.get('positive_topics', [])
        negative_topics = sentiment_results.get('negative_topics', [])
        overall_sentiment = sentiment_results.get('overall_sentiment', 0)
        
        if overall_sentiment > 0.3:
            for topic in positive_topics[:2]:
                ideas.append(f"Share success stories about {topic} in #{hashtag.replace('#', '')}")
        elif overall_sentiment < -0.3:
            for topic in negative_topics[:2]:
                ideas.append(f"Address challenges in {topic} and provide solutions")
        else:
            ideas.append(f"Provide analysis of current trends in #{hashtag.replace('#', '')}")
        
        # General ideas
        ideas.extend([
            "Post industry statistics with engaging visuals",
            "Share customer testimonials or success stories"
        ])
        
        return ideas[:5]
    
    def _get_default_sentiment(self) -> Dict[str, Any]:
        """Return default sentiment structure."""
        return {
            'overall_sentiment': 0.0,
            'sentiment_distribution': {
                'positive': 0.33,
                'neutral': 0.34,
                'negative': 0.33
            },
            'positive_topics': ['business', 'growth', 'innovation'],
            'negative_topics': ['challenges', 'competition'],
            'key_insights': [
                "Monitor industry trends regularly",
                "Engage with both positive and constructive discussions"
            ],
            'average_engagement': 0.0,
            'tweets_analyzed': 0
        }

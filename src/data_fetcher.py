"""
Module for fetching data from Twitter/X API.
Handles API interactions and data preprocessing.
"""

import tweepy
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional


class TwitterDataFetcher:
    """Handles fetching and preprocessing Twitter data."""
    
    def __init__(self, config):
        """
        Initialize Twitter client.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.client = self._initialize_client()
        
    def _initialize_client(self):
        """Initialize and return Twitter API client."""
        try:
            bearer_token = self.config.get('TWITTER_BEARER_TOKEN')
            if bearer_token and bearer_token != 'YOUR_TWITTER_BEARER_TOKEN':
                return tweepy.Client(bearer_token=bearer_token)
            return None
        except Exception as e:
            print(f"Warning: Could not initialize Twitter client: {e}")
            return None
    
    def fetch_trending_posts(self, hashtag: str, post_limit: int = 10) -> List[Dict]:
        """
        Fetch recent posts for a given hashtag.
        
        Args:
            hashtag (str): Hashtag to search for
            post_limit (int): Maximum number of posts to fetch
            
        Returns:
            List[Dict]: List of tweet data dictionaries
        """
        # If no client (no API key), return empty list
        if not self.client:
            return []
        
        try:
            # Clean hashtag
            clean_hashtag = hashtag.replace('#', '').strip()
            
            # Search for tweets
            query = f"#{clean_hashtag} lang:en -is:retweet"
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(post_limit, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if tweets.data:
                return self._process_tweets(tweets.data, tweets.includes)
            return []
            
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def _process_tweets(self, tweets, includes=None) -> List[Dict]:
        """Process raw tweet data into structured format."""
        processed_tweets = []
        
        # Create user map if includes provided
        user_map = {}
        if includes and 'users' in includes:
            user_map = {user.id: user for user in includes['users']}
        
        for tweet in tweets:
            # Get user info
            username = "Unknown"
            if tweet.author_id in user_map:
                username = user_map[tweet.author_id].username
            
            # Clean text
            clean_text = self._clean_tweet_text(tweet.text)
            
            # Calculate engagement score
            metrics = tweet.public_metrics
            engagement_score = (
                metrics.get('like_count', 0) * 0.4 +
                metrics.get('retweet_count', 0) * 0.3 +
                metrics.get('reply_count', 0) * 0.2 +
                metrics.get('quote_count', 0) * 0.1
            )
            
            processed_tweets.append({
                'id': tweet.id,
                'text': clean_text,
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'username': username,
                'likes': metrics.get('like_count', 0),
                'retweets': metrics.get('retweet_count', 0),
                'replies': metrics.get('reply_count', 0),
                'engagement_score': engagement_score,
                'url': f"https://twitter.com/{username}/status/{tweet.id}"
            })
        
        return processed_tweets
    
    def _clean_tweet_text(self, text: str) -> str:
        """Clean tweet text by removing URLs, mentions, and extra spaces."""
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        # Remove hashtag symbols but keep text
        text = re.sub(r'#', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def fetch_sample_trends(self) -> List[Dict]:
        """Return sample trend data for testing/demo purposes."""
        sample_tweets = [
            {
                'text': "Business innovation is accelerating with AI integration across industries.",
                'created_at': (datetime.now() - timedelta(hours=1)).isoformat(),
                'engagement_score': 85.5,
                'likes': 45,
                'retweets': 12
            },
            {
                'text': "Sustainability practices are becoming a competitive advantage for businesses.",
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'engagement_score': 72.3,
                'likes': 38,
                'retweets': 8
            },
            {
                'text': "Remote work challenges include maintaining team cohesion and productivity.",
                'created_at': (datetime.now() - timedelta(hours=3)).isoformat(),
                'engagement_score': 61.2,
                'likes': 29,
                'retweets': 5
            }
        ]
        return sample_tweets

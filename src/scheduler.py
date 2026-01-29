"""
Module for calculating optimal posting times based on sentiment and engagement data.
"""

from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import random


class PostingScheduler:
    """Calculates optimal posting times based on analysis results."""
    
    def __init__(self):
        """Initialize scheduler with default time slots."""
        self.time_slots = self._initialize_time_slots()
    
    def _initialize_time_slots(self) -> List[Dict]:
        """Initialize default time slots with base engagement scores."""
        slots = []
        
        # Define days and time ranges
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        time_ranges = [
            ('09:00', '11:00'),   # Morning
            ('11:00', '13:00'),   # Late morning
            ('13:00', '15:00'),   # Early afternoon
            ('15:00', '17:00'),   # Late afternoon
            ('17:00', '19:00'),   # Early evening
            ('19:00', '21:00'),   # Evening
        ]
        
        # Create slots
        for day in days:
            for start, end in time_ranges:
                # Base engagement varies by day and time
                base_score = self._calculate_base_score(day, start)
                
                slots.append({
                    'day': day,
                    'time_range': f"{start}-{end}",
                    'start_hour': int(start.split(':')[0]),
                    'base_engagement': base_score,
                    'sentiment_adjustment': 0.0
                })
        
        return slots
    
    def _calculate_base_score(self, day: str, start_time: str) -> float:
        """Calculate base engagement score for a time slot."""
        # Business days typically have higher engagement
        if day in ['Tuesday', 'Wednesday', 'Thursday']:
            base = 0.7
        elif day in ['Monday', 'Friday']:
            base = 0.6
        else:  # Weekend
            base = 0.5
        
        # Adjust for time of day
        hour = int(start_time.split(':')[0])
        if 9 <= hour <= 11:   # Morning peak
            base += 0.15
        elif 13 <= hour <= 15:  # Afternoon peak
            base += 0.10
        elif 19 <= hour <= 21:  # Evening
            base += 0.05
        
        return min(base, 0.95)  # Cap at 0.95
    
    def calculate_optimal_times(self, 
                               sentiment_results: Dict[str, Any],
                               engagement_history: List[Dict] = None) -> List[Dict]:
        """
        Calculate optimal posting times based on sentiment.
        
        Args:
            sentiment_results: Results from sentiment analysis
            engagement_history: Historical engagement data
            
        Returns:
            List[Dict]: List of recommended time slots
        """
        # Start with base slots
        recommended_slots = self.time_slots.copy()
        
        # Apply sentiment adjustment
        overall_sentiment = sentiment_results.get('overall_sentiment', 0)
        sentiment_adjustment = overall_sentiment * 0.2  # Sentiment contributes 20%
        
        # Apply engagement history if available
        history_adjustment = 0.0
        if engagement_history:
            history_adjustment = self._calculate_history_adjustment(engagement_history)
        
        # Calculate final scores for each slot
        for slot in recommended_slots:
            # Combine base engagement, sentiment, and history
            final_score = (
                slot['base_engagement'] * 0.6 +
                sentiment_adjustment * 0.3 +
                history_adjustment * 0.1 +
                random.uniform(-0.05, 0.05)  # Small random variation
            )
            
            # Ensure score is within bounds
            slot['score'] = max(0.1, min(0.99, final_score))
            slot['sentiment_adjustment'] = sentiment_adjustment
        
        # Sort by score and return top recommendations
        recommended_slots.sort(key=lambda x: x['score'], reverse=True)
        
        # Format and return top 5 slots
        top_slots = []
        for slot in recommended_slots[:5]:
            top_slots.append({
                'day': slot['day'],
                'time': slot['time_range'],
                'score': round(slot['score'], 3),
                'recommendation': self._get_recommendation_text(slot['score'])
            })
        
        return top_slots
    
    def _calculate_history_adjustment(self, engagement_history: List[Dict]) -> float:
        """Calculate adjustment based on historical engagement data."""
        if not engagement_history:
            return 0.0
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(engagement_history)
            
            # Calculate average engagement for similar times
            current_hour = datetime.now().hour
            current_weekday = datetime.now().weekday()
            
            # Filter for similar times (within 2 hours)
            similar_times = df[
                abs(df['hour_of_day'] - current_hour) <= 2
            ]
            
            if not similar_times.empty:
                return float(similar_times['estimated_engagement'].mean())
            
            return 0.5  # Default if no similar times found
            
        except Exception as e:
            print(f"Error calculating history adjustment: {e}")
            return 0.5
    
    def _get_recommendation_text(self, score: float) -> str:
        """Get recommendation text based on score."""
        if score >= 0.8:
            return "Excellent time to post - high expected engagement"
        elif score >= 0.7:
            return "Good time to post - above average engagement expected"
        elif score >= 0.6:
            return "Moderate time - average engagement expected"
        else:
            return "Lower priority - consider other time slots first"
    
    def get_time_slot_insights(self, sentiment_results: Dict) -> List[str]:
        """Generate insights about posting times based on sentiment."""
        insights = []
        overall_sentiment = sentiment_results.get('overall_sentiment', 0)
        
        if overall_sentiment > 0.5:
            insights.append("High positive sentiment suggests posting during peak business hours")
            insights.append("Consider posting in morning slots when audiences are planning their day")
        elif overall_sentiment < -0.3:
            insights.append("Negative sentiment suggests careful timing - avoid peak frustration hours")
            insights.append("Consider afternoon slots when audiences may be more receptive to solutions")
        else:
            insights.append("Neutral sentiment - focus on consistent posting schedule")
            insights.append("Test different time slots to optimize engagement")
        
        # Add general insights
        insights.extend([
            "Tuesday-Thursday typically have highest business engagement",
            "Morning posts (9-11 AM) often perform well for business content",
            "Consider time zones of your target audience"
        ])
        
        return insights

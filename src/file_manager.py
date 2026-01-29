"""
Module for handling file operations including reading, writing, and data management.
"""

import csv
import json
import os
from datetime import datetime, timedelta  # FIXED: Added timedelta import
from typing import List, Dict, Any
import pandas as pd


class FileManager:
    """Manages all file operations for the application."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize file manager.
        
        Args:
            data_dir (str): Directory for data files
        """
        self.data_dir = data_dir
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_engagement_history(self) -> List[Dict]:
        """Load engagement history from CSV file."""
        history_file = os.path.join(self.data_dir, "engagement_history.csv")
        
        if os.path.exists(history_file):
            try:
                df = pd.read_csv(history_file)
                return df.to_dict('records')
            except Exception as e:
                print(f"Error loading engagement history: {e}")
        
        # Return default history if file doesn't exist
        return self._create_default_history()
    
    def _create_default_history(self) -> List[Dict]:
        """Create default engagement history."""
        default_history = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            for hour in [9, 11, 14, 16, 19]:  # Sample hours
                default_history.append({
                    'timestamp': date.replace(hour=hour).isoformat(),
                    'day_of_week': date.weekday(),
                    'hour_of_day': hour,
                    'estimated_engagement': 0.5 + (0.3 * (i % 7) / 7),  # Weekly pattern
                    'sentiment_score': 0.1 * (i % 5) - 0.2  # Varying sentiment
                })
        
        return default_history
    
    def save_engagement_history(self, history: List[Dict]):
        """Save engagement history to CSV file."""
        try:
            history_file = os.path.join(self.data_dir, "engagement_history.csv")
            df = pd.DataFrame(history)
            df.to_csv(history_file, index=False)
        except Exception as e:
            print(f"Error saving engagement history: {e}")
    
    def save_analysis_results(self, results: Dict[str, Any]):
        """Save analysis results to JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = os.path.join(self.data_dir, f"analysis_{timestamp}.json")
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Also append to master log
            self._append_to_analysis_log(results)
            
        except Exception as e:
            print(f"Error saving analysis results: {e}")
    
    def _append_to_analysis_log(self, results: Dict[str, Any]):
        """Append analysis to master log CSV."""
        try:
            log_file = os.path.join(self.data_dir, "analysis_log.csv")
            
            # Prepare row for CSV
            row = {
                'timestamp': results.get('timestamp', datetime.now().isoformat()),
                'hashtag': results.get('hashtag', 'unknown'),
                'tweets_analyzed': len(results.get('sentiment_results', {}).get('tweets_analyzed', 0)),
                'overall_sentiment': results.get('sentiment_results', {}).get('overall_sentiment', 0),
                'top_recommendation': results.get('optimal_times', [{}])[0].get('time', '') if results.get('optimal_times') else ''
            }
            
            # Write to CSV
            file_exists = os.path.exists(log_file)
            
            with open(log_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
                
        except Exception as e:
            print(f"Error appending to analysis log: {e}")
    
    def load_sample_data(self) -> List[Dict]:
        """Load sample data for demonstration purposes."""
        return [
            {
                'text': "Digital transformation is essential for business survival in 2024.",
                'created_at': datetime.now().isoformat(),
                'engagement_score': 85.5,
                'likes': 42,
                'retweets': 15
            },
            {
                'text': "Sustainability reporting is becoming mandatory for large corporations.",
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'engagement_score': 72.3,
                'likes': 38,
                'retweets': 9
            },
            {
                'text': "AI tools are helping small businesses compete with larger enterprises.",
                'created_at': (datetime.now() - timedelta(hours=4)).isoformat(),
                'engagement_score': 91.2,
                'likes': 56,
                'retweets': 21
            },
            {
                'text': "Supply chain disruptions continue to affect global business operations.",
                'created_at': (datetime.now() - timedelta(hours=6)).isoformat(),
                'engagement_score': 64.7,
                'likes': 31,
                'retweets': 7
            }
        ]
    
    def export_to_csv(self, results: Dict[str, Any]) -> str:
        """Export results to CSV format string."""
        try:
            # Prepare data for export
            export_data = []
            
            # Add sentiment summary
            export_data.append({
                'Section': 'Sentiment Summary',
                'Overall Sentiment': results.get('sentiment_results', {}).get('overall_sentiment', 0),
                'Tweets Analyzed': results.get('tweets_analyzed', 0),
                'Positive Topics': ', '.join(results.get('sentiment_results', {}).get('positive_topics', [])[:3]),
                'Negative Topics': ', '.join(results.get('sentiment_results', {}).get('negative_topics', [])[:2])
            })
            
            # Add optimal times
            for i, time_slot in enumerate(results.get('optimal_times', []), 1):
                export_data.append({
                    'Section': f'Optimal Time {i}',
                    'Day': time_slot.get('day', ''),
                    'Time': time_slot.get('time', ''),
                    'Engagement Score': time_slot.get('score', 0),
                    'Recommendation': time_slot.get('recommendation', '')
                })
            
            # Add content suggestions
            for i, suggestion in enumerate(results.get('content_suggestions', []), 1):
                export_data.append({
                    'Section': f'Content Idea {i}',
                    'Suggestion': suggestion,
                    'Priority': 'High' if i <= 2 else 'Medium'
                })
            
            # Convert to CSV string
            df = pd.DataFrame(export_data)
            return df.to_csv(index=False)
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return "Section,Error\nExport,Error during export\n"
    
    def format_schedule_text(self, results: Dict[str, Any]) -> str:
        """Format posting schedule as text for copying."""
        try:
            text = "📅 POSTING SCHEDULE RECOMMENDATIONS\n"
            text += "=" * 40 + "\n\n"
            
            text += "📊 SENTIMENT ANALYSIS SUMMARY\n"
            text += "-" * 30 + "\n"
            sentiment = results.get('sentiment_results', {})
            text += f"Overall Sentiment: {sentiment.get('overall_sentiment', 0):.2f}\n"
            text += f"Tweets Analyzed: {results.get('tweets_analyzed', 0)}\n\n"
            
            text += "⏰ OPTIMAL POSTING TIMES\n"
            text += "-" * 30 + "\n"
            for i, slot in enumerate(results.get('optimal_times', []), 1):
                text += f"{i}. {slot.get('day')} {slot.get('time')}\n"
                text += f"   Engagement Score: {slot.get('score'):.3f}\n"
                text += f"   {slot.get('recommendation', '')}\n\n"
            
            text += "💡 CONTENT SUGGESTIONS\n"
            text += "-" * 30 + "\n"
            for i, idea in enumerate(results.get('content_suggestions', []), 1):
                text += f"{i}. {idea}\n"
            
            text += "\n" + "=" * 40 + "\n"
            text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            
            return text
            
        except Exception as e:
            return f"Error formatting schedule: {str(e)}"

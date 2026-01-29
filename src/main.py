#!/usr/bin/env python3
"""
Main application file for Sentiment-Driven Social Media Posting Assistant.
This module coordinates all components of the application.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import TwitterDataFetcher
from src.sentiment_analyzer import SentimentAnalyzer
from src.scheduler import PostingScheduler
from src.file_manager import FileManager
from src.config import ConfigManager
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt


class SocialMediaAssistant:
    """Main class coordinating all components of the posting assistant."""
    
    def __init__(self):
        """Initialize all components of the application."""
        self.config = ConfigManager()
        self.data_fetcher = TwitterDataFetcher(self.config)
        self.analyzer = SentimentAnalyzer(self.config)
        self.scheduler = PostingScheduler()
        self.file_manager = FileManager()
        
        # Load or create engagement history
        self.engagement_history = self.file_manager.load_engagement_history()
        
    def run_analysis(self, hashtag=None, post_limit=None):
        """
        Run complete analysis pipeline.
        
        Args:
            hashtag (str): Hashtag to analyze
            post_limit (int): Number of posts to fetch
            
        Returns:
            dict: Analysis results including sentiment, optimal times, and content suggestions
        """
        try:
            # Step 1: Fetch data
            st.info("🔄 Fetching trending posts...")
            tweets = self.data_fetcher.fetch_trending_posts(
                hashtag=hashtag,
                post_limit=post_limit or self.config.get('POST_LIMIT', 10)
            )
            
            if not tweets:
                st.warning("No tweets found. Using sample data for demonstration.")
                tweets = self.file_manager.load_sample_data()
            
            # Step 2: Analyze sentiment
            st.info("🔍 Analyzing sentiment...")
            sentiment_results = self.analyzer.analyze_sentiment_batch(tweets)
            
            # Step 3: Determine optimal posting times
            st.info("⏰ Calculating optimal posting schedule...")
            optimal_times = self.scheduler.calculate_optimal_times(
                sentiment_results,
                self.engagement_history
            )
            
            # Step 4: Generate content suggestions
            st.info("💡 Generating content ideas...")
            content_suggestions = self.analyzer.generate_content_ideas(
                sentiment_results,
                hashtag or self.config.get('DEFAULT_HASHTAG', '#business')
            )
            
            # Step 5: Save results
            self.file_manager.save_analysis_results({
                'timestamp': datetime.now().isoformat(),
                'hashtag': hashtag,
                'sentiment_results': sentiment_results,
                'optimal_times': optimal_times,
                'content_suggestions': content_suggestions
            })
            
            # Step 6: Update engagement history (simulated)
            self._simulate_engagement_update(optimal_times)
            
            return {
                'tweets_analyzed': len(tweets),
                'sentiment_results': sentiment_results,
                'optimal_times': optimal_times,
                'content_suggestions': content_suggestions,
                'tweets_sample': tweets[:3]  # First 3 tweets for display
            }
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            # Return demo data for testing
            return self._get_demo_data()
    
    def _simulate_engagement_update(self, optimal_times):
        """Simulate updating engagement history with new data."""
        # In a real application, this would track actual engagement
        # For this project, we'll simulate some data
        import random
        new_entry = {
            'timestamp': datetime.now().isoformat(),
            'day_of_week': datetime.now().weekday(),
            'hour_of_day': datetime.now().hour,
            'estimated_engagement': random.uniform(0.5, 1.0),
            'sentiment_score': random.uniform(-0.5, 0.5)
        }
        self.engagement_history.append(new_entry)
        self.file_manager.save_engagement_history(self.engagement_history)
    
    def _get_demo_data(self):
        """Return demonstration data for testing without API keys."""
        return {
            'tweets_analyzed': 8,
            'sentiment_results': {
                'overall_sentiment': 0.65,
                'positive_topics': ['innovation', 'growth', 'strategy'],
                'negative_topics': ['competition', 'challenges'],
                'sentiment_distribution': {'positive': 0.6, 'neutral': 0.3, 'negative': 0.1}
            },
            'optimal_times': [
                {'day': 'Tuesday', 'time': '10:00-11:00', 'score': 0.85},
                {'day': 'Wednesday', 'time': '14:00-15:00', 'score': 0.78},
                {'day': 'Friday', 'time': '09:00-10:00', 'score': 0.72}
            ],
            'content_suggestions': [
                "Share insights about business innovation trends",
                "Post about growth strategies for SMEs",
                "Discuss overcoming common business challenges"
            ],
            'tweets_sample': [
                "Business innovation is key to staying competitive in today's market.",
                "Growing a business requires both strategy and adaptability.",
                "Challenges are opportunities in disguise for resilient entrepreneurs."
            ]
        }


def create_streamlit_app():
    """Create and run the Streamlit web interface."""
    st.set_page_config(
        page_title="Sentiment-Driven Posting Assistant",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Sentiment-Driven Social Media Posting Assistant")
    st.markdown("""
    This tool analyzes trending topics and suggests optimal posting times based on sentiment analysis.
    It helps businesses maximize engagement on social media platforms.
    """)
    
    # Initialize assistant
    assistant = SocialMediaAssistant()
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        hashtag = st.text_input(
            "Enter hashtag or keyword:",
            value=assistant.config.get('DEFAULT_HASHTAG', '#business')
        )
        
        post_limit = st.slider(
            "Number of posts to analyze:",
            min_value=5,
            max_value=50,
            value=assistant.config.get('POST_LIMIT', 10)
        )
        
        analyze_button = st.button("🚀 Analyze & Generate Schedule", type="primary")
        
        st.markdown("---")
        st.info("**Note:** Add your API keys in `config.ini` for full functionality.")
    
    # Main content area
    if analyze_button:
        with st.spinner("Analyzing trends and generating recommendations..."):
            results = assistant.run_analysis(hashtag, post_limit)
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Sentiment Analysis Results")
            st.metric("Tweets Analyzed", results['tweets_analyzed'])
            
            # Sentiment score gauge
            sentiment_score = results['sentiment_results']['overall_sentiment']
            st.progress(sentiment_score, text=f"Overall Sentiment: {sentiment_score:.2f}")
            
            # Sentiment distribution
            dist = results['sentiment_results']['sentiment_distribution']
            dist_df = pd.DataFrame({
                'Sentiment': list(dist.keys()),
                'Percentage': [v * 100 for v in dist.values()]
            })
            st.bar_chart(dist_df.set_index('Sentiment'))
            
            # Topics
            st.write("**Positive Topics:**", ", ".join(results['sentiment_results']['positive_topics'][:3]))
            if results['sentiment_results']['negative_topics']:
                st.write("**Topics to Approach Carefully:**", ", ".join(results['sentiment_results']['negative_topics'][:3]))
        
        with col2:
            st.subheader("⏰ Optimal Posting Schedule")
            times_df = pd.DataFrame(results['optimal_times'])
            st.dataframe(times_df, use_container_width=True)
            
            # Visualize schedule
            fig, ax = plt.subplots(figsize=(10, 4))
            times_df['score_num'] = times_df['score'] * 100
            ax.bar(range(len(times_df)), times_df['score_num'])
            ax.set_xticks(range(len(times_df)))
            ax.set_xticklabels([f"{row['day']}\n{row['time']}" for _, row in times_df.iterrows()])
            ax.set_ylabel('Engagement Score (%)')
            ax.set_title('Recommended Posting Times')
            st.pyplot(fig)
        
        # Content suggestions
        st.subheader("💡 Content Suggestions")
        for i, suggestion in enumerate(results['content_suggestions'], 1):
            st.write(f"{i}. {suggestion}")
        
        # Sample tweets analyzed
        with st.expander("View Sample Tweets Analyzed"):
            for tweet in results['tweets_sample']:
                st.write(f"• {tweet}")
        
        # Export options
        st.subheader("📤 Export Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save as CSV"):
                csv_data = assistant.file_manager.export_to_csv(results)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"posting_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📋 Copy Schedule to Clipboard"):
                schedule_text = assistant.file_manager.format_schedule_text(results)
                st.code(schedule_text, language=None)
        
        with col3:
            if st.button("🔄 Run Analysis Again"):
                st.rerun()
    
    else:
        # Display welcome/instructions
        st.info("👈 Configure your analysis in the sidebar and click 'Analyze & Generate Schedule' to begin.")
        
        # Show sample dashboard
        with st.expander("📊 View Sample Analysis (Demo Mode)"):
            results = assistant._get_demo_data()
            st.write("**Sample Results (without API configuration):**")
            st.json(results, expanded=False)


if __name__ == "__main__":
    create_streamlit_app()

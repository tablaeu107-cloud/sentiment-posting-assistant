# Sentiment-Driven Social Media Posting Assistant

## 📋 Project Overview
A Python-based application that analyzes trending topics on social media, performs sentiment analysis using Gemini AI, and recommends optimal posting times to maximize engagement for businesses.

## 🎯 Problem Statement
Social media managers often post content based on intuition rather than data, leading to suboptimal engagement. This tool addresses this by:
- Analyzing real-time sentiment of trending topics
- Identifying optimal posting times based on historical engagement patterns
- Generating data-driven content suggestions

## 👥 Intended Users
- Small business owners managing their own social media
- Digital marketing agencies
- Content creators and social media managers
- Entrepreneurs seeking data-driven insights

## 🚀 Key Functionalities
1. **Trend Analysis**: Fetches and analyzes trending posts for specified hashtags
2. **Sentiment Analysis**: Uses Gemini AI to determine overall sentiment and key topics
3. **Optimal Scheduling**: Calculates best posting times based on sentiment and engagement data
4. **Content Suggestions**: Generates relevant content ideas based on analysis
5. **Data Export**: Saves results in multiple formats (CSV, JSON, text)

## 🛠️ Technologies Used
- **Python 3.8+**
- **Gemini 2.5 Flash API** (for sentiment analysis)
- **Tweepy** (for Twitter/X API integration)
- **Streamlit** (for web interface)
- **Pandas** (for data manipulation)
- **Matplotlib** (for data visualization)

## 📁 Project Structure

sentiment_posting_assistant/
├── src/
│ ├── main.py # Main application controller
│ ├── data_fetcher.py # Twitter data fetching
│ ├── sentiment_analyzer.py # Gemini AI integration
│ ├── scheduler.py # Posting time optimization
│ ├── file_manager.py # File operations
│ └── config.py # Configuration management
├── data/ # Data storage directory
├── requirements.txt # Python dependencies
├── config.ini # Configuration file
└── README.md # This file


Installation Steps
Clone the repository

bash

git clone https://github.com/tablaeu107-cloud/sentiment-posting-assistant.git
cd sentiment-posting-assistant

Create and activate a virtual environment

bash
# Create virtual environment
python3 -m venv venv4

# Activate the virtual environment
# On macOS/Linux:
source venv4/bin/activate

# On Windows:
# venv4\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Run the application

bash
streamlit run src/main.py
Additional Notes:
Make sure Python 3.8 or higher is installed on your system

The virtual environment name (venv4) can be customized to your preference

If you don't have a requirements.txt file, you may need to install dependencies manually:

bash
pip install streamlit tweepy google-generativeai pandas python-dotenv

Access the web interface

Open your browser and go to http://localhost:8501

Enter a hashtag and click "Analyze & Generate Schedule"

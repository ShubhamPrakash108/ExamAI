# ExamAI - Your Helping Friend

ExamAI is a Streamlit-based web application that helps students and learners by automatically generating study materials from YouTube educational content. The app can search for relevant videos, generate quiz questions, and create summaries from video content.

### Note: I will remove my API keys(that is in the code) after two days.

## Features

- YouTube video search functionality
- Automatic question and answer generation
- Video summary generation from captions
- Interactive user interface with video thumbnails
- Separate controls for Q&A and summary generation
- Color-coded presentation of questions and answers

## Running on Google Colab (Recommended Method)

1. Create a new Google Colab notebook

2. Install the required packages:
```python
!pip install -r requirements.txt
!pip install pyngrok
```

3. Set up ngrok for public access:
```python
from pyngrok import ngrok

# Authenticate with ngrok
!ngrok authtoken YOUR_NGROK_AUTH_TOKEN  # Replace with your ngrok auth token

# Run Streamlit in the background
!streamlit run /content/app.py &>/content/logs.txt &

# Create a public URL
public_url = ngrok.connect(addr="8501", proto="http")
print(f"Streamlit app is live at: {public_url}")
```

Note: You'll need to:
- Sign up for a free ngrok account at https://ngrok.com/
- Get your auth token from ngrok dashboard
- Replace `YOUR_NGROK_AUTH_TOKEN` with your actual token

4. The app will be accessible via the URL provided by ngrok

## Prerequisites

- Google Colab account (for recommended method)
- A Google API key for YouTube Data API v3
- A Google API key for Gemini Pro model
- ngrok account (free)


## Usage

1. Enter a topic in the search box to find relevant YouTube videos
2. For each video, you can:
   - Click "Generate Q&A" to create multiple-choice questions
   - Click "Generate Summary" to create a study summary
   - Open the video in a new tab

## Component Details

### Search Function
- Uses YouTube Data API to search for relevant videos
- Displays video thumbnails, titles, channel names, and durations

### Q&A Generation
- Creates multiple-choice questions based on video content
- Provides detailed explanations for answers
- Color-coded presentation:
  - Questions in red (#ed2828)
  - Options in blue (#1702f7)
  - Correct answers in green (#29ad1a)
  - Explanations in light green (#90f073)

### Summary Generation
- Extracts captions from YouTube videos
- Generates comprehensive study notes using Gemini Pro
- Handles cases where captions are unavailable

## Dependencies

- streamlit
- google-api-python-client
- isodate
- educhain
- langchain-google-genai
- youtube-transcript-api
- python-dotenv
- pyngrok (for Colab deployment)

## Troubleshooting

1. If you encounter an error about port 8501 being in use:
```python
# In Colab, kill any existing Streamlit processes
!kill -9 $(pgrep streamlit)
```

2. If ngrok connection expires (valid for 2 hours):
```python
# Restart the connection
public_url = ngrok.connect(addr="8501", proto="http")
print(f"New URL: {public_url}")
```

## Limitations

- Requires videos to have available captions for summary generation
- Subject to YouTube API quota limitations
- Dependent on Gemini Pro API availability
- ngrok free tier connections expire after 2 hours
- May need to restart Colab runtime occasionally

## License

[MIT License](LICENSE)

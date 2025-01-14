import streamlit as st
from googleapiclient.discovery import build
import isodate
from educhain import Educhain, LLMConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Initialize the AI model
gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=""
)
gemini_config = LLMConfig(custom_model=gemini_model)
client = Educhain(gemini_config)

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    return None

def get_video_captions(video_id):
    """Retrieve video captions if available"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript_list])
    except Exception:
        return None

def generate_notes(caption_text):
    """Generate structured notes from caption text"""
    prompt = f"""Based on the following video transcript, create comprehensive study notes. 
    Focus on key concepts, important points, and main ideas. Format the notes in a clear, 
    organized manner: {caption_text[:5000]}"""
    
    response = gemini_model.invoke(prompt).content
    return response

def generate_qna(video_link):
    """Generate questions and answers"""
    questions = client.qna_engine.generate_questions_from_youtube(
        url=video_link,
        num=3
    )
    return questions

def display_qna(questions):
    """Display questions and answers in a structured format"""
    st.markdown("### Generated Questions and Answers")
    
    # questions is directly a list of MultipleChoiceQuestion objects
    for i, q in enumerate(questions.questions, 1):  # Access the questions attribute
        st.markdown(f"#### Question {i}")
        
        # Question box with light background
        st.markdown(f"""
        <div style='background-color: #ed2828; padding: 10px; border-radius: 5px; margin-bottom: 10px'>
            {q.question}
        </div>
        """, unsafe_allow_html=True)
        # Other Options
        st.markdown("**All Options:**")
        for j, option in enumerate(q.options, 1):
            is_correct = option == q.answer
            background_color = '#1702f7' if is_correct else '#1702f7'
            st.markdown(f"""
            <div style='background-color: {background_color}; padding: 5px; border-radius: 5px; margin-bottom: 5px'>
                {j}. {option}
            </div>
            """, unsafe_allow_html=True)
        # Correct Answer
        st.markdown("**Correct Answer:**")
        st.markdown(f"""
        <div style='background-color: #29ad1a; padding: 10px; border-radius: 5px; margin-bottom: 10px'>
            {q.answer}
        </div>
        """, unsafe_allow_html=True)
        
        # Explanation
        st.markdown("**Explanation:**")
        st.markdown(f"""
        <div style='background-color: #90f073; padding: 10px; border-radius: 5px; margin-bottom: 10px'>
            {q.explanation}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
# Rest of the code remains the same
def get_youtube_recommendations(query, max_results=5):
    api_key = ""  
    youtube = build("youtube", "v3", developerKey=api_key)
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    ).execute()
   
    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
    video_details = youtube.videos().list(
        part="snippet,contentDetails",
        id=",".join(video_ids)
    ).execute()
    
    videos = []
    for item in video_details.get("items", []):
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        duration = item["contentDetails"]["duration"]
        url = f"https://www.youtube.com/watch?v={item['id']}"
        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
        readable_duration = convert_duration(duration)
        
        videos.append({
            "title": title,
            "channel": channel,
            "duration": readable_duration,
            "url": url,
            "thumbnail": thumbnail
        })
   
    return videos

def convert_duration(duration):
    parsed_duration = isodate.parse_duration(duration)
    hours, remainder = divmod(parsed_duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    result = []
    if hours > 0:
        result.append(f"{int(hours)}h")
    if minutes > 0:
        result.append(f"{int(minutes)}m")
    if seconds > 0:
        result.append(f"{int(seconds)}s")
    return " ".join(result)

# Streamlit UI
st.title("ExamAI - Your Helping Friend")

origin = st.text_input("Enter a topic to search for YouTube videos:")

if origin:
    videos_list = get_youtube_recommendations(origin, max_results=5)
    
    st.write("### Recommended Videos:")
    for idx, video in enumerate(videos_list, start=1):
        with st.container():
            st.image(video["thumbnail"], width=1000)
            
            st.markdown(
                f"**[{video['title']}]({video['url']})**\n"
                f"- Channel: {video['channel']}\n"
                f"- Duration: {video['duration']}\n"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Generate Q&A ({idx})"):
                    st.markdown(f"[Open Video in New Tab]({video['url']})")
                    questions = generate_qna(video_link=video['url'])
                    display_qna(questions)
            
            with col2:
                if st.button(f"Generate Summary ({idx})"):
                    st.markdown(f"[Open Video in New Tab]({video['url']})")
                    video_id = get_video_id(video['url'])
                    captions = get_video_captions(video_id) if video_id else None
                    
                    if captions:
                        st.markdown("### Video Summary")
                        notes = generate_notes(captions)
                        st.markdown(notes)
                    else:
                        st.warning("Captions are not available for this video. Unable to generate summary.")
            
            st.markdown("---")

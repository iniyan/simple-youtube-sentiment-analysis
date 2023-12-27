import os
import re
from googleapiclient.discovery import build
from textblob import TextBlob

# Set your YouTube API key here
API_KEY = 'APIkey'

# Function to extract comments from a YouTube video
def get_video_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []

    # Get video comments
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    )

    while request:
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        request = youtube.commentThreads().list_next(request, response)

    return comments

# Function to perform sentiment analysis on comments
def analyze_sentiment(comments):
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for comment in comments:
        analysis = TextBlob(comment)
        # Classify sentiment as positive, negative, or neutral
        if analysis.sentiment.polarity > 0:
            positive_count += 1
        elif analysis.sentiment.polarity < 0:
            negative_count += 1
        else:
            neutral_count += 1

    total_comments = len(comments)
    print(f"Total Comments: {total_comments}")
    print(f"Positive Comments: {positive_count} ({(positive_count / total_comments) * 100:.2f}%)")
    print(f"Negative Comments: {negative_count} ({(negative_count / total_comments) * 100:.2f}%)")
    print(f"Neutral Comments: {neutral_count} ({(neutral_count / total_comments) * 100:.2f}%)")

# Main function
def main():
    video_url = input("Enter YouTube video URL: ")
    video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", video_url)
    
    if video_id_match:
        video_id = video_id_match.group(0)
        comments = get_video_comments(API_KEY, video_id)
        analyze_sentiment(comments)
    else:
        print("Invalid YouTube video URL. Please provide a valid URL.")

if __name__ == "__main__":
    main()

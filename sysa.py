import csv
import os
import re
from googleapiclient.discovery import build
from textblob import TextBlob

# ANSI escape codes for color formatting
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
ENDC = '\033[0m'  # Reset color

# Set your YouTube API key here
API_KEY = 'apikey'

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
    positive_percentage = (positive_count / total_comments) * 100
    negative_percentage = (negative_count / total_comments) * 100
    neutral_percentage = (neutral_count / total_comments) * 100

    return {
        'Total Comments': total_comments,
        'Positive Comments': positive_count,
        'Positive Comments Percentage': positive_percentage,
        'Negative Comments': negative_count,
        'Negative Comments Percentage': negative_percentage,
        'Neutral Comments': neutral_count,
        'Neutral Comments Percentage': neutral_percentage,
    }

# Function to get video details (title and thumbnail URL) using video ID
def get_video_details(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Get video details
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )

    response = request.execute()

    if 'items' in response and response['items']:
        video_info = response['items'][0]['snippet']
        title = video_info['title']
        thumbnail_url = video_info['thumbnails']['default']['url']
        return {'Title': title, 'Thumbnail URL': thumbnail_url}
    else:
        return {'Title': '', 'Thumbnail URL': ''}

# Main function
def main():
    input_file_path = input("Enter the path of the CSV file containing video URLs: ")

    # Check if the input file exists
    if not os.path.exists(input_file_path):
        print(f"Error: The file '{input_file_path}' does not exist.")
        return

    # Read video URLs from the CSV file
    with open(input_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        videos = list(reader)

    # Prepare output CSV file
    output_file_path = 'sentiment_results.csv'
    with open(output_file_path, 'w', newline='') as output_file:
        fieldnames = [
            'Video Title', 'Video URL', 'Total Comments',
            'Positive Comments', 'Positive Comments Percentage',
            'Negative Comments', 'Negative Comments Percentage',
            'Neutral Comments', 'Neutral Comments Percentage',
            'Thumbnail URL'
        ]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        # Analyze sentiment for each video
        for video_url in videos:
            video_url = video_url[0]  # Assuming the URL is in the first column
            video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", video_url)

            if video_id_match:
                video_id = video_id_match.group(0)
                comments = get_video_comments(API_KEY, video_id)
                sentiment_results = analyze_sentiment(comments)
                video_details = get_video_details(API_KEY, video_id)

                # Write results to the output CSV file
                writer.writerow({
                    'Video Title': video_details['Title'],
                    'Video URL': video_url,
                    'Total Comments': sentiment_results['Total Comments'],
                    'Positive Comments': sentiment_results['Positive Comments'],
                    'Positive Comments Percentage': sentiment_results['Positive Comments Percentage'],
                    'Neutral Comments': sentiment_results['Neutral Comments'],
                    'Neutral Comments Percentage': sentiment_results['Neutral Comments Percentage'],
                    'Negative Comments': sentiment_results['Negative Comments'],
                    'Negative Comments Percentage': sentiment_results['Negative Comments Percentage'],
                    'Thumbnail URL': video_details['Thumbnail URL']
                })
            else:
                print(f"Invalid YouTube video URL: {video_url}")

    print(f"Results saved to {output_file_path}")

if __name__ == "__main__":
    main()

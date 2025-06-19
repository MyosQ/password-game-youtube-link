import sys
import os
from dotenv import load_dotenv
import requests
from datetime import timedelta
import isodate
import logging
import http

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.environ["API_KEY"]

# Cache?
def search_videos(query: str) -> list:
    """Search for YouTube videos based on a query.
    :param query: Search query string.
    :param max_total: Maximum number of video IDs to return.
    :return: List of video IDs.
    """
    search_url = "https://www.googleapis.com/youtube/v3/search"
    max_total = 100  # Maximum total results to return
    yt_max_results = 50  # YouTube API max results per request
    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": yt_max_results,
        "key": API_KEY,
        "fields": "items(id/videoId),nextPageToken",
    }
    video_ids = []
    page_token = None

    while len(video_ids) < max_total:
        # Add page token if available
        if page_token:
            search_params["pageToken"] = page_token

        # Make the API request
        res = requests.get(search_url, params=search_params)
        if res.status_code != http.HTTPStatus.OK:
            logger.error(f"Error fetching data: {res.status_code} - {res.text}")
            continue
        res_json = res.json()

        # Append video IDs from the current response
        video_ids += [item["id"]["videoId"] for item in res_json["items"]]
        page_token = res_json.get("nextPageToken")

        # Check if we have reached the maximum number of results
        if not page_token:
            break

    return video_ids

# Cache?
def get_video_durations(video_ids: list) -> dict:
    """Get durations of a list of YouTube videos.
    :param video_ids: List of YouTube video IDs.
    :return: Dictionary mapping video IDs to their durations. Example:
    {
        "video_id_1": timedelta(seconds=300),
        "video_id_2": timedelta(seconds=600),
    """
    details_url = "https://www.googleapis.com/youtube/v3/videos"
    details_params = {
        "part": "contentDetails",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    response = requests.get(details_url, params=details_params)
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f"Error fetching video details: {response.status_code} - {response.text}")
        sys.exit(1)

    durations = {}
    for item in response.json().get("items", []):
        vid_id = item["id"]
        iso_duration = item["contentDetails"]["duration"]
        duration = isodate.parse_duration(iso_duration)
        durations[vid_id] = duration

    return durations

def filter_videos_by_duration(durations: dict, target_duration: timedelta) -> dict:
    """Filter videos by duration to match the target duration.
    :param durations: Dictionary of video IDs and their durations.
    :param target_duration: Target duration as a timedelta object.
    :return: Dictionary of video IDs that match the target duration.
    """
    filtered_videos = {vid_id: dur for vid_id, dur in durations.items() if dur == target_duration}
    return filtered_videos

def get_best_video(durations: dict):
    """Find the best video id that match the target duration.
    :param durations: Dictionary of video IDs and their durations.
    :return: Tuple of video ID and information string.
    """
    def num_upper_case(s: str) -> int:
        return sum(c.isupper() for c in s)

    def num_digits(s: str) -> int:
        return sum(c.isdigit() for c in s)

    # Order by num upper case, then by num digits, ascending
    # Use video ids, ie key
    sorted_videos = sorted(
        durations.keys(),
        key=lambda vid_id: (
            num_upper_case(vid_id),
            num_digits(vid_id),
            durations[vid_id]
        )
    )
    print(f"Sorted videos: {sorted_videos}")
    return


def main(minutes: int, seconds: int):
    """
    Main function to run the YouTube search.

    :param minutes: Number of minutes to search for.
    :param seconds: Number of seconds to search for.
    :param max_results: Maximum number of results to return.
    """

    # 1. Search for videos
    search_query = f"{minutes} minutes {seconds} seconds"
    video_ids = search_videos(search_query)
    print(f"Found {len(video_ids)} videos for query: {search_query}")

    # 2. Get video durations
    durations = get_video_durations(video_ids)
    print(f"Retrieved durations for {len(durations)} videos.")

    # 3. Filter videos by duration to match target duration
    target_duration = timedelta(minutes=minutes, seconds=seconds)
    filtered_videos = filter_videos_by_duration(durations, target_duration)
    print(f"Filtered {len(filtered_videos)} videos matching target duration: {target_duration}")
    print("Filtered videos:", filtered_videos)

    # 4. Get the video with the "best" video id
    get_best_video(filtered_videos)

if __name__ == "__main__":
    minutes = 20
    seconds = 22
    main(minutes, seconds)
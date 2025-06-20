import sys
import os
from dotenv import load_dotenv
import requests
from datetime import timedelta
import isodate
import logging
import http
import argparse

from utils.formatting import bold, green, indent

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY: str = os.environ["API_KEY"]
YT_MAX_RES_PER_REQUEST: int = 50  # YouTube API max results per request

def get_video_duration_category(duration: timedelta) -> str:
    """Get the category of video duration.
    :param duration: Duration as a timedelta object.
    :return: Category string.
    """
    if not isinstance(duration, timedelta):
        raise ValueError("Duration must be a timedelta object.")
    elif duration < timedelta(minutes=4):
        return "short"
    elif duration < timedelta(minutes=20):
        return "medium"
    else:
        return "long"

def get_yt_search_query(duration: timedelta) -> str:
    """Get the YouTube search query based on the duration.
    :param duration: Duration as a timedelta object.
    :return: Search query string.
    """
    if not isinstance(duration, timedelta):
        raise ValueError("Duration must be a timedelta object.")

    minutes: int = duration.seconds // 60
    seconds: int = duration.seconds % 60
    return f"{minutes} minutes {seconds} seconds"

def search_videos_by_length(duration: timedelta) -> list:
    """Search for YouTube videos based on a query.
    :param duration: Duration as a timedelta object.
    :return: List of video IDs.
    """
    query = get_yt_search_query(duration)
    search_url = "https://www.googleapis.com/youtube/v3/search"
    max_total = 30  # Maximum total results to return
    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoDuration": get_video_duration_category(duration),
        "key": API_KEY,
        "fields": "items(id/videoId),nextPageToken",
    }
    video_ids = []
    page_token = None

    while len(video_ids) < max_total:
        # Limit the number of results per request
        search_params["maxResults"] = str(min(YT_MAX_RES_PER_REQUEST, max_total - len(video_ids)))

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

def get_video_durations(video_ids: list) -> dict:
    """Get durations of a list of YouTube videos.
    :param video_ids: List of YouTube video IDs.
    :return: Dictionary mapping video IDs to their durations. Example:
    {
        "video_id_1": timedelta(seconds=300),
        "video_id_2": timedelta(seconds=600),
        ...
    """
    details_url = "https://www.googleapis.com/youtube/v3/videos"
    durations = {}

    for i in range(0, len(video_ids), YT_MAX_RES_PER_REQUEST):
        chunk = video_ids[i:i + YT_MAX_RES_PER_REQUEST]
        details_params = {
            "part": "contentDetails",
            "id": ",".join(chunk),
            "key": API_KEY,
            "fields": "items(id,contentDetails(duration))",
        }
        response = requests.get(details_url, params=details_params)
        if response.status_code != http.HTTPStatus.OK:
            logger.error(f"Error fetching video details: {response.status_code} - {response.text}")
            sys.exit(1)

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

def sort_videos(durations: dict) -> list:
    """Find the best video id that match the target duration.
    :param durations: Dictionary of video IDs and their durations.
    :return: Tuple of video ID and information string.
    """
    def num_upper_case(s: str) -> int:
        return sum(c.isupper() for c in s)

    def num_digits(s: str) -> int:
        return sum(c.isdigit() for c in s)

    # Order by num upper case, then by num digits, ascending
    sorted_videos = sorted(
        durations.keys(),
        key=lambda vid_id: (
            num_upper_case(vid_id),
            num_digits(vid_id),
            durations[vid_id]
        )
    )
    return sorted_videos

def print_results(video_ids: list):
    """Print the results in a formatted way.
    :param video_ids: List of video IDs.
    """
    if not video_ids:
        print("No videos found :( 🌓🥚🐛")
        return

    print("\n" + indent(bold("Sorted video ids:")))
    for video_id in video_ids:
        print(f"{indent(green(video_id))}")
    print()

def main(minutes: int, seconds: int):
    """
    Main function to run the YouTube search.

    :param minutes: Number of minutes to search for.
    :param seconds: Number of seconds to search for.
    """

    # 1. Search for videos
    duration = timedelta(minutes=minutes, seconds=seconds)
    video_ids = search_videos_by_length(duration)
    logger.info(f"Got {bold(len(video_ids))} videos from search")

    # 2. Get video durations
    durations = get_video_durations(video_ids)
    logger.info(f"Retrieved durations for {bold(len(durations))} videos.")

    # 3. Filter videos by duration to match target duration
    target_duration = timedelta(minutes=minutes, seconds=seconds)
    filtered_videos = filter_videos_by_duration(durations, target_duration)
    logger.info(f"Found {bold(len(filtered_videos))} videos matching target duration: {target_duration}")

    # 4. Sort and print videos by ID characteristics
    sorted_videos = sort_videos(filtered_videos)
    logger.info(f"Sorted {bold(len(filtered_videos))} videos by ID characteristics.")
    print_results(sorted_videos)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search YouTube videos by duration.")
    parser.add_argument("--minutes", type=int, default=20, help="Number of minutes")
    parser.add_argument("--seconds", type=int, default=23, help="Number of seconds")
    args = parser.parse_args()

    main(args.minutes, args.seconds)
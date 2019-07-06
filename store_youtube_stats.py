import json
import urllib.parse
import urllib.request
import os

GOOGLE_API_KEY = 'YOUR-API-KEY'
BASE_YOUTUBE_URL = 'https://www.googleapis.com/youtube/v3'


class PlayListItemsAPI:
    def __init__(self,playlist_id: str,next_token = None):
        self.result = get_result(build_playlist_items_url(playlist_id,50,next_token))
        self.next_token = next_token
        
class VideoAPI:
    def __init__(self,video_id : str):
        self.result = get_result(build_video_statistics_url(video_id))


def build_playlist_items_url(playlist_id : str, 
                            max_results : int, 
                            next_page_token = None) -> str:
    parameters = [
        ('key', GOOGLE_API_KEY), ('part', 'snippet'),
        ('maxResults',max_results),
        ('playlistId',playlist_id)
    ]
    if next_page_token != None: # if token is None, youre building URL for first page
        parameters.append(['pageToken',next_page_token])
        
    print("\t",BASE_YOUTUBE_URL + '/playlistItems?' + urllib.parse.urlencode(parameters))	
    return BASE_YOUTUBE_URL + '/playlistItems?' + urllib.parse.urlencode(parameters)


def build_video_statistics_url(video_id : str) -> str:
    '''Builds URL to gather statitstics for Youtube video '''
    parameters = [
        ('key',GOOGLE_API_KEY),
        ('part','statistics'),
        ('id',video_id)
    ]
    return BASE_YOUTUBE_URL +'/videos?' + urllib.parse.urlencode(parameters)

def get_result(url: str) -> dict:
    response = None
    try:
        response = urllib.request.urlopen(url)
        json_text = response.read().decode(encoding = 'utf-8')
        return json.loads(json_text)
    finally:
        if response != None:
            response.close()


def get_playlist_video_count(playlist : PlayListItemsAPI) -> int:
    '''Returns number of videos in playlist. Assumes result being passed in 
    was constructed from playlists API and contains the following keys'''
    return int(playlist.result["pageInfo"]["totalResults"])

def get_video_id(playlist : PlayListItemsAPI , video_index : int) -> str:
    ''' Given a dictionary of JSON response and the index of the video within the
        JSON response, returns the video ID.... Typically used during iteration'''
    return playlist.result["items"][video_index]["snippet"]["resourceId"]["videoId"]

def get_video_publish_date(playlist: PlayListItemsAPI , video_index: int) -> str:
    ''' Given a dictionary of JSON response and the index of the video within the
        JSON response, returns the date video was published.... Typically used during iteration'''
    return playlist.result["items"][video_index]["snippet"]["publishedAt"][:10]

def get_page_video_count(playlist : PlayListItemsAPI) -> int:
    ''' Given a dictionary of JSon responses, provides the number of videos listed in the dictionary
        .... useful for iteration'''
    return len(playlist.result["items"])

def get_video_likes_and_dislikes(video: VideoAPI) -> tuple:
    return (int(video.result["items"][0]["statistics"]["likeCount"]),
            int(video.result["items"][0]["statistics"]["dislikeCount"])
    )            

def get_video_view_count(video: VideoAPI) -> int:
    return int(video.result["items"][0]["statistics"]["viewCount"])


def get_video_comment_count(video : VideoAPI) -> int:
    return int(video.result["items"][0]["statistics"]["commentCount"])

def get_video_title(playlist: PlayListItemsAPI, video_index: int) -> str:
    return playlist.result["items"][video_index]["snippet"]["title"]

def main():
    playlist_id = input('Playlist ID: ')
    playlist = PlayListItemsAPI(playlist_id) # first page
    total_video_count = get_playlist_video_count(playlist)

    file_name = input("Enter file name to insert data")
    mode = "a" if file_name in os.listdir(".") else "w"
    next_page_token = None
    with open(file_name,mode) as f:
        while (total_video_count > 0):
            ### print phase
            page_video_count = get_page_video_count(playlist)
            for index in range(page_video_count):
                video_id = get_video_id(playlist,index)
                video_stats = get_result(build_video_statistics_url(video_id))
                video_stats = VideoAPI(video_id)
                print(get_video_title(playlist,index),end="\t")
                print(get_video_publish_date(playlist,index), end = "\t")
                if ("#" in get_video_title(playlist,index)):
                    views = get_video_view_count(video_stats)
                    print(views)
                    f.write(get_video_title(playlist,index).split()[3][1:] + "\t" + str(views) + "\n")
                else:
                    print()
            # increment phase// set playlist_result to next page and find new token for next page
            next_page_token = playlist.result['nextPageToken'] if (total_video_count > 50) else None
            print(next_page_token)
            playlist = PlayListItemsAPI(playlist_id,next_page_token)
            total_video_count -= page_video_count

if __name__ == '__main__':
    main()

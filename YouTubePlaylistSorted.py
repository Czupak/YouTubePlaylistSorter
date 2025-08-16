import sys
import os
import datetime as dt
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class YouTube:

    def __init__(self):
        self.token_file = 'token.pickle'
        self.credentials_file = 'credentials.json'
        self.valid_sort_by = ['published']
        self.youtube = None
        self.validate()
        self.authenticate()

    def validate(self):
        if not os.path.isfile(self.credentials_file):
            sys.exit(f'{self.credentials_file} missing, please create it using credentials.sample.json as example.')

    def run(self,
            source_playlist_id: str,
            destination_playlist_name: str,
            sort_by: str = 'published') -> None:
        if sort_by not in self.valid_sort_by:
            sys.exit(f'Not supported sort_by={sort_by}')
        # TODO: Check if it exists
        new_playlist = self.create_playlist(destination_playlist_name,
                                            'Sorted by publication order')

        videos = self.get_playlist_videos(source_playlist_id)
        videos = sorted(videos, key=lambda x: x[sort_by])
        print(len(videos))
        i = 0
        for video in videos:
            i += 1
            print(
                f'{i}/{len(videos)} [{int(i / len(videos) * 100)}%: {video=}')
            self.add_video_to_playlist(new_playlist, video['id'])

    def authenticate(self):
        self.youtube = build('youtube', 'v3', credentials=self._authenticate())

    # def check_quota(self):
    #     youtube = build('serviceusage', 'v1', credentials=self._authenticate())
    #     quota_response = (
    #         youtube.services().quota(name='services/youtube.googleapis.com:quota')
    #         .execute()
    #     )
    #
    #     for metric in quota_response.get('metricValues', []):
    #         print(f"{metric['displayName']:<30} "
    #               f"{metric['currentValue']:>6} / {metric['maxValue']} {metric['unit']}")

    def _authenticate(self):
        scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
        creds = None
        if os.path.exists(self.token_file):
            print(f'Cached token found [{self.token_file}].')
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(f'Refreshing token file [{self.token_file}].')
                creds.refresh(Request())
            else:
                print(f'Authenticating [{self.token_file}].')
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as token:
                # noinspection PyTypeChecker
                pickle.dump(creds, token)
                print(f'Token cached [{self.token_file}].')

        return creds

    def reset_authentication_cache(self):
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            print(f'Token file removed [{self.token_file}].')
        else:
            print(f'Token file does not exist [{self.token_file}].')

    def parse_date(self, text):
        return dt.datetime.fromisoformat(text)

    def get_playlist_videos(self, playlist_id):
        videos = []
        request = self.youtube.playlistItems().list(part="contentDetails",
                                                    playlistId=playlist_id,
                                                    maxResults=50)
        while request:
            response = request.execute()
            for item in response['items']:
                print(item)
                video_id = item['contentDetails']['videoId']
                if 'videoPublishedAt' in item['contentDetails']:
                    published = item['contentDetails']['videoPublishedAt']
                    published = self.parse_date(published)
                else:
                    published = dt.datetime.now(dt.timezone.utc)
                videos.append({"id": video_id, "published": published})
            request = self.youtube.playlistItems().list_next(request, response)
        return videos

    def list_playlists(self):
        request = self.youtube.playlists().list(part="snippet", mine=True)
        response = request.execute()
        for item in response['items']:
            print(f"Title: {item['snippet']['title']}, ID: {item['id']}")

    def create_playlist(self, title, description):
        try:
            playlist_request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description
                    },
                    "status": {
                        "privacyStatus":
                        "public"  # Options: public, private, unlisted
                    }
                })
            response = playlist_request.execute()
            print(
                f"Playlist '{title}' created successfully! ID: {response['id']}"
            )
            return response['id']
        except HttpError as e:
            print(f"An error occurred: {e}")

    def add_video_to_playlist(self, playlist_id, video_id):
        try:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                })
            response = request.execute()
            print(
                f"Video '{video_id}' added to playlist '{playlist_id}' successfully!"
            )
        except Exception as e:
            print(f"An error occurred: {e}")


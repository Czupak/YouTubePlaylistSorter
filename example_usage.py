from YouTubePlaylistSorted import YouTube

if __name__ == '__main__':
    yt = YouTube()
    source_playlist_id, destination_playlist_name = 'SOURCE_PLAYLIST_ID', 'DESTINATION_PLAYLIST_NAME'
    yt.run(source_playlist_id, destination_playlist_name)

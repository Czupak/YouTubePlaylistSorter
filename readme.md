# YouTube Playlist Sorter
## About
This script allows to create playlist from some other playlist and sort the videos.

Supported sorting methods:
- by publication time ascending
- TODO
## Usage
`example_usage.py`

This will create playlist "DESTINATION_PLAYLIST_NAME" on your account and insert videos from a playlist with SOURCE_PLAYLIST_ID.

You can find playlist id in the playlist url after `list=`.
```python
from YouTubePlaylistSorted import YouTube

if __name__ == '__main__':
    yt = YouTube()
    source_playlist_id, destination_playlist_name = 'SOURCE_PLAYLIST_ID', 'DESTINATION_PLAYLIST_NAME'
    yt.run(source_playlist_id, destination_playlist_name)
```

## Installation
### Create virtual environment and install packages

```bash
python -m venv .venv
.venv/bin/activate
pip install -r requirements.txt
```
### Update credentials
TODO

Create `credentials.json` based on `credentials.sample.json`.

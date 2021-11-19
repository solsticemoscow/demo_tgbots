import youtube_dl
import os


class YT_DOWNLOADER(object):

    def __init__(self, link='https://www.youtube.com/watch?v=yBX-33bbK6I'):
        self.url = link
        self.mp3file = ''


    def progress_hook(self, response):
        # if response['status'] == 'downloading':
        #     print("Downloading...")
        if response["status"] == "finished":
            file_name = response["filename"]
            self.mp3file = os.path.splitext(file_name)[0]+'.mp3'


    def get_start(self, link):
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                self.url, download=False)
            title = meta['title']
            file = title + '.mp3'


    def get_download(self, url):
        path = 'FILES/'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtml': path + '%(title)s.mp3',
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', }]
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                return self.mp3file
        except Exception as e:
            return e







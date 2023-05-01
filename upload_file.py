import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

# Replace this with the path to the file you want to monitor
FILE_PATH = './file.txt'

# Replace this with the API endpoint you want to upload the file to
API_ENDPOINT = 'https://cms.hitness.club/files'
AUTH_TOKEN= os.environ['AUTH_TOKEN']
FILE_ID ='4cb520df-78b2-497a-afa0-b66004793edf'


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.debounced_upload = None
        self.debounce_interval = 1  # 1 second debounce interval

    def on_modified(self, event):
        if event.src_path == FILE_PATH:
            if self.debounced_upload:
                self.debounced_upload.cancel()

            self.debounced_upload = threading.Timer(self.debounce_interval, self.upload_file)
            self.debounced_upload.start()

    def upload_file(self):
        with open(FILE_PATH, 'rb') as file:
            files = {'file': (os.path.basename(FILE_PATH), file)}
            data = {'title': 'program'}
            response = requests.patch(f'{API_ENDPOINT}/{FILE_ID}', files=files, data=data, headers={'Authorization': f'Bearer {AUTH_TOKEN}'})
            print(f"File uploaded: {response.status_code},\n {response.request.body},\n {response.request.url},\n {response.request.headers}")


def main():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(
        FILE_PATH), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()

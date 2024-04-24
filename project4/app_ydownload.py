'''
2024.01.24

function:
    API youtube download

code by Dan
'''

import os

from fastapi import FastAPI
from typing import Union
from datetime import date

#### PATH
BASEDIR = '/mnt/storage_10tb/nas_mount/data'

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print("Start server")

@app.on_event("shutdown")
def shutdown_event():
    print("End server")
    
@app.get('/download_youtube')
def select_target(url,person):
    today = str(date.today().year) + "_" + str(date.today().month) + "_" + str(date.today().day)
    path = os.path.join(BASEDIR, person, today)
    os.makedirs(path, exist_ok=True)
    cmd = f'yt-dlp -x "wav" --audio-format "wav" --audio-quality "0" -o "{path}/%(title)s.%(ext)s" {url}'
    os.system(cmd)
    return f"NAS download successful"


if __name__ == "__main__":    
    # start server with initial setting
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
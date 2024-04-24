# PYTHON BASE
import os
import argparse
import subprocess

# EXTERNAL LIBRARY
from glob import glob
from tqdm import tqdm
from config import cfg
from logger import Logger

from speechbrain.inference.speaker import SpeakerRecognition
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

def readfile(fpath:str)-> list:
   file = open(fpath,"r")
   rows = file.readlines()
   return rows

def cutaudio(fpath:str,savepath:str,start:str,end:str)-> None:
   cmd = ["ffmpeg","-i",fpath,"-ss",start,"-to",end,"-c","copy",savepath]
   subprocess.call(cmd)

# Deepfake Detection Data Audio
class D3A:
   def __init__(self):
      self.logger = Logger(cfg['loggername'])
      self.adir = cfg['adir'] # audio folder
      self.pdir = cfg['pdir'] # result dir
      self.sdir = cfg['sdir'] # script dir
      self.rdir = cfg['rdir'] # reference audio dir
      self.ddir = cfg['ddir'] # donwload lists tsv dir
      self.ptarget = cfg['ptarget'] # preprocess targets
   
   @staticmethod
   def yt_dlp(url:str,savedir:str,savename:str)-> None:
      cmd = ["yt-dlp","-q","-x",url,"--audio-format","wav","--audio-quality","0","-o",f"{savedir}/{savename}.%(ext)s"]
      subprocess.call(cmd)
   
   @staticmethod
   def whisper(audiopath:str,savedir:str)-> None: # audio path | output path
      cmd = ["whisper",audiopath,"--language","English","--output_dir",savedir,"--output_format","srt"]
      subprocess.call(cmd)
   
   @staticmethod
   def calculate_similarity(aud_ref:str,aud_test:str)-> str: # aud_ref: reference audio | aud_test: test audio
      score, prediction = verification.verify_files(aud_ref,aud_test)
      return score
   
   def download(self)-> None:
      for target in self.ptarget:
         self.logger.step_info(f"download {target}","start")
         rows = readfile(self.ddir,f"{target}.tsv")
         for row in rows[1:]:
            ori_name,save_name,url = row.split("\t")
            if url.startswith("https://") and (target in save_name):
               self.yt_dlp(url,self.adir,save_name)
               self.logger.success_url(url)
            else:
               self.logger.error_url(url)
         self.logger.step_info("download","complete")

   def split(self)-> None:
      for target in self.ptarget:
         self.logger.step_info(f"split {target}","start")
         audios = sorted(glob(os.path.join(self.adir,"*.wav")))
         for apath in audios:
            self.whisper(apath,self.sdir)
            aname = os.path.basename(apath[:-4])
            script_path = os.path.join(self.sdir,aname+".srt")
            if os.path.isfile(script_path):
               rows = readfile(script_path)
               index = [rows[x].strip() for x in range(0,len(rows),4)]
               start = [rows[x+1].split("-->")[0].strip().replace(",",".") for x in range(0,len(rows),4)]
               end = [rows[x+1].split("-->")[-1].strip().replace(",",".") for x in range(0,len(rows),4)]
               for index, start, end in zip(index,start,end):
                  savepath = os.path.join(self.pdir,f"{aname}_{str(index).zfill(5)}.wav")
                  os.makedirs(os.path.dirname(savepath),exist_ok=True)
                  cutaudio(apath,savepath,start,end)
            else:
               self.logger.error_file(script_path)
         self.logger.step_info(f"split {target}","complete")

   def clean(self)-> None:
      for target in self.ptarget:
         self.logger.step_info(f"clean {target}","start")
         refaudios = sorted(glob(os.path.join(self.rdir,f"{target}*.wav")))
         testaudios = sorted(glob(os.path.join(self.pdir,f"{target}*.wav")))
         file = open("result.txt","w")
         for taudio in tqdm(testaudios):
            result = []
            for raudio in refaudios:
               result.append(self.calculate_similarity(raudio,taudio))
               cmd1 = ["rm","-rf",os.path.basename(taudio)]
               cmd2 = ["rm","-rf",os.path.basename(raudio)]
               subprocess.call(cmd1)
               subprocess.call(cmd2)
            score = round(sum(result).item()/len(result),2)
            if score < 0.55:
               cmd3 = ["rm","-rf",taudio]
               subprocess.call(cmd3)
            file.write(f"{taudio}\t{score}\n")
         self.logger.step_info(f"clean {target}","complete")


if __name__ == "__main__":
   johnwick = D3A()
   # johnwick.download()   # STEP1: download youtube url
   # johnwick.split()      # STEP2: split audio -> sentences
   johnwick.clean() # STEP3: clean irrelvant audio
   
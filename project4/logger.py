import logging



class Logger:
    def __init__(self,name:str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(u'%(asctime)s [%(levelname)s] %(message)s')
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)    
        
    def step_info(self,step:str,status:str)-> None:
        self.logger.info(f"Step: {step}\tStatus: {status}")
    
    def success_url(self,url:str)-> None:
        self.logger.info(f"URL: {url.strip()} downloaded")
    
    def error_url(self,url:str)-> None:
        self.logger.error(f"Invalid URL error: {url}")
    
    def error_file(self,fpath:str)-> None:
        self.logger.error(f"{fpath} does not exist.")


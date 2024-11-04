from dotenv import load_dotenv
import js
import os
from os.path import join, dirname
    def test():    
        os.environ["NEW"] = "NEW"
        dotenv_path = join(dirname(__file__), '/.env')
        load_dotenv(dotenv_path)
        print(os.environ)
        print(os.getenv("TEST"))

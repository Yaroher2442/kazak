import requests
import zlib,hashlib,uuid 
import json
from flask import Flask , request , abort , redirect ,

flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET', 'POST'])
def fl():
    return 'hellow'    

if __name__ == '__main__':
    # main()
    flask_app.run()
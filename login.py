from flask import Flask, jsonify, abort, request, make_response
import os, copy, sys, time, uuid ,hashlib
import json
import hashlib, requests, json, smtplib
import urllib.request
from flask import Flask , request , abort , redirect , Response ,url_for
from flask_login import LoginManager , login_required , UserMixin , login_user, current_user
from DB import Database

flask_app = Flask(__name__)

db=Database()
# db.select()

class API(object):
    def __init__(self, arg):
        super(API, self).__init__()
        self.arg = arg

    @flask_app.route('/login' , methods=['GET' , 'POST'])
    def login():
        if request.method == 'POST':
            data=request.get_data()
            encode_data=json.loads(data.decode())       

            email=encode_data['email']
            password=encode_data['password']

            registeredUser = U_Rep.get_user(email)

            db.create_connection()
            if db.find_user(email)!=False:
                hash_pass=db.find_user(email)
                def check_password(hashed_password, user_password):
                    password, salt = hashed_password.split(':')
                    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
                if check_password(hash_pass,password):
                    item={'Status':'User is login'}
                    resp = make_response(jsonify(item))
                    resp.headers['Access-Control-Allow-Origin'] = '*'
                    return resp
                else:
                    item={'Status':'Password false'}
                    resp = make_response(jsonify(item))
                    resp.headers['Access-Control-Allow-Origin'] = '*'
                    return resp
            else:
                item={'Status':'User not found'}
                resp = make_response(jsonify(item))
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp         

            if registeredUser != None and registeredUser.password == password:
                print(registeredUser.password)
                print('Logged in..')
                login_user(registeredUser)
                item={'Status':'User is login'}
                resp = make_response(jsonify(item))
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp
            else:
                item={'Status':'User not found'}
                resp = make_response(jsonify(item))
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp
        else:
            return abort(401)

    @flask_app.route('/register' , methods = ['GET' , 'POST'])
    def register():
        if request.method == 'POST':

            email=request.form.get('email')
            password=request.form.get('password')

            def hash_password(password):
                salt = uuid.uuid4()
                return salt,hashlib.sha256(salt.hex.encode() + password.encode()).hexdigest() + ':' + salt.hex

            u_id,hash_p=hash_password(password)
            new_U=(str(u_id),email,str(hash_p),encode_data['name'],encode_data['surname'])
            db.create_connection(g._database)
            db.insert_User(new_U)

            new_user = User(email , password , U_Rep.next_index())
            U_Rep.save_user(new_user)
            
            return 'Registered Successfully'
        else:
            return abort(401)

@flask_app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
       
@login_manager.user_loader
def load_user(userid):
    print(users_repository.get_user_by_id(userid))
    return users_repository.get_user_by_id(userid)


# print(json.dumps(encode_data,sort_keys=True, indent=4))
if __name__ == '__main__':
    flask_app.run()

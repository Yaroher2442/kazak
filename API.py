# -*- coding: utf-8 -*-
import os, copy, sys, time, uuid ,hashlib
import json
import hashlib, requests, json
import urllib.request

from flask import jsonify, make_response ,redirect, url_for
from flask import Flask , request , abort , redirect , Response ,url_for ,render_template ,render_template_string, flash

import sqlite3
from flask import g

from bs4 import BeautifulSoup

from DB import Database

DATAFILE=os.path.join(os.getcwd(),'db','data_file.db')
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
         db = g._database = sqlite3.connect(DATAFILE)
         
    return db

flask_app = Flask(__name__)
flask_app.secret_key = os.urandom(24)


@flask_app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def html_error_replacer(file_name,error):
		old_html_str=''
		soup = BeautifulSoup(open(os.path.join(os.getcwd(),'templates', file_name), 'r' , encoding= 'utf-8'), "lxml")
		err_tag =soup.find(id='error')
		err_tag.string = error
		return render_template_string(soup.prettify())

class API(object):
	def __init__(self, arg):
		super(API, self).__init__()
		self.arg = arg

	@flask_app.route('/', methods=['GET', 'POST'])
	def log():
		if request.method == 'GET':
			get_db()
			print(g._database)
			return render_template('auth.html')
		else:
			return abort(401)

	@flask_app.route('/index_admin', methods=['GET', 'POST'])
	def index_admin():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("index_admin.html")
#---------------------------------------------------------------------
	@flask_app.route('/sud_dela', methods=['GET', 'POST'])
	def sud_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			get_db()
			db=Database(g._database)
			d_table = db.get_join_table('Litigation')
			return render_template("sud_dela_admin.html",
				data=d_table)
#----------------------------------------------------------------------
	@flask_app.route('/bank_dela', methods=['GET', 'POST'])
	def bank_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("bank_dela_admin.html")

	@flask_app.route('/pre_sud', methods=['GET', 'POST'])
	def pre_sud():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("pre_sud_admin.html")

	@flask_app.route('/none_sud', methods=['GET', 'POST'])
	def none_sud():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("none_sud_admin.html")
	
	@flask_app.route('/employees', methods=['GET', 'POST'])
	def employees():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("employees.html")

	@flask_app.route('/login' , methods=['GET' , 'POST'])
	def login():
		if request.method == 'POST':     
			email=request.form.get('email')
			password=request.form.get('password')
			get_db()
			db=Database(g._database)
			if db.find_user(email)[0][3]!=False:
				hash_pass=db.find_user(email)[0][3]
				def check_password(hashed_password, user_password):
					password, salt = hashed_password.split(':')
					return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
				if check_password(hash_pass,password):
					response = make_response(redirect('/sud_dela'))
					response.set_cookie('user_id',db.find_user(email)[0][0])
					return response
				else:
					return html_error_replacer('auth.html','Password false')
			else:
				return html_error_replacer('auth.html','User not found or name invalid')   
		else:
			return render_template('auth.html')

	@flask_app.route('/register' , methods = ['GET' , 'POST'])
	def register():
		if request.method == 'POST':
			email=request.form.get('email')
			password=request.form.get('password')
			Access_level=request.form.get('Access_level')
			name=request.form.get('name')
			surname=request.form.get('surname')
			lastname=request.form.get('lastname')
			def hash_password(password):
				salt = uuid.uuid4()
				return salt,hashlib.sha256(salt.hex.encode() + password.encode()).hexdigest() + ':' + salt.hex
			u_id,hash_p=hash_password(password)
			new_U=(str(u_id),Access_level,email,str(hash_p),name,surname,lastname)
			get_db()
			db=Database(g._database)
			db.insert_User(new_U)
			return 'Registered Successfully'
		else:
			return abort(401)

	@flask_app.errorhandler(401)
	def page_not_found(e):
	    return Response('<p>Login failed</p>')
	
# print(json.dumps(encode_data,sort_keys=True, indent=4))
if __name__ == '__main__':
    flask_app.run()

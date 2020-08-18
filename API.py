# -*- coding: utf-8 -*-
import os, copy, sys, time, uuid ,hashlib 
import json
import hashlib, requests, json
import urllib.request

from flask import jsonify, make_response ,redirect, url_for
from flask import Flask , request , abort , redirect , Response ,url_for ,render_template ,render_template_string, flash

import sqlite3
from flask import g

from werkzeug.utils import secure_filename

from bs4 import BeautifulSoup

from DB import Database

from pprint import pprint

DATAFILE=os.path.join(os.getcwd(),'db','data_file.db')
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
         db = g._database = sqlite3.connect(DATAFILE)
         
    return db

flask_app = Flask(__name__)
flask_app.secret_key = os.urandom(24)
flask_app.config['UPLOAD_FOLDER']=os.path.join(os.getcwd(),'U_files')
# flask_app.config['UPLOAD_FOLDER_AGREE'] = os.path.join(os.getcwd(),'U_files','agreement')
# flask_app.config['UPLOAD_FOLDER_PAY'] = os.path.join(os.getcwd(),'U_files','payment')
ALLOWED_EXTENSIONS = {'pdf','jpg','jpeg'}

@flask_app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def html_error_replacer(file_name,error):
		soup = BeautifulSoup(open(os.path.join(os.getcwd(),'templates', file_name), 'r' , encoding= 'utf-8'), "lxml")
		err_tag =soup.find('label',id='error')
		err_tag.string = error
		return render_template_string(soup.prettify())

def success_replacer(file_name,success):
		soup = BeautifulSoup(open(os.path.join(os.getcwd(),'templates', file_name), 'r' , encoding= 'utf-8'), "lxml")
		success_tag =soup.find('p',id='success_here')
		success_tag.string = success
		pprint(soup)
		return render_template_string(soup.prettify())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def tables_sets(table_name):
	tables={
	'Affairs':['t_id','u_id','Client','Type','Practice','Project_Manager','Lawyers','Agreement','Invoice','Came_from','Comment','Invoice_status'],
	'Litigation':['t_id','Case_number','Tribunal','Judge'],
	'Bankruptcy':[],
	'Pre_trial_settlement':[],
	'Enforcement_proceedings':[],
	'Non_judicial':[],
	'Сourts':[]
	}
	return tables[table_name]
class API(object):
	def __init__(self, arg):
		super(API, self).__init__()
		self.arg = arg

	@flask_app.route('/', methods=['GET', 'POST'])
	def log():
		if request.method == 'GET':
			get_db()
			if request.cookies.get('user_id') == None:
				return render_template('auth.html')
			else:
				return redirect('/sud_dela')
		else:
			return abort(401)

	@flask_app.route('/index_admin', methods=['GET', 'POST'])
	def index_admin():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			return render_template("index_admin.html")
#---------------------------------------------------------------------
	@flask_app.route('/add_sud_delo', methods=['GET', 'POST'])
	def add_sud_delo():
		if request.method == 'POST':
			# image = request.files.get('file1')
			new_t_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)

			file_agree = request.files["Agreement"]
			file_invoice = request.files["Invoice"]
			if file_agree and file_invoice :					
				if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
					if new_t_id not in os.listdir(os.path.join(os.getcwd(),flask_app.config['UPLOAD_FOLDER'])):
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
					else:
						return html_error_replacer(os.path.join('admin','add','add_sud_delo.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('admin','add','add_sud_delo.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				pprint(adding_dict)
				list_to_Affairs=[]
				for margin in tables_sets('Affairs'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Судебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],request.cookies.get('user_id'),'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],request.cookies.get('user_id'),'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Litigation=[]
				for margin in tables_sets('Litigation'):
					print(margin)
					if margin == 't_id':
						list_to_Litigation.append(new_t_id)
					else:
						list_to_Litigation.append(adding_dict[margin][0])
				pprint(list_to_Litigation)
				db.insert_tables('Litigation',tuple(list_to_Litigation))

				return redirect('/sud_dela')
			else:
				return html_error_replacer(os.path.join('admin','add','add_sud_delo.html'),'Не загружены файлы')

		if request.method == 'GET':
			if request.cookies.get('user_id') == None:
				return redirect('/login')
			else:
				user=request.cookies.get('user_id')
				get_db()
				db=Database(g._database)
				user_info=db.find_user_by_id(user)
				role=user_info[0]
				name=' '.join(user_info[1:])
				return render_template('admin/add/add_sud_delo.html',
					role=role,
					name=name,
					urists=[1,2,3])



#---------------------------------------------------------------------
	@flask_app.route('/sud_dela', methods=['GET', 'POST'])
	def sud_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table('Litigation')
			if d_table != False:
				colors=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					buf=item[2]
					item[2]=';\n'.join(json.loads(buf))
				return render_template("admin/sud_dela.html",
				data=d_table,
				role=role,
				name=name,
				urists=[1,2,3],
				colors=colors)
			else:
				return render_template("admin/sud_dela.html",
				data=[],
				role=role,
				name=name,
				urists=[1,2,3],
				colors=[])
			

#----------------------------------------------------------------------
	@flask_app.route('/bank_dela', methods=['GET', 'POST'])
	def bank_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("bank_dela_admin.html")
#---------------------------------------------------------------------
	@flask_app.route('/pre_sud', methods=['GET', 'POST'])
	def pre_sud():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("pre_sud_admin.html")
#---------------------------------------------------------------------
	@flask_app.route('/none_sud', methods=['GET', 'POST'])
	def none_sud():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("none_sud_admin.html")
#---------------------------------------------------------------------	
	@flask_app.route('/employees', methods=['GET', 'POST'])
	def employees():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			print(request.cookies.get('user_id'))
			return render_template("employees.html")
#---------------------------------------------------------------------
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

# -*- coding: utf-8 -*-
import os, copy, sys, time, uuid  
import json
import hashlib,zlib,requests, json
import urllib.request
import shutil

from flask import jsonify, make_response ,redirect, url_for, send_from_directory
from flask import Flask , request , abort , redirect , Response ,url_for ,render_template ,render_template_string, flash

import sqlite3
from flask import g

from werkzeug.utils import secure_filename

from bs4 import BeautifulSoup

from DB import Database

from pprint import pprint

#_______________________________________________________________________________________________
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
#_______________________________________________________________________________________________
def html_error_replacer(file_name,error):
		soup = BeautifulSoup(open(os.path.join(os.getcwd(),'templates', file_name), 'r' , encoding= 'utf-8'), "lxml")
		err_tag = soup.find(id='error')
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
def tables_sets(mode,table_name=None):
	tables={
	'Affairs':['t_id','u_id','Client','Type','Practice','Project_Manager','Lawyers','Agreement','Invoice','Came_from','Comment','Invoice_status'],
	'Litigation':['t_id','Case_number','Tribunal','Judge'],
	'Bankruptcy':['t_id','Bankruptcy_case_number','Arbitration_manager'],
	'Pre_trial_settlement':['t_id','Case_number','Agency',],
	'Enforcement_proceedings':['t_id','Executive_case_number','Amount','FSSP','Bailiff'],
	'Non_judicial':['t_id','Nature_of_work','Term'],
	'Sud':['c_id','u_id','client','date','time','lawyer','judge','tribunal','instance','comment'],
	'users':['id','alevel','email','password','name','surname','lastname']
	}
	if mode == 'keys':
		return tables.keys()
	elif mode == 'fields':
		return tables[table_name]
#_______________________________________________________________________________________________
class API(object):
	def __init__(self, arg):
		super(API, self).__init__()
		self.arg = arg
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
	@flask_app.route('/download_files/<t_id>/<type_f>/<filename>', methods=['GET', 'POST'])
	def download_files(t_id,type_f,filename):
		if request.method == 'GET':
			try:
				directory=os.path.join(flask_app.config['UPLOAD_FOLDER'],t_id,type_f)
				return send_from_directory(directory, filename=filename, as_attachment=True)
			except FileNotFoundError:
				abort(404)
#---------------------------------------------------------------------
	@flask_app.route('/admin/delite_element/<type>/<way>/<t_id>', methods=['GET', 'POST'])
	@flask_app.route('/user/delite_element/<type>/<way>/<t_id>', methods=['GET', 'POST'])
	def delite_element(type,way,t_id):
		if request.method == 'GET' :
			get_db()
			db=Database(g._database)
			for i in tables_sets(mode='keys'):
				db.delite_data(i,t_id)
			path=os.path.join(flask_app.config['UPLOAD_FOLDER'],t_id)
			shutil.rmtree(path)
			print('/'+type+'/'+way)
			return redirect('/'+type+'/'+way)
#---------------------------------------------------------------------
	@flask_app.route('/admin/delite_sud/<type>/<way>/<c_id>', methods=['GET', 'POST'])
	@flask_app.route('/user/delite_sud/<type>/<way>/<c_id>', methods=['GET', 'POST'])
	def delite_sud(type,way,c_id):
		if request.method == 'GET' :
			get_db()
			db=Database(g._database)
			db.delite_sud(c_id)
			return redirect('/'+type+'/'+way)
#---------------------------------------------------------------------
	@flask_app.route('/admin/change_invoice_status/<type>/<way>/<t_id>', methods=['GET', 'POST'])
	@flask_app.route('/user/change_invoice_status/<type>/<way>/<t_id>', methods=['GET', 'POST'])
	def change_invoice_status(type,way,t_id):
		if request.method == 'GET' :
			get_db()
			db=Database(g._database)
			db.change_invoice_status(t_id,'#008000')
			return redirect('/'+type+'/'+way)
#---------------------------------------------------------------------
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
	@flask_app.route('/admin/restore_pass', methods=['GET', 'POST'])
	@flask_app.route('/admin/restore_pass/<email>', methods=['GET', 'POST'])
	def restore_pass(email=None):
		if request.method == 'GET' :
			if email != None:
				password=zlib.crc32(email.encode())
				ls=[]
				ls.append(password)
				return render_template('/admin/restore_pass.html', passw=ls)
			else:
				return render_template('/admin/restore_pass.html')
		if request.method == 'POST':
			password=zlib.crc32(request.form.get('email').encode())
			ls=[]
			ls.append(password)
			return render_template('/admin/restore_pass.html', passw=ls)
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
	@flask_app.route('/admin/admin_users', methods=['GET', 'POST'])
	def admin_admin_users():
		if request.method == 'GET' :
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])

			staff=db.get_all_users()
			staff_to_up=[]
			for item in staff:
				lst=[]
				lst.append(staff.index(item)+1)
				lst.append(' '.join(item[1:4]))
				lst.append(item[4])
				lst.append(item[5])
				lst.append(item[0])
				staff_to_up.append(lst)
			return render_template('admin/staff.html',
				role=role,
				name=name,
				urists=[1,2,3,4,5],
				data=staff_to_up
				)
	@flask_app.route('/admin/add_user', methods=['GET', 'POST'])
	def admin_add_user():
		if request.method == 'POST' :
			get_db()
			db=Database(g._database)
			pprint(request.form.to_dict(flat=False))
			email=request.form.get('email')
			name=request.form.get('name')
			surname=request.form.get('surname')
			lastname=request.form.get('lastname')
			Access_level =request.form.get('Access_level')

			password=str(zlib.crc32(request.form.get('email').encode()))
			def hash_password(password):
				salt = uuid.uuid4()
				return salt,hashlib.sha256(salt.hex.encode() + password.encode()).hexdigest() + ':' + salt.hex
			u_id,hash_p=hash_password(password)

			new_U=(str(u_id),Access_level,email,str(hash_p),name,surname,lastname)
			db.insert_User(new_U)
			return redirect('/admin/admin_users')

		elif request.method == 'GET' :
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			if user_info==False:
				role = 'None'
				name = 'None'
			else:
				role=user_info[0]
				name=' '.join(user_info[1:])
			return render_template('admin/add/add_staff.html',
				role=role,
				name=name
				)
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
	@flask_app.route('/admin/add_sud_delo', methods=['GET', 'POST'])
	def admin_add_sud_delo():
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
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Судебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Litigation=[]
				for margin in tables_sets(table_name='Litigation', mode='fields'):
					if margin == 't_id':
						list_to_Litigation.append(new_t_id)
					else:
						list_to_Litigation.append(adding_dict[margin][0])
				db.insert_tables('Litigation',tuple(list_to_Litigation))

				return redirect('/admin/sud_dela')
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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				print(ur_up)
				return render_template('admin/add/add_sud_delo.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/admin/sud_dela', methods=['GET', 'POST'])
	def admin_sud_dela():
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
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					item[9]='download_files/'+'/'.join(item[9].split('\\')[-3:])
					x_lst=[item[11].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[11]='\n'.join([' '.join(i) for i in x_lst])
				return render_template("admin/sud_dela.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("admin/sud_dela.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
	@flask_app.route('/admin/add_bank_dela', methods=['GET', 'POST'])
	def admin_add_bank_dela():
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
						return html_error_replacer(os.path.join('admin','add','add_bank_dela.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('admin','add','add_bankr_delo.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Банкротное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Bankruptcy=[]
				for margin in tables_sets(table_name='Bankruptcy', mode='fields'):
					if margin == 't_id':
						list_to_Bankruptcy.append(new_t_id)
					else:
						list_to_Bankruptcy.append(adding_dict[margin][0])
				db.insert_tables('Bankruptcy',tuple(list_to_Bankruptcy))

				return redirect('/admin/bank_dela')
			else:
				return html_error_replacer(os.path.join('admin','add','add_bankr_delo.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('admin/add/add_bankr_delo.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/admin/bank_dela', methods=['GET', 'POST'])
	def admin_bank_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table('Bankruptcy')
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[7]='download_files/'+'/'.join(item[7].split('\\')[-3:])
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					x_lst=[item[10].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[10]='\n'.join([' '.join(i) for i in x_lst])
				return render_template("admin/bankr_dela.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("admin/bankr_dela.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
	@flask_app.route('/admin/add_none_sud', methods=['GET', 'POST'])
	def admin_add_none_sud():
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
						return html_error_replacer(os.path.join('admin','add','add_nesud_delo.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('admin','add','add_nesud_delo.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Несудебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Non_judicial=[]
				for margin in tables_sets(table_name='Non_judicial', mode='fields'):
					if margin == 't_id':
						list_to_Non_judicial.append(new_t_id)
					else:
						list_to_Non_judicial.append(adding_dict[margin][0])
				db.insert_tables('Non_judicial',tuple(list_to_Non_judicial))

				return redirect('/admin/none_sud')
			else:
				return html_error_replacer(os.path.join('admin','add','add_nesud_delo.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('admin/add/add_nesud_delo.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/admin/none_sud', methods=['GET', 'POST'])
	def admin_none_sud():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table('Non_judicial')
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[7]='download_files/'+'/'.join(item[7].split('\\')[-3:])
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					x_lst=[item[10].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[10]='\n'.join([' '.join(i) for i in x_lst])
				return render_template("admin/nesud_dela.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("admin/nesud_dela.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
	@flask_app.route('/admin/add_dosud_ureg', methods=['GET', 'POST'])
	def admin_add_dosud_ureg():
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
						return html_error_replacer(os.path.join('admin','add','add_dosud_ureg.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('admin','add','add_dosud_ureg.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Несудебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Pre_trial_settlement=[]
				for margin in tables_sets(table_name='Pre_trial_settlement', mode='fields'):
					if margin == 't_id':
						list_to_Pre_trial_settlement.append(new_t_id)
					else:
						list_to_Pre_trial_settlement.append(adding_dict[margin][0])
				db.insert_tables('Pre_trial_settlement',tuple(list_to_Pre_trial_settlement))

				return redirect('/admin/dosud_ureg')
			else:
				return html_error_replacer(os.path.join('admin','add','add_dosud_ureg.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('admin/add/add_dosud_ureg.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/admin/dosud_ureg', methods=['GET', 'POST'])
	def admin_dosud_ureg():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table('Pre_trial_settlement')
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[7]='download_files/'+'/'.join(item[7].split('\\')[-3:])
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					x_lst=[item[10].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[10]='\n'.join([' '.join(i) for i in x_lst])
				return render_template("admin/dosud_ureg.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("admin/dosud_ureg.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_	
	@flask_app.route('/admin/add_isp_proiz', methods=['GET', 'POST'])
	def admin_add_isp_proiz():
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
						return html_error_replacer(os.path.join('admin','add','add_isp_proiz.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('admin','add','add_isp_proiz.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Несудебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Enforcement_proceedings=[]
				for margin in tables_sets(table_name='Enforcement_proceedings', mode='fields'):
					if margin == 't_id':
						list_to_Enforcement_proceedings.append(new_t_id)
					else:
						list_to_Enforcement_proceedings.append(adding_dict[margin][0])
				db.insert_tables('Enforcement_proceedings',tuple(list_to_Enforcement_proceedings))

				return redirect('/admin/isp_proiz')
			else:
				return html_error_replacer(os.path.join('admin','add','add_isp_proiz.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('admin/add/add_isp_proiz.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/admin/isp_proiz', methods=['GET', 'POST'])
	def admin_isp_proiz():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table('Enforcement_proceedings')
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[9]='download_files/'+'/'.join(item[9].split('\\')[-3:])
					item[10]='download_files/'+'/'.join(item[10].split('\\')[-3:])
					x_lst=[item[12].split(' ')[i:i+3] for i in range(0, len(item[12].split(' ')), 3)]
					item[12]='\n'.join([' '.join(i) for i in x_lst])
				return render_template("admin/isp_proiz.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("admin/isp_proiz.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_
#A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_A_	
	@flask_app.route('/admin/add_sud', methods=['GET', 'POST'])
	def admin_add_sudy():
		if request.method == 'POST':
			new_c_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			adding_dict=request.form.to_dict(flat=False)
			list_to_Courts=[]
			for margin in tables_sets(table_name='Sud', mode='fields'):
				if margin == 'c_id':
					list_to_Courts.append(new_c_id)
				elif margin == 'u_id':
					list_to_Courts.append(request.cookies.get('user_id'))
				else:
					list_to_Courts.append(adding_dict[margin][0])
			print(adding_dict)
			print(list_to_Courts)
			db.insert_tables('Sud',tuple(list_to_Courts))
			return redirect('/admin/sudy')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				clients=[cl[0] for cl in db.get_clients()]
				return render_template('admin/add/add_sud.html',
					clients=clients,
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/admin/sudy', methods=['GET', 'POST'])
	def admin_sudy():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_courts()
			for item in d_table:
				item.insert(0,d_table.index(item)+1)
				item.append(item.pop(1))
				item.pop(1)
			if d_table != False:
				return render_template("admin/sudy.html",
				data=d_table,
				role=role,
				name=name)
			else:
				return render_template("admin/sudy.html",
				data=[],
				role=role,
				name=name,
				delite_href='')
##############################################################################################
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
	@flask_app.route('/user/add_sud_delo', methods=['GET', 'POST'])
	def user_add_sud_delo():
		if request.method == 'POST':
			# image = request.files.get('file1')
			new_t_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			user=request.cookies.get('user_id')
			user_info=db.find_user_by_id(user)

			file_agree = request.files["Agreement"]
			file_invoice = request.files["Invoice"]
			if file_agree and file_invoice :					
				if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
					if new_t_id not in os.listdir(os.path.join(os.getcwd(),flask_app.config['UPLOAD_FOLDER'])):
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
					else:
						return html_error_replacer(os.path.join('user','add','add_sud_delo.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('user','add','add_sud_delo.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Судебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Project_Manager':
						list_to_Affairs.append(' '.join(user_info[1:]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Litigation=[]
				for margin in tables_sets(table_name='Litigation', mode='fields'):
					if margin == 't_id':
						list_to_Litigation.append(new_t_id)
					else:
						list_to_Litigation.append(adding_dict[margin][0])
				db.insert_tables('Litigation',tuple(list_to_Litigation))

				return redirect('/user/sud_dela')
			else:
				return html_error_replacer(os.path.join('user','add','add_sud_delo.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('user/add/add_sud_delo.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/user/sud_dela', methods=['GET', 'POST'])
	def user_sud_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table_u_id('Litigation',user)
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					item[9]='download_files/'+'/'.join(item[9].split('\\')[-3:])
					x_lst=[item[11].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[11]='\n'.join([' '.join(i) for i in x_lst])
					item.pop(4)
				return render_template("user/sud_dela.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("user/sud_dela.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
	@flask_app.route('/user/add_bank_dela', methods=['GET', 'POST'])
	def user_add_bank_dela():
		if request.method == 'POST':
			# image = request.files.get('file1')
			new_t_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			user=request.cookies.get('user_id')
			user_info=db.find_user_by_id(user)

			file_agree = request.files["Agreement"]
			file_invoice = request.files["Invoice"]
			if file_agree and file_invoice :					
				if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
					if new_t_id not in os.listdir(os.path.join(os.getcwd(),flask_app.config['UPLOAD_FOLDER'])):
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
					else:
						return html_error_replacer(os.path.join('user','add','add_bank_dela.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('user','add','add_bankr_delo.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Банкротное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Project_Manager':
						list_to_Affairs.append(' '.join(user_info[1:]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Bankruptcy=[]
				for margin in tables_sets(table_name='Bankruptcy', mode='fields'):
					if margin == 't_id':
						list_to_Bankruptcy.append(new_t_id)
					else:
						list_to_Bankruptcy.append(adding_dict[margin][0])
				db.insert_tables('Bankruptcy',tuple(list_to_Bankruptcy))

				return redirect('/bank_dela')
			else:
				return html_error_replacer(os.path.join('user','add','add_bankr_delo.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('user/add/add_bankr_delo.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/user/bank_dela', methods=['GET', 'POST'])
	def user_bank_dela():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table_u_id('Bankruptcy',user)
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[7]='download_files/'+'/'.join(item[7].split('\\')[-3:])
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					x_lst=[item[10].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[10]='\n'.join([' '.join(i) for i in x_lst])
					item.pop(4)
				return render_template("user/bankr_dela.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("user/bankr_dela.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
	@flask_app.route('/user/add_none_sud', methods=['GET', 'POST'])
	def user_add_none_sud():
		if request.method == 'POST':
			# image = request.files.get('file1')
			new_t_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			user=request.cookies.get('user_id')
			user_info=db.find_user_by_id(user)

			file_agree = request.files["Agreement"]
			file_invoice = request.files["Invoice"]
			if file_agree and file_invoice :					
				if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
					if new_t_id not in os.listdir(os.path.join(os.getcwd(),flask_app.config['UPLOAD_FOLDER'])):
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
					else:
						return html_error_replacer(os.path.join('user','add','add_nesud_delo.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('user','add','add_nesud_delo.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Несудебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Project_Manager':
						list_to_Affairs.append(' '.join(user_info[1:]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Non_judicial=[]
				for margin in tables_sets(table_name='Non_judicial', mode='fields'):
					if margin == 't_id':
						list_to_Non_judicial.append(new_t_id)
					else:
						list_to_Non_judicial.append(adding_dict[margin][0])
				db.insert_tables('Non_judicial',tuple(list_to_Non_judicial))

				return redirect('/none_sud')
			else:
				return html_error_replacer(os.path.join('user','add','add_nesud_delo.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('user/add/add_nesud_delo.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/user/none_sud', methods=['GET', 'POST'])
	def user_none_sud():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table_u_id('Non_judicial',user)
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[7]='download_files/'+'/'.join(item[7].split('\\')[-3:])
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					x_lst=[item[10].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[10]='\n'.join([' '.join(i) for i in x_lst])
					item.pop(4)
				return render_template("user/nesud_dela.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("user/nesud_dela.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
	@flask_app.route('/user/add_dosud_ureg', methods=['GET', 'POST'])
	def user_add_dosud_ureg():
		if request.method == 'POST':
			# image = request.files.get('file1')
			new_t_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			user=request.cookies.get('user_id')
			user_info=db.find_user_by_id(user)

			file_agree = request.files["Agreement"]
			file_invoice = request.files["Invoice"]
			if file_agree and file_invoice :					
				if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
					if new_t_id not in os.listdir(os.path.join(os.getcwd(),flask_app.config['UPLOAD_FOLDER'])):
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
					else:
						return html_error_replacer(os.path.join('user','add','add_dosud_ureg.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('user','add','add_dosud_ureg.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Несудебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Project_Manager':
						list_to_Affairs.append(' '.join(user_info[1:]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Pre_trial_settlement=[]
				for margin in tables_sets(table_name='Pre_trial_settlement', mode='fields'):
					if margin == 't_id':
						list_to_Pre_trial_settlement.append(new_t_id)
					else:
						list_to_Pre_trial_settlement.append(adding_dict[margin][0])
				db.insert_tables('Pre_trial_settlement',tuple(list_to_Pre_trial_settlement))

				return redirect('/dosud_ureg')
			else:
				return html_error_replacer(os.path.join('user','add','add_dosud_ureg.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('user/add/add_dosud_ureg.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/user/dosud_ureg', methods=['GET', 'POST'])
	def user_dosud_ureg():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_join_table_u_id('Pre_trial_settlement',user)
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[7]='download_files/'+'/'.join(item[7].split('\\')[-3:])
					item[8]='download_files/'+'/'.join(item[8].split('\\')[-3:])
					x_lst=[item[10].split(' ')[i:i+3] for i in range(0, len(item[11].split(' ')), 3)]
					item[10]='\n'.join([' '.join(i) for i in x_lst])
					item.pop(4)
				return render_template("user/dosud_ureg.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("user/dosud_ureg.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_	
	@flask_app.route('/user/add_isp_proiz', methods=['GET', 'POST'])
	def user_add_isp_proiz():
		if request.method == 'POST':
			# image = request.files.get('file1')
			new_t_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			user=request.cookies.get('user_id')
			user_info=db.find_user_by_id(user)

			file_agree = request.files["Agreement"]
			file_invoice = request.files["Invoice"]
			if file_agree and file_invoice :					
				if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
					if new_t_id not in os.listdir(os.path.join(os.getcwd(),flask_app.config['UPLOAD_FOLDER'])):
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
						os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
					else:
						return html_error_replacer(os.path.join('user','add','add_isp_proiz.html'),'Такие файлы уже существуют')
					file_agree_filename = secure_filename(file_agree.filename)
					file_invoice_filename = secure_filename(file_invoice.filename)
					file_agree.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					file_invoice.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
				else: 
					return html_error_replacer(os.path.join('user','add','add_isp_proiz.html'),'Ошибка файлов, попробуйте ещё раз')

				adding_dict=request.form.to_dict(flat=False)
				list_to_Affairs=[]
				for margin in tables_sets(table_name='Affairs', mode='fields'):
					if margin == 't_id':
						list_to_Affairs.append(new_t_id)
					elif margin == 'u_id':
						list_to_Affairs.append(request.cookies.get('user_id'))
					elif margin == 'Type':
						list_to_Affairs.append('Несудебное дело')
					elif margin == 'Agreement':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
					elif margin == 'Invoice':
						list_to_Affairs.append(os.path.join(flask_app.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
					elif margin == 'Practice':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Lawyers':
						list_to_Affairs.append(json.dumps(adding_dict[margin]))
					elif margin == 'Project_Manager':
						list_to_Affairs.append(' '.join(user_info[1:]))
					else:
						list_to_Affairs.append(adding_dict[margin][0])
				db.insert_tables('Affairs',tuple(list_to_Affairs))

				list_to_Enforcement_proceedings=[]
				for margin in tables_sets(table_name='Enforcement_proceedings', mode='fields'):
					if margin == 't_id':
						list_to_Enforcement_proceedings.append(new_t_id)
					else:
						list_to_Enforcement_proceedings.append(adding_dict[margin][0])
				db.insert_tables('Enforcement_proceedings',tuple(list_to_Enforcement_proceedings))

				return redirect('/isp_proiz')
			else:
				return html_error_replacer(os.path.join('user','add','add_isp_proiz.html'),'Не загружены файлы')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				return render_template('user/add/add_isp_proiz.html',
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/user/isp_proiz', methods=['GET', 'POST'])
	def user_isp_proiz():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]

			name=' '.join(user_info[1:])
			d_table = db.get_join_table_u_id('Enforcement_proceedings',user)
			if d_table != False:
				colors=[]
				delite_hrs=[]
				for i in d_table:
					colors.append(i.pop(-1))
				for item in d_table:
					item.append(item.pop(1))
					item[2]=' ;\n'.join(json.loads(item[2]))+' .'
					item[4]=' ;\n'.join(json.loads(item[4]))+' .'
					item[9]='download_files/'+'/'.join(item[9].split('\\')[-3:])
					item[10]='download_files/'+'/'.join(item[10].split('\\')[-3:])
					x_lst=[item[12].split(' ')[i:i+3] for i in range(0, len(item[12].split(' ')), 3)]
					item[12]='\n'.join([' '.join(i) for i in x_lst])
					item.pop(4)
				return render_template("user/isp_proiz.html",
				data=d_table,
				role=role,
				name=name,
				colors=colors)
			else:
				return render_template("user/isp_proiz.html",
				data=[],
				role=role,
				name=name,
				colors=[],
				delite_href='')
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_
#U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_U_	
	@flask_app.route('/user/add_sud', methods=['GET', 'POST'])
	def user_add_sudy():
		if request.method == 'POST':
			new_c_id=str(uuid.uuid4())
			get_db()
			db=Database(g._database)
			user=request.cookies.get('user_id')
			user_info=db.find_user_by_id(user)

			adding_dict=request.form.to_dict(flat=False)
			list_to_Courts=[]
			for margin in tables_sets(table_name='Sud', mode='fields'):
				if margin == 'c_id':
					list_to_Courts.append(new_c_id)
				elif margin == 'u_id':
					list_to_Courts.append(request.cookies.get('user_id'))
				else:
					list_to_Courts.append(adding_dict[margin][0])
			db.insert_tables('Sud',tuple(list_to_Courts))
			return redirect('/user/sudy')

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
				urists=db.get_urists()
				ur_up=[' '.join(i) for i in urists]
				clients=[cl[0] for cl in db.get_clients()]
				return render_template('user/add/add_sud.html',
					clients=clients,
					role=role,
					name=name,
					urists=ur_up)
	@flask_app.route('/user/sudy', methods=['GET', 'POST'])
	def user_sudy():
		if request.cookies.get('user_id') == None:
			return redirect('/login')
		else:
			user=request.cookies.get('user_id')
			get_db()
			db=Database(g._database)
			user_info=db.find_user_by_id(user)
			role=user_info[0]
			name=' '.join(user_info[1:])
			d_table = db.get_courts_u_id(user)
			for item in d_table:
				item.insert(0,d_table.index(item)+1)
				item.append(item.pop(1))
				item.pop(1)
			if d_table != False:
				return render_template("user/sudy.html",
				data=d_table,
				role=role,
				name=name)
			else:
				return render_template("user/sudy.html",
				data=[],
				role=role,
				name=name,
				delite_href='')
#L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_
#L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_
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
					if db.find_user(email)[0][1]=='Суперпользователь':
						way='/admin/sud_dela'
					elif db.find_user(email)[0][1]=='Пользователь':
						way='/user/sud_dela'
					elif db.find_user(email)[0][1]=='Секретарь':
						way='/secretary'	
					else: way='/login'
					response = make_response(redirect(way))
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
#L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_
#_______________________________________________________________________________________________
#_______________________________________________________________________________________________
	@flask_app.errorhandler(401)
	def page_not_found(e):
	    return Response('<p>Login failed</p>')
	@flask_app.errorhandler(404)
	def not_found(e):
	    return Response('<p>file not found</p>')
#_______________________________________________________________________________________________
#_______________________________________________________________________________________________
if __name__ == '__main__':
    flask_app.run()

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

application = Flask(__name__)
application.secret_key = os.urandom(24)
application.config['UPLOAD_FOLDER']=os.path.join(os.getcwd(),'U_files')
ALLOWED_EXTENSIONS = {'pdf','jpg','jpeg'}
DATAFILE=os.path.join(os.getcwd(),'db','data_file.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
         db = g._database = sqlite3.connect(DATAFILE)       
    return db

def html_error_replacer(file_name,error):
        user=request.cookies.get('user_id')
        get_db()
        db=Database(g._database)
        user_info=db.find_user_by_id(user)
        role=user_info[0]
        name=' '.join(user_info[1:])
        urists=db.get_urists()
        ur_up=[' '.join(i) for i in urists]

        soup = BeautifulSoup(render_template(file_name.replace('\\','/')
            ,role=role,
            name=name,
            urists=ur_up)
        , "lxml")
        err_tag = soup.find(id='error')
        err_tag.string = error
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

def settings_by_template(template_name,field):
    data=[
        {
        'template_name': 'sud_dela',
        'data_set':
            {
            'table_name':'Litigation',
            'start_from':8,
            'delo_count':4,
            'Type': 'Судебное дело'
            }
        },
        {
        'template_name': 'bankr_dela',
        'data_set':
            {
            'table_name':'Bankruptcy',
            'start_from':7,
            'delo_count':3,
            'Type': 'Банкротное дело'
            }
        },
        {
        'template_name': 'nesud_dela',
        'data_set':
            {
            'table_name':'Non_judicial',
            'start_from':7,
            'delo_count':3,
            'Type': 'Несудебное дело'
            }
        },
        {
        'template_name': 'dosud_ureg',
        'data_set':
            {
            'table_name':'Pre_trial_settlement',
            'start_from':7,
            'delo_count':3,
            'Type': 'Досудебное урегулирование'
            }
        },
        {
        'template_name': 'isp_proiz',
        'data_set':
            {
            'table_name':'Enforcement_proceedings',
            'start_from':9,
            'delo_count':5,
            'Type': 'Исполнительное производство'
            }
        },

    ]
    for d in data:
        if d['template_name']==template_name:
            return d['data_set'][field]
        else: continue
def acssec_translate(acsess):
    d_trans={
    'Руководитель':'admin',
    'Пользователь':'user',
    'Секретарь':'secretary'
    }
    return d_trans[acsess]
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
@application.route('/download_files/<t_id>/<type_f>/<filename>', methods=['GET', 'POST'])
def download_files(t_id,type_f,filename):
    if request.method == 'GET':
        try:
            directory=os.path.join(application.config['UPLOAD_FOLDER'],t_id,type_f)
            return send_from_directory(directory, filename=filename, as_attachment=True)
        except FileNotFoundError:
            abort(404)
#------------------------------------------------------------------
@application.route('/delite_element/<type>/<way>/<t_id>', methods=['GET', 'POST'])
def delite_element(type,way,t_id):
    if request.method == 'GET' :
        get_db()
        db=Database(g._database)
        for i in tables_sets(mode='keys'):
            db.delite_data(i,t_id)
        path=os.path.join(application.config['UPLOAD_FOLDER'],t_id)
        shutil.rmtree(path)
        return redirect('/'+type+'/'+'render'+'/'+way)
#---------------------------------------------------------------------
@application.route('/change_invoice_status/<type>/<way>/<t_id>', methods=['GET', 'POST'])
def change_invoice_status(type,way,t_id):
    if request.method == 'GET' :
        get_db()
        db=Database(g._database)
        db.change_invoice_status(t_id,'#008000')
        return redirect('/'+type+'/'+'render'+'/'+way)
#---------------------------------------------------------------------
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
#settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_settings_
@application.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@application.route('/',methods=['GET'])
def base():
    user=request.cookies.get('user_id')
    if user:
        get_db()
        db=Database(g._database)
        f_u=db.find_user_by_id(user)
        if f_u[0] == 'Руководитель':
            return redirect('/admin/render/sud_dela')
        elif f_u[0]== 'Пользователь':
            return redirect('/user/render/sud_dela')
        elif f_u[0]=='Секретарь':
            return redirect('/secretary')
    else:
        return redirect('/login')
#secretary______________________________________________
@application.route('/secretary', methods=['GET', 'POST'])
def secretary_sudy():
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
        if d_table != []:
            return render_template("secretary/sudy.html",
            data=d_table,
            role=role,
            name=name)
        else:
            return render_template("secretary/sudy.html",
            data=[],
            role=role,
            name=name,
            delite_href='')

#dela_pocess___________________________________________________
def file_saving(new_t_id,file_agree=None,file_invoice=None):
    if file_agree and file_invoice:
        if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id))
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
            file_agree_filename = secure_filename(file_agree.filename)
            file_invoice_filename = secure_filename(file_invoice.filename)
            file_agree.save(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
            file_invoice.save(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
            return True
        else:
            return False
    elif file_agree and not file_invoice:
        if  allowed_file(file_agree.filename):
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id))
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Agreement'))
            file_agree_filename = secure_filename(file_agree.filename)
            file_agree.save(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Agreement',file_agree_filename))
            return True
        else:
            return False
    elif file_invoice and not file_agree:
        if allowed_file(file_invoice.filename):
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id))
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Invoice'))
            file_invoice_filename = secure_filename(file_invoice.filename)
            file_invoice.save(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Invoice',file_invoice_filename))
            return True
        else:
            return False
    else: return False

@application.route('/admin/add/<template_name>', methods=['GET', 'POST'])
@application.route('/user/add/<template_name>', methods=['GET', 'POST'])
def add(template_name):
    print(template_name)
    if request.cookies.get('user_id') == None:
        return redirect('/login')
    if request.method == 'POST':
        new_t_id=str(uuid.uuid4())
        get_db()
        db=Database(g._database)
        file_agree = request.files["Agreement"]
        file_invoice = request.files["Invoice"]
        if file_agree or file_invoice  or (file_agree and file_invoice) :
            saving_status=file_saving(new_t_id,file_agree,file_invoice)
            if saving_status == False:
                return html_error_replacer(os.path.join('admin','add',f'{template_name}.html'),'Ошибка файлов, попробуйте ещё раз')
        else:
            file_saving(new_t_id,file_agree=None,file_invoice=None)

        adding_dict=request.form.to_dict(flat=False)
        list_to_Affairs=[]
        for margin in tables_sets(table_name='Affairs', mode='fields'):
            if margin == 't_id':
                list_to_Affairs.append(new_t_id)
            elif margin == 'u_id':
                list_to_Affairs.append(request.cookies.get('user_id'))
            elif margin == 'Agreement':
                if file_agree:
                    list_to_Affairs.append(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Agreement',secure_filename(file_agree.filename)))
                else:
                    list_to_Affairs.append('Нет файла')
            elif margin == 'Invoice':
                if file_invoice:
                    list_to_Affairs.append(os.path.join(application.config['UPLOAD_FOLDER'],new_t_id,'Invoice',secure_filename(file_invoice.filename)))
                else:
                    list_to_Affairs.append('Нет файла')
            elif margin == 'Type':
                list_to_Affairs.append('None')
            elif margin == 'Practice':
                list_to_Affairs.append(json.dumps(adding_dict[margin]))
            elif margin == 'Lawyers':
                list_to_Affairs.append(json.dumps(adding_dict[margin]))
            else:
                list_to_Affairs.append(adding_dict[margin][0])

        db.insert_tables('Affairs',tuple(list_to_Affairs))

        table_name=settings_by_template(template_name.lstrip('add_'),'table_name')
        list_to_table=[]
        for margin in tables_sets(table_name=table_name, mode='fields'):
            if margin == 't_id':
                list_to_table.append(new_t_id)
            else:
                list_to_table.append(adding_dict[margin][0])
        db.insert_tables(table_name,tuple(list_to_table))

        user=request.cookies.get('user_id')
        user_info=db.find_user_by_id(user)
        role=user_info[0]
        href_acsess=request.url.split('/')[3]
        if acssec_translate(role) == href_acsess:
            real_acsess=href_acsess
        else:   
            real_acsess=acssec_translate(role)
            return redirect(f'/{real_acsess}/add/{template_name}')
        t_name=template_name.lstrip('add_')
        return redirect(f'/{real_acsess}/render/{t_name}')

    if request.method == 'GET':
        user=request.cookies.get('user_id')
        get_db()
        db=Database(g._database)
        user_info=db.find_user_by_id(user)
        role=user_info[0]
        name=' '.join(user_info[1:])
        urists=db.get_urists()
        href_acsess=request.url.split('/')[3]
        if acssec_translate(role) == href_acsess:
            real_acsess=href_acsess
        else:   
            real_acsess=acssec_translate(role)
            return redirect(f'/{real_acsess}/add/{template_name}')

        ur_up=[' '.join(i) for i in urists]
        return render_template(f'{real_acsess}/add/{template_name}.html',
            role=role,
            name=name,
            urists=ur_up)

@application.route('/admin/render/<template_name>', methods=['GET', 'POST'])
@application.route('/user/render/<template_name>', methods=['GET', 'POST'])
def render(template_name):
    if request.cookies.get('user_id') == None:
        return redirect('/login')
    else:
        user=request.cookies.get('user_id')
        get_db()
        db=Database(g._database)
        user_info=db.find_user_by_id(user)
        role=user_info[0]
        name=' '.join(user_info[1:])

        href_acsess=request.url.split('/')[3]
        if acssec_translate(role) == href_acsess:
            real_acsess=href_acsess
        else:   
            real_acsess=acssec_translate(role)
            return redirect(f'/{real_acsess}/render/{template_name}')

        table_name=settings_by_template(template_name,'table_name')
        if request.method == 'GET':
            if real_acsess=='admin':
                d_table = db.get_join_table(table_name)
            else:
                d_table = db.get_join_table_u_id(table_name,user)
        else:
            dict_=request.form.to_dict(flat=False)
            practice=dict_['practice']
            lawyers=dict_['lawyers']
            client=request.form.get('client')
            if practice == [''] and client == '' and lawyers == ['']:
                if real_acsess=='admin':
                    d_table=db.get_join_table(table_name)
                else:
                    d_table=db.get_join_table_u_id(table_name,user)
            elif practice != [''] or client != '' or lawyers !=[''] :
                if real_acsess=='admin':
                    d_table = db.get_join_table_search(table_name,user,practice=practice,client=client,lawyers=lawyers)
                else:
                    d_table=db.get_join_table_search_u_id(table_name,user,practice=practice,client=client,lawyers=lawyers)
            else:
                return redirect(f'/{real_acsess}/render/{template_name}')

        if d_table != []:
            start_from=settings_by_template(template_name,'start_from')
            colors=[]
            delite_hrs=[]
            for i in d_table:
                colors.append(i.pop(-1))
            for item in d_table:
                item.append(item.pop(1))
                item[2]=' ;\n'.join(json.loads(item[2]))+' .'
                item[4]=' ;\n'.join(json.loads(item[4]))+' .'
                if item[start_from]=='Нет файла':
                    item[start_from]=='Нет файла'
                else:
                    item[start_from]='/download_files/'+'/'.join(item[start_from].split('\\')[-3:])
                if item[start_from+1]=='Нет файла':
                    item[start_from]=='Нет файла'
                else:
                    item[start_from+1]='/download_files/'+'/'.join(item[start_from+1].split('\\')[-3:])
                x_lst=[item[start_from+3].split(' ')[i:i+3] for i in range(0, len(item[start_from+3].split(' ')), 3)]
                item[start_from+3]='\n'.join([' '.join(i) for i in x_lst])
            serch_clients=db.get_clients()
            lawyers=[' '.join(i) for i in db.get_urists()]
            return render_template(f'/{real_acsess}/{template_name}'+'.html',
            data=d_table,
            role=role,
            name=name,
            colors=colors,
            serch_clients=serch_clients,
            lawyers=lawyers)
        else:
            return render_template(f'/{real_acsess}/{template_name}'+'.html',
            data=[],
            role=role,
            name=name,
            colors=[],
            delite_href='')

#one_delo________________________________________________________________
def file_updater(t_id,file_agree=None,file_invoice=None):
    if t_id not in os.listdir(application.config['UPLOAD_FOLDER']):
        os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],t_id))
    if file_agree and file_invoice:
        if  allowed_file(file_agree.filename) and allowed_file(file_invoice.filename):
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Agreement'))
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Invoice'))
            file_agree_filename = secure_filename(file_agree.filename)
            file_invoice_filename = secure_filename(file_invoice.filename)
            file_agree.save(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Agreement',file_agree_filename))
            file_invoice.save(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Invoice',file_invoice_filename))
            return True
        else:
            return False
    elif file_agree and not file_invoice:
        if  allowed_file(file_agree.filename):
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Agreement'))
            file_agree_filename = secure_filename(file_agree.filename)
            file_agree.save(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Agreement',file_agree_filename))
            return True
        else:
            return False
    elif file_invoice and not file_agree:
        if allowed_file(file_invoice.filename):
            os.mkdir(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Invoice'))
            file_invoice_filename = secure_filename(file_invoice.filename)
            file_invoice.save(os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Invoice',file_invoice_filename))
            return True
        else:
            return False
    else: return False

@application.route('/delo/<template_name>/<t_id>', methods=['GET', 'POST'])
def delo(template_name,t_id):
    get_db()
    db=Database(g._database)
    table_name=settings_by_template(template_name,'table_name')
    delo_data = db.get_delo(table_name,t_id)
    rez_table=[]

    af_table=delo_data[0][2:7]
    af_table.pop(1)
    af_table[1]=' ,'.join(json.loads(af_table[1]))
    af_table[3]=' ,'.join(json.loads(af_table[3]))

    t_count=settings_by_template(template_name,'delo_count')
    j_table=delo_data[0][-t_count+1:]

    files_t=delo_data[0][7:9]
    for f in files_t:
        if f!='Нет файла':
            files_t[files_t.index(f)]='/download_files/'+'/'.join(f.split('\\')[-3:])
        else:
            continue
    in_table=delo_data[0][9:11]

    rez_table=af_table+j_table+files_t+in_table
    Type=settings_by_template(template_name,'Type')
    return render_template('delo.html',
        type=Type,
        delo=[rez_table],
        t_id=t_id,
        template_name=template_name
        )
@application.route('/update_dello/<template_name>/<t_id>', methods=['GET', 'POST'])
def update_dello(template_name,t_id):
    if request.method=='POST':
        get_db()
        db=Database(g._database)
        Comment=request.form.get('Comment')
        print(Comment)
        if Comment!= None:
            db.update_dello(t_id,comment=Comment)
        if request.files!='':
            file_agree = request.files["Agreement"]
            file_invoice = request.files["Invoice"]
            if file_agree or file_invoice  or (file_agree and file_invoice) :
                saving_status=file_updater(t_id,file_agree,file_invoice)
                if file_agree and not file_invoice :
                    agree_file_way=os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Agreement',secure_filename(file_agree.filename))
                    db.update_dello(t_id,file_agree=agree_file_way)
                elif file_invoice and not file_agree:
                    invoice_file=agree_file_way=os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Invoice',secure_filename(file_invoice.filename))
                    db.update_dello(t_id,file_invoice=invoice_file)
                elif file_agree and file_invoice :
                    agree_file_way=os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Agreement',secure_filename(file_agree.filename))
                    invoice_file=agree_file_way=os.path.join(application.config['UPLOAD_FOLDER'],t_id,'Invoice',secure_filename(file_invoice.filename))
                    db.update_dello(t_id,file_agree=agree_file_way,file_invoice=invoice_file)
                if saving_status == False:
                    return redirect(f'/delo/{template_name}/{t_id}')
            else:
                return redirect(f'/delo/{template_name}/{t_id}')

        return redirect(f'/delo/{template_name}/{t_id}')


#sudy_____________________________________________________________________
@application.route('/admin/add_sudy', methods=['GET', 'POST'])
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
        db.insert_tables('Sud',tuple(list_to_Courts))
        return redirect('/admin/render/sudy')

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
            clients=db.get_clients()
            return render_template('admin/add/add_sudy.html',
                clients=clients,
                role=role,
                name=name,
                urists=ur_up)
@application.route('/admin/render/sudy', methods=['GET', 'POST'])
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
        if request.method == 'GET':
            d_table = db.get_courts()
        else:
            client=request.form.get('client')
            date=request.form.get('date')
            if client == '' and date == '':
                d_table = db.get_courts()
            elif client == '' and date != '':
                d_table=db.get_courts_search(date=date)
            elif client != '' and date == '':
                d_table=db.get_courts_search(client=client)
            elif client != '' and date != '':
                d_table=db.get_courts_search(client=client,date=date)
            else:
                redirect('/admin/render/sudy')
        if d_table == []:
            return render_template("/admin/sudy.html",
            data=[],
            role=role,
            name=name,
            delite_href='')
        else:
            for item in d_table:
                item.insert(0,d_table.index(item)+1)
                item.append(item.pop(1))
                item.pop(1)
            serch_clients=[]
            if db.get_courts_clients() ==[]:
                serch_clients=[]
            else:
                for cl in db.get_courts_clients():
                    serch_clients.append(cl[0])       
            return render_template("/admin/sudy.html",
                data=d_table, 
                role=role,
                serch_clients=serch_clients,
                name=name)
@application.route('/delite_sud/<type>/<way>/<c_id>', methods=['GET', 'POST'])
@application.route('/delite_sud/<type>/<way>/<c_id>', methods=['GET', 'POST'])
def delite_sud(type,way,c_id):
    if request.method == 'GET' :
        get_db()
        db=Database(g._database)
        db.delite_sud(c_id)
        return redirect('/'+type+'/'+way)
@application.route('/user/add_sudy', methods=['GET', 'POST'])
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
            elif margin == 'lawyer':
                list_to_Courts.append(' '.join(user_info[1:]))
            elif margin == 'u_id':
                list_to_Courts.append(request.cookies.get('user_id'))
            else:
                list_to_Courts.append(adding_dict[margin][0])
        db.insert_tables('Sud',tuple(list_to_Courts))
        return redirect('/user/render/sudy')
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
            clients=db.get_clients_u_id(user)
            return render_template('user/add/add_sudy.html',
                clients=clients,
                role=role,
                name=name,
                urists=ur_up)
@application.route('/user/render/sudy', methods=['GET', 'POST'])
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
        if request.method == 'GET':
            d_table = db.get_courts_u_id(u_id=user)
        else:
            client=request.form.get('client')
            date=request.form.get('date')
            if client == '' and date == '':
                d_table = db.get_courts_u_id(u_id=user)
            elif client == '' and date != '':
                d_table=db.get_courts_search_u_id(date=date,u_id=user)
            elif client != '' and date == '':
                d_table=db.get_courts_search_u_id(client=client,u_id=user)
            elif client != '' and date != '':
                d_table=db.get_courts_search_u_id(client=client,date=date,u_id=user)
            else:
                redirect('/user/render/sudy')
        if d_table == []:
            return render_template("/user/sudy.html",
            data=[],
            role=role,
            name=name,
            delite_href='')
        else:
            for item in d_table:
                item.insert(0,d_table.index(item)+1)
                item.append(item.pop(1))
                item.pop(1)
            serch_clients=[]
            for cl in db.get_courts_clients_u_id(u_id=user):
                serch_clients.append(cl[0])
            return render_template("/user/sudy.html",
                data=d_table,
                role=role,
                serch_clients=serch_clients,
                name=name)
#user_______________________________________________________________________
@application.route('/admin/render/staff', methods=['GET', 'POST'])
def admin_users():
    user=request.cookies.get('user_id')
    get_db()
    db=Database(g._database)
    user_info=db.find_user_by_id(user)
    role=user_info[0]
    name=' '.join(user_info[1:])
    if request.method == 'GET':
        staff=db.get_all_users()
    else:
        param=request.form.get('search_user')
        if param == '':
            staff=db.get_all_users()
        else:
            staff=db.get_users_search(param.split(' '))
    staff_to_up=[]
    for item in staff:
        lst=[]
        lst.append(staff.index(item)+1)
        lst.append(' '.join(item[1:4]))
        lst.append(item[4])
        lst.append(item[5])
        lst.append(item[0])
        staff_to_up.append(lst)
    search_urists=[]
    for u in db.get_all_users():
        search_urists.append(' '.join(u[1:4]))
    return render_template('/admin/staff.html',
        role=role,
        name=name,
        search_urists=search_urists,
        data=staff_to_up
        )
@application.route('/admin/add/add_staff', methods=['GET', 'POST'])
def admin_add_user():
    if request.method == 'POST' :
        get_db()
        db=Database(g._database)
        email=request.form.get('email')
        password=request.form.get('password')
        name=request.form.get('name')
        surname=request.form.get('surname')
        lastname=request.form.get('lastname')
        Access_level =request.form.get('Access_level')
        def hash_password(password):
            salt = uuid.uuid4()
            return salt,hashlib.sha256(salt.hex.encode() + password.encode()).hexdigest() + ':' + salt.hex
        u_id,hash_p=hash_password(password)
        new_U=(str(u_id),Access_level,email,str(hash_p),name,surname,lastname)
        db.insert_User(new_U)
        return redirect('/admin/render/staff')
    elif request.method == 'GET' :
        user=request.cookies.get('user_id')
        get_db()
        db=Database(g._database)
        user_info=db.find_user_by_id(user)
        if user_info==[]:
            role = 'None'
            name = 'None'
        else:
            role=user_info[0]
            name=' '.join(user_info[1:])
        return render_template('/admin/add/add_staff.html',
            role=role,
            name=name
            )
@application.route('/delite_user/<type_>/<way>/<_id>', methods=['GET', 'POST'])
def delite_user(type_,way,_id):
    get_db()
    db=Database(g._database)
    db.delite_user(_id)
    return redirect('/'+type_+'/'+'render'+'/'+way)

#login________________________________________________________________
@application.route('/login' , methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':     
        email=request.form.get('email').rstrip()
        password=request.form.get('password')
        get_db()
        db=Database(g._database)
        if db.find_user(email)!=[]:
            if db.find_user(email)[0][3]!=[]:
                hash_pass=db.find_user(email)[0][3]
                def check_password(hashed_password, user_password):
                    password, salt = hashed_password.split(':')
                    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
                if check_password(hash_pass,password):
                    if db.find_user(email)[0][1]=='Руководитель':
                        way='/admin/render/sud_dela'
                    elif db.find_user(email)[0][1]=='Пользователь':
                        way='/user/render/sud_dela'
                    elif db.find_user(email)[0][1]=='Секретарь':
                        way='/secretary'    
                    else: way='/login'
                    response = make_response(redirect(way))
                    response.set_cookie('user_id',db.find_user(email)[0][0])
                    return response
                else:
                    return html_error_replacer('auth.html','Password []')
            else:
                return html_error_replacer('auth.html','User not found or name invalid')   
        else:
            return html_error_replacer('auth.html','User not found or name invalid')
    else:
        return render_template('auth.html')
@application.route('/register' , methods = ['GET' , 'POST'])
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
@application.route('/logout' , methods = ['GET' , 'POST'])
def logout():
    user=request.cookies.get('user_id')
    response = make_response(redirect('/login'))
    response.set_cookie('user_id','logout',max_age=0)
    return response
if __name__ == '__main__':
    application.run(debug=True)
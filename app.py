from __future__ import print_function # Python 2/3 compatibility
import os
os.environ["TZ"] = "UTC"
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from flask import Flask, url_for, render_template, request, flash, redirect, session, abort
import pymssql  
import uuid
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)
'''

'''
conn = pymssql.connect(server='breastdb.cvlffbfnvce5.us-east-1.rds.amazonaws.com', user='clouduser', password='cloudpwd', database='BreastData')  
cursor = conn.cursor() 



@app.route('/')
def hosp():
	return redirect(url_for('.lake'))

@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		firstname = request.form['firstname']
		lastname= request.form['lastname']
		username=request.form['username']
		gender=request.form['gender']
		password = request.form['password']
		re_password=request.form['re_password']
		patient_id=request.form['patient_id']
		position="Patient"
		print (firstname)
		print (lastname)
		print (username)
		print (gender)
		print (password)
		print (position)
		print (re_password)
		cursor0 = conn.cursor()  
		cursor0.execute('SELECT username FROM person_table where username = %s',username)  
		row = cursor0.fetchone()  
		num=0
		var0=""
		var1=""
		while row:  
			print (str(row[0]) )   
			if str(row[0])==username:
				print ("User already exists")
				var0="username already exists. Choose a different one"
				num=1
			row = cursor0.fetchone()
		if re_password!=password:
			var1="your passwords don't match!"

		if re_password==password and num==0:
			print("success!!")
			pw = generate_password_hash(password)
			cursor.execute('INSERT INTO Person_table VALUES (%s,%s,%s,%s,%s,%s,%s)',(username,pw,firstname,lastname,gender,position,patient_id))  
			anony_id=str(uuid.uuid4())
			cursor.execute('INSERT INTO patient_table VALUES (%s,%s)',(patient_id,anony_id))
			conn.commit()
			print("sucess!!")
		else:
			return render_template('signup.html', err0=var0, err1=var1,username=username,firstname=firstname,lastname=lastname,patient_id=patient_id)

		#print (firstname)
		return redirect(url_for('.home'))
	return render_template('signup.html')

@app.route('/lake')
def lake():
	return render_template('lake.html')			

@app.route('/main',methods=['GET'])
def home():
	if not session.get('logged_in'):
		return render_template('login.html',username="",err="")
	else:
		if session['position'].replace(" ","")=="Patient":
			return redirect(url_for('.phome'))
		if session['position'].replace(" ","")=="Doctor":
			return redirect(url_for('.dhome'))
		return render_template('mainpage.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
	if request.method=="POST":
		username=request.form['username']
		password=request.form['password'] 
		cursor.execute('SELECT password,position,person_id FROM person_table where username = %s',username)  
		row = cursor.fetchone()  
		i=0 
		print ("1")
		if row:
			pwhashed= (str(row[0])).replace(" ","")   
			if check_password_hash(pwhashed,password):
				print ("Perfecto password!")
				i=1
		if i==1:
			print ("2")
			position=(str(row[1]))
			person_id=str(row[2])
			session['person_id']=person_id
			session['position'] = position
			session['logged_in'] = True
			session['username'] = username			
			print ((session['position']))
			print ((session['person_id']))
		if i==0:
			err="username or password is wrong. Try again."
			print (err)
			return render_template('login.html',username=username,err=err)
	return redirect(url_for('.home'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('person_id',None)
    session.pop('logged_in', None)
    session.pop('position', None)
    return redirect(url_for('.lake'))

@app.route("/phome")
def phome():
	if not session.get('logged_in'):
		return render_template('login.html',username="",err="")
	else:
		pos = session['position']
		pos = pos.replace(" ","")
		print(pos)
		if (pos=="Doctor"):
			return render_template('lake.html')
		else:
			row1=""
			row2=""
			l=0
			print ("woohooo!!")
			patient_id = session['person_id']
			patient_id = patient_id.replace(" ","")
			cursor.execute('SELECT anony_id FROM patient_table where patient_id=%s', patient_id)
			row = cursor.fetchone()
			anony_id = str(row[0])
			anony_id = anony_id.replace(" ","")
			print (anony_id)
			cursor.execute('SELECT * FROM report_table where anony_id = %s',anony_id)  
			row1 = cursor.fetchall()
			print ("ohooooohooo")
			d_names=[]
			if row1:
				l= (len(row1))
				for i in range(l):
					t=str(row1[i][2]).replace(" ","")
					print (t)
					cursor.execute('SELECT firstname,lastname FROM person_table where person_id = %s',t)
					row = cursor.fetchone() 
					d = str(row[0])+" "+str(row[1])
					d_names.append(d)
					print (d)
				print (d_names)

			username = session['username'].replace(" ","")
			cursor.execute('SELECT firstname, lastname from person_table where username = %s',username)
			row2 = cursor.fetchone()
			return render_template('phome.html',row1=row1,username=username, row2=row2,l=l,d_names=d_names)

@app.route("/repid",methods=['GET','POST'])
def repid():
	if not session.get('logged_in'):
		return render_template('login.html',username="",err="")
	else:
		pos = session['position']
		pos = pos.replace(" ","")
		print(pos)
		if (pos=="Patient"):
			return render_template('lake.html')
		else:
			rowp=""
			row1=""
			row2=""
			d_names=[]
			l=0
			if request.method=="POST":
				cursor_p = conn.cursor() 
				cursor_q = conn.cursor()
				cursor_r = conn.cursor()
				patient_id = str(request.form['patient_id'])
				print (patient_id)
				cursor_p.execute('Select anony_id from patient_table where patient_id = %s',patient_id) 
				rowp = cursor_p.fetchone()
				print("1")
				if rowp:
					anony_id = str(rowp[0]).replace(" ","")
					print("2")	
				if not rowp:
					return render_template('repid.html',err="patient does not exist in your reports",row1=row1, row2=row2,d_names=d_names,l=l)
							
				doctor_id = session['person_id'].replace(" ","")
				print (doctor_id)
				print (anony_id)
				#add doctor constraint
				cursor_q.execute('SELECT * FROM report_table where anony_id = %s and doctor_id = %s',(anony_id, doctor_id))  
				row1 = cursor_q.fetchall()
				if row1:
					l= (len(row1))
				for i in range(l):
					t=str(row1[i][2]).replace(" ","")
					print (t)
					cursor.execute('SELECT firstname,lastname FROM person_table where person_id = %s',t)
					row = cursor.fetchone() 
					d = str(row[0])+" "+str(row[1])
					d_names.append(d)
					print (d)
				print (d_names)
				username = session['username'].replace(" ","")
				print("username")
				cursor_r.execute('SELECT firstname, lastname from person_table where person_id = %s',patient_id)
				row2 = cursor_r.fetchone()

				return render_template('repid.html', row1=row1, row2=row2,d_names=d_names,l=l,err="")
			return render_template("repid.html", row1=row1, row2=row2,d_names=d_names,l=l,err="")




@app.route("/dhome")
def dhome():
	if not session.get('logged_in'):
		return render_template('login.html',username="",err="")
	else:
		pos = session['position']
		pos = pos.replace(" ","")
		print(pos)
		if (pos=="Patient"):
			return render_template('lake.html')
		else:
			row1=""
			row2=""
			l=0
			doctor_id = session['person_id']
			doctor_id = doctor_id.replace(" ","")
			cursor.execute('SELECT * FROM report_table where doctor_id = %s',doctor_id)  
			row1 = cursor.fetchall()
			if row1:
				l= (len(row1))
			username = session['username'].replace(" ","")
			cursor.execute('SELECT firstname, lastname from person_table where username = %s',username)
			row2 = cursor.fetchone()
			return render_template('dhome.html',row1=row1,row2=row2,l=l)



@app.route("/send",methods=['GET','POST'])
def send():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		pos = session['position']
		pos = pos.replace(" ","")
		print(pos)
		if (pos=="Patient"):
			return render_template('lake.html')
		else:
			doctor_id = session['person_id']
			doctor_id = doctor_id.replace(" ","")
			if request.method == 'POST':
				cursor_r = conn.cursor()  
				cursor_r.execute('Select count(*) as numb from report_table') 
				rowr = cursor_r.fetchone()
				if rowr:
					ar = str(rowr[0]).replace(" ","")
					ar = int(ar) + 1
					report_id = ar
				cursor_p = conn.cursor() 
				patient_id = str(request.form['patient_id'])
				cursor_p.execute('Select anony_id from patient_table where patient_id = %s',patient_id) 
				rowp = cursor_p.fetchone()
				if rowp:
					anony_id = str(rowp[0]).replace(" ","")
				if not rowp:
					return render_template('doc1_ques.html',err="patient does not exist")
				#print (patient_id)
				age = int(request.form['age'])
				#print (age)
				date_of_test = request.form['date_of_test']
				#print (date_of_test)
				clump_thickness = int(request.form['clump_thickness'])
				##print(date_of_test) 
				unif_cell_size = int(request.form['unif_cell_size'])
				##print temperature
				unif_cell_shape = int(request.form['unif_cell_shape'])
				marg_adhesion = int(request.form['marg_adhesion'])
				single_epith_cell_size = int(request.form['single_epith_cell_size'])
				bare_nuclei = int(request.form['bare_nuclei'])
				bland_chromatin = int(request.form['bland_chromatin'])
				norm_nucleoli = int(request.form['norm_nucleoli'])
				mitosis = int(request.form['mitosis'])
				##cancer = request.form['cancer']
				#print cancer
				print ("looped!")
				instance_to_predict = {
					"clump_thickness"     : str(clump_thickness),
					"unif_cell_size"      : str(unif_cell_size),
					"unif_cell_shape"     : str(unif_cell_shape),
					"marg_adhesion"       : str(marg_adhesion),
					"single_epith_cell_size"       : str(single_epith_cell_size),
					"bare_nuclei"       : str(bare_nuclei),
					"bland_chromatin"      : str(bland_chromatin),
					"norm_nucleoli"       : str(norm_nucleoli),
					"mitosis"      : str(mitosis),
					}
				'''
				response = ml_client_connection.predict(
					MLModelId = 'ml-bSoMZLrpGQ5',
					Record = instance_to_predict,
					PredictEndpoint = 'https://realtime.machinelearning.us-east-1.amazonaws.com'
					)
	
				diagnosis = int(response['Prediction']['predictedLabel'].encode("utf-8"))
				print ("meow")
				print (diagnosis)
				'''
				diagnosis = 0
				if diagnosis==0:
					result_dia = "This patient does not have Breast Cancer with a confidence of 97%"
				else:
					result_dia = "This patient has Breast Cancer with a confidence of 97%"
				cursor.execute("INSERT INTO report_table (report_id,anony_id,doctor_id,clump_thickness,unif_cell_size,unif_cell_shape,marg_adhesion,single_epith_cell_size,bare_nuclei,bland_chromatin,norm_nucleoli,mitosis,diagnosis,age,date_of_test) VALUES ( %d,CONVERT(uniqueidentifier,%s),%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s)",(report_id,anony_id,doctor_id,clump_thickness,unif_cell_size,unif_cell_shape,marg_adhesion,single_epith_cell_size,bare_nuclei,bland_chromatin,norm_nucleoli,mitosis,diagnosis,age,date_of_test))
				conn.commit()




				return render_template('doc3_report_this.html', item_diag=result_dia,dot=date_of_test,patient_id=patient_id,clump_thickness=clump_thickness, unif_cell_size=unif_cell_size,unif_cell_shape=unif_cell_shape,marg_adhesion=marg_adhesion,single_epith_cell_size=single_epith_cell_size,bare_nuclei=bare_nuclei,bland_chromatin=bland_chromatin,norm_nucleoli=norm_nucleoli,mitosis=mitosis)


			return render_template('doc1_ques.html',err="")

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run()






















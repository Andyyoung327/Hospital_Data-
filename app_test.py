from __future__ import print_function # Python 2/3 compatibility
import os
os.environ["TZ"] = "UTC"
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from flask import Flask, render_template, request, flash, redirect, session, abort
import pymssql  


app = Flask(__name__)

conn = pymssql.connect(server='breastdb.cvlffbfnvce5.us-east-1.rds.amazonaws.com', user='clouduser', password='cloudpwd', database='BreastData')  
cursor = conn.cursor()  


@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		firstname = request.form['firstname']
		lastname= request.form['lastname']
		username=request.form['username']
		gender=request.form['gender']
		password = request.form['password']
		position="Doctor"
		print (firstname)
		print (lastname)
		print (username)
		print (gender)
		print (password)
		print (position)
		cursor.execute('INSERT INTO Person_table VALUES (%s,%s,%s,%s,%s,%s)',(username,password,firstname,lastname,gender,position))  
		conn.commit()
		#print (firstname)
		return redirect(url_for('login'))
		return render_template('index1.html',firstname=firstname)
	return render_template('index2.html')

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run()

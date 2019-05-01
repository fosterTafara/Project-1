# FLASK, MySQL and Python Demo
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
# instantiate an object called app
app = Flask(__name__)

# Configure db
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Signal2019$$",
  database="project"
)

#admin retrive all info	
@app.route('/device-list')
def devicelist():
	mycursor = mydb.cursor()
	mycursor.execute("select * from device")
	device_details = mycursor.fetchall()
	return render_template('admin.html', device_details = device_details)

#return device function	
@app.route('/return', methods=['GET', 'POST'])
def returndevice():
	mycursor = mydb.cursor()
	mycursor.execute("select * from users")
	user_list = mycursor.fetchall()
	mydb.commit()
	mycursor.close()
	if request.method == 'POST':
     # Fetch form data			
		UserDetails = request.form
		user_id = UserDetails['user']
		#print (user_id)		
		mycursor = mydb.cursor()
		mycursor.execute("select device.deviceId, device.deviceType from device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s", (user_id,))		
		loan_devices = mycursor.fetchall()		
		mydb.commit()
		mycursor.close()
		return render_template('return.html', loan_devices = loan_devices,user_list = user_list)
	
	return render_template('return.html', user_list = user_list)

	
if (__name__) == ('__main__'):
	app.run(debug=True)
	
# FLASK, MySQL and Python Demo
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
# instantiate an object called app
app = Flask(__name__)

# Configure db
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="project"
)

@app.route('/device-list', methods =['GET', 'POST'])
def devicelist():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM device")
    device_details = mycursor.fetchall()
	  
    userDetails = request.form
    # mycursor = mydb.cursor()
    # mycursor.execute("SELECT device.deviceId, FROM device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s", (user_id,))
    # result = mycursor.fetchall()      
    mydb.commit()
    mycursor.close()
    # if len(result) == 0:
    # 	print (result[5][0])
    # else: 
    #     print (result[6][1])
	        
	return render_template('devicelist.html', device_details = device_details)












      
 #return device function	
@app.route('/return', methods=['GET', 'POST'])
def returndevice():
	mycursor = mydb.cursor()
	mycursor.execute("select * from users")
	user_list = mycursor.fetchall()	
	mycursor.close()
	NUM_USER = len(user_list)
	
	if request.method == 'POST':
		if 'NameSubmit' in request.form:
			# Fetch form data	
			NUM_USER =1
			UserDetails = request.form
			user_id = UserDetails['user']
			#print (user_id)		
			mycursor = mydb.cursor()
			mycursor.execute("select device.deviceId,device.deviceName, device.deviceType from device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s", (user_id,))		
			loan_devices = mycursor.fetchall()
			num_device = len(loan_devices)
			print(num_device)
			mycursor.close()
			return render_template('return.html', loan_devices = loan_devices,user_list = user_list,NUM_USER=NUM_USER,num_device=num_device)	
		
			if 'ReturnNow' in request.form:
				SelectedDevices = request.form.getlist('selected[]')
				mycursor = mydb.cursor()				
				DeviceDetails = request.form
				print(DeviceDetails)
	
	return render_template('return.html', user_list = user_list)



##put: devicechoice = request.args.get("DevID") into the check-out definition to capture the Device ID


###admin retrive all info	
##@app.route('/device-list')
##def devicelist():
##	mycursor = mydb.cursor()
##	mycursor.execute("select * from device")
##	device_details = mycursor.fetchall()
##	return render_template('admin.html', device_details = device_details)
	
if (__name__) == ('__main__'):
	app.run(debug=True)


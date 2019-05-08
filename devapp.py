# FLASK, MySQL and Python Demo
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from datetime import datetime

# instantiate an object called app
app = Flask(__name__)

app.config['SECRET_KEY'] = '0190f0f484f4c59d491ca93129dc63d2'

# Configure db
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="Project"

)


@app.route('/')
@app.route('/users/')  
def students():
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM users")
	result = mycursor.fetchall()
	mycursor.close()
	return render_template('users.html', title='Users', menu='users', users=result)


@app.route('/device-list', methods =['GET', 'POST'])
### do we really need methods for this app.route?
def devicelist():
	### Itemise all of the device details rather than use the asterisk so we could also add checkingsystem.userId, users.firstName, users.lastName. Then an outer join to incorporate the third table
	mycursor = mydb.cursor()
	mycursor.execute("SELECT device.deviceId, device.deviceName, device.deviceType, device.osType, device.osVersion, "
					 "device.deviceCpu, device.deviceBit, device.screenRes, device.deviceGrade, device.deviceUuid, device.deviceStatus, mostrecentborrow.userID, "
					 "users.firstName as mostrecentuser, users.lastName from device left outer join (SELECT deviceID, borrowDate AS mostrecentborrowDate, userID FROM checkingsystem "
					 "AS t WHERE BorrowDate = (SELECT MAX(borrowDate) FROM checkingsystem WHERE deviceID = t.deviceID)) mostrecentborrow on device.deviceID = mostrecentborrow.deviceID "
					 "left outer join users on mostrecentborrow.userID = users.userID")
	device_details = mycursor.fetchall()
	mycursor = mydb.cursor()    
	mydb.commit()
	mycursor.close()

	return render_template('devicelist.html', device_details = device_details)

def devicedetails():	
	mycursor = mydb.cursor()
	mycursor.execute("select * from device left outer join latestborrow on device.deviceId = latestborrow.deviceId left outer join users on users.userid = latestborrow.userid")	
	device_details = mycursor.fetchall()	
	return device_details

def loandevices(userid):
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute("select device.deviceId,device.deviceName, device.deviceType, checkingsystem.dueDate from device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s AND checkingsystem.returnDate is NULL", (user_id,))		
	loan_devices = mycursor.fetchall()	
	return loan_devices

def holddevices(userid):
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute("select device.deviceId,device.deviceName, device.deviceType, device.deviceStatus from device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s AND checkingsystem.holdDate is not NULL and checkingsystem.borrowDate is NULL", (user_id,))		
	hold_devices = mycursor.fetchall()
	return hold_devices
	
@app.route('/device-list/search', methods=['POST'])
def searchdevices():
	deviceSearch = request.form
	device_search_term = deviceSearch['device_search_details']
	mycursor = mydb.cursor()
	#mycursor.execute("SELECT * FROM device WHERE deviceName LIKE '%{}%' OR deviceType LIKE '%{}%' "
					#"OR osType LIKE '%{}%' OR osVersion LIKE '%{}%' OR deviceRam LIKE '%{}%' "
					#"OR deviceCpu LIKE '%{}%' OR deviceBit LIKE '%{}%' OR screenRes LIKE '%{}%' "
					#"OR deviceGrade LIKE '%{}%'".format(device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term))
	mycursor.execute("SELECT device.deviceId, device.deviceName, device.deviceType, device.osType, device.osVersion, "
					"device.deviceCpu, device.deviceBit, device.screenRes, device.deviceGrade, device.deviceUuid, device.deviceStatus, mostrecentborrow.userID, "
					"users.firstName as mostrecentuser, users.lastName from Device left outer join (SELECT deviceID, borrowDate AS MostRecentBorrowDate, userID FROM checkingsystem "
					"AS t WHERE BorrowDate = (SELECT MAX(borrowDate) FROM checkingsystem WHERE deviceID = t.deviceID)) Mostrecentborrow on device.deviceID = Mostrecentborrow.deviceID "
					"left outer join Users on Mostrecentborrow.userID = Users.userID where deviceName LIKE '%{}%' OR deviceType LIKE '%{}%' "
					"OR osType LIKE '%{}%' OR osVersion LIKE '%{}%' OR deviceRam LIKE '%{}%' "
					"OR deviceCpu LIKE '%{}%' OR deviceBit LIKE '%{}%' OR screenRes LIKE '%{}%' "
					"OR deviceGrade LIKE '%{}%' OR users.firstName LIKE '%{}%' OR users.lastName LIKE '%{}%'".format(device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term))	
	device_details = mycursor.fetchall()
	mycursor.close()
	return render_template('devicelist.html', title='Search', device_details=device_details, is_search=True)

@app.route('/device-borrow-return/<int:userid>', methods =['GET', 'POST'])
def deviceborrowreturn(userid):
	#if request.method == 'GET':
	user_id = userid

	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	
	loan_devices = loandevices(user_id)	
	num_device = len(loan_devices)

	hold_devices = holddevices(user_id)
	num_hold_device = len(hold_devices)	
	
	device_details = devicedetails()

	mycursor.close()
	
	if request.method == 'POST':

		if 'ReturnNow' in request.form:
		
			mycursor = mydb.cursor()
			SelectedDevices = request.form.getlist('selected[]')
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			for each_item in SelectedDevices:
			#USER_ID = SELECT(USERID IN THE CHECKING SYSTEM WHERE EACH_ITEM IS EQUAL TO DEVICEid)
				mycursor = mydb.cursor()
				mycursor.execute("UPDATE checkingsystem SET returnDate = current_time WHERE deviceID = {}".format(each_item))

				mycursor.execute('UPDATE Device SET deviceStatus = "Available" WHERE deviceId = {}'.format(each_item))                         

				mydb.commit()
				mycursor.close()
				mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details = devicedetails()
			mycursor.close()
			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

	if request.method == 'POST':
		if 'BorrowNow' in request.form:
			mycursor = mydb.cursor()
			device_details = devicedetails()			
			mycursor = mydb.cursor()
			BorrowedDevices = request.form.getlist('deviceSelected[]')
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			for each_item in BorrowedDevices:
				mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id, each_item, Current_Time))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE deviceID = {}".format(each_item))
				mycursor.execute('UPDATE device SET deviceStatus = "Unavailable" WHERE deviceId = {}'.format(each_item))
			mydb.commit()
			mycursor.close()
			
			mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
		
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details = devicedetails()
			mycursor.close()	
			
			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices)
		return render_template('deviceborrowreturn.html', userid=user_id,loan_devices=loan_devices, device_details=device_details, num_device=num_device, user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices)
	return render_template('deviceborrowreturn.html', userid=user_id,loan_devices=loan_devices, device_details=device_details, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

		

	
      
	
#checking out page
#added a variable to the app route url which is then able to be passes as a keyword to the function. (an alternative would have been to use ARGS)
@app.route('/check-out/<int:deviceid>', methods=['GET', 'POST'])
def checkout(deviceid):
	device_id= deviceid

	if request.method == 'POST':
		# press check-out button update availability
		formContent = request.form
		email_address = formContent['item']
		mycursor = mydb.cursor()
		mycursor.execute("SELECT userId from users WHERE email = '{}';" .format(email_address))
		user_id = mycursor.fetchone()
		mycursor.execute("SELECT d.deviceName FROM Device d INNER JOIN CheckingSystem c ON d.deviceId=c.deviceId WHERE d.deviceId = '{}';".format(device_id))
		device_name = mycursor.fetchall()
		# ADD WHERE 
		mycursor.execute("SELECT COUNT(userId) FROM CheckingSystem WHERE borrowDate IS NOT NULL and returnDate IS NULL;")
		user_count = mycursor.fetchall()
		mycursor.close()	
		mycursor = mydb.cursor()
		current_date = datetime.now()
		current_date = current_date.strftime('%Y-%m-%d %H:%M:%S')
		mycursor.execute("INSERT INTO CheckingSystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id[0], device_id, current_date))
		mycursor.close()	
		mydb.commit()
		flash("You have borrowed {} and you now have {} devices!".format(device_name[0][0], user_count[0][0]))

		return redirect('/device-list')				 
	#select from the database (device id/name/type)	
	mycursor = mydb.cursor()
	mycursor.execute("SELECT deviceId, deviceName, deviceType from device WHERE deviceId = {};" .format(device_id))
	device_details = mycursor.fetchall() 
	# raise Exception(device_details)
	#select from the database (name)
	mycursor.execute("SELECT email, userId from users;")
	user_emails = mycursor.fetchall()
	mycursor.close()	
	return render_template('check-out.html', devices=device_details, emails=user_emails)	

 #return device function	
@app.route('/return', methods=['GET', 'POST'])
def returndevice():
	mycursor = mydb.cursor()
	mycursor.execute("select * from users")
	user_list = mycursor.fetchall()	
	mycursor.close()
	NUM_USER = len(user_list)
	
	if request.method == 'POST':
		#print(request.form)
		if 'NameSubmit' in request.form:
			# Fetch form data	
			NUM_USER =1
			UserDetails = request.form
			user_id = UserDetails['user']
			#print (user_id)		
			mycursor = mydb.cursor()
			mycursor.execute("select device.deviceId,device.deviceName, device.deviceType from device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s AND checkingsystem.returnDate is NULL", (user_id,))		
			loan_devices = mycursor.fetchall()
			num_device = len(loan_devices)
			print(num_device)
			mycursor.close()
			return render_template('return.html', loan_devices = loan_devices,user_list = user_list,NUM_USER=NUM_USER,num_device=num_device, user_id=user_id)	
		
		if 'ReturnNow' in request.form:
			#user_id = UserDetails['user']
			#print (user_id)			
			mycursor = mydb.cursor()
			SelectedDevices = request.form.getlist('selected[]')
			print(SelectedDevices)
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			for each_item in SelectedDevices:
			#USER_ID = SELECT(USERID IN THE CHECKING SYSTEM WHERE EACH_ITEM IS EQUAL TO DEVICEid)
				mycursor.execute("UPDATE checkingsystem SET returnDate = current_time WHERE deviceID = {}".format(each_item))
				mycursor.execute('UPDATE Device SET deviceStatus = "Available" WHERE deviceId = {}'.format(each_item))                         
				#print("success")
				mydb.commit()
				mycursor.close()
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


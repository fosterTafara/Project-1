# FLASK, MySQL and Python Demo
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from datetime import datetime
from datetime import timedelta

# instantiate an object called app
app = Flask(__name__)

app.config['SECRET_KEY'] = '0190f0f484f4c59d491ca93129dc63d2'

# Configure db
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="project"
)
	
def alldevicedetails():	
	mycursor = mydb.cursor()
	mycursor.execute("select * from devicedetails")	
	device_details = mycursor.fetchall()
	# for idx, item in enumerate(device_details):
	# 	if item[15] is not None:
	# 		the_time = item[15]
	# 		the_time = the_time.strftime('%d %B')
	# 		item = list(item)

	# 		item[15] = the_time
	# 		item = tuple(item)
	# 		device_details[idx] = item
	# for x in range (0,((len(device_details))+1)):
	# 	device_details[x][17]=device_details[x][17].strftime('%d %B' )
	# formatted = []
	# for item in device_details:
	# 	if item[17] is not None:
	# 			the_time = item[17]
	# 			the_time = the_time.strftime('%d %B')
	# 			item = list(item)
	# 			item[17] = the_time
	# 			item = tuple(item)
	# 	# 		device_details[idx] = item
	# 	formatted.append(item)
	mycursor.close()
	return device_details

def devicedetails(userid):
	user_id = userid
	mycursor = mydb.cursor()
	#mycursor.execute("SELECT * FROM devicedetails where devicedetails.userid <> %s or devicedetails.userid is null", (user_id,))
	mycursor.execute("SELECT * FROM devicedetails where devicedetails.userid is null or devicedetails.userid <> %s AND devicedetails.deviceid NOT IN (select latesthold.deviceid from latesthold where latesthold.userid = %s)", (user_id, userid,))

	#needed to redefine the query because it still contains holding item of the user - resolved
	#this was because of the left joins in the view which didn't allow for one device to be attached to two users.


	
	device_details_userid = mycursor.fetchall()
	# raise Exception(device_details_userid)
	mycursor.close()
	return device_details_userid

def loandevices(userid):
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute("select deviceId, deviceName, deviceType, dueDate from devicedetails where userId = %s AND returnDate is NULL", (user_id,))
	#this queries is correct now by using devicedetails view
		
	loan_devices = mycursor.fetchall()

	mycursor.close()
	return loan_devices

def holddevices(userid):
	user_id = userid
	mycursor = mydb.cursor()
	Current_Time = datetime.now()
	mycursor.execute("select device.deviceId,device.deviceName, device.deviceType, device.deviceStatus from device inner join latesthold on device.deviceId = latesthold.deviceId where latesthold.userId = %s", (user_id,))
	#this queries is correct now by using latesthold view

	hold_devices = mycursor.fetchall()
	mycursor.close()
	return hold_devices
	
@app.route('/device-borrow-return/<int:userid>', methods =['GET', 'POST'])
def deviceborrowreturn(userid):
	#if request.method == 'GET':
	user_id = userid

	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	
	# can't just use function, need to pass the value to the variables in render_template
	loan_devices = loandevices(user_id)
	num_device = len(loan_devices)

	hold_devices = holddevices(user_id)
	num_hold_device = len(hold_devices)
	# print(num_hold_device)
	
	device_details_userid = devicedetails(user_id)
	# raise Exception(device_details_userid)
	mycursor.close()
	
	if request.method == 'POST':
		if 'ReturnNow' in request.form:
			mycursor = mydb.cursor()
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['ReturnNow']

			mycursor = mydb.cursor()
			mycursor.execute("UPDATE checkingsystem SET returnDate = current_time WHERE deviceID = {} and userId={}".format(device_id, user_id))
			mycursor.execute("SELECT * from checkingsystem WHERE deviceID = {} and holdDate is not null and borrowDate is null".format(device_id))
			check_hold_number =mycursor.fetchall()
			if len(check_hold_number) == 0:
				mycursor.execute('UPDATE device SET deviceStatus = "Available" WHERE deviceId = {}'.format(device_id))
			else:
				mycursor.execute('UPDATE device SET deviceStatus = "On Hold" WHERE deviceId = {}'.format(device_id))
			mydb.commit()
			mycursor.close()
			mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)
			mycursor.close()
			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

		
	if request.method == 'POST':
		if 'BorrowNow' in request.form:
			mycursor = mydb.cursor()
			device_details_userid = devicedetails(user_id)
			mycursor = mydb.cursor()
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			print(DeviceDetails)
			#DeviceDetails is a dictionary in this case.
			device_id=DeviceDetails['BorrowNow']
			mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Current_Time))
			mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE deviceID = {}".format(device_id,))
			mycursor.execute('UPDATE device SET deviceStatus = "Unavailable" WHERE deviceId = {}'.format(device_id,))
			mydb.commit()	
			
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()
			
			mycursor.close()
			# flash("You have checked out device {}".format (device_id))
			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices, borrow_device=True, device_name=device_name)
		
	if request.method == 'POST':
		if 'HoldNow' in request.form:
			#This function should be modified based new user story, holdExpiry will only be updated once the device is returned
			mycursor = mydb.cursor(buffered=True)
			device_details_userid = devicedetails(user_id)
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['HoldNow']

			
			mycursor.execute("SELECT * from latesthold where deviceId ={} and userId={}".format(device_id,user_id))
			check_holding = mycursor.fetchall()
			
			if len(check_holding) != 0:
				flash('You have already held this item.')
			else: 
			

				mycursor.execute("SELECT dueDate from latestborrow where deviceId={} and borrowDate is not null".format(device_id,))					
				Due_Date=mycursor.fetchone()	
				
				Due_Date=Due_Date[0]
				print (Due_Date)
				
				mycursor.execute("SELECT * from checkingsystem where deviceId = {} and holdDate is not null and borrowDate is null".format(device_id,))
				
				check_hold_queue = mycursor.fetchall()
				hold_position = len(check_hold_queue)+1
				print(hold_position)
			
				#review the way to determine the holding position
				
				if hold_position ==1:			
					mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Due_Date))
					mycursor.execute("UPDATE checkingsystem SET holdExpiry = DATE_ADD(holdDate, INTERVAL 2 DAY) WHERE deviceID = {} and userId={}".format(device_id, user_id))
				
				elif hold_position ==2:	
					Due_Date = Due_Date + timedelta(days=5)
					mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Due_Date))
					mycursor.execute("UPDATE checkingsystem SET holdExpiry = DATE_ADD(holdDate, INTERVAL 2 DAY) WHERE deviceID = {} and userId={}".format(device_id, user_id))
					
				elif hold_position ==3:	
					Due_Date = Due_Date + timedelta(days=10)				
					mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Due_Date))
					mycursor.execute("UPDATE checkingsystem SET holdExpiry = DATE_ADD(holdDate, INTERVAL 2 DAY) WHERE deviceID = {} and userId={}".format(device_id, user_id))
				else:
					flash('Sorry you cannot put a hold on the device now. There have been 3 holds on the device please select another one !')
					
				mydb.commit()
				mycursor.close()
			
			mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)

			mycursor.close()	

			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices)	
		
		
	if request.method == 'POST':
		if 'BorrowHold' in request.form:

			print(user_id)
			mycursor = mydb.cursor(buffered=True)
			device_details_userid = devicedetails(user_id)			

			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['BorrowHold']
			#mycursor.execute("Select deviceStatus from devicedetails where deviceId = {}".format(device_id,))
			#device_Status = mycursor.fetchone()
			#print(device_Status)
			#if device_status == 'Available': no need to check because the device status will always "On hold" if we go with deleting Hold expired
			
			mycursor.execute("SELECT * from checkingsystem where deviceId = {} and holdDate is not null and borrowDate is null order by holdDate asc".format(device_id,))
			check_hold_queue = mycursor.fetchall()
			
			print (check_hold_queue)
			
			if len(check_hold_queue) ==1:
				#mycursor = mydb.cursor
				mycursor.execute("UPDATE checkingsystem SET borrowDate = '{}' where userId={} and deviceid={} and borrowDate is null".format(Current_Time,user_id,device_id))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE userId = {} and deviceid={} and borrowDate = '{}'".format(user_id,device_id,Current_Time))
				#mycursor.execute("UPDATE checkingsystem SET deviceStatus = 'Unavailable' WHERE deviceid={} and borrowDate = '{}'".format(user_id,device_id,Current_Time))
				mydb.commit()	
			
			else: 
				
				
				loan_devices = loandevices(user_id)		
				num_device = len(loan_devices)
				hold_devices = holddevices(user_id)
				num_hold_device = len(hold_devices)
				device_details_userid = devicedetails(user_id)
				mycursor.close()
			
			
				mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Current_Time))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE deviceID = {}".format(device_id,))
				mycursor.execute('UPDATE device SET deviceStatus = "Unavailable" WHERE deviceId = {}'.format(device_id,))
				mydb.commit()	
				mycursor = mydb.cursor()
				loan_devices = loandevices(user_id)		

				num_device = len(loan_devices)
				hold_devices = holddevices(user_id)
				num_hold_device = len(hold_devices)
				device_details_userid = devicedetails(user_id)

				mycursor.close()	
			
			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices)
				
	return render_template('deviceborrowreturn.html', userid=user_id,loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

	
@app.route('/', methods =['GET', 'POST'])
@app.route('/device-borrow-return', methods =['GET', 'POST'])
def borrowreturn():
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM users")
	users = mycursor.fetchall()

	device_details_userid = alldevicedetails()

	print(device_details_userid[0][0])
	
	if request.method == 'POST':
	
		userDetails = request.form
		user_id = userDetails['userid']
		mycursor = mydb.cursor()
		mycursor.execute("select * from users")
		user_details = mycursor.fetchall()
		print(user_id)	
		    
		#studentList = request.args.get("ID")
		#user_id = request.args.get("user_id")


		device_details = alldevicedetails()


		mycursor.close()
		return redirect('/device-borrow-return/{}'.format(user_id))
	
	return render_template('deviceborrowreturn.html', device_details_userid=device_details_userid, users=users, usertrue=True)	   

@app.route('/myview/<int:userid>', methods =['GET', 'POST'])
def myview(userid):
#if request.method == 'GET':
	user_id = userid

	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	
	# can't just use function, need to pass the value to the variables in render_template
	loan_devices = loandevices(user_id)
	num_device = len(loan_devices)

	hold_devices = holddevices(user_id)
	num_hold_device = len(hold_devices)
	# print(num_hold_device)
	
	device_details_userid = devicedetails(user_id)
	# raise Exception(device_details_userid)
	mycursor.close()
	
	if request.method == 'POST':
		if 'ReturnNow' in request.form:
			mycursor = mydb.cursor()
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['ReturnNow']

			mycursor = mydb.cursor()
			mycursor.execute("UPDATE checkingsystem SET returnDate = current_time WHERE deviceID = {} and userId={}".format(device_id, user_id))
			mycursor.execute("SELECT * from checkingsystem WHERE deviceID = {} and holdDate is not null and borrowDate is null".format(device_id))
			check_hold_number =mycursor.fetchall()
			if len(check_hold_number) == 0:
				mycursor.execute('UPDATE device SET deviceStatus = "Available" WHERE deviceId = {}'.format(device_id))
			else:
				mycursor.execute('UPDATE device SET deviceStatus = "On Hold" WHERE deviceId = {}'.format(device_id))
			mydb.commit()
			mycursor.close()
			mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)
			mycursor.close()
			return render_template('myview.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)
	
		
	if request.method == 'POST':
		if 'BorrowHold' in request.form:

			print(user_id)
			mycursor = mydb.cursor(buffered=True)
			device_details_userid = devicedetails(user_id)			

			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['BorrowHold']
			#mycursor.execute("Select deviceStatus from devicedetails where deviceId = {}".format(device_id,))
			#device_Status = mycursor.fetchone()
			#print(device_Status)
			#if device_status == 'Available': no need to check because the device status will always "On hold" if we go with deleting Hold expired
			
			mycursor.execute("SELECT * from checkingsystem where deviceId = {} and holdDate is not null and borrowDate is null order by holdDate asc".format(device_id,))
			check_hold_queue = mycursor.fetchall()
			
			print (check_hold_queue)
			
			if len(check_hold_queue) ==1:
				#mycursor = mydb.cursor
				mycursor.execute("UPDATE checkingsystem SET borrowDate = '{}' where userId={} and deviceid={} and borrowDate is null".format(Current_Time,user_id,device_id))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE userId = {} and deviceid={} and borrowDate = '{}'".format(user_id,device_id,Current_Time))
				#mycursor.execute("UPDATE checkingsystem SET deviceStatus = 'Unavailable' WHERE deviceid={} and borrowDate = '{}'".format(user_id,device_id,Current_Time))
				mydb.commit()	
			
			else: 
				
				
				loan_devices = loandevices(user_id)		
				num_device = len(loan_devices)
				hold_devices = holddevices(user_id)
				num_hold_device = len(hold_devices)
				device_details_userid = devicedetails(user_id)
				mycursor.close()
			
			
				mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Current_Time))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE deviceID = {}".format(device_id,))
				mycursor.execute('UPDATE device SET deviceStatus = "Unavailable" WHERE deviceId = {}'.format(device_id,))
				mydb.commit()	
				mycursor = mydb.cursor()
				loan_devices = loandevices(user_id)		

				num_device = len(loan_devices)
				hold_devices = holddevices(user_id)
				num_hold_device = len(hold_devices)
				device_details_userid = devicedetails(user_id)

				mycursor.close()	
			
			return render_template('myview.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices)
				
	return render_template('myview.html', userid=user_id,loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)


@app.route('/users/')  
def users():
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM users")
	users = mycursor.fetchall()
	mycursor.close()
	# if 'Userselect' in request.form: #this is the button name
		# print("HAPPY")
		# mycursor = mydb.cursor()
		# userDetails = request.form
		# print(userDetails)
		# # student_ID = courseDetails['studentId']
		# # coursename = courseDetails['courseone']
		# # print(student_ID)

		# return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

	return render_template('users.html', title='Users', menu='users', users=users)


# @app.route('/device-list', methods =['GET', 'POST'])
# ### do we really need methods for this app.route?
# def devicelist():
	# ### Itemise all of the device details rather than use the asterisk so we could also add checkingsystem.userId, users.firstName, users.lastName. Then an outer join to incorporate the third table
	# mycursor = mydb.cursor()
	# mycursor.execute("SELECT device.deviceId, device.deviceName, device.deviceType, device.osType, device.osVersion, "
					 # "device.deviceCpu, device.deviceBit, device.screenRes, device.deviceGrade, device.deviceUuid, device.deviceStatus, mostrecentborrow.userID, "
					 # "users.firstName as mostrecentuser, users.lastName from device left outer join (SELECT deviceID, borrowDate AS mostrecentborrowDate, userID FROM checkingsystem "
					 # "AS t WHERE BorrowDate = (SELECT MAX(borrowDate) FROM checkingsystem WHERE deviceID = t.deviceID)) mostrecentborrow on device.deviceID = mostrecentborrow.deviceID "
					 # "left outer join users on mostrecentborrow.userID = users.userID")
	# device_details = mycursor.fetchall()
	# mycursor = mydb.cursor()    
	# mydb.commit()
	# mycursor.close()

	# return render_template('devicelist.html', device_details = device_details)


	return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)
		   

	
# #checking out page
# #added a variable to the app route url which is then able to be passes as a keyword to the function. (an alternative would have been to use ARGS)
# @app.route('/check-out/<int:deviceid>', methods=['GET', 'POST'])
# def checkout(deviceid):
	# device_id= deviceid

	# if request.method == 'POST':
		# # press check-out button update availability
		# formContent = request.form
		# email_address = formContent['item']
		# mycursor = mydb.cursor()
		# mycursor.execute("SELECT userId from users WHERE email = '{}';" .format(email_address))
		# user_id = mycursor.fetchone()
		# mycursor.execute("SELECT d.deviceName FROM Device d INNER JOIN CheckingSystem c ON d.deviceId=c.deviceId WHERE d.deviceId = '{}';".format(device_id))
		# device_name = mycursor.fetchall()
		# # ADD WHERE 
		# mycursor.execute("SELECT COUNT(userId) FROM CheckingSystem WHERE borrowDate IS NOT NULL and returnDate IS NULL;")
		# user_count = mycursor.fetchall()
		# mycursor.close()	
		# mycursor = mydb.cursor()
		# current_date = datetime.now()
		# current_date = current_date.strftime('%Y-%m-%d %H:%M:%S')
		# mycursor.execute("INSERT INTO CheckingSystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id[0], device_id, current_date))
		# mycursor.close()	
		# mydb.commit()
		# flash("You have borrowed {} and you now have {} devices!".format(device_name[0][0], user_count[0][0]))

		# return redirect('/device-list')				 
	# #select from the database (device id/name/type)	
	# mycursor = mydb.cursor()
	# mycursor.execute("SELECT deviceId, deviceName, deviceType from device WHERE deviceId = {};" .format(device_id))
	# device_details = mycursor.fetchall() 
	# # raise Exception(device_details)
	# #select from the database (name)
	# mycursor.execute("SELECT email, userId from users;")
	# user_emails = mycursor.fetchall()
	# mycursor.close()	
	# return render_template('check-out.html', devices=device_details, emails=user_emails)	

 # #return device function	
# @app.route('/return', methods=['GET', 'POST'])
# def returndevice():
	# mycursor = mydb.cursor()
	# mycursor.execute("select * from users")
	# user_list = mycursor.fetchall()	
	# mycursor.close()
	# NUM_USER = len(user_list)
	
	# if request.method == 'POST':
		# #print(request.form)
		# if 'NameSubmit' in request.form:
			# # Fetch form data	
			# NUM_USER =1
			# UserDetails = request.form
			# user_id = UserDetails['user']
			# #print (user_id)		
			# mycursor = mydb.cursor()
			# mycursor.execute("select device.deviceId,device.deviceName, device.deviceType from device inner join checkingsystem on device.deviceId = checkingsystem.deviceId where checkingsystem.userId = %s AND checkingsystem.returnDate is NULL", (user_id,))		
			# loan_devices = mycursor.fetchall()
			# num_device = len(loan_devices)
			# print(num_device)
			# mycursor.close()
			# return render_template('return.html', loan_devices = loan_devices,user_list = user_list,NUM_USER=NUM_USER,num_device=num_device, user_id=user_id)	
		
		# if 'ReturnNow' in request.form:
			# #user_id = UserDetails['user']
			# #print (user_id)			
			# mycursor = mydb.cursor()
			# SelectedDevices = request.form.getlist('selected[]')
			# print(SelectedDevices)
			# Current_Time = datetime.now()
			# Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			# DeviceDetails = request.form
			# for each_item in SelectedDevices:
			# #USER_ID = SELECT(USERID IN THE CHECKING SYSTEM WHERE EACH_ITEM IS EQUAL TO DEVICEid)
				# mycursor.execute("UPDATE checkingsystem SET returnDate = current_time WHERE deviceID = {}".format(each_item))
				# mycursor.execute('UPDATE Device SET deviceStatus = "Available" WHERE deviceId = {}'.format(each_item))                         
				# #print("success")
				# mydb.commit()
				# mycursor.close()
	# return render_template('return.html', user_list = user_list)

# @app.route('/device-list/search', methods=['POST'])
# def searchdevices():
	# deviceSearch = request.form
	# device_search_term = deviceSearch['device_search_details']
	# mycursor = mydb.cursor()
	# #mycursor.execute("SELECT * FROM device WHERE deviceName LIKE '%{}%' OR deviceType LIKE '%{}%' "
					# #"OR osType LIKE '%{}%' OR osVersion LIKE '%{}%' OR deviceRam LIKE '%{}%' "
					# #"OR deviceCpu LIKE '%{}%' OR deviceBit LIKE '%{}%' OR screenRes LIKE '%{}%' "
					# #"OR deviceGrade LIKE '%{}%'".format(device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term))
	# mycursor.execute("SELECT device.deviceId, device.deviceName, device.deviceType, device.osType, device.osVersion, "
					# "device.deviceCpu, device.deviceBit, device.screenRes, device.deviceGrade, device.deviceUuid, device.deviceStatus, mostrecentborrow.userID, "
					# "users.firstName as mostrecentuser, users.lastName from Device left outer join (SELECT deviceID, borrowDate AS MostRecentBorrowDate, userID FROM checkingsystem "
					# "AS t WHERE BorrowDate = (SELECT MAX(borrowDate) FROM checkingsystem WHERE deviceID = t.deviceID)) Mostrecentborrow on device.deviceID = Mostrecentborrow.deviceID "
					# "left outer join Users on Mostrecentborrow.userID = Users.userID where deviceName LIKE '%{}%' OR deviceType LIKE '%{}%' "
					# "OR osType LIKE '%{}%' OR osVersion LIKE '%{}%' OR deviceRam LIKE '%{}%' "
					# "OR deviceCpu LIKE '%{}%' OR deviceBit LIKE '%{}%' OR screenRes LIKE '%{}%' "
					# "OR deviceGrade LIKE '%{}%' OR users.firstName LIKE '%{}%' OR users.lastName LIKE '%{}%'".format(device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term, device_search_term))	
	# device_details = mycursor.fetchall()
	# mycursor.close()
	# return render_template('devicelist.html', title='Search', device_details=device_details, is_search=True)
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


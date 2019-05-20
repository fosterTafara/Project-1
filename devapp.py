# FLASK, MySQL and Python Demo
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from datetime import datetime
from datetime import timedelta




# instantiate an object called app
app = Flask(__name__)

app.config['SECRET_KEY'] = '0190f0f484f4c59d491ca93129dc63d2'
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Signal2019$$",
  database="project"
)
## Define our functions
def alldevicedetails():	
	mycursor = mydb.cursor()
	mycursor.execute("select * from devicedetails")	
	device_details = mycursor.fetchall()
	mycursor.close()
	return device_details

def devicedetails(userid):
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM devicedetails where devicedetails.userid is null or devicedetails.userid <> %s AND devicedetails.deviceid NOT IN (select latesthold.deviceid from latesthold where latesthold.userid = %s)", (user_id, userid,))
	device_details_userid = mycursor.fetchall()
	mycursor.close()
	return device_details_userid

def loandevices(userid):
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute("select deviceId, deviceName, deviceType, dueDate from devicedetails where userId = %s AND returnDate is NULL", (user_id,))
	loan_devices = mycursor.fetchall()
	mycursor.close()
	return loan_devices

def holddevices(userid):
	user_id = userid
	mycursor = mydb.cursor()
	Current_Time = datetime.now()
	mycursor.execute("select device.deviceId,device.deviceName, device.deviceType, device.deviceStatus, latesthold.holdPosition from device inner join latesthold on device.deviceId = latesthold.deviceId where latesthold.userId = %s", (user_id,))
	#this queries is correct now by using latesthold view

	hold_devices = mycursor.fetchall()
	mycursor.close()
	return hold_devices

## main template	
@app.route('/device-borrow-return/<int:userid>', methods =['GET', 'POST'])
def deviceborrowreturn(userid):
	#if request.method == 'GET':
	user_id = userid


	if request.method == 'POST':
		if 'ReturnNow' in request.form:
			print("ReturnNow")
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
				mycursor.execute("UPDATE device SET deviceStatus = 'Available' WHERE deviceId = {}".format(device_id))
			else:
				mycursor.execute("UPDATE device SET deviceStatus = 'On Hold' WHERE deviceId = {}".format(device_id))
				#update the holdExpiry for first hold in the queue
				mycursor.execute("UPDATE checkingsystem SET holdExpiry = DATE_ADD(Current_Time, INTERVAL 2 DAY) WHERE deviceId = {} and holdPosition = 1".format(device_id))
			mydb.commit()
		
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()	
			
			flash("You have returned {}.".format (device_name[0]))

			mycursor.close()
			
## Borrowing an item that is not on hold
	if request.method == 'POST':
		if 'BorrowNow' in request.form:
			print("BorrowNow")
			mycursor = mydb.cursor()
			device_details_userid = devicedetails(user_id)
			mycursor = mydb.cursor()
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form

			device_id=DeviceDetails['BorrowNow']
			mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, borrowDate) Values ('{}', '{}', '{}')" .format(user_id, device_id, Current_Time))
			mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY) WHERE deviceID = {}".format(device_id,))
			mycursor.execute('UPDATE device SET deviceStatus = "Unavailable" WHERE deviceId = {}'.format(device_id,))
			mydb.commit()	
			
			
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()
			
			mycursor.close()
			flash("You have checked out device {}.".format (device_name[0]))


	## Use of buffered=True	to fetchone when you have an issue of fetching the data
	if request.method == 'POST':
		if 'HoldNow' in request.form:
			mycursor = mydb.cursor(buffered=True)
			device_details_userid = devicedetails(user_id)
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')

	##Capture the device id in the row of the hold now button
	#DeviceDetails here is a dictionary from the form. 
			DeviceDetails = request.form
			device_id=DeviceDetails['HoldNow']
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()		
			mycursor.execute("SELECT * from latesthold where deviceId ={} and userId={}".format(device_id,user_id))
			check_holding = mycursor.fetchall()
			
	
			
			if len(check_holding) != 0:
				flash('You have already held this item.')

			else: 	
				mycursor.execute("SELECT deviceStatus from device where deviceId={}".format(device_id,))
				deviceStatus = mycursor.fetchone()
				mycursor.execute("SELECT * from latesthold where deviceId = {}".format(device_id,))
				check_hold_queue = mycursor.fetchall()
				hold_position = len(check_hold_queue)+1
					

				if hold_position ==1:			
					mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Current_Time, hold_position))
					flash("You have placed a hold on {}. You are number {} in the queue.".format (device_name[0], hold_position))					

				elif hold_position ==2:
					mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Current_Time, hold_position))					
					flash("You have placed a hold on {}. You are number {} in the queue.".format (device_name[0], hold_position))					

				elif hold_position ==3:						
					mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Current_Time, hold_position))					
					flash("You have placed a hold on {}. You are number {} in the queue.".format (device_name[0], hold_position))					

				else:
					flash('Sorry you cannot put a hold on the device now. There have been 3 holds on the device. Please check again later!')
				mydb.commit()
				mycursor.close()

	## When the item on hold is now available to borrow: enabled only when you are first in queue
		
	if request.method == 'POST':
		if 'BorrowHold' in request.form:
			mycursor = mydb.cursor(buffered=True)
			device_details = alldevicedetails()	
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['BorrowHold']			
			mycursor.execute("SELECT holdPosition from latesthold where deviceId = {} and userId = {}".format(device_id, user_id))
			hold_position = mycursor.fetchone()			
			hold_position = hold_position[0]
			
			if hold_position ==1:
				
				mycursor = mydb.cursor(buffered=True)
				mycursor.execute("UPDATE checkingsystem SET borrowDate = '{}' where userId={} and deviceid={} and borrowDate is null".format(Current_Time,user_id,device_id))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY), holdPosition = null WHERE userId = {} and deviceid={} and borrowDate = '{}'".format(user_id,device_id,Current_Time))
				mycursor.execute ("UPDATE device set deviceStatus = 'Unavailable' where deviceid={}".format(device_id,))
				mycursor.execute("UPDATE checkingsystem SET holdPosition = 1 WHERE deviceid={} and holdPosition =2 and borrowDate is null".format(device_id,))
				mycursor.execute("UPDATE checkingsystem SET holdPosition = 2 WHERE deviceid={} and holdPosition =3 and borrowDate is null".format(device_id,))
				mydb.commit()		

			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()
			mycursor.close()
			flash("You have checked out device {}".format (device_name[0]))		

	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	
	## Query for holding item is available to borrow: 
	mycursor.execute('SELECT latesthold.userid, latesthold.deviceId, latesthold.holdPosition, device.deviceName, device.deviceStatus from latesthold, device where device.deviceid = latesthold.deviceid and latesthold.userid ={} and device.deviceStatus = "On Hold" and latesthold.holdPosition = 1'.format (user_id))
	hold_avai_borrow = mycursor.fetchall()
	item_hold_avai_borrow = len(hold_avai_borrow)
	## print(item_hold_avai_borrow)
	
	## Query for overdue items
	mycursor.execute('SELECT checkingsystem.deviceId, checkingsystem.dueDate, device.deviceName, checkingsystem.userId	FROM checkingsystem, device	where device.deviceId = checkingsystem.deviceId and checkingsystem.userId= {} and dueDate < NOW() and returnDate is NULL'.format (user_id))
	over_due = mycursor.fetchall()
	items_over_due = len(over_due)
	
	## Query for items due soon
	mycursor.execute('SELECT checkingsystem.deviceId, checkingsystem.dueDate, device.deviceName, checkingsystem.userId FROM checkingsystem, device where device.deviceId = checkingsystem.deviceId and checkingsystem.userId= {} and (dueDate > NOW() AND dueDate <= NOW() + interval 1 day and returnDate is NULL)'.format (user_id))
	due_soon = mycursor.fetchall()
	item_due_soon = len(due_soon)

	
	# can't just use function, need to pass the value to the variables in render_template
	loan_devices = loandevices(user_id)
	num_device = len(loan_devices)

	hold_devices = holddevices(user_id)
	num_hold_device = len(hold_devices)


	## List of Onhold status
	mycursor.execute('SELECT userid, deviceid FROM statusonhold')
	user_id_Onhold = mycursor.fetchall()
	
	
	## List of Anyhold status
	mycursor.execute('SELECT userid, deviceid, holdPosition, holdExpiry FROM latesthold')
	user_id_Anyhold = mycursor.fetchall()

	device_details = alldevicedetails()
	mycursor.close()

	return render_template('deviceborrowreturn.html', hold_avai_borrow = hold_avai_borrow, item_hold_avai_borrow=item_hold_avai_borrow, over_due=over_due, items_over_due=items_over_due, item_due_soon=item_due_soon, due_soon=due_soon, userid=user_id,loan_devices=loan_devices, device_details=device_details, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices, user_id_Onhold=user_id_Onhold, user_id_Anyhold=user_id_Anyhold)



	
@app.route('/', methods =['GET', 'POST'])
@app.route('/device-borrow-return', methods =['GET', 'POST'])
def borrowreturn():
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM users")
	users = mycursor.fetchall()
	device_details= alldevicedetails()	
	if request.method == 'POST':
		userDetails = request.form
		user_id = userDetails['userid']
		mycursor = mydb.cursor()
		mycursor.execute("select * from users")
		user_details = mycursor.fetchall()
		print(user_id)	

		#user_id = request.args.get("user_id")
		device_details = alldevicedetails()
		mycursor.close()
		return redirect('/device-borrow-return/{}'.format(user_id))
	return render_template('deviceborrowreturn.html', device_details=device_details, users=users, usertrue=True)	   

## used <int:userid> could have used args
@app.route('/myview/<int:userid>', methods =['GET', 'POST'])
def myview(userid):
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
				mycursor.execute("UPDATE device SET deviceStatus = 'Available' WHERE deviceId = {}".format(device_id))
			else:
				mycursor.execute("UPDATE device SET deviceStatus = 'On Hold' WHERE deviceId = {}".format(device_id))
				#update the holdExpiry for first hold in the queue
				mycursor.execute("UPDATE checkingsystem SET holdExpiry = DATE_ADD(Current_Time, INTERVAL 2 DAY) WHERE deviceId = {} and holdPosition = 1".format(device_id))
			mydb.commit()
			mycursor.close()
			mycursor = mydb.cursor()
			mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()	
			mycursor.close()
			flash("You have returned {}".format (device_name[0]))
			mycursor.close()

	
	if request.method == 'POST':
		if 'BorrowHold' in request.form:

			print(user_id)
			mycursor = mydb.cursor(buffered=True)
			device_details = alldevicedetails()			

			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['BorrowHold']		
			mycursor.execute("SELECT holdPosition from latesthold where deviceId = {} and userId = {}".format(device_id, user_id))
			hold_position = mycursor.fetchone()
			hold_position = hold_position[0]
			
			#this function is only called when hold_position = 1, otherwise it is disabled so no other case.
			if hold_position ==1:		
				mycursor = mydb.cursor(buffered=True)
				mycursor.execute("UPDATE checkingsystem SET borrowDate = '{}' where userId={} and deviceid={} and borrowDate is null".format(Current_Time,user_id,device_id))
				mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 3 DAY), holdPosition = null WHERE userId = {} and deviceid={} and borrowDate = '{}'".format(user_id,device_id,Current_Time))
				mycursor.execute ("UPDATE device set deviceStatus = 'Unavailable' where deviceid={}".format(device_id,))
				mycursor.execute("UPDATE checkingsystem SET holdPosition = 1 WHERE deviceid={} and holdPosition =2 and borrowDate is null".format(device_id,))
				mycursor.execute("UPDATE checkingsystem SET holdPosition = 2 WHERE deviceid={} and holdPosition =3 and borrowDate is null".format(device_id,))			
				mydb.commit()				
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()
			mycursor.close()
			flash("You have checked out device {}".format (device_name[0]))		
			


#if request.method == 'GET':
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute('select users.userId, users.firstName, users.lastName, users.email, users.locationid, building.buildingAddress from users inner join building on users.locationid = building.locationid where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	
	## Query for holding item is available to borrow: 
	mycursor.execute('SELECT latesthold.userid, latesthold.deviceId, latesthold.holdPosition, device.deviceName, device.deviceStatus from latesthold, device where device.deviceid = latesthold.deviceid and latesthold.userid ={} and device.deviceStatus = "On Hold" and latesthold.holdPosition = 1'.format (user_id))
	hold_avai_borrow = mycursor.fetchall()
	item_hold_avai_borrow = len(hold_avai_borrow)
	hold_avai_borrow_list=[]
	
	for item in hold_avai_borrow:
		hold_avai_borrow_list.append(item[1])
		
	## Query for overdue items
	mycursor.execute('SELECT checkingsystem.deviceId, checkingsystem.dueDate, device.deviceName, checkingsystem.userId	FROM checkingsystem, device	where device.deviceId = checkingsystem.deviceId and checkingsystem.userId= {} and dueDate < NOW() and returnDate is NULL'.format (user_id))
	over_due = mycursor.fetchall()
	items_over_due = len(over_due)
	over_due_list=[]
	for item in over_due:
		over_due_list.append(item[0])
	#print(due_soon_list)	
	
	## Query for items due soon
	mycursor.execute('SELECT checkingsystem.deviceId, checkingsystem.dueDate, device.deviceName, checkingsystem.userId FROM checkingsystem, device where device.deviceId = checkingsystem.deviceId and checkingsystem.userId= {} and (dueDate > NOW() AND dueDate <= NOW() + interval 1 day and returnDate is NULL)'.format (user_id))
	due_soon = mycursor.fetchall()
	item_due_soon = len(due_soon)
	#print(due_soon)
	due_soon_list=[]
	for item in due_soon:
		due_soon_list.append(item[0])
	#print(due_soon_list)	
	
	
	# can't just use function, need to pass the value to the variables in render_template
	loan_devices = loandevices(user_id)
	num_device = len(loan_devices)

	hold_devices = holddevices(user_id)
	num_hold_device = len(hold_devices)
	# print(num_hold_device)
				
	return render_template('myview.html', item_due_soon=item_due_soon, due_soon=due_soon, items_over_due=items_over_due, over_due=over_due, item_hold_avai_borrow=item_hold_avai_borrow, hold_avai_borrow=hold_avai_borrow, over_due_list=over_due_list, hold_avai_borrow_list=hold_avai_borrow_list, due_soon_list=due_soon_list, userid=user_id,loan_devices=loan_devices, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

@app.route('/users/')  
def users():
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM users")
	users = mycursor.fetchall()
	mycursor.close()
	return render_template('users.html', title='Users', menu='users', users=users)

	return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)
		   

@app.route('/admin-devices/<int:userid>', methods =['GET']) 
def admindevices(userid):
	user_id = userid	
	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	device_details = alldevicedetails()
	mycursor.close()
	return render_template('admindevices.html', user_id=user_id, device_details=device_details, user_details = user_details)


@app.route('/admin-devices/<int:userid>/update/<int:deviceid>', methods =['GET', 'POST']) 
def updatedevice(userid,deviceid):
	if request.method == 'POST':	
		DeviceDetails = request.form
		device_id = DeviceDetails['deviceid']
		device_name = DeviceDetails['devicename']
		device_type = DeviceDetails['devicetype']
		os_type = DeviceDetails['ostype']
		os_version = DeviceDetails['osversion']
		device_ram = DeviceDetails['deviceram']
		device_cpu = DeviceDetails['devicecpu']
		device_bit = DeviceDetails['devicebit']
		screen_res = DeviceDetails['screenres']
		device_grade = DeviceDetails['devicegrade']
		device_uuid = DeviceDetails['deviceuuid']
		mycursor = mydb.cursor()
		mycursor.execute("Update device SET deviceName = '{}' , deviceType = '{}', osType = '{}', osVersion = '{}', deviceRam='{}', deviceCpu='{}', deviceBit='{}', screenRes='{}', deviceGrade='{}', deviceUuid='{}' where deviceId = '{}' ".format(device_name,device_type,os_type,os_version,device_ram,device_cpu,device_bit,screen_res,device_grade,device_uuid,device_id))
		mydb.commit()
		
		flash("You have successfully updated device {}.".format (device_name))
	
	user_id = userid
	device_id = deviceid
	mycursor = mydb.cursor()
	mycursor.execute('select * from device where deviceId ={}'.format(device_id))
	device_details =  mycursor.fetchall()	
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()		
	mycursor.close()	
	return render_template('deviceupdate.html', user_id=user_id, device_details=device_details, user_details = user_details)

@app.route('/admin-devices/<int:userid>/add-new/', methods =['GET', 'POST']) 
def adddevice(userid):		
	if request.method == 'POST':	
		DeviceDetails = request.form
		device_id = DeviceDetails['deviceid']
		device_name = DeviceDetails['devicename']
		device_type = DeviceDetails['devicetype']
		os_type = DeviceDetails['ostype']
		os_version = DeviceDetails['osversion']
		device_ram = DeviceDetails['deviceram']
		device_cpu = DeviceDetails['devicecpu']
		device_bit = DeviceDetails['devicebit']
		screen_res = DeviceDetails['screenres']
		device_grade = DeviceDetails['devicegrade']
		device_uuid = DeviceDetails['deviceuuid']
		status = 'Available'
		mycursor = mydb.cursor()
		mycursor.execute("INSERT INTO device (deviceId,deviceName, deviceType, osType, osVersion, deviceRam, deviceCpu, deviceBit, screenRes, deviceGrade, deviceUuid, deviceStatus) Values ('{}', '{}', '{}','{}', '{}','{}', '{}','{}', '{}','{}', '{}','{}')" .format(device_id,device_name,device_type,os_type,os_version,device_ram,device_cpu,device_bit,screen_res,device_grade,device_uuid, status))
		mydb.commit()
		
		flash("You have successfully added a new device {}.".format (device_name))
	user_id = userid
	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()	
	mycursor.close()
	return render_template('deviceadd.html', user_id=user_id, user_details = user_details)

	
if (__name__) == ('__main__'):
	app.run(debug=True)


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
  passwd="password",
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
	#mycursor.execute("SELECT * FROM devicedetails where devicedetails.userid <> %s or devicedetails.userid is null", (user_id,))
	mycursor.execute("SELECT * FROM devicedetails where devicedetails.userid is null or devicedetails.userid <> %s AND devicedetails.deviceid NOT IN (select latesthold.deviceid from latesthold where latesthold.userid = %s)", (user_id, userid,))

	#needed to redefine the query because it still contains holding item of the user - resolved
	#this was because of the left joins in the view which didn't allow for one device to be attached to two users.
	
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
	
@app.route('/device-borrow-return/<int:userid>', methods =['GET', 'POST'])
def deviceborrowreturn(userid):
		#if request.method == 'GET':
	user_id = userid

	mycursor = mydb.cursor()
	mycursor.execute('select * from users where UserId ={}'.format(user_id))
	user_details = mycursor.fetchall()
	
	## Query for holding item is available to borrow: 
	mycursor.execute('SELECT latesthold.userid, latesthold.deviceId, latesthold.holdPosition, device.deviceName, device.deviceStatus from latesthold, device where device.deviceid = latesthold.deviceid and latesthold.userid ={} and device.deviceStatus = "On Hold" and latesthold.holdPosition = 1'.format (user_id))
	hold_avai_borrow = mycursor.fetchall()
	item_hold_avai_borrow = len(hold_avai_borrow)
	print(item_hold_avai_borrow)
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
	# print(user_id_OnholdTuple)
	# user_id_Onhold=[]
	# for eachID in user_id_OnholdTuple:
		# user_id_Onhold.append(eachID[0])
	print(user_id_Onhold)
	
	## List of Anyhold status
	mycursor.execute('SELECT userid, deviceid, holdPosition, holdExpiry FROM latesthold')
	user_id_Anyhold = mycursor.fetchall()
	# print(user_id_AnyholdTuple)
	# user_id_Anyhold=[]
	# for eachID in user_id_AnyholdTuple:
		# user_id_Anyhold.append(eachID[0])
	print(user_id_Anyhold)
	print(user_id)

	device_details = alldevicedetails()
	mycursor.close()

## when an item is returned check whether there is a hold and update status accordingly	
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

			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices, user_id_Onhold=user_id_Onhold, user_id_Anyhold=user_id_Anyhold)
		
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
			mycursor.execute("UPDATE checkingsystem SET dueDate = DATE_ADD(NOW(), INTERVAL 5 DAY) WHERE deviceID = {}".format(device_id,))
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
			flash("You have checked out device {}".format (device_name[0]))

			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices, borrow_device=True, user_id_Onhold=user_id_Onhold, user_id_Anyhold=user_id_Anyhold)

		
	if request.method == 'POST':
		if 'HoldNow' in request.form:
			#This function should be modified based new user story, holdExpiry will only be updated once the device is returned
			mycursor = mydb.cursor(buffered=True)
			device_details_userid = devicedetails(user_id)
			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['HoldNow']
			mycursor.execute("select deviceName from device where deviceId = {}".format(device_id))
			device_name = mycursor.fetchone()

			
			mycursor.execute("SELECT * from latesthold where deviceId ={} and userId={}".format(device_id,user_id))
			check_holding = mycursor.fetchall()
			
			print ('beforeif')
			
			if len(check_holding) != 0:
				flash('You have already held this item.')

			else: 	
				mycursor.execute("SELECT deviceStatus from device where deviceId={}".format(device_id,))
				deviceStatus = mycursor.fetchone()
				print (deviceStatus)
				mycursor.execute("SELECT * from latesthold where deviceId = {}".format(device_id,))
				check_hold_queue = mycursor.fetchall()
				hold_position = len(check_hold_queue)+1
				print(hold_position)
				

				
				if deviceStatus[0] == "Unavailable":				
					print ('afterif')
					mycursor.execute("SELECT dueDate from latestborrow where deviceId={} and borrowDate is not null".format(device_id,))					
					Due_Date=mycursor.fetchone()	
					
					Due_Date=Due_Date[0]				
							
					#insert a holding record in checking system
					
					if hold_position ==1:			
						mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Due_Date, hold_position))
						flash("You have placed a hold on {}. You are number {} in the queue".format (device_name[0], hold_position))					

					elif hold_position ==2:	
						Due_Date = Due_Date + timedelta(days=5)
						mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Due_Date, hold_position))					
						flash("You have placed a hold on {}. You are number {} in the queue".format (device_name[0], hold_position))					

					elif hold_position ==3:	
						Due_Date = Due_Date + timedelta(days=10)				
						mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Due_Date, hold_position))					
						flash("You have placed a hold on {}. You are number {} in the queue".format (device_name[0], hold_position))					

					
					else:
						flash('Sorry you cannot put a hold on the device now. There have been 3 holds on the device. Please check again later!')
					

					mydb.commit()
					mycursor.close()					
				
				else:
					mycursor.execute("SELECT holdExpiry from latesthold where deviceId={}".format(device_id,))					
					Hold_Date=mycursor.fetchone()	
					
					Hold_Date=Hold_Date[0]
					#print (Hold_Date)				
							
				
					#insert a holding record in checking system
					
					if hold_position ==2:			
						mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Hold_Date, hold_position))

					elif hold_position ==3:	
						Hold_Date = Hold_Date+ timedelta(days=5)
						mycursor.execute("INSERT INTO checkingsystem (userId, deviceId, holdDate,holdPosition) Values ('{}', '{}', '{}', '{}')" .format(user_id, device_id, Hold_Date, hold_position))					
					
						flash("You have place a hold on {}".format (device_name[0]))
					
					else:
						flash('Sorry you cannot put a hold on the device now. There have been 3 holds on the device. Please check again later!')
					
					mydb.commit()
					mycursor.close()
			
			mycursor = mydb.cursor()
			loan_devices = loandevices(user_id)
			num_device = len(loan_devices)
			hold_devices = holddevices(user_id)
			num_hold_device = len(hold_devices)
			device_details_userid = devicedetails(user_id)

			mycursor.close()	

			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices, user_id_Onhold=user_id_Onhold, user_id_Anyhold=user_id_Anyhold)	
		
		
	if request.method == 'POST':
		if 'BorrowHold' in request.form:

			print(user_id)
			mycursor = mydb.cursor(buffered=True)
			device_details = alldevicedetails()			

			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['BorrowHold']
			#mycursor.execute("Select deviceStatus from devicedetails where deviceId = {}".format(device_id,))
			#device_Status = mycursor.fetchone()
			#print(device_Status)
			#if device_status == 'Available': no need to check because the device status will always "On hold" if we go with deleting Hold expired
			
			mycursor.execute("SELECT holdPosition from latesthold where deviceId = {} and userId = {}".format(device_id, user_id))
			hold_position = mycursor.fetchone()
			
			hold_position = hold_position[0]
			
			print(hold_position)
			
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

			return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices, user_id_Onhold=user_id_Onhold, user_id_Anyhold=user_id_Anyhold)
		

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

@app.route('/myview/<int:userid>', methods =['GET', 'POST'])
def myview(userid):
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
		hold_avai_borrow_list.append(item[0])
		
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

			return render_template('myview.html', userid=user_id, loan_devices=loan_devices, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)
	
		
	if request.method == 'POST':
		if 'BorrowHold' in request.form:

			print(user_id)
			mycursor = mydb.cursor(buffered=True)
			device_details = alldevicedetails()			

			Current_Time = datetime.now()
			Current_Time = Current_Time.strftime('%Y-%m-%d %H:%M:%S')
			DeviceDetails = request.form
			device_id=DeviceDetails['BorrowHold']
			#mycursor.execute("Select deviceStatus from devicedetails where deviceId = {}".format(device_id,))
			#device_Status = mycursor.fetchone()
			#print(device_Status)
			#if device_status == 'Available': no need to check because the device status will always "On hold" if we go with deleting Hold expired
			
			mycursor.execute("SELECT holdPosition from latesthold where deviceId = {} and userId = {}".format(device_id, user_id))
			hold_position = mycursor.fetchone()
			
			hold_position = hold_position[0]
			
			print(hold_position)
			
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
			return render_template('myview.html', userid=user_id, loan_devices=loan_devices, num_device=num_device,user_details=user_details, num_hold_device=num_hold_device,hold_devices=hold_devices)
				
	return render_template('myview.html',over_due_list=over_due_list, hold_avai_borrow_list=hold_avai_borrow_list, due_soon_list=due_soon_list, userid=user_id,loan_devices=loan_devices, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)


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
		# return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details_userid=device_details_userid, num_device=num_device,user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)

	return render_template('users.html', title='Users', menu='users', users=users)

	return render_template('deviceborrowreturn.html', userid=user_id, loan_devices=loan_devices, device_details=device_details, num_device=num_device, user_details=user_details,num_hold_device=num_hold_device,hold_devices=hold_devices)
		   
	
if (__name__) == ('__main__'):
	app.run(debug=True)


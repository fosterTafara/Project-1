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

@app.route('/device-list')
def devicelist():
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM device")
        device_details = mycursor.fetchall()
        return render_template('devicelist.html', device_details = device_details)



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
	

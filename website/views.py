from flask import Blueprint, render_template, session, redirect, url_for
import boto3

# Rekognition instance
rekognition = boto3.client('rekognition')
# S3 bucket instance 
s3 = boto3.client('s3')
#dynamoDB instance
dynamodb = boto3.client('dynamodb')

#Defining routes
views = Blueprint('views', __name__)

#Render login
@views.route('/')
def renderLogin():
    return render_template("login.html")

#Render the index.html file 
@views.route('/home')
def renderHome():
    return render_template("index.html")


#Render student registration html page 
@views.route('/add/student')
def renderStudent():
    return render_template("addStudent.html")

# Render video upload html page
@views.route('/upload')
def renderVideo():
    return render_template("videoUpload.html")

# Render student deletion page
@views.route('/delete')
def renderDelete():
    return render_template("deleteStudents.html")
    
# Render attendance log html page
@views.route('/attendance/log')
def renderAttendanceLog():
    return render_template("attendanceLog.html")

# Render students list html page
@views.route('/student/list')
def renderStudentList():
    return render_template("studentsList.html")

##################################Functions####################################

#Function to allow admin to login
@views.route('/login_admin', methods=['POST'])
def login():
    return render_template('login.html')


#Function that handles adding students to face collection 
@views.route('/register_students', methods=['GET', 'POST'])
def register():
    return render_template("addStudent.html")


#Function to upload video to S3 bucket 
@views.route('/upload_video', methods=['POST'])
def upload_video():
    return render_template("videoUpload.html")


# Delete a student
@views.route('/delete_student', methods=['GET', 'POST'])
def remove():
    return render_template("deleteStudents.html")


# Logout 
@views.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('email', None)
   return redirect(url_for('views.renderLogin'))
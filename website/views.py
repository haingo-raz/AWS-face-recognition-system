from flask import Blueprint, render_template, request, session, flash, redirect, url_for
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
    if 'email' in session:
        return render_template("index.html")
    return redirect(url_for('views.renderLogin'))


#Render student registration html page 
@views.route('/add/student')
def renderStudent():
    if 'email' in session:
        return render_template("addStudent.html")
    return redirect(url_for('views.renderLogin'))

# Render video upload html page
@views.route('/upload')
def renderVideo():
    if 'email' in session:
        return render_template("videoUpload.html")
    return redirect(url_for('views.renderLogin'))

# Render student deletion page
@views.route('/delete')
def renderDelete():
    if 'email' in session:
        return render_template("deleteStudents.html")
    return redirect(url_for('views.renderLogin'))
    
# Render attendance log html page
@views.route('/attendance/log')
def renderAttendanceLog():
    if 'email' in session:
        return render_template("attendanceLog.html")
    return redirect(url_for('views.renderLogin'))
    
# Render students list html page
@views.route('/student/list')
def renderStudentList():
    if 'email' in session:
        return render_template("studentsList.html")
    return redirect(url_for('views.renderLogin'))

##################################Functions####################################

#Function to allow admin to login
@views.route('/login_admin', methods=['POST'])
def login():
# Get the email and password from the login form
    email = request.form['email'].lower() # put all the letters in small case
    password = request.form['password']

    adminTable = "admin" # DynamoDB table 

    # Check if the email and password match a record in the DynamoDB table
    try:
        response = dynamodb.get_item(
            TableName= adminTable,
            Key={
                'email': {'S': email}
            }
        )

        # If the email exists and the password matches, redirect to the home page
        if 'Item' in response:
            item = response['Item']
            if 'password' in item and item['password']['S'] == password:
                # Save email in session
                session['email'] = request.form['email']
                # flash("Successfully logged in!")
                return render_template('index.html')

    except Exception as e:
        print(e)

    # If the email or password is incorrect, display an error message
    message = 'Incorrect email or password'
    return render_template('login.html', message=message)


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
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
import boto3

# Rekognition instance
rekognition = boto3.client('rekognition')
# S3 bucket instance 
s3 = boto3.client('s3')
#dynamoDB instance
dynamodb = boto3.client('dynamodb')

# AWS Services global variables 
students_bucket = "studentsdetails" # Where images are uploaded
students_table = "students" # Where students' details are stored 
collection_id = 'studentsInfo' # specify aws rekognition face collection 
video_bucket = "recordedvideo"

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

        # Access all the items of the students dynamoDB table
        response = dynamodb.scan(TableName=students_table)
        items = response['Items']

        # Put the results in an array
        rows = []
        for item in items:
            row = {}
            for key, val in item.items():
                row[key] = val['S'] if 'S' in val else val['N']
            rows.append(row)

        return render_template("addStudent.html", rows=rows)
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
        # Get the items in the collection
        collection_id = 'studentsInfo' #specific face collection for students here

        # List the faces in the collection
        faces = []
        response = rekognition.list_faces(CollectionId=collection_id)

        for face in response['Faces']:
            face_id = face['FaceId']
            external_id = face['ExternalImageId']

            faces.append({
                'face_id': face_id,
                'external_id': external_id
            })

        return render_template("deleteStudents.html", faces=faces)
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

        # Access all the items of the students dynamoDB table
        response = dynamodb.scan(TableName=students_table)
        items = response['Items']

        # Put the results in an array
        rows = []
        for item in items:
            row = {}
            for key, val in item.items():
                row[key] = val['S'] if 'S' in val else val['N']
            rows.append(row)

        return render_template("studentsList.html", rows=rows)
    return redirect(url_for('views.renderLogin'))

@views.route('/collection')
def renderCollection():
    if 'email' in session:

        # Get the face collection ID
        collection_id = 'studentsInfo' #specific face collection for students here

        # List the faces in the collection
        faces = []
        response = rekognition.list_faces(CollectionId=collection_id)
        for face in response['Faces']:
            face_id = face['FaceId']
            external_id = face['ExternalImageId']
            faces.append({
                'face_id': face_id,
                'external_id': external_id
            })

        return render_template("collections.html", faces=faces)
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
    collection_id = 'studentsInfo' # add new student to the studentsInfo face collection
    name = str(request.form['name']) #student name will be set to external image id
    name = name.strip() # remove space before or after the string to avoid error
    name = name.replace(" ", "_") ##Remove space in between the first and last name to avoid ExternalID face collection error
    student_id = str(request.form['id'])
    photo_file = request.files['photo']

    # Check if the entered student id is already in the system database 
    results = dynamodb.scan(
        TableName= students_table,
        ProjectionExpression="student_id"
    )

    ids = [item["student_id"] for item in results["Items"]]
    # Extract the values from the dictionary which is the default format from dynamoDB responses
    id_values = [id_dict['S'] for id_dict in ids]

    if student_id in id_values: 
        flash('The id ' + student_id + ' is already registered in the database')

    else: 
        # Upload image to S3 bucket to get public link 
        s3.upload_fileobj(photo_file, students_bucket, photo_file.filename)

        image_s3_url = "https://"+ students_bucket +".s3.amazonaws.com/"+ photo_file.filename
        
        #Index the uploaded image
        response = rekognition.index_faces(
            CollectionId=collection_id, 
            Image={
                'S3Object': {
                    'Bucket': students_bucket,
                    'Name': photo_file.filename
                }
            }, 
            ExternalImageId=name, 
            QualityFilter='AUTO', 
            DetectionAttributes=['ALL']
        )

        face_record = response['FaceRecords']

        # Send feedback to the client side 
        if len(face_record) == 0:
            flash("No faces found")    
        else:
            flash("Successfully registered student")

        #Save to dynamoDB table, which will be pulled to frontend
        dynamodb.put_item(
            TableName='students', 
            Item={
                'student_name': {"S": name.replace("_", " ")}, #Replace _ with space
                'student_id': {"S": student_id},
                'image_url': {"S": image_s3_url}
            }
        )

    return render_template("addStudent.html")


#Function to upload video to S3 bucket 
@views.route('/upload_video', methods=['POST'])
def upload_video():
    file = request.files.get('video')
    filename = file.filename

    #upload the video to the recordedvideo S3 bucket
    if file: 
        s3.upload_fileobj(file, video_bucket, filename)
        flash('Video uploaded successfully! Please wait for a couple of minutes before the attendance log can be generated')
    else:
       flash('Please choose a video file to upload.')# if no file input provided

    return render_template("videoUpload.html")


# Delete a student
@views.route('/delete_student', methods=['GET', 'POST'])
def remove():
    
    student_name = request.form['studentname'] # studentname will be set to external image id
    face_id = str(request.form['face_id']) # Get the studentID 
    
    face_list = []

    face_list.append(face_id)
    
    # Delete face from face collection 
    response = rekognition.delete_faces(
        CollectionId = collection_id,
        FaceIds = face_list
    )

    # Query the student id of the provided name to be able to delete dynamoDB item with both partition and sort key
    response = dynamodb.query(
        TableName=students_table,
        KeyConditionExpression='student_name = :name',
        ExpressionAttributeValues={
            ':name': {'S': student_name}
        },
    )

    id_value = response['Items'][0]['student_id']['S']

    # Delete student from the dynamoDB based on external id given 
    dynamodb.delete_item(
        TableName=students_table, 
        Key={
            'student_name': {'S': student_name}, # delete by name
            'student_id': {'S': id_value} # delete by id 
        }
    )

    flash(student_name + " was successfully deleted from the database")

    return render_template("deleteStudents.html")

# Logout 
@views.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('email', None)
   return redirect(url_for('views.renderLogin'))
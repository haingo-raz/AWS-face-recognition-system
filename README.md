## Table of Contents

## About 

This project is a face recognition based attendance system that works with stored/recorded video. It is mostly recommended in a class setting, but it can be used in other places such as an office or a social event. Upon a video upload, the attendance operation will be triggered and the attendance log will be displayed on the front end of the website. Students can be registered in and deleted from the system.

## Aim
- This research aims to improve conventional attendance systems at Universities using recent technology.

## Technology/Services
- Python Flask
- boto3
- Werkzeug
- time
- datetime
- pytz
- requests
- SCSS 
- Javascript

| AWS Service | Functionality| Usage in the project|
|-------------|--------------|
|AWS Rekognition |Video analysis|analyze the faces in the uploaded videos|
|AWS DynamoDB|NoSQL Database| Used to store login details, student details and attendance results|
|AWS Lambda|Functions called in response to other AWS events| Manage the face recognition operation|
|AWS CloudWatch|Monitors AWS| Used to check the logs of performed AWS operations|
|AWS S3 |Storage service | Used to store uploaded pictures of registered students

## Functionalities

### Login and log out
Only users with provided credentials can log in the system.

![login](https://github.com/haingo-raz/face-recognition-based-attendance-system/blob/main/website/static/assets/login.png)

### Registering a student 
To register a student, the registration form takes their full name, studentID and photo.

![registration](https://github.com/haingo-raz/face-recognition-based-attendance-system/blob/main/website/static/assets/registration.png)

### Removing a student from the system 
The name of the student to be deleted will be required prior removal.

![removal](https://github.com/haingo-raz/face-recognition-based-attendance-system/blob/main/website/static/assets/removal.png)

### Uploading a video to perform attendance
Users will be able to upload a video from their local machine to perform attendance on.

![upload](https://github.com/haingo-raz/face-recognition-based-attendance-system/blob/main/website/static/assets/upload.png)

### Displaying list of students
The list of students registered in the system will be displayed in the website.

![students](https://github.com/haingo-raz/face-recognition-based-attendance-system/blob/main/website/static/assets/students.png)

### Displaying attendance log
The history of the performed attendance will be diplayed on the front end of the website.

![attendance](https://github.com/haingo-raz/face-recognition-based-attendance-system/blob/main/website/static/assets/attendance.png)

# How does each functionality work technically?

## Detailed usage of AWS
| Service | Function | What does it do? |
|---------|----------|------------------|
|DynamoDB| get_item| Returns a set of attributes for the item with the given primary key|
|DynamoDB|scan|Returns one or more items and item attributes by accessing every item in a table or a secondary index|
|DynamoDB|put_item|Creates a new item, or replaces an old item with a new item|
|DynamoDB|query| Returns all of the items from the table or index with that partition key value.|
|S3|upload_fileobj|Uploads a file-like object to S3|
|Rekognition|delete_faces|Deleted faces from a collection|
|Rekognition|list_faces|Lists all the faces in a collection|
|Rekognition|start_face_search| Start searching for faces in a stored video|
|Rekognition|get_face_search| Get the face search results|

## Login and log out
Only users with provided credentials can log in the system. A dynamoDB table holds all the email address that are allowed in the system. To log in, a user has to enter a matching email and password from that dynamoDB table. First of all, we use the dynamoDB function get_item with parameters from the login form. If the dynamoDB response has an Item in its response, that means the email address has been found in the dynamoDB table. Then the entered password is also compared to the password within the dynamoDB response. If the password matches, the user can successfully log in. Otherwise, an error message will be shown on the frontend end, and the user won't be able to log in.

## Registering a student 
To register a student, the form takes their full name, studentID and photo. 
- First of all, the provided student ID is checked against all the students id that are found in the students dynamoDB table. If it is a duplicate, the registration will not take place. To get all the students ID from the database, we use the dynamoDB scan function with ProjectionExpression the attribute 'student_id'. Then all those ids are saved in an array and the entered id from the form will be searched in that array. If it is found, then a student with that ID cannot be created. 
- If there are no issues with the student ID, the provided student picture will be uploaded to an S3 object using s3 'upload_fileobj' function to get a public link (deploying the student image). Then that image will be indexed using the Rekognition 'index_faces' function. To index the face, the external id is set the name of students with spaces replaced with a _ as the external image id does not support a space. 
- Then the student name, their ID and the public URL of the image uploded in S3 will be stored in a students dynamoDB table. The dynamoDB table 'put_item' function has been used to add an item to an existing dynamoDB table. 

## Removing a student from the system 
When deleting a student, both their details in the amazon Rekognition face collection and their record in the students dynamoDB table are deleted. However, their images from the S3 object are not deleted. 
Their face are deleted from the face rekognition face collection with the help of the 'delete_faces' function providing the collectionId they are in and the face id. 
It is worth noting that the form to delete students only has their name in a select dropdown input. To delete a record in the students dynamoDB table, both partition key and sort key of the record to be deleted need to be provided. In this case, those are student_name and student_id. The student name is received from the deletion form. However, the student_id with the corresponding name from the form need to be queried using the dynamoDB 'query' function. The student_id input is hidden on the frontend, but sent to the server as soon as an app user clicks on the remove student button.

## Uploading a video and the attendance operation itself
Uploading a video is fairly simple. Just request the video file received from the form on the frontend then upload to an S3 object using the s3 upload_fileobj function. 

## How does the face recognition operation work? 
- The current date of the attendance is given by the datetime and timezone (pytz) package.
- The lambda function is triggered by video upload to the recordedvideo S3 bucket. The lambda events receive the bucket name and the name of the video uploaded. 
- The built in functions rekognition start_face_search and get_face_search allow to find faces within the stored video and compare them with the amazon rekognition face collection we have already created before all the operations. 
- We have collected all the registered students' face id in array named faceIds and all their names in an array named studentNames. Those will be useful to distinguish students who were present from students who were absent. As a matter of fact, the rekognition function only dress a list of which students from the face collection were found in the video, not who were absent. So that needs a little if and else..
- The response from the get_face_search returns details about the individuals who were identified in the video. Those results include their FaceId and their ExternalImageId. To get the name of the students who were present, we just need to replace the _ in the externalID with a space. Once the name of the student is received, their id can be queried from the students dynamoDB table using the query function. 
- Now do some conditions, if the externalId of the student found from face search is inside the list of array of all the students we have created earlier, set their status as present and add their record to the database (id, date, name, status = present). Then everytime a student is marked present, remove their ExternalImageID and their faceId from both the studentNames and faceIds array. Logically, the studentNames array contains all the externalImageIds of all registered students and the FaceIds of all the registered students. But once, you delete all the students that were detected in the video from that array, the rest of the undetected students = absent students would be left in the studentNames and faceIds array which would make the attendance more manageable. 
- Now after all the present students' details were removed from both studentNames and faceIds array, we are looping through all the faceId in the faceIds and we set the attendance status to absent. We can get the names of the absent students from the studentNames array without forgetting to replace the _ with a blank space. The student_id of the absent students can be queried with the help of their names using dynamoDB query function. Then we put the record in the database (student_id, date, student_name, status = absent).

## Getting the students list
- To display a list of students on the client side of the application, scan the dynamoDB students database using dynamoDB scan function. Put the results in a row and then send it to the frontend application by sending it in the return line. 
- To get and display the faces in the face collection, use rekognition 'list_faces' built in function. Get all the FaceIds and ExtenalImageIds from the response and put them in an array, send this array to the frontend by using the return statement. 

## Getting the attendance log
Getting the attendance log is also as simple as scanning the dynamoDB table that holds the attendance results.

# Challenges and successes

- Making use of layers in order to use external Python libraries in the cloud. Public library ARNs were taken from [this github repository](https://github.com/keithrozario/Klayers) 
- Uploading an image to S3 and indexing the same image could not be done concurrenlty. At first the images were directly indexed locally? However, they were uploaded to an S3 bucket before being indexed. In fact, uploading to S3 is asynchronous. 
- Avoiding naming table attributes with reserved keywords such as name 
- Avoiding mistyping parameters when for instance calling dynamoDB operations 
- Linking students' data with both dynamoDB and S3 and rekognition. S3 is good for image upload and retrieval and dynamoDB to store texts. 

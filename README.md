## Table of Contents

## About 

This project is a face recognition based attendance system that works with stored/recorded video. It is mostly recommended in a class setting, but it can be used in other places such as an office or a simple event. Upon a video upload, the attendance operation will be triggered and the attendance log will be displayed on the front end of the website. A list of registered individuals is also displayed on the website. Furthermore, a person can be removed from the list.

## Benefits
- Timesaving in a big classroom. For instance +70 students. 

## Technology/Services

- Python 
- SCSS 
- Javascript
- AWS S3 
- AWS Rekognition 
- AWS DynamoDB
- AWS Lambda
- AWS CloudWatch


## Python package required 
- Flask 
- boto3
- Werkzeug
- requests

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





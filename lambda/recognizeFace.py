import boto3
import time
from datetime import datetime
from pytz import timezone

# This function is stored to the cloud on AWS lambda, it is triggered on video upload to S3

#Time UTC+4 when attendance was taken
format = "%Y-%m-%d %H:%M:%S"
now_utc = datetime.now(timezone('UTC'))
dateTime = now_utc.astimezone(timezone('Asia/Dubai'))
attendance_dateTime = dateTime.strftime(format)

# S3 instance
s3 = boto3.client('s3')
# Rekognition instance
rekognition = boto3.client('rekognition')
# DynamoDB instance 
dynamodb = boto3.client('dynamodb')

# AWS services global variables
collectionName = 'studentsInfo' # collection name where all students are registered 
students_table = "students" # Holds students'details
attendance_table = "attendancetable"


def lambda_handler(event, context):
    
    # Get bucket and key of the S3 object that triggered the Lambda function
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    
    print(f"Processing video: s3://{bucket}/{key}")
    
    # Start face detection job
    response = rekognition.start_face_search(
        Video={
            'S3Object':{
                'Bucket':bucket,
                'Name':key
            }
        },
        CollectionId=collectionName
    )
    
    # Get job id from start_face_search operation
    job_id = response['JobId']

    print(f"Started face search job with job id: {job_id} within {collectionName}")

    maxResults = 30 #this will be the number of students within a video 
    paginationToken = ''

    
    # Wait for face search job to complete
    while True:
        response = rekognition.get_face_search(
            JobId=job_id,
            MaxResults=maxResults,
            NextToken=paginationToken
        )
        status = response['JobStatus']
        
        if status == 'IN_PROGRESS':
            print('...')
            time.sleep(5)
        if status == 'SUCCEEDED':
            break
        elif status == 'FAILED':
            raise Exception('Face detection failed')
        

    faceIds = [] # Hold faceIds of all students
    studentNames = [] # Hold all the student names == ExternalImageID
    status = "absent" # Initialise attendance status
    

    #Get all students from face collection's name == ExternalImageID and faceId == FaceId
    results = rekognition.list_faces(
        CollectionId=collectionName
    )

    for face in results['Faces']:
        face_id = face['FaceId'] #face
        external_id = face['ExternalImageId'] #student name

        faceIds.append(face_id)
        studentNames.append(external_id)
        

    #loop through the recognized "Person"s from GetFaceSearch
    for personMatch in response['Persons']:
            print('Person Index: ' + str(personMatch['Person']['Index'])) #index of the Person recognised,first person is 0
            print('Timestamp: ' + str(personMatch['Timestamp'])) #when was the face recognised

            print(personMatch) #only return the actual current recognised person with their respective index 

            #Looking for matching faces 
            if ('FaceMatches' in personMatch):
                for faceMatch in personMatch['FaceMatches']:
                    print('Face ID: ' + faceMatch['Face']['FaceId'])
                    print('Similarity: ' + str(faceMatch['Similarity']))
                    print('Recognised: ' + str(faceMatch['Face']['ExternalImageId'])) #Print recognised person name

                    #Name of the present students with removed _ if apply
                    student_name = str(faceMatch['Face']['ExternalImageId']).replace("_", " ")

                    # Pull student ID of recognised faces 
                    results = dynamodb.query(
                        TableName= students_table,
                        KeyConditionExpression='student_name= :student_name',
                        ExpressionAttributeValues= {
                            ':student_name': {"S": student_name}
                        },
                        ProjectionExpression='student_id'
                    )

                    #Extract the student ID
                    if 'Items' in results:
                        items = results['Items']
                        student_id = items[0]['student_id']['S']

                    # Save attendance status in database
                    # Only handles the students who are present 
                    if str(faceMatch['Face']['ExternalImageId']) in studentNames:
                        status = "present"
                        
                        # Database: Student name (ExternalImageId) - Student ID (FaceId) - Date (attendance date and time) - Status (Present/Absent)
                        dynamodb.put_item(
                            TableName= attendance_table, 
                            Item={
                                'id': {'S': student_id}, # Corresponding student ID for present students
                                'date': {'S': str(attendance_dateTime)},
                                'student_name': {'S': student_name},
                                'status': {'S': status},
                            }
                        )

                        # Remove detected students from the list to get an array of absent students
                        studentNames.remove(str(faceMatch['Face']['ExternalImageId'])) 
                        faceIds.remove(str(faceMatch['Face']['FaceId']))

                    #Handle absent students
                    for faceId in faceIds:
                        status = "absent"
                        index = faceIds.index(faceId)

                        absent_student_name = str(studentNames[index]).replace("_"," ")

                        # Query student ID of the absent student
                        response = dynamodb.query(
                            TableName= students_table,
                            KeyConditionExpression='student_name= :student_name',
                            ExpressionAttributeValues= {
                                ':student_name': {"S": absent_student_name}
                            },
                            ProjectionExpression='student_id'
                        )

                        #Extract the student ID
                        if 'Items' in response:
                            items = response['Items']
                            absent_student_id = items[0]['student_id']['S']

                        dynamodb.put_item(
                            TableName= attendance_table, 
                            Item={
                                'id': {'S': absent_student_id},
                                'date': {'S': str(attendance_dateTime)},
                                'student_name': {'S': absent_student_name},
                                'status': {'S': status},
                            }
                        )
       
    #if rekognition recognised more individuals than the set MaxResults 
    if 'NextToken' in response:
        paginationToken = response['NextToken']
    else:
        print("finished")    

    print("Face search operation completed")
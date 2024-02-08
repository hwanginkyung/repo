import boto3
import json

def detect_labels(photo, bucket):

     session = boto3.Session(profile_name='hik')
     client = session.client('rekognition')
     answers=[]
     response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
     MaxLabels=10,
     # Uncomment to use image properties and filtration settings
     #Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"],
     #Settings={"GeneralLabels": {"LabelInclusionFilters":["Cat"]},
     # "ImageProperties": {"MaxDominantColors":10}}
     )
     print('Detected labels for ' + photo)
     print()
     for label in response['Labels']:
         print("Label: " + label['Name'])
         print("Confidence: " + str(label['Confidence']))
         print("Instances:")
         answers.append(label['Name'])
        #  for instance in label['Instances']:
        #      print(" Bounding box")
        #      print(" Top: " + str(instance['BoundingBox']['Top']))
        #      print(" Left: " + str(instance['BoundingBox']['Left']))
        #      print(" Width: " + str(instance['BoundingBox']['Width']))
        #      print(" Height: " + str(instance['BoundingBox']['Height']))
        #      print(" Confidence: " + str(instance['Confidence']))
        #      print()

         print("Parents:")
         for parent in label['Parents']:
            if parent['Name']=='Person':
                person=True
            print(" " + parent['Name'])

        #  print("Aliases:")
        #  for alias in label['Aliases']:
        #      print(" " + alias['Name'])

        #      print("Categories:")
        #  for category in label['Categories']:
        #      print(" " + category['Name'])
        #      print("----------")
        #      print()

     if "ImageProperties" in str(response):
         print("Background:")
         print(response["ImageProperties"]["Background"])
         print()
         print("Foreground:")
         print(response["ImageProperties"]["Foreground"])
         print()
         print("Quality:")
         print(response["ImageProperties"]["Quality"])
         print()

     return answers,person

def detect_text(photo, bucket):

    session = boto3.Session(profile_name='hik')
    client = session.client('rekognition')
    answers=[]
    response = client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    textDetections = response['TextDetections']
    print('Detected text\n----------')
    for text in textDetections:
        print('Detected text:' + text['DetectedText'])
        print('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
        print('Id: {}'.format(text['Id']))
        if 'ParentId' in text:
            print('Parent Id: {}'.format(text['ParentId']))
        print('Type:' + text['Type'])
        print()
        answers.append(text['DetectedText'])
    return answers

def detect_faces(photo, bucket, region):
    answers=[]

    session = boto3.Session(profile_name='hik',
                            region_name=region)
    client = session.client('rekognition', region_name=region)

    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                   Attributes=['ALL'])

    print('Detected faces for ' + photo)
    n=0
    for faceDetail in response['FaceDetails']:
        answers.append([])
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))
        avg=(faceDetail['AgeRange']['Low']+faceDetail['AgeRange']['High'])/2
        print(list(faceDetail['Gender'].values())[0])
        answers[n].append(list(faceDetail['Gender'].values())[0])
        answers[n].append(str(avg))
        print(str(list(faceDetail['FaceOccluded'].values())[0]))
        if(str(list(faceDetail['Smile'].values())[0])=='True'):
            answers[n].append('Smile')
        # Access predictions for individual face details and print them
        if(str(list(faceDetail['Eyeglasses'].values())[0])=='True'):
            answers[n].append('Eyeglasses')
        if(str(list(faceDetail['FaceOccluded'].values())[0])=="True"):
            answers[n].append('FaceOccluded')
        answers[n].append(list(faceDetail['Emotions'][0].values())[0])
        print("Gender: " + str(faceDetail['Gender']))
        print(faceDetail['Smile'])
        print("Eyeglasses: " + str(faceDetail['Eyeglasses']))
        print("Face Occluded: " + str(faceDetail['FaceOccluded']))
        print("Emotions: " + str(faceDetail['Emotions'][0]))
        n+=1
    return answers

def main():
    photo = 'original/485_2077_4657.jpg'
    bucket = 'rekog-test-hik'
    region='us-east-1'
    tags1, person = detect_labels(photo, bucket)
    tags2 = detect_text(photo, bucket)
    print(tags1)
    print(tags2)
    tags3=[]
    if person==True :
        tags3=detect_faces(photo, bucket, region)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('test')
    with table.batch_writer() as batch:
        batch.put_item(
            Item={
                'image': 'standard_user',
                'tags': 'test1',
                'tags1': tags1 ,
                'tags2': tags2,
                'tags3': tags3
            }
        )
if __name__ == "__main__":
    main()

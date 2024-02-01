import boto3
import json

def detect_labels(photo, bucket):

     session = boto3.Session(profile_name='hik')
     client = session.client('rekognition')

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

     return len(response['Labels']),person

def detect_text(photo, bucket):

    session = boto3.Session(profile_name='hik')
    client = session.client('rekognition')

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
    return len(textDetections)

def detect_faces(photo, bucket, region):
    
    session = boto3.Session(profile_name='hik',
                            region_name=region)
    client = session.client('rekognition', region_name=region)

    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                   Attributes=['ALL'])

    print('Detected faces for ' + photo)
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')

        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))

        # Access predictions for individual face details and print them
        print("Gender: " + str(faceDetail['Gender']))
        print("Smile: " + str(faceDetail['Smile']))
        print("Eyeglasses: " + str(faceDetail['Eyeglasses']))
        print("Face Occluded: " + str(faceDetail['FaceOccluded']))
        print("Emotions: " + str(faceDetail['Emotions'][0]))

    return len(response['FaceDetails'])

def main():
    photo = 'images (1).jpg'
    bucket = 'test-image-hik'
    region='us-east-1'
    label_count, person = detect_labels(photo, bucket)
    print("Labels detected: " + str(label_count))
    text_count = detect_text(photo, bucket)
    print("Text detected: " + str(text_count))
    if person==True :
        face_count=detect_faces(photo, bucket, region)
        print("Faces detected: " + str(face_count))

if __name__ == "__main__":
    main()

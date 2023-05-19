from celery import shared_task
from time import sleep
from firebase import Firebase
from .models import  TemporaryFile
import boto3
from .helper import *

firebaseConfig = {
"apiKey": "AIzaSyBKMgZ-oKLTlH6Jk1UudnijBjOxH_KZ0EY",
  "authDomain": "ecowiser-a7435.firebaseapp.com",
  "databaseURL": "https://ecowiser-a7435-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "ecowiser-a7435",
  "storageBucket": "ecowiser-a7435.appspot.com",
  "messagingSenderId": "697889804664",
  "appId": "1:697889804664:web:f49385d8b23a5cf4b4388d"
}
firebase = Firebase(firebaseConfig)
db = firebase.database()

s3 = boto3.resource(
    service_name='s3',
    aws_access_key_id='your key id',
    aws_secret_access_key="your key secret",
)
S3_BUCKET_NAME = "ecowiser"

bucket = s3.Bucket(S3_BUCKET_NAME)


@shared_task
def sleepy(duration):
    sleep(duration)
    return None


@shared_task
def update_key(key):
    sleep(5)
    db.child("all_keys").child(key).set(True)
    return None


@shared_task
def upload_to_s3(image_upload_id, object_key,file_ext):
    my_uploaded_file = TemporaryFile.objects.get(id=image_upload_id)
    # print(my_uploaded_file)
    bucket.upload_fileobj(my_uploaded_file.file, object_key ,ExtraArgs={'ContentType': f'video/{file_ext}'})
    object_acl = s3.ObjectAcl(S3_BUCKET_NAME, object_key)
    object_acl.put(ACL='public-read')
    # os.remove(f"static/{object_key}.mp4")
    db.child("all_keys").child(object_key).update({"uploaded_s3":True,"video_link":f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_key}"})
    return None


@shared_task
def upload_to_dynamodb(image_upload_id, object_key, file_ext):
    my_uploaded_file = TemporaryFile.objects.get(id=image_upload_id)
    handle_uploaded_file(my_uploaded_file.file,f"static/{object_key}.{file_ext}")
    extract_subtitles(f"static/{object_key}.{file_ext}",f"static/{object_key}.txt")
    if all_subtitles := parse_subtitle_file(f"static/{object_key}.txt"):
        upload_sub_to_dynamo(all_subtitles, object_key)
        db.child("all_keys").child(object_key).update({"uploaded_dynamodb":True,"subtitles": True})
    else:
        db.child("all_keys").child(object_key).update({"uploaded_dynamodb":True,"subtitles": False})
    return None
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import  TemporaryFile
from .task import *
from .helper import *
from firebase import Firebase
from django.contrib import messages

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


def index(request):
    if request.method == 'POST':
        data = {
            "uploaded_s3":False,
            "uploaded_dynamodb":False,
            "subtitles": False
        }
        object_key = random_string_generator(10)
        resp = db.child("all_keys").child(object_key).set(data)
        my_uploaded_file = request.FILES['my_uploaded_file']
        file_ext = my_uploaded_file.name.split(".")[-1]
        image_upload = TemporaryFile.objects.create(file=my_uploaded_file)
        upload_to_s3.delay(image_upload.id, object_key,file_ext)
        upload_to_dynamodb.delay(image_upload.id, object_key,file_ext)
        # if all_subtitles:
        # return render(request, "parse.html",{"video_exists" : True,"video_link": f"static/{object_key}.mp4","all_subtitles":all_subtitles})
        # else:
        #     return render(request, "nosubtitles.html",{"video_exists" : True,"video_link": f"static/{object_key}.mp4","all_subtitles":all_subtitles})
        return redirect(f"/status/{object_key}")

    return render(request, "index.html",{"video_exists" : True,"video_link":f"./static/mbsa.mp4","all_subtitles":[]})

def object_page(request, object_key):
    if status_data := db.child("all_keys").child(object_key).get().val():
        return render(request, "final.html",{"status_data":dict(status_data)})
    else:
        return HttpResponse("Invalid Object Key in the URL")
    
def search(request, object_key):
    if request.method == 'POST':
        search_query = request.POST.get("query")
        result = search_subtitles(search_query, object_key)
        if result:
            messages.success(request, 'Follwing Below are your results!')
        else:
            messages.error(request, 'Oops!! No such subtitles found')
        return render(request, "search.html",{"subtitles":result,"object_key":object_key})
    return render(request, "search.html",{"subtitles":[],"object_key":object_key})
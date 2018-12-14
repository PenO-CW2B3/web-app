from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import CustomUser, Log
from background_task import background
import random
from time import sleep
import serial
import os, re, os.path
import shutil
from datetime import datetime
import pytz
from picamera import PiCamera

import sys
sys.path.append("/home/pi/smartLock")
from facial_recognition import give_name, finalize

for i in range(10):
    try:
        ser = serial.Serial('/dev/ttyACM' + str(i), 9600)
        break
    except:
        pass

def authentication(fingerprint_ID, i=1):
    camera = PiCamera()
    path = "/home/pi/smartLock/knn_examples/test/"
    date = datetime.now(pytz.timezone('Europe/Brussels')).strftime("%H:%M:%S_%d-%m-%Y")
    capture_image(camera, path + date + ".jpg")
    face = give_name()
    try:
        print(face)
        if fingerprint_ID == int(CustomUser.objects.filter(username=face).values_list("fingerprint_ID", flat=True)[0]):
            print("success")
            ser.write(b"correct_face")
            log = Log(username = face, timestamp = timezone.now())
            log.save()
            finalize()
        else:
            for root, dirs, files in os.walk(path):
                for file in files:
                    os.remove(os.path.join(root, file))
            ser.write(b"failed_face")
            while not ser.in_waiting:
                pass
            if ser.readline().decode().rstrip() == "pincode":
                backup_password()
    except:
        for root, dirs, files in os.walk(path):
            for file in files:
                os.remove(os.path.join(root, file))
        if i < 3:
          authentication(fingerprint_ID, i+1)
        else:
          ser.write(b"failed_face")
          while not ser.in_waiting:
              pass
          if ser.readline().decode().rstrip() == "pincode":
              backup_password()

def backup_password():
    backup_password_toggler = Group.objects.get(name="backup_password_toggler")
    permission = Permission.objects.get(name="Can see backup password")
    backup_password_toggler.permissions.add(permission)
    delete_backup_password()
    return HttpResponseRedirect("")

@background(schedule=120)
def delete_backup_password():
    backup_password_toggler = Group.objects.get(name="backup_password_toggler")
    permission = Permission.objects.get(name="Can see backup password")
    backup_password_toggler.permissions.remove(permission)
    ser.write(b"abort")

def add_new_fingerprint(new_user):
    ser.write(b"new_user")
    sleep(2)
    existing_fingerprints = [int(i[0]) for i in CustomUser.objects.exclude(fingerprint_ID__exact='').values_list("fingerprint_ID")]
    fingerprint_ID_range = [i for i in (range(1,128)) if i not in existing_fingerprints]
    new_fingerprint_ID = random.choice(fingerprint_ID_range)
    ser.write(str(new_fingerprint_ID).encode())
    while not ser.in_waiting:
        pass
    if ser.readline().decode().rstrip() == "finger_success":
       CustomUser.objects.filter(username=new_user).update(fingerprint_ID=new_fingerprint_ID)

def start_picture_procedure():
    ser.write(b"picture_procedure")

def add_new_face(new_user, photo_number):
    path = "/home/pi/smartLock/knn_examples/train/" + str(new_user)
    if not os.path.exists(path):
        os.makedirs(path)
    date = datetime.now(pytz.timezone('Europe/Brussels')).strftime("%H:%M:%S_%d-%m-%Y")
    while not ser.in_waiting:
        pass
    if ser.readline().decode().rstrip() == "take_picture":
        camera = PiCamera()
        capture_image(camera, path + "/" + date + ".jpg")
        ser.write(b"picture_taken")

def delete_user_photos(user):
    path = "/home/pi/smartLock/knn_examples/train/" + str(user)
    if os.path.exists(path):
        shutil.rmtree(path)

def capture_image(camera, path):
    camera.resolution = (400, 400)
    camera.start_preview()
    sleep(2)
    camera.capture(path)
    camera.stop_preview()
    camera.close()

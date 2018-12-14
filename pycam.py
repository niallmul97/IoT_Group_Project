#!/usr/bin/python3
import sys
import time
import subprocess
import uuid
import requests
import pprint
import csv
import re
from wia import Wia
from numpy import linalg as np
from picamera import PiCamera
from picamera import PiResolution

#Method that runs the main menu,
#allows a user to create a new user or attempt to sign in.
def mainMenu():

    print("1: Create User")
    print("2: Verify User")
    print("0: Exit")

    selection=input("Enter Choice: ")

    if selection == "1":
        createUser()
        mainMenu()
        
    elif selection == "2":
        verifyUser()
        mainMenu()
        
    elif selection == "0":
        exit()
        
    else:
        print("Invalid choice")
        mainMenu()

#Uses the Pi camera module to take a picture, trigger an event from Wia
#which uses AWS face detection to determine if there is a face, using JS,
#the relevant face landmark data is extracted and added to the "user" database.
def createUser():

    camera = PiCamera()
    camera.resolution = (1000,800)
    camera.start_preview()
    time.sleep(2)
    fileName = str(uuid.uuid4())+".jpeg"
    camera.capture('/home/pi/Desktop/scrot/'+fileName)
    camera.stop_preview()
    camera.close()
    wia = Wia()
    wia.access_token = "d_sk_Dku9mWR5BvmqGBu4DlVbleEZ"
    
    try:
        wia.Event.publish(name = "user",file = '/home/pi/Desktop/scrot/'+fileName)
        print("")
        print("Image uploading...")
        time.sleep(1)
        print("")
        print("Image uploaded!")
        print("")

    except Exception as error:
        print(error)


#Follows the same principle of createUser() but the image data gets sent to
#the "images" database. The method ecuDst() is then called, which takes in the
#values from the retrieveUser() and retrieveImage() functions. 
def verifyUser():
    camera = PiCamera()
    camera.resolution = (1000,800)
    camera.start_preview()
    time.sleep(2)
    fileName = str(uuid.uuid4())+".jpeg"
    camera.capture('/home/pi/Desktop/scrot/'+fileName)
    camera.stop_preview()
    camera.close()
    wia = Wia()
    wia.access_token = "d_sk_Dku9mWR5BvmqGBu4DlVbleEZ"
    
    try:
        wia.Event.publish(name = "image",file = '/home/pi/Desktop/scrot/'+fileName)
        print("")
        print("Image uploading...")
        time.sleep(1)
        print("")
        print("Image uploaded!")
        print("")

    except Exception as error:
        print(error)

    eucDst(retrieveUser(), retrieveImage())
    #clearUsers()


#Gets the landmark data back from mLab and extracts it into an array of floats
def retrieveUser():
    usersMlab='https://api.mlab.com/api/1/databases/iot_group_project/collections/users?apiKey=W_YDSBzIBqKayQxWC4aIk9DrnSHAkTUM'
    response=requests.get(usersMlab)
    data=response.json()
    emptyStr = ""
    user = []

    for i in data:
        emptyStr = emptyStr + str(i)

    words = emptyStr.split(",")
    x = 0
        
    while x < len(words):
            
        try:
            user.append(float(words[x]))
                
        except:
            print("")
                
        x+=1

    del user[18:]
    print(user)

    return user


#Gets the landmark data back from mLab and extracts it into an array of floats    
def retrieveImage():
    imagesMlab='https://api.mlab.com/api/1/databases/iot_group_project/collections/images?apiKey=W_YDSBzIBqKayQxWC4aIk9DrnSHAkTUM'
    response=requests.get(imagesMlab)
    data=response.json()
    emptyStr = ""
    image = []

    for i in data:
        emptyStr = emptyStr + str(i)

    words = emptyStr.split(",")
    x = 0
        
    while x < len(words):
            
        try:
            image.append(float(words[x]))
                
        except:
            print("")
                
        x+=1
        
    del image[18:]
    print(image)
        
    return image


#Takes in the user and image arrays from both the
#retrieveUser() and retrieveImage() methods. Finds the euclidean distance
#of both the arrays, and subtracts them. If the result "dist" is less than
#0.2 and greater than -0.2, then the programm determines that this is
#correct user, and that they may enter.
def eucDst(user, image):
    a = user
    b = image
    dist = np.norm(a) - np.norm(b)
    print(dist)
    if dist < 0.3 and dist > -0.3:
        print("")
        print("Known user, welcome!")
        time.sleep(1)
        print("")
        print("Fetching fuel data...")
        print("")
        time.sleep(2)
        fuelData()
    else:
        print("")
        print("Unknown User")
        print("")

def fuelData():
    irPrice='https://api.thingspeak.com/channels/649578/fields/1.json?api_key=JRW86DSYYH92L763&results=2'
    responseIR=requests.get(irPrice)
    dataIR=responseIR.json()
    emptyStrIR=''
    abc=''
    irFuel=[]

    for i in str(dataIR):
        emptyStrIR = emptyStrIR + str(i)

    words = emptyStrIR.split(",")
    abc=re.findall("(?<![a-zA-Z:])[-+]?\d*\.?\d+", str(words))
    for i in abc:
        try:
            if float(i) < 0.9 and float(i) > 0.1:
                irFuel.append(float(i))
        except:
            print('')
    del irFuel[:-1]

    usPrice= 'https://api.thingspeak.com/channels/645426/fields/1.json?api_key=36U0UI02F1F2G37Q&results=2'  
    responseUS=requests.get(usPrice)
    dataUS=responseUS.json()
    emptyStrUS=''
    abc=''
    usFuel=[]

    for i in str(dataUS):
        emptyStrUS = emptyStrUS + str(i)

    words = emptyStrUS.split(",")
    abc=re.findall("(?<![a-zA-Z:])[-+]?\d*\.?\d+", str(words))
    for i in abc:
        try:
            if float(i) < 2.9 and float(i) > 2.1:
                usFuel.append(float(i))
        except:
            print('')
    del usFuel[:-1]

    print("Miles per gallon ($):")
    print(usFuel[0])
    print("")
    print("Miles per litre (€):")
    print(irFuel[0])
    print("")

    
    
def exit():
    print("")
    print("shutting down...")
    print("")
    time.sleep(2)
    print("Goodbye!")
    print("")
    time.sleep(1)
    sys.exit

mainMenu()

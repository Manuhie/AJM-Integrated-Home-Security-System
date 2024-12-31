import pathlib
import face_recognition as fr
import sys
import os
import cv2
import face_recognition
import numpy as np
from time import sleep
import serial
import urllib3
##include a machine learning plat form that is going to integrate a face recognizer from multiple angles
arduino = serial.Serial(port='COM3', baudrate=500000, timeout=1)
numberOfPeoples = 0 #baudrate and port problem
image = face_recognition.load_image_file('Face Recognition AJM/test.jpg')
face_locations = face_recognition.face_locations(image)
def sendEmail1():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://maker.ifttt.com/trigger/EMERG_TO_POLICE/with/key/bCso9TDsJt7Zguj3g1_i1c')
def sendEmail2():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://maker.ifttt.com/trigger/STRANGER_AROUND_HOME/json/with/key/bCso9TDsJt7Zguj3g1_i1c')
def sendEmail3():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://maker.ifttt.com/trigger/DEVICE_THEFT/with/key/bCso9TDsJt7Zguj3g1_i1c')
def checkStat():
    while True:
        stat = arduino.readline()
        dstat = stat.decode('utf-8')
        if dstat == "OK":
            break
        elif dstat == "EMERG":
            sendEmail1()
            break
        else :
            break 

def openDoor():
    arduino.write(bytes("OPEN", 'utf-8'))
def get_encoded_faces():
    """
    looks through the faces folder and encodes all
    the faces

    :return: dict of (name, image encoded)
    """
    encoded = {}

    for dirpath, dnames, fnames in os.walk("Face Recognition AJM/faces"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png"):
                face = fr.load_image_file('Face Recognition AJM/faces/' + f)
                encoding = fr.face_encodings(face)[0]
                encoded[f.split(".")[0]] = encoding

    return encoded


def unknown_image_encoded(img):
    """
    encode a face given the file name
    """
    face = fr.load_image_file("faces/" + img)
    encoding = fr.face_encodings(face)[0]

    return encoding

def askForPIN(username):
    arduino.write("CHECK".encode("utf-8"))
    sleep(0.1)
    arduino.write(f"Welcome {username}".encode("utf-8"))
    checkStat()
def sideCam(known, noPeople):
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())
    img = cv2.imread('Face Recognition AJM/test1.jpg', 1)
    face_locations = face_recognition.face_locations(img)
    unknown_face_encodings = face_recognition.face_encodings(img, face_locations)
    knownFace = 0
    face_names = []
    for face_encoding in unknown_face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(faces_encoded, face_encoding)
        name = "Unknown"
        # use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            knownFace += 1
    numberOfPeoples = len(face_locations)
    if noPeople == numberOfPeoples:
        if known == knownFace:
            return True
        elif known > knownFace:
            return False   
    elif noPeople < numberOfPeoples:
        return "LESS"
    else:
        return 'no'
def classify_face(im):
    global trials 
    trials = 3
    knownFace = 0
    turns = 0
    turns +=1
    """
    will find all of the faces in a given image and label
    them if it knows what they are

    :param im: str of file path
    :return: list of face names
    """
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    img = cv2.imread(im, 1)
    #img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    #img = img[:,:,::-1]
 
    face_locations = face_recognition.face_locations(img)
    unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

    face_names = []
    for face_encoding in unknown_face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(faces_encoded, face_encoding)
        name = "Unknown"
        

        # use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            knownFace += 1

        face_names.append(name)
    numbers = True
    facial = False
    numberOfPeoples = len(face_locations)
    # Display the resulting image
    statusr = sideCam(knownFace, numberOfPeoples)
    if  statusr == False:
        if trials >= 1:
            trials += -1
            arduino.write(bytes("TRIALS", 'utf-8'))
            return
        else:
            arduino.write(bytes("LOCK", 'utf-8'))
            lock()
    elif statusr == "LESS":
        numbers = False
        arduino.write(bytes("CLOSER", 'utf-8'))
    elif statusr == True:
        facial = True
    elif statusr == 'no':
        return



    print(f"Known: {knownFace} People No: {numberOfPeoples} Turns: {turns}")
    if (facial, knownFace == numberOfPeoples):
        if turns <= numberOfPeoples:
            openDoor()
            sleep(5)
    elif (knownFace >= 1, numbers):
        askForPIN(face_names)
    else:
        sendEmail2()
def lock():
    while True:
        ioot=1
def imageCapture():
    cv2.destroyAllWindows()
    img_counter = 0
    cam = cv2.VideoCapture(1)
    ret, frame = cam.read()
    cv2.imshow("test", frame)
    img_name = "Face Recognition AJM/test1.jpg".format(img_counter)
    cv2.imwrite(img_name, frame)
    cam.release()
    cv2.destroyAllWindows()
    cam = cv2.VideoCapture(1)
    ret, frame = cam.read()
    cv2.imshow("test", frame)
    img_name = "Face Recognition AJM/test.jpg".format(img_counter)
    cv2.imwrite(img_name, frame)
    cam.release()
    cv2.destroyAllWindows()
def motion():
    cv2.destroyAllWindows()
    cascPath = pathlib.Path(cv2.__file__).parent.absolute()/"data/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(str(cascPath))
    video_capture = cv2.VideoCapture(1)
    code = True
    while code:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        try:
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception:
             sendEmail3()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        
        )

        # Draw a rectangle around the faces
        for (x) in faces:
            video_capture.release()
            imageCapture()
            video_capture = cv2.VideoCapture(1)
            classify_face("Face Recognition AJM/test.jpg")
            sleep(1)
            



while True:
    
    motion()

from PIL import Image
import os
import cv2
import math
import statistics
import json

t = os.path.dirname(__file__)
def filepath (path):
    return (os.path.join(t, path))

def processImage (img):
    w = img.width
    h = img.height
    x = 0
    y = 0

    redPixels = [[], []]
    whitePixels = [[], []]

    base = [0, 0]

    x = 0
    y = 0
    while x < w:
        y = 0        
        while y < h:
            if img.getpixel((x,y))[0] >= 75:
                if img.getpixel((x,y))[1] >= 75 and img.getpixel((x,y))[2] >= 75:
                    whitePixels[0].append (x)
                    whitePixels[1].append (y)
                else:
                    redPixels[0].append (x)
                    redPixels[1].append (y)
            y+=1
        x+=1
    
    try:
        base[0] = statistics.median (redPixels[0])
        base[1] = statistics.median (redPixels[1])
    except:
        pass
    
    return ([whitePixels, base])


def processVideo (gap):
    location = []
    angle = []
    angleUncertainty = []
    raw = []
    base = [[], []]
    baseFound = False
    vid = cv2.VideoCapture (filepath ("sample.MP4"))
    totalFrames = vid.get (cv2.CAP_PROP_FRAME_COUNT)
    #totalFrames = 150
    currentFrame = 0

    while currentFrame < totalFrames:
        global wholeFrame
        wholeFrame = False
        vid.set (cv2.CAP_PROP_POS_FRAMES, currentFrame)
        x,frame = vid.read()

        try:
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        except:
            break

        img = Image.fromarray(frame)
        
        frameResult = processImage (img)
        try:
            pass
        except:
            print (location)
            print ("error")
            return ("error")
        location.append(frameResult [0])
        #print (frameResult)
        #print (frameResult [1][0])
        if not baseFound:
            if base[0].__len__() == 25:
                #print (base)
                
                if statistics.stdev(base[0]) + statistics.stdev(base[1]) < 20.5:
                    baseFound = True
                    base[0] = statistics.median (base[0])
                    base[1] = statistics.median (base[1])
                else:
                    base[0].remove(max(base[0]))
                    base[1].remove(max(base[1]))
                    base[0].remove(min(base[0]))
                    base[1].remove(min(base[1]))
                    base[0].append (frameResult [1][0])
                    base[1].append (frameResult [1][1])
            else:
                base[0].append (frameResult [1][0])
                base[1].append (frameResult [1][1])

        print (str(math.floor((currentFrame+gap+1)/gap)) + "/" + str(math.floor(totalFrames/gap)) + " (" + str(math.floor(100*(((currentFrame+gap+1)/gap))/math.floor(totalFrames/gap))) + "%), Base Found: " + str(baseFound), end='\r')
        
        currentFrame += gap

    for value in location:
        cords = []
        angles = []
        
        for index, x in enumerate(value[0]):
            cords.append ([x, value[1][index]])
        
        for cord in cords:
            cord[0] = cord[0]-base[0]
            cord[1] = cord[1]-base[1]

        for cord in cords:
            try:
                angles.append (math.atan(cord[0]/cord[1]))
            except:
                pass
        try:
            angle.append (statistics.median (angles))
        except:
            angle.append (0)
        try:
            angleUncertainty.append ((max(angles)-min(angles))/2)
        except:
            angleUncertainty.append (0)
        
        raw.append (cords)

    with open(filepath("angle.json"), "w") as file:
        json.dump (angle, file)

    with open(filepath("angleUncertainty.json"), "w") as file:
        json.dump (angleUncertainty, file)

    with open(filepath("raw.json"), "w") as file:
        json.dump (raw, file)

processVideo (1)

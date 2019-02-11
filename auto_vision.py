import seamonsters as sea

ALIGN_EXPONENT = 1.5
ALIGN_SCALE = 0.1
ALIGN_MAX_VEL = 2 # feet per second
ALIGN_TOLERANCE = 1 # degrees

def strafeAlign(drive,vision):
    while True:
        hasTarget = vision.getNumber('tv', None) # 1 if target, 0 if none

        if hasTarget == None:
            print("No limelight connection!")
            yield
            continue
        elif hasTarget == 0:
            print("No vision targets")
            yield
            continue

        xOffset = vision.getNumber('tx', None)
        speed = sea.feedbackLoopScale(xOffset, ALIGN_SCALE, ALIGN_EXPONENT, ALIGN_MAX_VEL)
        print("%.3f degrees %.3f speed" % (xOffset, speed))
        
        drive.drive(speed,0,0)

        if abs(xOffset) <= ALIGN_TOLERANCE:
            yield True
        else:
            yield False
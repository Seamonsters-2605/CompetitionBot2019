import seamonsters as sea

ALIGN_EXPONENT = 0.8
ALIGN_SCALE = 1 / 2
ALIGN_MAX_VEL = 6 # feet per second
ALIGN_TOLERANCE = 2 # degrees

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
        print(xOffset, "degrees")

        speed = abs(xOffset) ** ALIGN_EXPONENT * ALIGN_SCALE
        if speed > .25:
            speed = .25
        if xOffset < 0:
            drive.drive(-speed,0,0)
        else:
            drive.drive(speed,0,0)
        if abs(xOffset) <= ALIGN_TOLERANCE:
            #Original tolerance: 1
            yield True
        else:
            yield False
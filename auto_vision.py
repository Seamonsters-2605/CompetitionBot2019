import seamonsters as sea
import drivetrain
import math

ALIGN_EXPONENT = 1.5
ALIGN_SCALE = 0.1
ALIGN_MAX_VEL = 2 # feet per second
ALIGN_TOLERANCE = 1 # degrees

FWD_SPEED = 1

def driveIntoVisionTarget(drive, vision, superDrive, distance=None):
    try:
        drivetrain.slowPositionGear.applyGear(superDrive)
        vision.putNumber('pipeline', 0)
        yield

        distTravelled = 0
        while True:
            hasTarget = vision.getNumber('tv', None) # 1 if target, 0 if none

            if hasTarget == None:
                print("No limelight connection!")
                return False
            elif hasTarget == 0:
                print("No vision targets")
                drive.drive(0, 0, 0)
                yield False
                continue

            xOffset = vision.getNumber('tx', None)
            speed = sea.feedbackLoopScale(xOffset, ALIGN_SCALE, ALIGN_EXPONENT, ALIGN_MAX_VEL)
            print("%.3f degrees %.3f speed" % (xOffset, speed))
            
            mag = math.hypot(speed, FWD_SPEED)
            d = math.atan2(FWD_SPEED, speed)

            drive.drive(mag,d,0)
            distTravelled += FWD_SPEED / sea.ITERATIONS_PER_SECOND # TODO not real time

            if distance is not None and distTravelled > distance:
                return True
            try:
                yield True
            except:
                return False
    finally:
        drive.drive(0, 0, 0)
        vision.putNumber('pipeline', 1)


def driveIntoVisionTargetOrGiveUpAndDriveForward(drive, vision, superDrive, distance):
    success = yield from sea.ensureFalse(
        driveIntoVisionTarget(drive, vision, superDrive, distance), 50)
    if not success:
        print("Giving up and driving forward")
        distTravelled = 0
        while distTravelled < distance:
            drive.drive(FWD_SPEED, math.pi / 2, 0)
            distTravelled += FWD_SPEED / sea.ITERATIONS_PER_SECOND # TODO not real time
            yield
        drive.drive(0, 0, 0)
    superDrive.disable()

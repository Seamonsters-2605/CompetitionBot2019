import cscore
import time

def startCamera(num):
    cam = cscore.UsbCamera("usbcam" + str(num), num)
    cam.setVideoMode(cscore.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
    cam.setBrightness(40)
    mjpegServer = cscore.MjpegServer("httpserver" + str(num), 1187 + num)
    mjpegServer.setSource(cam)

def main():
    startCamera(0)
    startCamera(1)

    while True:
        time.sleep(0.1)

import cscore
import time
import logging

logger = logging.getLogger("cameraserver")

def main():
    logger.info("The camera server started! you made it this far i'm proud of you")
    try:
        cam = cscore.UsbCamera("usbcam0", 0)
        cam.setVideoMode(cscore.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
        cam.setBrightness(40)
        mjpegServer = cscore.MjpegServer(name="httpserver0", port=5806)
        mjpegServer.setSource(cam)    
        while True:
            time.sleep(0.1)
    except Exception as e:
        print("Camera server is dead :(", e)

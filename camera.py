import cscore
import time

print("imported camera!")

def main():
    cam = cscore.UsbCamera("usbcam0", 0)
    cam.setVideoMode(cscore.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
    cam.setBrightness(40)
    mjpegServer = cscore.MjpegServer(name="httpserver0", port=5806)
    mjpegServer.setSource(cam)

    while True:
        time.sleep(0.1)

import picamera
import subprocess

# start the ffmpeg process with a pipe for stdin
# I'm just copying to a file, but you could stream to somewhere else
ffmpeg = subprocess.Popen([
    'ffmpeg', '-i', '-',
    '-vcodec', 'copy',
    '-an', '/home/pi/test.mpg',
    ], stdin=subprocess.PIPE)

# initialize the camera
camera = picamera.PiCamera(resolution=(800, 480), framerate=25)

# start recording to ffmpeg's stdin
camera.start_recording(ffmpeg.stdin, format='h264', bitrate=2000000)
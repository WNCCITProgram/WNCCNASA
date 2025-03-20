"""
    Name: video_streaming_picamera.py
    Author: 
    Created: 10/21/21
    Purpose: Stream video to a web interface
"""
# Adapted from a sample script from
# https://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
#
# Run the script at a terminal
# On a device on the netowrk:  Go to http://your-pi-address:8000
# with your web-browser to view the video stream.

import io
import picamera                  # Raspberry Pi Camera library
import logging
import socketserver              # Create a server socket for clients to connect to
import socket                    # For finding local IP address
from threading import Condition
from http import server          # Create a web server

# HTML for streaming web page
PAGE = """\
<html>
<head>
<title>GoPiGo Streaming Video</title>
</head>
<body>
<h1>GoPiGo Streaming Video</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and
            # notify all clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header(
                'Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


# Get local IP address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    # Create streaming output object
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    print("Streaming started at: " + str(get_ip_address()) + ":8000")
    try:
        # Set port number of streaming server
        address = ('', 8000)
        # Create Streaming Server object
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

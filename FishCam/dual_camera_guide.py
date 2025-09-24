#!/usr/bin/env python3
"""
Simple Dual Camera Modification for web_stream.py
=================================================

This shows the minimal changes needed to add a second camera to your existing web_stream.py.
Copy these patterns into your current file or use this as a reference.

Key Changes:
1. Create two MediaRelay instances (one per camera)
2. Add new endpoints: /stream0.mjpg and /stream1.mjpg  
3. Update HTML to show both streams
4. Use camera_info.json from camera_test.py to auto-detect cameras
"""

# Add this function near the top of your web_stream.py file:
def load_available_cameras():
    """Load camera indexes from camera_info.json if available."""
    import json
    try:
        with open("camera_info.json", "r") as f:
            data = json.load(f)
            cameras = [cam["index"] for cam in data["cameras"]]
            print(f"Found cameras from camera_info.json: {cameras}")
            return cameras[:2]  # Return first two cameras
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        print("camera_info.json not found, using default cameras [0, 1]")
        return [0, 1]

# Replace the global relay variable with this:
"""
# OLD (single camera):
relay = None

# NEW (dual camera):
camera_indexes = load_available_cameras()
relays = {}  # Dictionary to hold multiple relays
"""

# Update your StreamingHandler.do_GET method to handle multiple streams:
"""
def do_GET(self):
    if self.path == "/" or self.path == "/index.html":
        # Send dual camera HTML page (see HTML_DUAL_PAGE below)
        content = HTML_DUAL_PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        
    elif self.path == "/stream.mjpg":
        # Keep original single stream for backward compatibility
        self._handle_stream(relays.get(camera_indexes[0]) if camera_indexes else None, "primary")
        
    elif self.path == "/stream0.mjpg":
        # Camera 0 stream
        self._handle_stream(relays.get(camera_indexes[0]) if camera_indexes else None, "camera0")
        
    elif self.path == "/stream1.mjpg":
        # Camera 1 stream  
        self._handle_stream(relays.get(camera_indexes[1]) if len(camera_indexes) > 1 else None, "camera1")
        
    else:
        self.send_error(404)

def _handle_stream(self, relay, stream_name):
    # Extract the streaming logic from your current /stream.mjpg handler
    if relay is None:
        self.send_error(503, f"Stream {stream_name} not available")
        return
        
    # ... rest of your existing streaming code ...
"""

# HTML page for dual camera view:
HTML_DUAL_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>WNCC Aquaponics - Dual Camera</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f0f0f0; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        h1 { 
            text-align: center; 
            color: #333; 
        }
        .camera-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
            margin: 20px 0; 
        }
        .camera-box { 
            background: white; 
            padding: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .camera-title { 
            text-align: center; 
            font-weight: bold; 
            margin-bottom: 10px; 
            color: #555; 
        }
        .camera-stream { 
            width: 100%; 
            height: auto; 
            border-radius: 4px; 
        }
        .single-view { 
            text-align: center; 
            margin-top: 20px; 
        }
        .single-view a { 
            margin: 0 10px; 
            color: #007bff; 
            text-decoration: none; 
        }
        @media (max-width: 768px) { 
            .camera-grid { 
                grid-template-columns: 1fr; 
            } 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WNCC Aquaponics System - Camera Monitoring</h1>
        <div class="camera-grid">
            <div class="camera-box">
                <div class="camera-title">Main Camera (Fish Tank)</div>
                <img src="/stream0.mjpg" class="camera-stream" alt="Camera 0 Stream">
            </div>
            <div class="camera-box">
                <div class="camera-title">Secondary Camera (Plant Beds)</div>
                <img src="/stream1.mjpg" class="camera-stream" alt="Camera 1 Stream">
            </div>
        </div>
        <div class="single-view">
            <strong>Individual Streams:</strong>
            <a href="/stream0.mjpg" target="_blank">Camera 0 Only</a> |
            <a href="/stream1.mjpg" target="_blank">Camera 1 Only</a> |
            <a href="/stream.mjpg" target="_blank">Original Stream</a>
        </div>
    </div>
</body>
</html>
'''

# Update your main() function initialization:
"""
def main():
    global relays, camera_indexes
    
    print("Starting dual camera streaming server...")
    print(f"Attempting to use cameras: {camera_indexes}")
    
    # Initialize relays for each available camera
    for cam_idx in camera_indexes:
        try:
            relay = MediaRelay()
            relay.start_capture(cam_idx)
            relays[cam_idx] = relay
            print(f"✓ Camera {cam_idx} initialized successfully")
        except Exception as e:
            print(f"✗ Camera {cam_idx} failed: {e}")
            relays[cam_idx] = None
    
    if not any(relays.values()):
        print("ERROR: No cameras could be initialized!")
        return
    
    # Start server
    try:
        with socketserver.TCPServer(("", 8000), StreamingHandler) as httpd:
            print("Server started at http://0.0.0.0:8000")
            print("Available streams:")
            if relays.get(camera_indexes[0]): 
                print("  Camera 0: http://0.0.0.0:8000/stream0.mjpg")
            if len(camera_indexes) > 1 and relays.get(camera_indexes[1]): 
                print("  Camera 1: http://0.0.0.0:8000/stream1.mjpg")
            print("  Dual view: http://0.0.0.0:8000/")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Clean up
        for relay in relays.values():
            if relay:
                relay.stop_capture()
"""

print("=" * 60)
print("DUAL CAMERA IMPLEMENTATION GUIDE")
print("=" * 60)
print("Option 1: Use the new dual_camera_stream.py (standalone)")
print("Option 2: Modify your existing web_stream.py with the patterns above")
print("Option 3: Simple side-by-side approach (see below)")
print("=" * 60)

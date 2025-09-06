# ---------------------------- WEB PAGE HTML ------------------------------- #
""" This is the HTML code for the web page for testing in a browser.
 It's a multi-line string (triple quotes) so you can write it like a document."""
PAGE = """
<html>
<head>
<title>USB Camera Streaming - Optimized</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { 
    font-family: Arial, sans-serif; 
    margin: 20px; 
    background-color: #f0f0f0; 
}
.container { 
    max-width: 800px; 
    margin: 0 auto; 
    background-color: white; 
    padding: 20px; 
    border-radius: 10px; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
}
.stream-img { 
    max-width: 100%; 
    height: auto; 
    border: 2px solid #333; 
    border-radius: 5px; 
}
.info { 
    margin-top: 15px; 
    padding: 10px; 
    background-color: #e6f3ff; 
    border-radius: 5px; 
    font-size: 14px; 
}
</style>
</head>
<body>
<div class="container">
    <h1>USB Camera Streaming</h1>
    <p>Live video feed from USB camera - Optimized for bandwidth</p>
    <img src="stream.mjpg" class="stream-img" alt="Camera Stream"/>
    <div class="info">
        <strong>Stream Info:</strong><br>
        Resolution: 640x480 | Quality: High | Frame Rate: Up to 15 FPS<br>
        Optimized for fast loading and reduced bandwidth usage
    </div>
</div>
</body>
</html>
"""
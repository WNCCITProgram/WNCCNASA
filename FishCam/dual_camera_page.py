#!/usr/bin/env python3
"""
Dual Camera HTML Page Generator
===============================

This module handles HTML page generation for the dual camera streaming server.
Separated from dual_camera_stream.py for better organization and maintainability.
"""


def generate_html_page(camera_indexes, get_camera_config_func):
    """
    Generate HTML page with camera-specific titles.
    
    Args:
        camera_indexes: List of available camera indexes
        get_camera_config_func: Function to get camera configuration by index
    
    Returns:
        str: Complete HTML page as string
    """
    camera_boxes = ""
    available_cameras = []
    
    # Generate camera boxes for available cameras
    for cam_idx in camera_indexes:
        config = get_camera_config_func(cam_idx)
        camera_boxes += f'''
            <div class="camera-box">
                <div class="camera-title">Camera {cam_idx} - {config["description"]}</div>
                <img src="/stream{cam_idx}.mjpg" class="camera-stream" alt="Camera {cam_idx} Stream">
            </div>'''
        available_cameras.append(f'<a href="/stream{cam_idx}.mjpg">Camera {cam_idx} Stream</a>')
    
    direct_links = " | ".join(available_cameras)
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>WNCC Aquaponics - Multi-Camera Monitor</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .camera-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .camera-box {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .camera-title {{
            text-align: center;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
        }}
        .camera-stream {{
            width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        .info {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            .camera-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>WNCC Aquaponics - Multi-Camera Monitor</h1>
        <div class="camera-grid">{camera_boxes}
        </div>
        <div class="info">
            <p>Refresh the page if streams don't load. Direct stream URLs:</p>
            <p>{direct_links}</p>
        </div>
    </div>
</body>
</html>
'''


def generate_simple_dual_camera_page():
    """
    Generate a simple dual camera HTML page (legacy format).
    
    Returns:
        str: Complete HTML page as string
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Dual Camera Stream</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
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
            margin-top: 20px;
        }
        .camera-box {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .camera-title {
            text-align: center;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
        }
        .camera-stream {
            width: 100%;
            height: auto;
            border-radius: 4px;
        }
        .info {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
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
        <h1>WNCC Aquaponics - Dual Camera Monitor</h1>
        <div class="camera-grid">
            <div class="camera-box">
                <div class="camera-title">Camera 0 - Main View</div>
                <img src="/stream0.mjpg" class="camera-stream" alt="Camera 0 Stream">
            </div>
            <div class="camera-box">
                <div class="camera-title">Camera 1 - Secondary View</div>
                <img src="/stream1.mjpg" class="camera-stream" alt="Camera 1 Stream">
            </div>
        </div>
        <div class="info">
            <p>Refresh the page if streams don't load. Direct stream URLs:</p>
            <p><a href="/stream0.mjpg">Camera 0 Stream</a> | <a href="/stream1.mjpg">Camera 1 Stream</a></p>
        </div>
    </div>
</body>
</html>
"""

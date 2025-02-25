# create_project_part1.py

import pathlib
import os
import shutil

def create_base_structure():
    # Base directory
    base_dir = pathlib.Path.cwd() / 'measurement_project'
    
    # Create project structure
    folders = [
        base_dir,
        base_dir / 'config',
        base_dir / 'measurement',
        base_dir / 'measurement/templates/measurement',
        base_dir / 'measurement/static/measurement/css',
        base_dir / 'measurement/static/measurement/js',
        base_dir / 'media',
    ]
    
    # Create directories
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    # Create manage.py
    manage_py_content = '''
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''
    with open(base_dir / 'manage.py', 'w') as f:
        f.write(manage_py_content)

    # Create requirements.txt
    requirements_content = '''
django>=4.2.0
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.7.0
numpy>=1.24.0
Pillow>=9.5.0
'''
    with open(base_dir / 'requirements.txt', 'w') as f:
        f.write(requirements_content)

    # Create models.py
    models_content = '''
from django.db import models
from django.contrib.auth.models import User

class CalibrationData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pixels_per_cm = models.FloatField()
    reference_object_size = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Measurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dimensions = models.JSONField()
    mode = models.CharField(max_length=20)
    additional_data = models.JSONField(null=True, blank=True)
    image = models.ImageField(upload_to='measurements/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
'''
    with open(base_dir / 'measurement/models.py', 'w') as f:
        f.write(models_content)

    # Create settings.py
    settings_content = '''
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'measurement',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'measurement/static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
'''
    with open(base_dir / 'config/settings.py', 'w') as f:
        f.write(settings_content)

    print("Base project structure created successfully!")
    print("Created files:")
    print("- manage.py")
    print("- requirements.txt")
    print("- measurement/models.py")
    print("- config/settings.py")
    print("\nReady for Part 2: Views and URLs")

if __name__ == "__main__":
    create_base_structure()

def create_views_and_urls():
    base_dir = pathlib.Path.cwd() / 'measurement_project'

    # Create views.py
    views_content = '''
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
import cv2
import numpy as np
import base64
import torch
import logging
from .models import Measurement, CalibrationData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        
    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            height, width = image.shape[:2]
            
            # Add grid lines
            cv2.line(image, (width//3, 0), (width//3, height), (0, 255, 0), 1)
            cv2.line(image, (2*width//3, 0), (2*width//3, height), (0, 255, 0), 1)
            cv2.line(image, (0, height//3), (width, height//3), (0, 255, 0), 1)
            cv2.line(image, (0, 2*height//3), (width, 2*height//3), (0, 255, 0), 1)
            
            # Object detection
            results = self.model(image)
            
            # Draw detections
            for det in results.xyxy[0]:
                x1, y1, x2, y2, conf, cls = det.cpu().numpy()
                if conf > 0.5:
                    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        return None

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\\r\\n'
                   b'Content-Type: image/jpeg\\r\\n\\r\\n' + frame + b'\\r\\n\\r\\n')

def home(request):
    context = {
        'measurement_modes': {
            'single': 'Single Object',
            'multiple': 'Multiple Objects',
            'area': 'Area Measurement',
            'volume': 'Volume Estimation',
            'angle': 'Angle Measurement'
        }
    }
    return render(request, 'measurement/home.html', context)

def video_feed(request):
    return StreamingHttpResponse(
        gen(VideoCamera()),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@csrf_exempt
def capture_and_measure(request):
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image')
            mode = request.POST.get('mode', 'single')
            
            if not image_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No image data received'
                })
            
            success, dimensions = estimate_dimensions(image_data)
            
            if success and request.user.is_authenticated:
                Measurement.objects.create(
                    user=request.user,
                    dimensions=dimensions,
                    mode=mode
                )
            
            return JsonResponse({
                'success': success,
                'dimensions': dimensions
            })
                
        except Exception as e:
            logger.error(f"Error in capture_and_measure: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def estimate_dimensions(image_data):
    try:
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")

        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        results = model(image)
        
        if len(results.xyxy[0]) > 0:
            det = results.xyxy[0][0]
            x1, y1, x2, y2, conf, cls = det.cpu().numpy()
            
            pixel_width = x2 - x1
            pixel_height = y2 - y1
            
            PIXELS_PER_CM = 37.79
            width_cm = round(pixel_width / PIXELS_PER_CM, 2)
            height_cm = round(pixel_height / PIXELS_PER_CM, 2)
            
            return True, {'width': width_cm, 'height': height_cm}
            
        return False, None
        
    except Exception as e:
        logger.error(f"Error in estimation: {str(e)}")
        return False, None

@csrf_exempt
def calibrate(request):
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image')
            reference_size = float(request.POST.get('reference_size'))
            
            success, pixels_per_cm = process_calibration(image_data, reference_size)
            
            if success and request.user.is_authenticated:
                CalibrationData.objects.create(
                    user=request.user,
                    pixels_per_cm=pixels_per_cm,
                    reference_object_size=reference_size
                )
            
            return JsonResponse({
                'success': success,
                'pixels_per_cm': pixels_per_cm
            })
        except Exception as e:
            logger.error(f"Error in calibration: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def process_calibration(image_data, reference_size):
    try:
        return True, 37.79  # Placeholder implementation
    except Exception as e:
        logger.error(f"Error in calibration processing: {str(e)}")
        return False, None
'''
    with open(base_dir / 'measurement/views.py', 'w') as f:
        f.write(views_content)

    # Create urls.py
    urls_content = '''
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('capture_and_measure/', views.capture_and_measure, name='capture_and_measure'),
    path('calibrate/', views.calibrate, name='calibrate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
    with open(base_dir / 'measurement/urls.py', 'w') as f:
        f.write(urls_content)

    # Create config/urls.py
    config_urls_content = '''
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('measurement.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
    with open(base_dir / 'config/urls.py', 'w') as f:
        f.write(config_urls_content)

    print("Views and URLs created successfully!")
    print("Created files:")
    print("- measurement/views.py")
    print("- measurement/urls.py")
    print("- config/urls.py")
    print("\nReady for Part 3: Templates and Static Files")

if __name__ == "__main__":
    create_base_structure()
    create_views_and_urls()

def create_templates_and_static():
    base_dir = pathlib.Path.cwd() / 'measurement_project'

    # Create base.html
    base_template_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Object Measurement System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/static/measurement/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Object Measurement System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <span class="nav-link">Welcome, {{ user.username }}</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'admin:logout' %}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'admin:login' %}">Login</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% block content %}{% endblock %}

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/measurement/js/main.js"></script>
</body>
</html>
'''
    with open(base_dir / 'measurement/templates/measurement/base.html', 'w') as f:
        f.write(base_template_content)

    # Create home.html
    home_template_content = '''
{% extends 'measurement/base.html' %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="video-container">
                <img id="video-feed" src="{% url 'video_feed' %}" alt="Video Feed">
                <div class="overlay-controls">
                    <div class="measurement-guides" id="measurement-guides"></div>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="controls">
                <div class="mb-3">
                    <label for="measurement-mode" class="form-label">Measurement Mode</label>
                    <select id="measurement-mode" class="form-select">
                        {% for key, value in measurement_modes.items %}
                            <option value="{{ key }}">{{ value }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="mb-3">
                    <button id="capture-btn" class="btn btn-primary">
                        <i class="fas fa-camera"></i> Capture and Measure
                    </button>
                </div>

                <div class="mb-3">
                    <button id="calibrate-btn" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#calibrationModal">
                        <i class="fas fa-ruler"></i> Calibrate
                    </button>
                </div>

                <div id="measurements" class="card">
                    <div class="card-body">
                        <h5 class="card-title">Measurements</h5>
                        <div id="measurement-results">
                            <!-- Results will be displayed here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Calibration Modal -->
<div class="modal fade" id="calibrationModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Calibration</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <label for="reference-size" class="form-label">Reference Object Size (cm)</label>
                    <input type="number" class="form-control" id="reference-size" step="0.1" min="0">
                    <small class="form-text text-muted">Enter the known size of your reference object</small>
                </div>
                <button id="calibrate-capture-btn" class="btn btn-primary">
                    <i class="fas fa-camera"></i> Capture Reference Object
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Error Modal -->
<div class="modal fade" id="errorModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Error</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p id="error-message"></p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    with open(base_dir / 'measurement/templates/measurement/home.html', 'w') as f:
        f.write(home_template_content)

    # Create style.css
    css_content = '''
.video-container {
    position: relative;
    width: 100%;
    border: 2px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    background-color: #000;
}

#video-feed {
    width: 100%;
    height: auto;
    display: block;
}

.overlay-controls {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.measurement-guides {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.controls {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

#measurements {
    margin-top: 20px;
}

.object-measurement {
    margin-bottom: 15px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 4px;
    border-left: 4px solid #007bff;
}

.btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.measurement-result {
    font-size: 1.1em;
    margin: 10px 0;
    padding: 10px;
    background: #e9ecef;
    border-radius: 4px;
}

.calibration-guide {
    position: absolute;
    border: 2px dashed #fff;
    pointer-events: none;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.measuring {
    animation: pulse 1s infinite;
}
'''
    with open(base_dir / 'measurement/static/measurement/css/style.css', 'w') as f:
        f.write(css_content)

    # Create main.js
    js_content = '''
$(document).ready(function() {
    let measuring = false;
    let calibrating = false;

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    $('#capture-btn').click(function() {
        const mode = $('#measurement-mode').val();
        if (!measuring) {
            measuring = true;
            $(this).addClass('measuring').prop('disabled', true);
            captureAndMeasure(mode);
        }
    });

    $('#calibrate-capture-btn').click(function() {
        const referenceSize = $('#reference-size').val();
        if (!referenceSize) {
            showError('Please enter reference size');
            return;
        }
        if (!calibrating) {
            calibrating = true;
            $(this).prop('disabled', true);
            calibrate(referenceSize);
        }
    });

    $('#measurement-mode').change(function() {
        updateMeasurementGuides($(this).val());
    });
});

function captureAndMeasure(mode) {
    const video = document.getElementById('video-feed');
    const canvas = document.createElement('canvas');
    canvas.width = video.width;
    canvas.height = video.height;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    $.ajax({
        url: '/capture_and_measure/',
        type: 'POST',
        data: {
            'image': imageData,
            'mode': mode
        },
        success: function(response) {
            if (response.success) {
                displayMeasurements(response.dimensions, mode);
            } else {
                showError('Measurement failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            showError('Error: ' + error);
        },
        complete: function() {
            $('#capture-btn').removeClass('measuring').prop('disabled', false);
            measuring = false;
        }
    });
}

function calibrate(referenceSize) {
    const video = document.getElementById('video-feed');
    const canvas = document.createElement('canvas');
    canvas.width = video.width;
    canvas.height = video.height;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    $.ajax({
        url: '/calibrate/',
        type: 'POST',
        data: {
            'image': imageData,
            'reference_size': referenceSize
        },
        success: function(response) {
            if (response.success) {
                showSuccess('Calibration successful!');
                $('#calibrationModal').modal('hide');
            } else {
                showError('Calibration failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            showError('Error: ' + error);
        },
        complete: function() {
            $('#calibrate-capture-btn').prop('disabled', false);
            calibrating = false;
        }
    });
}

function displayMeasurements(dimensions, mode) {
    let html = '';
    
    switch(mode) {
        case 'single':
            html = `
                <div class="measurement-result">
                    <div>Width: ${dimensions.width} cm</div>
                    <div>Height: ${dimensions.height} cm</div>
                </div>
            `;
            break;
        case 'multiple':
            html = '<h6>Multiple Objects:</h6>';
            dimensions.forEach((dim, index) => {
                html += `
                    <div class="object-measurement">
                        <div>Object ${index + 1}:</div>
                        <div>Width: ${dim.width} cm</div>
                        <div>Height: ${dim.height} cm</div>
                    </div>
                `;
            });
            break;
        case 'area':
            html = `
                <div class="measurement-result">
                    <div>Area: ${dimensions.area} cm²</div>
                </div>
            `;
            break;
        case 'volume':
            html = `
                <div class="measurement-result">
                    <div>Volume: ${dimensions.volume} cm³</div>
                    <div>Height: ${dimensions.height} cm</div>
                </div>
            `;
            break;
        case 'angle':
            html = `
                <div class="measurement-result">
                    <div>Angle: ${dimensions.angle}°</div>
                </div>
            `;
            break;
    }
    
    $('#measurement-results').html(html);
}

function updateMeasurementGuides(mode) {
    const guides = $('#measurement-guides');
    guides.empty();

    switch(mode) {
        case 'angle':
            guides.append('<div class="guide-line angle-guide"></div>');
            break;
        case 'area':
            guides.append('<div class="guide-box area-guide"></div>');
            break;
        // Add more guide types as needed
    }
}

function showError(message) {
    $('#error-message').text(message);
    new bootstrap.Modal(document.getElementById('errorModal')).show();
}

function showSuccess(message) {
    // You could create a success toast or modal here
    alert(message);
}
'''
    with open(base_dir / 'measurement/static/measurement/js/main.js', 'w') as f:
        f.write(js_content)

    print("Templates and static files created successfully!")
    print("Created files:")
    print("- measurement/templates/measurement/base.html")
    print("- measurement/templates/measurement/home.html")
    print("- measurement/static/measurement/css/style.css")
    print("- measurement/static/measurement/js/main.js")
    print("\nProject setup is complete!")

if __name__ == "__main__":
    create_base_structure()
    create_views_and_urls()
    create_templates_and_static()
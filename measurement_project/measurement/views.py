
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
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

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

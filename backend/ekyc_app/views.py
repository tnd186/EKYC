# Standard library
import io
import base64
import json
import logging

# Third-party libraries
from PIL import Image
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Local libraries
from ekyc_app.services.face_recognition import FaceRecognition
from ekyc_app.services.face_orientation import FaceOrientation
from ekyc_app.services.ocr_vic import OCRVIC
from ekyc_app.services.face_matching import FaceMatching
from .models import ViewResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize models
fr_model = FaceRecognition()
fo_model = FaceOrientation()
ocr_model = OCRVIC()
fm_model = FaceMatching()


@csrf_exempt
def challenge_response(request):
    """
    Handle face orientation challenge.

    Args:
        request: HTTP request containing image and challenge respectively. JSON body:{"image", "challenge"}

    Returns:
        JsonResponse: True or False based on the challenge result.
    """

    if request.method == "POST":
        try:
            # Load and parse request JSON
            body = json.loads(request.body)
            data = body.get("image")
            challenge = body.get("challenge")

            # Decode the base64 image and convert to NumPy array
            image_data = base64.b64decode(data)
            image = Image.open(io.BytesIO(image_data))
            image_np = np.array(image)

            # Detect facial landmarks and determine orientation
            _, _, landmarks = fr_model(image_np, 10)  
            orientation = fo_model(landmarks)  

            # Return whether orientation matches the challenge
            return JsonResponse({"result": orientation == challenge})
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    # Log non-POST and return a default False result
    logger.info("Received non-POST request")
    return JsonResponse({"result": False})


@csrf_exempt
def ocr_vic(request):
    """
    Handle OCR for the front side of a Vietnam ID card (CMND/CCCD).

    Args:
        request: HTTP request containing the 'frontImage' file (multipart/form-data).

    Returns:
        JsonResponse: OCR result as JSON or an error message.
    """
    if request.method == "POST":
        try:
            # Retrieve the image file from request.FILES
            front_image = request.FILES.get("frontImage")
            if front_image is None:
                return JsonResponse({"error": "Missing 'frontImage' in request.FILES"}, status=400)

            # Open the image and convert to a NumPy array
            image = Image.open(front_image)
            image_np = np.array(image)

            # Perform OCR on the image
            data = ocr_model(image_np)

            # Return OCR results
            return JsonResponse({"result": data})

        except Exception as e:
            logger.error(f"Error processing OCR request: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    # Log non-POST requests and return a default False result
    logger.info("Received non-POST request for ocr_vic")
    return JsonResponse({"result": False})


@csrf_exempt
def face_verification(request):
    """
    Verify face similarity between a camera-captured image and an ID card image.

    Args:
        request: HTTP request containing JSON body with 'cam_image' and 'card_image' as base64 strings.

    Returns:
        JsonResponse: Similarity score (float) or an error message.
    """
    if request.method == "POST":
        try:
            # Parse JSON payload
            body = json.loads(request.body)
            cam_b64 = body.get("cam_image")
            card_b64 = body.get("card_image")

            if not cam_b64 or not card_b64:
                return JsonResponse({"error": "Missing 'cam_image' or 'card_image' in request body"}, status=400)

            # Decode base64-encoded images
            cam_data = base64.b64decode(cam_b64)
            card_data = base64.b64decode(card_b64)

            # Load images and convert to NumPy arrays
            cam_img = Image.open(io.BytesIO(cam_data))
            cam_np = np.array(cam_img)
            card_img = Image.open(io.BytesIO(card_data))
            card_np = np.array(card_img)

            # Detect faces
            face_cam, _, _ = fr_model(cam_np, 2)   # detect face in camera image
            face_card, _, _ = fr_model(card_np, 1) # detect face in ID card image

            # Compute similarity score
            score = fm_model(face_cam, face_card).item()

            # Return similarity score
            return JsonResponse({"result": score})

        except Exception as e:
            logger.error(f"Error processing face verification request: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    # Log non-POST requests and return a default False result
    logger.info("Received non-POST request for face_verification")
    return JsonResponse({"result": False})


@csrf_exempt
def save_view_result(request):
    """
    Save verification results to the database.

    Args:
        request: HTTP request containing JSON body with various verification results.

    Returns:
        JsonResponse: status 'success' or 'failed' depending on the save operation.
    """
    if request.method == "POST":
        try:
            # Parse JSON payload
            data = json.loads(request.body)

            # Extract OCR results dictionary
            ocr_data = data.get("ocrResult", {}).get("result", {})

            # Create ViewResult instance
            view_result = ViewResult(
                front_image=data.get("frontImage"),
                back_image=data.get("backImage"),
                face_result=data.get("faceResult", {}).get("result"),
                face_portrait=data.get("facePortrait"),
                challenge_result=data.get("challengeResult"),
                check_id_result=data.get("checkIDResult"),
                ocr_id=ocr_data.get("0"),
                ocr_nation=ocr_data.get("4"),
                ocr_name=ocr_data.get("1"),
                ocr_sex=ocr_data.get("3"),
                ocr_dob=ocr_data.get("2"),
                ocr_origin=ocr_data.get("5"),
                ocr_por=ocr_data.get("6"),
                accepted=data.get("accepted"),
            )
            view_result.save()

            # Return success status
            return JsonResponse({"status": "success"})

        except KeyError as e:
            logger.error(f"Missing key in save_view_result: {e}")
            return JsonResponse({"status": "failed", "error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error saving view result: {e}")
            return JsonResponse({"status": "failed", "error": str(e)}, status=500)

    # Log non-POST requests and return failed status
    logger.info("Received non-POST request for save_view_result")
    return JsonResponse({"status": "failed"}, status=400)


@csrf_exempt
def check_id_exists(request):
    """
    Check if an ID number already exists in the database for an accepted record.

    Args:
        request: HTTP request containing JSON body with 'ocr_id'.

    Returns:
        JsonResponse: {'result': True/False} or an error message.
    """
    if request.method == "POST":
        try:
            # Parse JSON payload
            data = json.loads(request.body)
            ocr_id = data.get("ocr_id")

            if not ocr_id:
                return JsonResponse({"error": "ocr_id not provided"}, status=400)

            # Check if record exists
            exists = ViewResult.objects.filter(ocr_id=ocr_id, accepted="true").exists()
            logger.info(f"Check ID exists: {exists}")

            return JsonResponse({"result": exists})

        except Exception as e:
            logger.error(f"Error checking ID existence: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    # Invalid request method
    return JsonResponse({"error": "Invalid request method"}, status=400)
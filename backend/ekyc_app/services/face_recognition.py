# Import libraries
import numpy as np
from facenet_pytorch import MTCNN
from typing import Tuple, Optional, Union

class FaceRecognition:
    def __init__(self):
        """
        Initialize MTCNN for face detection.
        """
        self.mtcnn = MTCNN()  # Create a MTCNN object to detect faces in an image
        self.face = None
        self.box = None
        self.landmarks = None


    def __call__(self, img: np.ndarray, padding: Optional[Union[float, int]] = None) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Detects faces in an image and returns the largest face crop.

        Args:
            img: Input image as a numpy array.
            padding: A scale factor (float) or fixed value (int) to adjust the bounding box.
                    If float, the box size is scaled; if int, a fixed value is added.

        Returns:
            tuple: A tuple (face crop, bounding box, landmarks) if a face is detected,
                otherwise (img, None, None).
        """

        # Use MTCNN to detect bounding boxes, confidence scores, and landmarks
        boxes, prob, landmarks = self.mtcnn.detect(img, landmarks=True)

        # If no face is detected, return the original image with None for box and landmarks
        if boxes is None:
            return img, None, None

        # Filter bounding boxes with confidence > 0.9
        mask = prob > 0.9
        boxes = boxes[mask]
        if boxes.size == 0:
            return img, None, None

        # If landmarks are available, apply the same filter to landmarks
        if landmarks is not None:
            landmarks = landmarks[mask]

        # Clip the box values to avoid negative numbers and convert to uint32
        boxes = np.clip(boxes, 0, np.inf).astype(np.uint32)

        # Calculate the area of each bounding box
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        # Get the index of the bounding box with the largest area
        max_index = int(np.argmax(areas))
        # Apply padding to the largest bounding box if needed
        max_box = FaceRecognition.padding_face(boxes[max_index], padding)
        max_landmarks = landmarks[max_index] if landmarks is not None else None
        x1, y1, x2, y2 = max_box

        # Crop the image using the bounding box to get the face
        self.face = img[y1:y2, x1:x2, ...]
        self.box = max_box
        self.landmarks = max_landmarks

        return self.face, self.box, self.landmarks


    @staticmethod
    def padding_face(box: np.ndarray, padding: Optional[Union[float, int]] = None) -> np.ndarray:
        """
        Applies padding to the face bounding box.

        Args:
            box: A numpy array with [x1, y1, x2, y2].
            padding: If a float, multiply the box size; if an int, add a fixed padding value.

        Returns:
            np.ndarray: The padded bounding box as a np.uint32 array.
        """

        x1, y1, x2, y2 = box
        # Calculate the center of the bounding box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        # Calculate the width and height of the bounding box
        w = x2 - x1
        h = y2 - y1
        
        if padding is not None:
            # If padding is a float: scale the current width and height
            if isinstance(padding, float):
                w = w * padding
                h = h * padding
            # If padding is an int: add a fixed value to width and height
            else:
                w = w + padding
                h = h + padding

        # Recalculate the coordinates of the bounding box after padding
        x1 = cx - w // 2
        x2 = cx + w // 2
        y1 = cy - h // 2
        y2 = cy + h // 2

        # Ensure the bounding box does not have negative values
        return np.clip([x1, y1, x2, y2], 0, np.inf).astype(np.uint32)

# Import libraries
import numpy as np
import torch
from typing import Union, List, Tuple

class FaceOrientation:
    """
    Calculate face direction using landmarks for left eye, right eye, and nose.
    """
    def __init__(self):
        """
        Initialize landmarks for face direction.
        """
        self.left_eye = None
        self.right_eye = None
        self.nose = None

    def __call__(self, landmarks: np.ndarray) -> str:
        """
        Finds face direction using eye and nose landmarks.

        Args:
            landmarks: A numpy array with at least 3 points: left_eye, right_eye, nose.

        Returns:
            str: Face direction: 'front', 'right', or 'left'.
        """

        # Convert landmarks to float arrays
        self.left_eye = np.asarray(landmarks[0], dtype=np.float32)
        self.right_eye = np.asarray(landmarks[1], dtype=np.float32)
        self.nose = np.asarray(landmarks[2], dtype=np.float32)

        # Get vectors: left eye to right eye, left eye to nose
        left2right_eye = self.right_eye - self.left_eye
        lefteye2nose = self.nose - self.left_eye
        left_angle = self.calculate_angle(left2right_eye, lefteye2nose)

        # Get vectors: right eye to left eye, right eye to nose
        right2left_eye = self.left_eye - self.right_eye
        righteye2nose = self.nose - self.right_eye
        right_angle = self.calculate_angle(right2left_eye, righteye2nose)

        # Decide face direction
        if 25 <= left_angle <= 60 and 25 <= right_angle <= 60:
            return 'front'
        elif left_angle < right_angle:
            return 'right'
        else:
            return 'left'

    @staticmethod
    def calculate_angle(v1: Union[List, Tuple, torch.Tensor, np.ndarray],
                        v2: Union[List, Tuple, torch.Tensor, np.ndarray]) -> float:
        """
        Computes the angle between two vectors.

        Args:
            v1: First vector.
            v2: Second vector.

        Returns:
            float: Angle in degrees (rounded).
        """

        # Convert to numpy arrays 
        v1 = np.asarray(v1, dtype=np.float32)
        v2 = np.asarray(v2, dtype=np.float32)

        # Compute length of each vector
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # If any vector is zero, return 0 to avoid division error
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        # Compute cosine similarity and clip value between [-1, 1]
        cosine = np.dot(v1, v2) / (norm_v1 * norm_v2)
        cosine = np.clip(cosine, -1.0, 1.0)
        
        # Get angle in degrees
        rad = np.arccos(cosine)
        degrees = np.degrees(rad)
        return float(np.round(degrees))

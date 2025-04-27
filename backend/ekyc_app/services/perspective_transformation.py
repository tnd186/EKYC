# Import libraries
import cv2
import numpy as np
import qrdet
import math
from typing import List, Tuple, Any

class PerTransfor:
    def __init__(self, output_size: Tuple[int, int] = (800, 500)) -> None:
        """
        Initialize with the output image size and create an instance of QRDetector.
        """
        self.detector = qrdet.QRDetector()
        self.output_size = output_size

    def detect_center_qr(self, img: np.ndarray) -> np.ndarray:
        """
        Detects a QR code in the image and returns the center coordinates of the first QR code.

        Args:
            img: Input image as a numpy array.

        Returns:
            np.ndarray: Center coordinates (x, y) as a numpy array of type float32.
        """

        qr_codes = self.detector.detect(img)
        if not qr_codes:
            raise ValueError("No QR code detected in the image.")
        x1, y1, x2, y2 = qr_codes[0]['bbox_xyxy']
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return list(map(int, [center_x, center_y]))

    def __call__(self, img: np.ndarray, corners: List[Tuple[float, float]]) -> np.ndarray:
        """
        Performs a perspective transformation based on the given corners.

        Args:
            img: The input image as a numpy array.
            corners: A list of corners (x, y) to be transformed.

        Returns:
            warped_img: The warped image with the defined output size.
        """

        w, h = self.output_size

       # Sort the corners based on the distance from the center QR code
        center = self.detect_center_qr(img)
        distances = [
            (math.sqrt((center[0] - x)**2 + (center[1] - y)**2), (x, y))
            for x, y in corners
        ]
        distances.sort(key=lambda x: x[0])
        
        # Order the corners in the following order: top-left, top-right, bottom-right, bottom-left.
        sorted_corners = np.array([d[1] for d in distances], dtype=np.float32)      
        dst_points = np.array([
            [w, 0],
            [w, h],
            [0, 0],
            [0, h]
        ], dtype=np.float32)

        # Perspective transformation of the image
        matrix = cv2.getPerspectiveTransform(sorted_corners, dst_points)
        warped_img = cv2.warpPerspective(img, matrix, (w, h))
        return warped_img

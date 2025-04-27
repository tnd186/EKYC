# Import libraries
from ultralytics import YOLO
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional

class TextDetection:
    def __init__(self, model_path: str, conf: float = 0.3):
        """
        Initializes the detector with the model path and confidence threshold.

        Args:
            model_path: Path to the YOLO model.
            conf: Confidence threshold for detection.
        """

        self.detector = YOLO(model_path)
        self.conf = conf
        
    def __call__(self, img_array: np.ndarray) -> List[Tuple[int, Image.Image]]:
        """
        Detects text in an image and crops text areas based on bounding boxes.

        Args:
            img_array: Input image as a numpy array.

        Returns:
            class_id, cropped_img: A list of tuples sorted by class_id and top position.
        """

        # Use YOLO to predict regions containing text.
        results = self.detector.predict(source=img_array, conf=self.conf, save=False)

        # Convert the numpy array image to PIL format for cropping.
        img = Image.fromarray(img_array)
        detected_items = []

        for result in results[0]:
            # Get the bounding box in the format [x_center, y_center, width, height].
            bbox = result.boxes.xywh.tolist()[0]
            # Get the class_id.
            class_id = int(result.boxes.cls.tolist()[0])
            
            x_center, y_center, width, height = bbox
            top_y = y_center - height / 2.0
            
            # Crop the image using the bounding box.
            cropped_img = self.crop_image(img, bbox)
            if cropped_img is not None:
                detected_items.append((class_id, top_y, bbox, cropped_img))
        
        # Sort the cropped images by class_id and top position (top_y).
        detected_items.sort(key=lambda x: (x[0], x[1]))
        return [(item[0], item[3]) for item in detected_items]
    
    @staticmethod
    def crop_image(img: Image.Image, bbox: List[float]) -> Optional[Image.Image]:
        """
        Crops the image based on the bounding box and filters out regions with unsuitable brightness or size.

        Args:
            img: Input PIL image.
            bbox: List in the format [x_center, y_center, width, height].

        Returns:
            cropped_img: Cropped PIL Image or None if it doesn't meet the criteria.
        """

        # Crop the image using the calculated coordinates and convert it to RGB.
        x_center, y_center, width, height = bbox
        left = x_center - width / 2.0
        top = y_center - height / 2.0
        right = x_center + width / 2.0
        bottom = y_center + height / 2.0
        cropped_img = img.crop((left, top, right, bottom)).convert("RGB")

        # Convert the cropped image to a numpy array to calculate the average brightness.
        cropped_np = np.array(cropped_img)
        mean_val = np.mean(cropped_np)
        
        # Skip the region if the brightness is too low or too high.
        if mean_val < 35 or mean_val > 220:
            return None
        
        # Skip the region if the cropped area is too small.
        if cropped_img.size[0] < 10 or cropped_img.size[1] < 10:
            return None
        
        return cropped_img

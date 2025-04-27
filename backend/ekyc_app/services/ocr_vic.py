# Import libraries
import os
from typing import Optional, Union, Dict, Any
import numpy as np
from .corner_detection import CornerDetection
from .perspective_transformation import PerTransfor
from .text_detection import TextDetection
from .text_recognition import TextRecognition

class OCRVIC:
    """
    OCRVIC integrates the full OCR process for CCCD: corner detection, perspective transformation, text detection, and text recognition.
    """

    def __init__(
        self, 
        model_path_cd: Optional[str] = None, 
        model_path_td: Optional[str] = None, 
        model_path_tr: Optional[str] = None, 
        config_path_tr: Optional[str] = None
    ) -> None:
        """
        Initializes the OCRVIC class with paths to model weights and configuration files.

        Args:
            model_path_cd: Path to the corner detection model.
            model_path_td: Path to the text detection model.
            model_path_tr: Path to the text recognition model.
            config_path_tr: Path to the text recognition configuration file.
        """

        # Set up model paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if model_path_cd is None:
            model_path_cd = os.path.join(base_dir, 'weights', 'corner_detection.pt')
        if model_path_td is None:
            model_path_td = os.path.join(base_dir, 'weights', 'text_detection.pt')
        if model_path_tr is None:
            model_path_tr = os.path.join(base_dir, 'weights', 'text_recognition.pth')
        if config_path_tr is None:
            config_path_tr = os.path.join(base_dir, 'configs', 'config_text_recognition.yml')
        
        # Initialize modules
        self.corner_detection = CornerDetection(model_path=model_path_cd)
        self.perspective_transformation = PerTransfor()
        self.text_detection = TextDetection(model_path=model_path_td)
        self.text_recognition = TextRecognition(model_path=model_path_tr, config_path=config_path_tr)


    def __call__(self, front_image: Union[str, np.ndarray]) -> Dict[int, str]:
        """
        Performs the OCR process on the CCCD image.

        Args:
            front_image (Union[str, np.ndarray]): The front image, which can be a file path or an image array.

        Returns:
            dict: A dictionary where keys are class IDs and values are the recognized texts.
        """

        front_text: Dict[int, str] = {}

        if front_image is not None:
            # Detect corners
            corners = self.corner_detection(front_image)

            # Apply perspective transformation
            warped_image = self.perspective_transformation(front_image, corners)
            # Detect text regions
            result_detected = self.text_detection(warped_image)
            # Process detected regions
            for class_id, cropped_img in result_detected:
                # Recognize text from the cropped region
                text, _ = self.text_recognition(cropped_img)
                # Store the recognized text
                if class_id not in front_text:
                    front_text[class_id] = text
                else:
                    front_text[class_id] += " " + text

        return front_text

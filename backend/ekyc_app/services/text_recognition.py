# Import libraries
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor
from PIL import Image
from typing import Tuple, Union

class TextRecognition:
    def __init__(self, model_path: str, config_path: str):
        """
        Initializes the TextRecognition class with the model weights and config file.

        Args:
            model_path (str): Path to the model weights.
            config_path (str): Path to the configuration file.
        """

        config = Cfg.load_config_from_file(config_path)
        config['weights'] = model_path
        self.recognizer = Predictor(config)

    def __call__(self, img: Union[Image.Image, str]) -> Tuple[str, float]:
        """
        Recognizes text from the input image.

        Args:
            img (PIL.Image.Image or str): The input image, which can be a PIL Image object or a file path.

        Returns:
            text, confidence: A tuple containing the recognized text and its confidence score.
        """

        if isinstance(img, str):
            img = Image.open(img)
        
        text, confidence = self.recognizer.predict(img, return_prob=True)
        return text, confidence

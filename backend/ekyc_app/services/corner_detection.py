from ultralytics import YOLO
import numpy as np

class CornerDetection:
    """
    This class uses a YOLO model to find corners and calculate the missing one if only three are found.
    """

    def __init__(self, model_path: str, conf_threshold: float = 0.45):
        """
        Sets up the YOLO model and defines the offsets for each corner.

        Args:
            model_path: The path to the YOLO model.
            conf_threshold: The confidence threshold for predictions.

        """       
        self.detector = YOLO(model_path)
        self.conf_threshold = conf_threshold
        # Offsets for each corner: (x_offset, y_offset)
        self.offsets = {
            0: (-0.5, -0.5),  # top-left
            1: (0.5, -0.5),   # top-right
            2: (0.5, 0.5),    # bottom-right
            3: (-0.5, 0.5)    # bottom-left
        }
        # Formula to calculate the missing corner: missing_class: (a, b, c)
        self.missing_formula = {
            0: (1, 3, 2),
            1: (0, 2, 3),
            2: (1, 3, 0),
            3: (0, 2, 1)
        }

    def __call__(self, img_source) -> np.ndarray:
        """
        Detects corners from the input image and computes the missing one if needed.

        Args:
            img_source: A file path to an image or an image array.

        Returns:
            np.ndarray: A numpy array with shape (4, 2) containing the four corner coordinates.
        """

        results = self.detector.predict(source=img_source, conf=self.conf_threshold, save=False)
        detected_corners = {}

        # Process each prediction to get the corner coordinates.
        for result in results[0]:
            bbox = result.boxes.xywh.tolist()[0]  # [x_center, y_center, width, height]
            class_id = int(result.boxes.cls.tolist()[0])
            if class_id in self.offsets:
                x_center, y_center, width, height = bbox
                x_offset, y_offset = self.offsets[class_id]
                corner = [
                    x_center + x_offset * width,
                    y_center + y_offset * height
                ]
                detected_corners[class_id] = corner

        # If a corner is missing, calculate it using the formula.
        for class_id in range(4):
            if class_id not in detected_corners:
                try:
                    # Calculate the missing corner:
                    # missing_corner = 2 * (average of two corners) - third corner
                    a, b, c = self.missing_formula[class_id]
                    if a in detected_corners and b in detected_corners and c in detected_corners:
                        corner_a = detected_corners[a]
                        corner_b = detected_corners[b]
                        corner_c = detected_corners[c]
                        mid_x = (corner_a[0] + corner_b[0]) / 2
                        mid_y = (corner_a[1] + corner_b[1]) / 2
                        detected_corners[class_id] = [2 * mid_x - corner_c[0], 2 * mid_y - corner_c[1]]
                    else:
                        raise ValueError(f"Not enough corners to calculate for class {class_id}.")
                except KeyError:
                    raise ValueError(f"Can not calculating the missing corner for class {class_id}.")

        # Arrange the corners in order: 0: top-left, 1: top-right, 2: bottom-right, 3: bottom-left.
        corners = [detected_corners[i] for i in range(4)]
        return np.array(corners, dtype=np.float32)

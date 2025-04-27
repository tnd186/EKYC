# Import libraries
import numpy as np
import torch
import cv2
from facenet_pytorch import InceptionResnetV1

class FaceMatching:
    def __init__(self):
        """
        Initialize the InceptionResnetV1 model.
        """
        self.irv1 = InceptionResnetV1(pretrained='vggface2').eval()

    def __call__(self, face1: np.ndarray, face2: np.ndarray) -> float:
        """
        Calculates the similarity between two faces.

        Args:
            face1: The first face image as a numpy array.
            face2: The second face image as a numpy array.

        Returns:
            similar: Similarity score (0-100).
        """

        # Convert face images from numpy arrays to tensors.
        face1_tensor = self.face_transform(face1)
        face2_tensor = self.face_transform(face2)

        # Get the embeddings for each face without computing gradients.
        with torch.no_grad():
            emb1 = self.irv1(face1_tensor)
            emb2 = self.irv1(face2_tensor)

        # Calculate the Euclidean distance and then the similarity score.
        dis = self.euclidean_distance(emb1, emb2).item()
        similar = self.calculate_similarity(dis)
        return similar

    @staticmethod
    def face_transform(face: np.ndarray) -> torch.Tensor:
        """
        Preprocesses the face image: resizes, normalizes, and converts it to a tensor.

        Args:
            face: The input face image as a numpy array.

        Returns:
            face_tensor: A face tensor with shape (1, 3, 160, 160).
        """

        # Resize the image to 160x160 pixels.
        size = (160, 160)
        face_resized = cv2.resize(face, size)
        # Normalize the image: subtract 127.5 and divide by 128.
        face_normalized = (face_resized.astype(np.float32) - 127.5) / 128.0

        # Change image format from HWC to CHW and add a batch dimension.
        face_tensor = torch.from_numpy(face_normalized).permute(2, 0, 1)
        if face_tensor.ndim == 3:
            face_tensor = face_tensor.unsqueeze(0)

        return face_tensor.float()

    @staticmethod
    def euclidean_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """
        Calculates the Euclidean distance between two tensors.

        Args:
            x: The first face embedding.
            y: The second face embedding.

        Returns:
            torch.Tensor: The Euclidean distance as a tensor.
        """
        return torch.norm(x - y, p=2)

    @staticmethod
    def calculate_similarity(dis: float) -> float:
        """
        Calculates the similarity score from the Euclidean distance using an exponential decay.

        Args:
            dis: The Euclidean distance.

        Returns:
            float: A similarity score between 0 and 100.
        """
        similar = round(100 * np.exp(-0.8 * (dis - 0.6)), 2)
        return np.clip(similar, 0, 100)

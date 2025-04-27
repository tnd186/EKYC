from django.db import models

class ViewResult(models.Model):
    # URL of the front image of the citizen ID card (CCCD)
    front_image = models.CharField(max_length=255)
    
    # URL of the back image of the citizen ID card (CCCD)
    back_image = models.CharField(max_length=255)
    
    # Similarity score between the user's portrait and the citizen ID card
    face_result = models.CharField(max_length=255)
    
    # URL of the user's portrait image
    face_portrait = models.CharField(max_length=255)
    
    # Result of the authenticity challenge test
    challenge_result = models.CharField(max_length=255)
    
    # ID verification result (checks if the ID has been used to create an account before)
    check_id_result = models.CharField(max_length=255)
    
    # Citizen ID number
    ocr_id = models.CharField(max_length=255)
    
    # Nationality
    ocr_nation = models.CharField(max_length=255)
    
    # Full name
    ocr_name = models.CharField(max_length=255)
    
    # Gender
    ocr_sex = models.CharField(max_length=255)
    
    # Date of birth
    ocr_dob = models.CharField(max_length=255)
    
    # Place of origin
    ocr_origin = models.CharField(max_length=255)
    
    # Place of permanent residence
    ocr_por = models.CharField(max_length=255)
    
    # Final result of the eKYC process (True: accepted, False: rejected)
    accepted = models.CharField(max_length=255)

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './UploadCard.css';

const UploadCard = () => {
  // State
  const [frontImage, setFrontImage] = useState(null);
  const [backImage, setBackImage] = useState(null);
  const navigate = useNavigate();

  // Handle uploaded image
  const handleImageUpload = (event, setImage) => {
    const file = event.target.files[0];
    if (file) {
      setImage({ file, imageUrl: URL.createObjectURL(file) });
    }
  };

  // Navigate to capture-face page
  const handleNextButtonClick = () => {
    if (frontImage && backImage) {
      navigate('/capture-face', { state: { frontImage, backImage: backImage.imageUrl } });
    }
  };

  useEffect(() => {
    const fetchOCRResult = async () => {
      if (!frontImage) return;
      try {
        const formData = new FormData();
        formData.append('frontImage', frontImage.file);

        // Send to backend for OCR extraction
        const ocrResponse = await fetch('http://127.0.0.1:8000/api/ocr_vic/', {
          method: 'POST',
          body: formData,
        });
        const ocrResult = await ocrResponse.json();

        if (!ocrResult) return;
        localStorage.setItem('ocrResult', JSON.stringify(ocrResult));

        // Check if ID exists in MongoDB
        const ocrId = ocrResult.result['0'];
        const checkIdResponse = await fetch('http://127.0.0.1:8000/api/check_id_exists/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ocr_id: ocrId }),
        });

        const checkIdResult = await checkIdResponse.json();
        localStorage.setItem('checkIDResult', JSON.stringify(checkIdResult.result ? 'Thẻ đã được sử dụng' : 'Thẻ chưa được sử dụng để đăng ký'));
        
      } catch (error) {
        console.error('Error uploading front image:', error);
      }
    };

    fetchOCRResult();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [frontImage]);

  return (
    <div id="upload-card-frame">
      {/* Progress indicator */}
      <div id="process-1" />
      <div id="process-2" />
      <div id="process-3" />
      <div id="connect-1-2" />
      <div id="connect-2-3" />
      <span id="text-1">1</span>
      <span id="text-2">2</span>
      <span id="text-3">3</span>
  
      {/* Front image upload section */}
      <div id="front-vic-frame" />
      <div id="image-illu-front-vic" />
      <span id="text-front-vic">a) Hình chụp mặt trước của thẻ</span>
      <span id="text-illu-front-vic">Hình minh họa</span>
      <div
        id="upload-front-vic-button"
        className={frontImage ? 'uploaded' : ''}
        style={{
          background: frontImage
            ? `url(${frontImage.imageUrl}) 100% / cover no-repeat`
            : '',
        }}
      >
        <input
          type="file"
          accept="image/*"
          id="frontImageUpload"
          className="upload-input"
          onChange={(e) => handleImageUpload(e, setFrontImage)}
        />
        {!frontImage && (
          // Shown if the front image is not uploaded
          <label htmlFor="frontImageUpload" className="upload-label">
            <div id="icon-front-vic-button" />
            <span id="text-front-vic-button">Tải hình lên</span>
          </label>
        )}
      </div>
  
      {/* Back image upload section */}
      <div id="back-vic-frame" />
      <div id="image-illu-back-vic" />
      <span id="text-back-vic">b) Hình chụp mặt sau của thẻ</span>
      <span id="text-illu-back-vic">Hình minh họa</span>
      <div
        id="upload-back-vic-button"
        className={backImage ? 'uploaded' : ''}
        style={{
          background: backImage
            ? `url(${backImage.imageUrl}) 100% / cover no-repeat`
            : '',
        }}
      >
        <input
          type="file"
          accept="image/*"
          id="backImageUpload"
          className="upload-input"
          onChange={(e) => handleImageUpload(e, setBackImage)}
        />
        {!backImage && (
          // Shown if the back image is not uploaded
          <label htmlFor="backImageUpload" className="upload-label">
            <div id="icon-back-vic-button" />
            <span id="text-back-vic-button">Tải hình lên</span>
          </label>
        )}
      </div>
    
      {/* Next page button */}
      <button type="button" id="next-button" onClick={handleNextButtonClick}>
        <span id="text-next-button">Tiếp Tục</span>
      </button>

      {/* End page spacer */}
      <span id="space-end-page-1" />
    </div>
  );
  
};

export default UploadCard;

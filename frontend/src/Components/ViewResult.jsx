import React, { useEffect, useMemo } from "react";
import { useLocation } from "react-router-dom";
import "./ViewResult.css"; 

const ViewResult = () => {
  // Get data from the route
  const location = useLocation();
  const {
    frontImage,
    backImage,
    faceResult,
    facePortrait,
    challengeResult,
  } = location.state || {};

  // Get data from localStorage using useMemo
  const ocrResult = useMemo(() => {
    return JSON.parse(localStorage.getItem("ocrResult")) || { result: [] };
  }, []);

  const checkIDResult = useMemo(() => {
    return JSON.parse(localStorage.getItem("checkIDResult")) || "";
  }, []);

  // Determine color classes for results
  const faceResultClass = faceResult?.result >= 80 ? "result-green" : "result-red";
  const challengeResultClass = challengeResult === "Không phát hiện giả mạo" ? "result-green" : "result-red";
  const checkIDResultClass = checkIDResult === "Thẻ chưa được sử dụng để đăng ký" ? "result-green" : "result-red";

  // Determine if overall data meets requirements
  const accepted = (
    checkIDResultClass === 'result-green' &&
    challengeResultClass === 'result-green' &&
    faceResultClass === 'result-green' &&
    frontImage &&
    backImage &&
    facePortrait &&
    ocrResult.result[0] &&
    ocrResult.result[1] &&
    ocrResult.result[2] &&
    ocrResult.result[3] &&
    ocrResult.result[4] &&
    ocrResult.result[5] &&
    ocrResult.result[6]
  ) ? "true" : "false";

  useEffect(() => {
    const convertBlobToBase64 = async (blobUrl) => {
      return new Promise((resolve, reject) => {
        fetch(blobUrl)
          .then((response) => response.blob())
          .then((blob) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          });
      });
    };
  
    const saveData = async () => {
      try {
        // Convert Blob URLs to Base64
        const frontImageBase64 = frontImage ? await convertBlobToBase64(frontImage.imageUrl) : null;
        const backImageBase64 = backImage ? await convertBlobToBase64(backImage) : null;
  
        // Send data to the save_view_result API to store in MongoDB
        const response = await fetch("http://127.0.0.1:8000/api/save_view_result/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            frontImage: frontImageBase64,  
            backImage: backImageBase64,              
            faceResult: faceResult,           
            facePortrait: facePortrait,        
            challengeResult: challengeResult,  
            ocrResult: ocrResult,              
            checkIDResult: checkIDResult,      
            accepted: accepted,                
          }),
        });
        // eslint-disable-next-line
        const saveResult = await response.json();
      } catch (error) {
        console.error("Error saving result:", error);
      }
    };
  
    saveData();
  }, [frontImage, backImage, faceResult, facePortrait,
    challengeResult, ocrResult, checkIDResult, accepted,]);
  
  return (
    <div id="result-frame">
      {/* Progress indicators */}
      <div id="background"></div>
      <div id="process-1"></div>
      <div id="process-2"></div>
      <div id="process-3"></div>
      <div id="connect-1-2"></div>
      <div id="connect-2-3"></div>
      <span id="text-1">1</span>
      <span id="text-2">2</span>
      <span id="text-3">3</span>

      <span id="result-text">Kết quả xác minh danh tính</span>

      {/* ID card front, back, and portrait images */}
      <div id="front-vic" style={{ backgroundImage: `url(${frontImage?.imageUrl})` }}></div>
      <div id="back-vic" style={{ backgroundImage: `url(${backImage})` }}></div>
      <div id="face-portrait" style={{ backgroundImage: `url(${facePortrait})` }}></div>

      <div id="ocr-frame"></div>

      {/* OCR information from the ID card */}
      <span id="id-text">Số CCCD</span>
      <div id="id-field">{ocrResult.result[0] || "N/A"}</div>

      <span id="nation-text">Quốc tịch</span>
      <div id="nation-field">{ocrResult.result[4] || "N/A"}</div>

      <span id="name-text">Họ và tên</span>
      <div id="name-field">{ocrResult.result[1] || "N/A"}</div>

      <span id="sex-text">Giới tính</span>
      <div id="sex-field">{ocrResult.result[3] || "N/A"}</div>

      <span id="dob-text">Ngày sinh</span>
      <div id="dob-field">{ocrResult.result[2] || "N/A"}</div>

      <span id="origin-text">Quê quán</span>
      <div id="origin-field">{ocrResult.result[5] || "N/A"}</div>

      <span id="por-text">Nơi thường trú</span>
      <div id="por-field">{ocrResult.result[6] || "N/A"}</div>

      {/* Face recognition result */}
      <span id="fv-text">Độ tương đồng ảnh chân dung và CCCD</span>
      <div id="fv-field" className={faceResultClass}>{faceResult?.result || "N/A"} %</div>

      {/* Face movement verification */}
      <span id="ld-text">Xác thực chuyển động khuôn mặt</span>
      <div id="ld-field" className={challengeResultClass}>{challengeResult || "N/A"}</div>

      {/* Account status check */}
      <span id="acc-status-text">Kiểm tra tình trạng tài khoản</span>
      <div id="acc-status-field" className={checkIDResultClass}>{checkIDResult || "N/A"}</div>

      {/* End page spacer */}
      <span id="space-end-page-3"></span>
    </div>
  );
};

export default ViewResult;

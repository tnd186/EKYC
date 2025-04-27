import React, { useRef, useState, useEffect, useCallback } from 'react'; 
import { useLocation, useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import './CaptureFace.css';

const CaptureFace = () => { 
  // Get data from the route
  const location = useLocation();
  const navigate = useNavigate();
  const { frontImage, backImage } = location.state || {};

  // References
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const progressCanvasRef = useRef(null);

  // State
  const [isCorrect, setIsCorrect] = useState(false);
  const [faceResult, setFaceResult] = useState(null);
  const [facePortrait, setFacePortrait] = useState(null);
  const [countCorrect, setCountCorrect] = useState(0);
  const [countChallenge, setCountChallenge] = useState(1);
  const [countFrame, setCountFrame] = useState(0);
  const [challenge, setChallenge] = useState('front');
  const [instruction, setInstruction] = useState('Bắt đầu xác thực khuôn mặt');
  const [isCapturing, setIsCapturing] = useState(false);
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);

  // Generate random challenge
  const randomChallengeResponse = (currentChallenge) => { 
    const options = ['right', 'left', 'front'].filter(option => option !== currentChallenge);
    const newChallenge = options[Math.floor(Math.random() * options.length)];
    setChallenge(newChallenge);

    const instructions = {
      front: 'Quay mặt vào giữa',
      left: 'Quay mặt sang trái',
      right: 'Quay mặt sang phải'
    };
    setInstruction(instructions[newChallenge]);
  };

  // Draw progress circle for verification
  const drawProgress = (count) => {
    const canvas = progressCanvasRef.current;
    const context = canvas.getContext('2d');
    const radius = canvas.width / 2;
    const startAngle = -0.5 * Math.PI;
    const endAngle = startAngle + (count / 4) * 2 * Math.PI;

    context.clearRect(0, 0, canvas.width, canvas.height);
    context.beginPath();
    context.arc(radius, radius, radius - 5, startAngle, endAngle);
    context.lineWidth = 10;
    context.strokeStyle = 'rgba(0, 119, 190, 1)';
    context.stroke();
  };

  // Animate progress drawing
  const animateProgress = (startCount, targetCount) => {
    let currentCount = startCount;
    const step = (targetCount - startCount) / 100;

    const animate = () => {
      if (currentCount < targetCount) {
        currentCount += step;
        drawProgress(currentCount);
        requestAnimationFrame(animate);
      } else {
        drawProgress(targetCount);
      }
    };
    requestAnimationFrame(animate);
  };

  useEffect(() => {
    animateProgress(countChallenge - 2, countChallenge - 1);
  }, [countChallenge]);

  // Process the captured image from the webcam 
  const capture = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();

    // Convert the captured webcam image for processing
    const img = new Image();
    img.src = imageSrc;
    img.onload = async () => {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d', { willReadFrequently: true });
      context.drawImage(img, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg');
      const base64Image = dataUrl.split(',')[1];

      try {
        // Send captured image to check challenge
        const challengeResponse = await fetch('http://127.0.0.1:8000/api/challenge_response/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: base64Image, challenge })
        });

        if (!isCorrect && countChallenge <= 4) {
          const result = await challengeResponse.json(); 
          setIsCorrect(result.result);
          setCountFrame(prev => prev + 1);

          // If more than 50 frames and not correct, then change challenge
          if (countFrame >= 50) {
            setCountChallenge(prev => prev + 1);
            setCountFrame(0);
            if (countChallenge < 4) randomChallengeResponse(challenge);
          }
        } else if (isCorrect && countChallenge <= 4) {
          setCountFrame(prev => prev + 1);
          if (countFrame === 10){
            // When the first challenge is passed, send the face image for verification against the ID card
            if (countCorrect === 0) {
              setFacePortrait(dataUrl);
              const reader = new FileReader();
              reader.readAsDataURL(frontImage.file);
              reader.onloadend = async () => {
                const base64FrontImage = reader.result.split(',')[1];

                // Send image for face verification
                const faceResponse = await fetch('http://127.0.0.1:8000/api/face_verification/', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ cam_image: base64Image, card_image: base64FrontImage })
                });
                setFaceResult(await faceResponse.json());
              };
            }
            setCountChallenge(prev => prev + 1);
            setCountCorrect(prev => prev + 1);
            if (countChallenge < 4) randomChallengeResponse(challenge);
            setIsCorrect(false);
          }
        }

        // When all challenges are completed, display the result
        if (countChallenge === 5) {
          const challengeResult = countCorrect === 4 ? 'Không phát hiện giả mạo' : 'Phát hiện giả mạo';
          setIsCapturing(false);
          setInstruction('Hoàn thành xác thực');

          setTimeout(() => {
            navigate('/view-result', { state: { frontImage, backImage, faceResult, facePortrait, challengeResult } });
          }, 2000);
        }
      } catch (error) {
        console.error('Error sending image:', error);
      }
    };
  }, [isCorrect, countCorrect, countFrame, challenge, countChallenge]);

  // Control the image capture frequency 
  useEffect(() => {
    let interval;
    if (isCapturing) interval = setInterval(capture, 200);
    return () => clearInterval(interval);
  }, [capture, isCapturing]);

  // Start the verification process 
  const startCapture = () => {
    setIsButtonDisabled(true);
    setInstruction(3);
    const countdownInterval = setInterval(() => {
      setInstruction(prev => {
        if (prev === 1) {
          clearInterval(countdownInterval);
          setIsCapturing(true);
          return 'Hướng mặt gần vào giữa';
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Reset the frame count when the result is correct
  useEffect(() => {
    setCountFrame(0);
  }, [isCorrect]);

  return (
    <div id="capture-face-frame">
      {/* Progress bar */}
      <div id="process-1" />
      <div id="process-2" />
      <div id="process-3" />
      <div id="connect-1-2" />
      <div id="connect-2-3" />
      <span id="text-1">1</span>
      <span id="text-2">2</span>
      <span id="text-3">3</span>
  
      {/* Webcam and canvas area */}
      <div id="web-cam">
        <Webcam audio={false} ref={webcamRef} screenshotFormat="image/jpeg" />
        <canvas ref={canvasRef} style={{ display: 'none' }} width={550} height={550} />
        <canvas
          ref={progressCanvasRef}
          style={{ position: 'absolute', top: 0, left: 0 }}
          width={550}
          height={550}
        />
      </div>
  
      {/* Start verification button */}
      <button id="start-button" onClick={startCapture} disabled={isButtonDisabled}>
        <span id="text-start-button" className={instruction > 0 ? 'countdown' : 'default'}>
          {instruction}
        </span>
      </button>
  
      {/* End page spacer */}
      <span id="space-end-page-2" />
    </div>
  );
  
};

export default CaptureFace;

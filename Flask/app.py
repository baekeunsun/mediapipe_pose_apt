from flask import Flask,render_template,Response
import cv2
import mediapipe as mp
import winsound as ws

### WSGI Application
app=Flask(__name__)
camera=cv2.VideoCapture(0)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

word = ""

def beepsound():
    fr = 1000    # range : 37 ~ 32767
    du = 500     # 1000 ms ==1second
    ws.Beep(fr, du) # winsound.Beep(frequency, duration)


def generate_frames():
    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        
        flag = False

        while True:

            ## read the camera frame
            success, frame = camera.read()
            if not success:
                continue
            else:
                    
                
                frame.flags.writeable = False    # 성능 향상을 위해 이미지 쓰기불가시켜 참조로 전달
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame)   # pose 검출

                frame.flags.writeable = True    # 다시 쓰기 가능으로 변경
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                min_i = 1.0

                if results.pose_landmarks:
                    for i in results.pose_landmarks.landmark:
                        min_i = min(min_i, i.visibility)

                    if min_i > 0.6: # 0.5 ~ 0.6사이가 좋을듯
                        flag = True

                    if flag:
                        word = "thank you"
                        mp_drawing.draw_landmarks(
                            frame,
                            results.pose_landmarks,
                            mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                    else:
                        word = "please go back"


                frame = cv2.flip(frame, 1)
                frame = cv2.putText(frame, word,(100,70),cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,0,0),3,cv2.LINE_AA)

                ret, buffer =cv2.imencode('.jpg',frame)
                frame = buffer.tobytes()

            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ =='__main__':
    app.run(debug=True)

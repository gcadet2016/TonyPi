#!/usr/bin/env python3.10
# OpevCVとbottleによる簡単なMotion JPEGストリーミングWeb表示コード
# Non testé - modification du port de 8080 à 8099

import cv2
from bottle import route, run, response
 
@route('/', method="GET")
def top():
    return '<img src="http://192.168.1.52:8099/streaming"/>'
 
@route('/streaming')
def streaming():
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    except TypeError:
        cap = cv2.VideoCapture(0)
 
    if cap.isOpened() is False:
        raise IOError
     
    print("VideoCapture OK!")
 
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("default fps=", fps)
 
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    #cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
 
    # コマンド v4l2-ctl --list-formats-ext で使用可能な解像度を確認しておく
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
 
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("Camera now fps=", fps)
 
    response.set_header('Content-type', 'multipart/x-mixed-replace;boundary=--frame')
 
    while True:
        ret, img = cap.read()
        if not ret:
            continue
 
        ret, jpeg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 100])
 
        if not ret:
            continue
        # Motion JPEG(MJPG) をブラウザへ送信
        yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
 
    cap.release()
 
if __name__ == '__main__':
    print('Starting run')
    run(
        host='192.168.1.52',
        port=8099,
        reloader=True,
        debug=True)
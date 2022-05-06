# app.py
import os
from flask import Flask, request

from s3_connect import s3_connection, s3_put_object
from s3_config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION

app = Flask(__name__)
s3 = s3_connection()


@app.route('/fileUpload', methods=['POST'])
def upload():
    f = request.files['file']
    f.save("./temp")

    ret = s3_put_object(s3, AWS_S3_BUCKET_NAME, "./temp", "ar_image/temp")
    if ret:
        return "파일 저장 성공"
    else:
        return "파일 저장 실패"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI图片处理 - 网页版
拼多多反AI检测图片处理工具，运营通过浏览器上传图片即可使用。
"""
import os, io, random, json, zipfile, uuid, atexit, shutil
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import piexif
from flask import Flask, render_template, request, send_file, jsonify

# ==================== 配置（固定参数，无需用户选择） ====================
CAMERA = {
    "Make": b"Apple",
    "Model": b"iPhone 14 Pro",
    "LensMake": b"Apple",
    "LensModel": b"iPhone 14 Pro back triple camera 6.86mm f/1.78",
    "FNumber": (178, 100),
    "FocalLength": (686, 100),
    "ISO": [100, 125, 160, 200, 250, 320, 400, 500],
    "ExposureTime": [(1, 100), (1, 120), (1, 60), (1, 80), (1, 50)],
    "Software": b"16.5.1",
    "SerialNumber": b"F17L9X7X",
    "LensSerial": b"AXB123456",
    "Body": b"iPhone 14 Pro",
    "date_range_days": 30,
}

# ==================== 图像处理函数（移植自原脚本） ====================

def add_realistic_noise(img_array, iso=400):
    """模拟真实CMOS传感器噪点"""
    base_noise = 2.0
    iso_factor = (iso / 100) * 0.8
    noise_intensity = base_noise + iso_factor
    luminance_noise = np.random.normal(0, noise_intensity * 0.7, img_array.shape[:2])
    chroma_noise = np.random.normal(0, noise_intensity * 0.4, img_array.shape[:2])
    noisy_img = img_array.astype(np.float32)
    for i in range(3):
        noisy_img[:, :, i] += luminance_noise
    noisy_img[:, :, 0] += chroma_noise * 0.8
    noisy_img[:, :, 2] += chroma_noise * 1.2
    return np.clip(noisy_img, 0, 255).astype(np.uint8)


def simulate_jpeg_compression_artifacts(img):
    """模拟JPEG压缩痕迹"""
    img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    img = Image.open(buffer)
    return img


def add_lens_chromatic_aberration(img):
    """添加镜头色差"""
    r, g, b = img.split()
    r = r.transform(img.size, Image.AFFINE, (1, 0, 0.8, 0, 1, 0))
    b = b.transform(img.size, Image.AFFINE, (1, 0, -0.8, 0, 1, 0))
    return Image.merge('RGB', (r, g, b))


def generate_detailed_time():
    """生成随机拍摄时间"""
    days = random.randint(1, CAMERA["date_range_days"])
    base = datetime.now() - timedelta(days=days)
    hour = random.randint(8, 20)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    shoot_time = base.replace(hour=hour, minute=minute, second=second)
    return shoot_time.strftime("%Y:%m:%d %H:%M:%S")


def generate_random_gps():
    """生成随机GPS坐标"""
    locations = [
        (31.2304, 121.4737),
        (39.9042, 116.4074),
        (23.1291, 113.2644),
        (30.5728, 104.0668),
        (29.5630, 106.5516),
    ]
    lat, lon = random.choice(locations)
    lat += random.uniform(-0.01, 0.01)
    lon += random.uniform(-0.01, 0.01)

    def to_dms(value):
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = int(((value - degrees) * 60 - minutes) * 60 * 100)
        return (degrees, 1), (minutes, 1), (seconds, 100)

    return {
        piexif.GPSIFD.GPSLatitude: to_dms(abs(lat)),
        piexif.GPSIFD.GPSLatitudeRef: b'N' if lat >= 0 else b'S',
        piexif.GPSIFD.GPSLongitude: to_dms(abs(lon)),
        piexif.GPSIFD.GPSLongitudeRef: b'E' if lon >= 0 else b'W',
        piexif.GPSIFD.GPSAltitude: (random.randint(10, 100), 1),
    }


def process_image(input_bytes, filename):
    """处理单张图片，返回处理后的JPEG字节"""
    # 打开图片
    img = Image.open(io.BytesIO(input_bytes))
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode in ('RGBA', 'LA'):
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert('RGB')
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size

    # 锐度微调
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(0.95)

    # 添加色差
    img = add_lens_chromatic_aberration(img)

    # 添加传感器噪点
    iso = random.choice(CAMERA["ISO"])
    img_array = np.array(img)
    img_array = add_realistic_noise(img_array, iso=iso)
    img = Image.fromarray(img_array)

    # JPEG压缩痕迹
    img = simulate_jpeg_compression_artifacts(img)

    # EXIF
    shoot_time = generate_detailed_time()
    exp_time = random.choice(CAMERA["ExposureTime"])
    focal = CAMERA["FocalLength"]
    fnum = CAMERA["FNumber"]

    zeroth_ifd = {
        piexif.ImageIFD.Make: CAMERA["Make"],
        piexif.ImageIFD.Model: CAMERA["Model"],
        piexif.ImageIFD.DateTime: shoot_time.encode(),
        piexif.ImageIFD.Software: CAMERA["Software"],
        piexif.ImageIFD.Orientation: 1,
        piexif.ImageIFD.XResolution: (72, 1),
        piexif.ImageIFD.YResolution: (72, 1),
        piexif.ImageIFD.ResolutionUnit: 2,
        piexif.ImageIFD.HostComputer: CAMERA["Body"],
    }

    exif_ifd = {
        piexif.ExifIFD.LensMake: CAMERA["LensMake"],
        piexif.ExifIFD.LensModel: CAMERA["LensModel"],
        piexif.ExifIFD.DateTimeOriginal: shoot_time.encode(),
        piexif.ExifIFD.DateTimeDigitized: shoot_time.encode(),
        piexif.ExifIFD.ISOSpeedRatings: iso,
        piexif.ExifIFD.FNumber: fnum,
        piexif.ExifIFD.ExposureTime: exp_time,
        piexif.ExifIFD.FocalLength: focal,
        piexif.ExifIFD.ExposureProgram: 2,
        piexif.ExifIFD.MeteringMode: 5,
        piexif.ExifIFD.Flash: random.choice([0, 0, 0, 16]),
        piexif.ExifIFD.WhiteBalance: 0,
        piexif.ExifIFD.PixelXDimension: width,
        piexif.ExifIFD.PixelYDimension: height,
        piexif.ExifIFD.SceneCaptureType: 0,
        piexif.ExifIFD.Contrast: 0,
        piexif.ExifIFD.Saturation: 0,
        piexif.ExifIFD.Sharpness: 0,
        piexif.ExifIFD.BodySerialNumber: CAMERA["SerialNumber"],
        piexif.ExifIFD.LensSerialNumber: CAMERA["LensSerial"],
    }

    exif_dict = {
        "0th": zeroth_ifd,
        "Exif": exif_ifd,
        "GPS": generate_random_gps(),
        "1st": {},
        "thumbnail": None
    }

    exif_bytes = piexif.dump(exif_dict)

    # 输出
    out_name = Path(filename).stem + ".jpg"
    out_buf = io.BytesIO()
    img.save(out_buf, 'JPEG', quality=92, exif=exif_bytes)
    out_buf.seek(0)
    return out_name, out_buf.read()


# ==================== Flask Web 服务 ====================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB上限
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'temp')

# 启动时清理旧临时文件
if os.path.exists(app.config['UPLOAD_FOLDER']):
    shutil.rmtree(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': '请选择图片文件'}), 400

    session_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
    total = len([f for f in files if f.filename])

    zip_buf = io.BytesIO()
    processed_count = 0

    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if not f.filename:
                continue
            try:
                img_bytes = f.read()
                out_name, out_data = process_image(img_bytes, f.filename)
                zf.writestr(out_name, out_data)
                processed_count += 1
            except Exception as e:
                zf.writestr(f'_failed_{f.filename}.txt', str(e))

    zip_buf.seek(0)

    # 保存zip到临时目录供下载
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}.zip')
    with open(zip_path, 'wb') as f:
        f.write(zip_buf.read())

    return jsonify({
        'success': True,
        'total': total,
        'processed': processed_count,
        'download': f'/download/{session_id}.zip'
    })


@app.route('/download/<filename>')
def download(filename):
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(zip_path):
        return '文件不存在或已过期', 404
    return send_file(zip_path, as_attachment=True, download_name='processed_images.zip')


@atexit.register
def cleanup():
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)


if __name__ == '__main__':
    print('=' * 50)
    print('AI图片处理工具 - 网页版')
    print('=' * 50)
    print('启动中...')
    # 确保templates目录存在
    tmpl_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(tmpl_dir, exist_ok=True)
    # 启动
    import webbrowser
    webbrowser.open('http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)

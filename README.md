# AI图片处理网页版

将AI生成图片伪装成真实相机拍摄的工具，运营通过浏览器上传图片即可使用。

## 使用方法

方式一：双击 `start.bat`
方式二：命令行执行 `python app.py`

浏览器自动打开 `http://localhost:5000`。

## 功能

- 上传图片后自动处理（添加传感器噪点、镜头色差、JPEG压缩痕迹、EXIF信息）
- 一键下载处理后的ZIP包

## 依赖

```bash
pip install -r requirements.txt
```

## 技术

Flask + Pillow + piexif + numpy

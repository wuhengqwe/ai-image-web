# AI图片处理工具 - 网页版

拼多多反AI检测图片处理工具。

## 在线使用

👉 **https://wuhengqwe.github.io/ai-image-web/**

打开链接，上传图片即可处理，所有操作在浏览器本地完成，不会上传到服务器。

## 功能

- 传感器噪点注入（模拟真实CMOS噪点）
- 镜头色差添加（红蓝通道偏移）
- JPEG压缩痕迹模拟
- 锐度微调
- 完整EXIF信息（相机型号、GPS、序列号等）

## 技术

纯前端实现，使用 Canvas + piexifjs + JSZip。

## 服务端版

`server/` 目录下为 Flask 服务版，需要 Python 环境运行。

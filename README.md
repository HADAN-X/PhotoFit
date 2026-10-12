# 证件照压缩工具

## 中文

选择图片，设置尺寸和文件大小限制，预览并保存压缩后的 JPEG。支持 JPG、PNG、BMP、WebP、TIFF。输出默认保存在原图目录，原图不会被覆盖。

### 使用

1. 在 GitHub 的 **Releases** 页面下载 `证件照压缩工具-Windows-x64.zip`。
2. 解压 ZIP，双击 `证件照压缩工具.exe`。无需安装 Python 或其他依赖。
3. 选择图片，填写可选的最大/最小宽高（像素）和最大文件大小（KB）。留空表示不限制。
4. 可选输出文件夹，然后点击“压缩并保存”。留空时保存到原图目录，文件名添加 `_compressed.jpg`。

### 开发与发布

需要 Python 3.11+。运行 `python -m pip install -r requirements.txt`，再运行 `python src/compressed_gui.py`。推送 `v` 开头的版本标签（如 `v1.0.0`）后，GitHub Actions 会自动构建 Windows 下载包并发布 Release。

## English

Choose an image, set optional size and file-size limits, preview the result, and save it as JPEG. Supports JPG, PNG, BMP, WebP, and TIFF. The output is saved beside the original image by default; the original is never overwritten.

### How to use

1. Download `证件照压缩工具-Windows-x64.zip` from **Releases** on GitHub.
2. Extract the ZIP and run `证件照压缩工具.exe`. No Python or other dependencies are required.
3. Choose an image. Optionally enter minimum/maximum width and height in pixels and a maximum file size in KB. Leave a field blank for no limit.
4. Optionally choose an output folder, then click **Compress and Save**. If no folder is selected, the JPEG is saved beside the original with `_compressed` added to its filename.

### Development and releases

Requires Python 3.11+. Run `python -m pip install -r requirements.txt`, then `python src/compressed_gui.py`. Push a version tag such as `v1.0.0` to build and publish a Windows download through GitHub Actions.

## License

MIT. See [LICENSE](LICENSE).

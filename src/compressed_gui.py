from __future__ import annotations

import io
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps, ImageTk


APP_NAME = "证件照压缩工具"
IMAGE_TYPES = [("图片文件", "*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff"), ("所有文件", "*.*")]


class CompressorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(APP_NAME)
        root.geometry("960x720")
        root.minsize(780, 620)
        self.source = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.max_w = tk.StringVar(value="1000")
        self.max_h = tk.StringVar()
        self.min_w = tk.StringVar()
        self.min_h = tk.StringVar()
        self.max_kb = tk.StringVar(value="200")
        self.status = tk.StringVar(value="请选择一张图片开始")
        self.original_photo = None
        self.result_photo = None
        self.image = None
        self.build_ui()

    def build_ui(self):
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)
        frame = ttk.Frame(root, padding=16)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="输入图片").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(frame, textvariable=self.source).grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Button(frame, text="选择图片…", command=self.choose_image).grid(row=0, column=2, padx=(8, 0), pady=5)
        ttk.Label(frame, text="输出文件夹").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(frame, textvariable=self.output_dir).grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Button(frame, text="浏览…", command=self.choose_output).grid(row=1, column=2, padx=(8, 0), pady=5)
        ttk.Label(frame, text="留空时保存到原图所在文件夹").grid(row=2, column=1, sticky="w", pady=(0, 6))

        opts = ttk.LabelFrame(root, text="压缩限制（像素 / KB；留空表示不限制）", padding=12)
        opts.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        for i in range(10):
            opts.columnconfigure(i, weight=1 if i in (1, 3, 5, 7, 9) else 0)
        entries = [("最大宽", self.max_w), ("最大高", self.max_h), ("最小宽", self.min_w), ("最小高", self.min_h), ("最大文件", self.max_kb)]
        for i, (label, var) in enumerate(entries):
            col = i * 2
            ttk.Label(opts, text=label).grid(row=0, column=col, sticky="e", padx=(0, 5))
            ttk.Entry(opts, textvariable=var, width=10).grid(row=0, column=col + 1, sticky="ew", padx=(0, 12))
        ttk.Label(opts, text="尺寸保持原图比例；最大文件大小按 JPEG 输出控制").grid(row=1, column=0, columnspan=10, sticky="w", pady=(10, 0))

        previews = ttk.Frame(root, padding=(16, 0, 16, 10))
        previews.grid(row=2, column=0, sticky="nsew")
        previews.columnconfigure(0, weight=1)
        previews.columnconfigure(1, weight=1)
        previews.rowconfigure(0, weight=1)
        self.original_box = self.make_preview(previews, 0, "原图")
        self.result_box = self.make_preview(previews, 1, "压缩预览")

        bottom = ttk.Frame(root, padding=(16, 4, 16, 16))
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        ttk.Label(bottom, textvariable=self.status).grid(row=0, column=0, sticky="w")
        self.compress_button = ttk.Button(bottom, text="压缩并保存", command=self.compress)
        self.compress_button.grid(row=0, column=1, padx=(10, 0))

    def make_preview(self, parent, col, title):
        box = ttk.LabelFrame(parent, text=title, padding=8)
        box.grid(row=0, column=col, sticky="nsew", padx=(0, 6) if col == 0 else (6, 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        label = ttk.Label(box, text="尚未载入图片", anchor="center")
        label.grid(row=0, column=0, sticky="nsew")
        info = ttk.Label(box, text="", anchor="center")
        info.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        return label, info

    def choose_image(self):
        path = filedialog.askopenfilename(title="选择要压缩的图片", filetypes=IMAGE_TYPES)
        if not path:
            return
        try:
            image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        except Exception as exc:
            messagebox.showerror("无法打开图片", str(exc))
            return
        self.source.set(path)
        self.image = image
        self.output_dir.set("")
        self.show_preview(image, self.original_box[0], "original_photo")
        self.original_box[1].configure(text=f"{image.width} × {image.height} px  |  {Path(path).stat().st_size / 1024:.1f} KB")
        self.result_box[0].configure(image="", text="设置参数后点击“压缩并保存”")
        self.result_box[1].configure(text="")
        self.status.set("已载入图片。原图不会被覆盖，输出文件名将添加 _compressed")

    def choose_output(self):
        path = filedialog.askdirectory(title="选择输出文件夹")
        if path:
            self.output_dir.set(path)

    def show_preview(self, image, label, attr):
        preview = image.copy()
        preview.thumbnail((430, 390), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(preview)
        setattr(self, attr, photo)
        label.configure(image=photo, text="")

    @staticmethod
    def parse_limit(value, name):
        value = value.strip()
        if not value:
            return None
        try:
            result = int(value)
            if result < 1:
                raise ValueError
            return result
        except ValueError:
            raise ValueError(f"{name}必须是大于 0 的整数，或留空。")

    def compress(self):
        if self.image is None:
            messagebox.showinfo("请选择图片", "请先选择一张图片。")
            return
        try:
            limits = [self.parse_limit(v.get(), n) for v, n in zip(
                (self.max_w, self.max_h, self.min_w, self.min_h, self.max_kb),
                ("最大宽度", "最大高度", "最小宽度", "最小高度", "最大文件大小")
            )]
            max_w, max_h, min_w, min_h, max_kb = limits
            if (min_w and max_w and min_w > max_w) or (min_h and max_h and min_h > max_h):
                raise ValueError("最小尺寸不能大于对应的最大尺寸。")
        except ValueError as exc:
            messagebox.showerror("参数有误", str(exc))
            return
        src = Path(self.source.get())
        outdir = Path(self.output_dir.get()) if self.output_dir.get().strip() else src.parent
        target_w, target_h = self.image.size
        scale_min = max((min_w or 0) / target_w, (min_h or 0) / target_h, 0)
        scale_max = min((max_w or target_w * 100) / target_w, (max_h or target_h * 100) / target_h)
        scale = min(max(1.0, scale_min), scale_max) if (max_w or max_h) else max(1.0, scale_min)
        if scale_min > scale_max:
            scale = scale_max
        size = (max(1, round(target_w * scale)), max(1, round(target_h * scale)))
        result = self.image.resize(size, Image.Resampling.LANCZOS) if size != self.image.size else self.image.copy()
        output = outdir / f"{src.stem}_compressed.jpg"
        self.compress_button.configure(state="disabled")
        self.status.set("正在压缩…")
        threading.Thread(target=self._save_result, args=(result, output, max_kb), daemon=True).start()

    def _save_result(self, result, output, max_kb):
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            if max_kb:
                low, high = 5, 95
                best = None
                while low <= high:
                    q = (low + high) // 2
                    buf = io.BytesIO()
                    result.save(buf, format="JPEG", quality=q, optimize=True, progressive=True)
                    if len(buf.getvalue()) <= max_kb * 1024:
                        best = buf.getvalue()
                        low = q + 1
                    else:
                        high = q - 1
                if best is None:
                    buf = io.BytesIO()
                    result.save(buf, format="JPEG", quality=5, optimize=True, progressive=True)
                    best = buf.getvalue()
            else:
                buf = io.BytesIO()
                result.save(buf, format="JPEG", quality=92, optimize=True, progressive=True)
                best = buf.getvalue()
            output.write_bytes(best)
            self.root.after(0, lambda: self._saved(result, output, len(best), max_kb))
        except Exception as exc:
            self.root.after(0, lambda error=str(exc): self._save_error(error))

    def _saved(self, result, output, byte_count, max_kb):
        self.compress_button.configure(state="normal")
        self.show_preview(result, self.result_box[0], "result_photo")
        self.result_box[1].configure(text=f"{result.width} × {result.height} px  |  {byte_count / 1024:.1f} KB")
        extra = "（图片内容较复杂，已使用最低质量，仍可能超过限制）" if max_kb and byte_count > max_kb * 1024 else ""
        self.status.set(f"已保存：{output}{extra}")

    def _save_error(self, error):
        self.compress_button.configure(state="normal")
        self.status.set("压缩失败")
        messagebox.showerror("压缩失败", error)


def main():
    root = tk.Tk()
    try:
        ttk.Style(root).theme_use("vista")
    except tk.TclError:
        pass
    CompressorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

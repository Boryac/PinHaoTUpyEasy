import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageChops, ImageOps, ImageTk
import os

class ImageBlenderApp:
    def __init__(self, master):
        self.master = master
        master.title("图片混合工具") # 设置窗口标题
        master.geometry("800x700") # 设置窗口初始大小
        master.resizable(False, False) # 禁止调整窗口大小

        self.image_files = [] # 存储选中的图片文件路径
        self.blended_image = None # 存储混合后的PIL图片对象

        # UI选项的变量
        self.bg_mode = tk.StringVar(value="white") # 默认背景模式为白色
        self.invert_colors_var = tk.BooleanVar(value=False) # 默认不反转颜色

        self._create_widgets()

    def _create_widgets(self):
        # --- 文件选择区 ---
        file_frame = ttk.LabelFrame(self.master, text="文件选择", padding="10")
        file_frame.pack(pady=10, padx=20, fill="x")

        ttk.Button(file_frame, text="导入图片", command=self.select_images).pack(pady=5)
        self.file_list_label = ttk.Label(file_frame, text="已选择图片：无", wraplength=700)
        self.file_list_label.pack(pady=5)

        # --- 混合选项区 ---
        options_frame = ttk.LabelFrame(self.master, text="混合选项", padding="10")
        options_frame.pack(pady=10, padx=20, fill="x")

        # 背景模式选择 (Radio Buttons)
        bg_mode_label = ttk.Label(options_frame, text="背景模式:")
        bg_mode_label.pack(anchor="w", pady=5)

        bg_white_radio = ttk.Radiobutton(options_frame, text="白底 (正片叠底)", variable=self.bg_mode, value="white")
        bg_white_radio.pack(anchor="w", padx=20)
        bg_black_radio = ttk.Radiobutton(options_frame, text="黑底 (加亮)", variable=self.bg_mode, value="black")
        bg_black_radio.pack(anchor="w", padx=20)

        # 反转颜色选项 (Checkbox)
        invert_checkbox = ttk.Checkbutton(options_frame, text="混合后反转颜色", variable=self.invert_colors_var)
        invert_checkbox.pack(anchor="w", pady=10)

        # --- 操作按钮区 ---
        action_frame = ttk.Frame(self.master, padding="10")
        action_frame.pack(pady=10, padx=20, fill="x")

        ttk.Button(action_frame, text="开始混合", command=self.blend_and_display).pack(side="left", padx=10)
        # 保存按钮，初始状态为禁用，混合完成后启用
        self.save_button = ttk.Button(action_frame, text="保存图片", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(side="left", padx=10)

        # --- 结果显示区 ---
        result_frame = ttk.LabelFrame(self.master, text="混合结果", padding="10")
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.canvas = tk.Canvas(result_frame, bg="lightgray", bd=2, relief="groove") # 用于显示图片的画布
        self.canvas.pack(fill="both", expand=True)
        # 绑定画布大小改变事件，以便在窗口大小变化时重新绘制图片
        self.canvas.bind("<Configure>", self.resize_image_on_canvas)

    def select_images(self):
        """打开文件对话框，让用户选择图片文件"""
        filetypes = [("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
        files = filedialog.askopenfilenames(
            title="选择图片文件", # 对话框标题
            filetypes=filetypes
        )
        if files:
            self.image_files = list(files)
            # 更新显示已选择图片的文件名
            self.file_list_label.config(text="已选择图片：\n" + "\n".join([os.path.basename(f) for f in self.image_files]))
            self.save_button.config(state=tk.DISABLED) # 重新选择文件后禁用保存按钮
            self.canvas.delete("all") # 清除画布上的旧图片
            self.blended_image = None
        else:
            self.file_list_label.config(text="已选择图片：无")
            self.image_files = []

    def blend_and_display(self):
        """执行图片混合操作并显示结果"""
        if len(self.image_files) < 2:
            messagebox.showwarning("警告", "请至少选择两张图片进行混合。")
            return

        self.blended_image = self._blend_images()

        if self.blended_image:
            # 如果勾选了反转颜色，则应用反转
            if self.invert_colors_var.get():
                self.blended_image = ImageOps.invert(self.blended_image)

            self.display_image_on_canvas(self.blended_image) # 在画布上显示混合结果
            self.save_button.config(state=tk.NORMAL) # 启用保存按钮
        else:
            messagebox.showerror("错误", "图片混合失败，请检查图片文件。")

    def _blend_images(self):
        """核心图片混合逻辑"""
        loaded_images = []
        max_width = 0
        max_height = 0

        # 加载所有图片，并找出所有图片的最大尺寸
        for fpath in self.image_files:
            try:
                img = Image.open(fpath).convert("RGB") # 确保图片为RGB模式
                loaded_images.append(img)
                max_width = max(max_width, img.width)
                max_height = max(max_height, img.height)
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {os.path.basename(fpath)}\n错误信息: {e}")
                return None

        # 根据选择的背景模式设置背景颜色
        bg_color = (255, 255, 255) if self.bg_mode.get() == "white" else (0, 0, 0)

        # 创建一个初始的合成图片，填充选定的背景颜色
        final_composite = Image.new('RGB', (max_width, max_height), bg_color)

        # 遍历所有加载的图片进行混合
        for i, img in enumerate(loaded_images):
            # 创建一个临时画布，尺寸与最终合成图片相同，并填充背景颜色
            temp_img_padded = Image.new('RGB', (max_width, max_height), bg_color)

            # 计算图片居中粘贴的坐标
            x_offset = (max_width - img.width) // 2
            y_offset = (max_height - img.height) // 2

            # 将当前图片粘贴到临时画布上
            temp_img_padded.paste(img, (x_offset, y_offset))

            if i == 0:
                # 第一张图片直接作为合成的起始图
                final_composite = temp_img_padded
            else:
                # 后续图片与当前合成图片进行混合
                if self.bg_mode.get() == "white":
                    # 正片叠底模式 (Multiply)，适用于白底
                    final_composite = ImageChops.multiply(final_composite, temp_img_padded)
                else: # 黑底模式
                    # 加亮模式 (Screen)，适用于黑底
                    final_composite = ImageChops.screen(final_composite, temp_img_padded)
        return final_composite

    def display_image_on_canvas(self, pil_image):
        """在Tkinter画布上显示PIL图片"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if not canvas_width or not canvas_height:
            # 如果画布尚未完全渲染，则等待Configure事件触发
            return

        # 调整图片大小以适应画布，保持宽高比
        img_width, img_height = pil_image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS) # 使用高质量缩放算法
        self.tk_image = ImageTk.PhotoImage(resized_image) # 转换为Tkinter可用的图片格式

        self.canvas.delete("all") # 清除画布上所有内容
        # 计算图片在画布上居中的位置
        x_center = (canvas_width - new_width) // 2
        y_center = (canvas_height - new_height) // 2
        self.canvas.create_image(x_center, y_center, anchor="nw", image=self.tk_image)
        self.canvas.image = self.tk_image # 必须保留引用，否则图片可能不显示

    def resize_image_on_canvas(self, event):
        """当画布大小改变时，重新调整并显示图片"""
        if self.blended_image:
            self.display_image_on_canvas(self.blended_image)

    def save_image(self):
        """保存混合后的图片"""
        if self.blended_image:
            filetypes = [
                ("PNG 文件", "*.png"),
                ("JPEG 文件", "*.jpg"),
                ("所有文件", "*.*")
            ]
            save_path = filedialog.asksaveasfilename(
                title="保存混合图片为", # 保存对话框标题
                defaultextension=".png", # 默认保存为PNG格式
                filetypes=filetypes
            )
            if save_path:
                try:
                    self.blended_image.save(save_path)
                    messagebox.showinfo("成功", f"图片已保存到:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("保存失败", f"保存图片时发生错误:\n{e}")
        else:
            messagebox.showwarning("警告", "没有图片可保存，请先混合图片。")

def main():
    root = tk.Tk()
    try:
        if 'aqua' in ttk.Style().theme_names():
            ttk.Style().theme_use('aqua')
        else:
            ttk.Style().theme_use('clam') # 'clam' 是一个常见的跨平台主题
    except tk.TclError:
        # 如果主题设置失败，则保持默认
        pass

    app = ImageBlenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
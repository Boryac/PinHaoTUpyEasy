import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
from PIL import Image, ImageChops, ImageOps, ImageTk
import os
import random

# --- Constants for Splitting/Scattering Function ---
OUTPUT_SIZE = 3072  # 3 * 1024, ensures divisibility by SMALL_BLOCK_SIZE
SMALL_BLOCK_SIZE = 32  # Smaller block size, e.g., 32x32 pixels
# Calculate grid dimensions
if OUTPUT_SIZE % SMALL_BLOCK_SIZE != 0:
    raise ValueError(f"OUTPUT_SIZE ({OUTPUT_SIZE}) must be perfectly divisible by SMALL_BLOCK_SIZE ({SMALL_BLOCK_SIZE})")
GRID_DIM = OUTPUT_SIZE // SMALL_BLOCK_SIZE  # e.g., 3072 / 32 = 96
N_BLOCKS = GRID_DIM * GRID_DIM  # Total block count, e.g., 96 * 96 = 9216

# --- NetEase Cloud Music Like Styling Colors ---
NCM_RED_ACCENT = "#FF3A3A"
NCM_LIGHT_BG = "#F5F5F5" # Very light gray background
NCM_WHITE_BG = "#FFFFFF"  # Pure white background
NCM_DARK_TEXT = "#333333" # Dark gray text
NCM_MEDIUM_TEXT = "#666666" # Medium gray text
NCM_BORDER_COLOR = "#D3D3D3" # Light gray border
NCM_CANVAS_BG = "#EDEDED" # Slightly darker gray for preview canvas
NCM_HOVER_BG = "#EAEAEA" # Light gray on hover

class ImageProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title("图片处理工具 (分散分割 & 混合叠加)")
        master.geometry("850x750") # Adjusted size for more space
        master.resizable(True, True) # Allow resizing to test scrolling better

        # --- Theme and Styling Configuration ---
        style = ttk.Style()
        try:
            # Try to use a modern theme if available
            # 'clam' is often easier to customize towards a flat look
            if 'clam' in style.theme_names():
                style.theme_use('clam')
            else:
                style.theme_use('default') # Fallback
        except tk.TclError:
            # Fallback if themes are not supported
            pass # Keep default theme

        # --- Configure Fonts ---
        # Get base font family and size from TkDefaultFont or use a fallback
        base_font_family = "sans-serif" # Generic fallback family
        base_font_size = 10 # Default size

        try:
            # CORRECTED: Use nametofont
            default_font_obj = font.nametofont("TkDefaultFont")
            base_font_family = default_font_obj.cget("family")
            # Get the default size from the object, we'll define our size for styles
            # base_font_size = default_font_obj.cget("size") # Don't necessarily use default size

        except tk.TclError:
             # CORRECTED: Catch tk.TclError
             print("Warning: Failed to get TkDefaultFont. Using fallback font family.")
             pass # base_font_family remains "sans-serif"

        # Define custom font objects based on the base family and desired sizes
        self.main_font = None
        self.bold_label_font = None
        self.tab_font = None

        try:
            self.main_font = font.Font(family=base_font_family, size=base_font_size)
            self.bold_label_font = font.Font(family=base_font_family, size=base_font_size, weight="bold")
            self.tab_font = font.Font(family=base_font_family, size=base_font_size + 1) # Slightly larger tabs
            print("Custom font objects created.")
        except tk.TclError:
            print("Warning: Could not create custom font objects. Relying on theme/system defaults.")
            # Fonts remain None, styles will just not apply the font option

        # --- Apply NetEase Cloud Music Inspired Styling ---

        # Basic Frame/Widget Background and Foreground
        # Configure the theme's default styles
        # Apply font only if the main_font object was successfully created
        base_style_config = {'background': NCM_LIGHT_BG, 'foreground': NCM_DARK_TEXT}
        if self.main_font:
             base_style_config['font'] = self.main_font

        style.configure('.', **base_style_config) # Apply light background/dark text to everything by default
        style.configure("TFrame", background=NCM_LIGHT_BG) # Ensure TFrame gets the background

        # Apply font to common text widgets
        if self.main_font:
            style.configure("TLabel", font=self.main_font)
            style.configure("TRadiobutton", font=self.main_font)
            style.configure("TCheckbutton", font=self.main_font)


        # Style for LabelFrame
        style.configure("TLabelframe",
                        background=NCM_WHITE_BG, # White background for content area
                        borderwidth=1,
                        relief="solid",
                        lightcolor=NCM_BORDER_COLOR, # Border color (clam uses light/dark color options)
                        darkcolor=NCM_BORDER_COLOR
                        )
        # Apply bold font to LabelFrame label if created
        label_frame_style_config = {'background': NCM_WHITE_BG, 'foreground': NCM_DARK_TEXT}
        if self.bold_label_font:
            label_frame_style_config['font'] = self.bold_label_font
        style.configure("TLabelframe.Label", **label_frame_style_config)

        # Style for Entry
        style.configure("TEntry",
                        fieldbackground=NCM_WHITE_BG, # White input area
                        foreground=NCM_DARK_TEXT,
                        borderwidth=1,
                        relief="solid",
                        bordercolor=NCM_BORDER_COLOR # Clam theme uses bordercolor
                       )
        # Add focus border color
        style.map("TEntry", bordercolor=[('focus', NCM_RED_ACCENT)])
        if self.main_font: # Apply font to Entry if available
            style.configure("TEntry", font=self.main_font)


        # Style for primary Button (Red Accent)
        style.configure("Accent.TButton",
                        background=NCM_RED_ACCENT,
                        foreground=NCM_WHITE_BG, # White text on red
                        borderwidth=0, # Remove border
                        relief="flat", # Flat look
                        padding=[15, 8] # Increased padding
                       )
        # Add hover effect for accent button
        style.map("Accent.TButton",
                  background=[('active', NCM_RED_ACCENT), ('pressed', NCM_RED_ACCENT)], # Keep red on active/pressed
                  foreground=[('disabled', NCM_MEDIUM_TEXT)], # Disabled text color
                  # Consider a slightly darker red on hover if desired: [('active', '#CC0000')]
                 )
        if self.main_font: # Apply font to Accent Button
             style.configure("Accent.TButton", font=self.main_font)


        # Style for secondary Button (Default/White)
        style.configure("TButton", # Use default TButton for secondary
                        background=NCM_WHITE_BG, # White background
                        foreground=NCM_DARK_TEXT, # Dark text
                        borderwidth=1, # Thin border
                        relief="solid",
                        bordercolor=NCM_BORDER_COLOR,
                        padding=[15, 8] # Increased padding
                       )
        # Add hover effect for default button
        style.map("TButton",
                  background=[('active', NCM_HOVER_BG), ('pressed', NCM_HOVER_BG)], # Light gray on hover/press
                  foreground=[('disabled', NCM_MEDIUM_TEXT)], # Disabled text color
                  bordercolor=[('active', NCM_RED_ACCENT)] # Red border on hover (optional nice touch)
                 )
        if self.main_font: # Apply font to Default Button
            style.configure("TButton", font=self.main_font)


        # Style for Notebook Tabs
        style.configure("TNotebook", background=NCM_LIGHT_BG, borderwidth=0) # Notebook background matches window
        # Apply font to Notebook Tab if created
        tab_style_config = {'background': NCM_LIGHT_BG, 'foreground': NCM_MEDIUM_TEXT, 'padding': [20, 10], 'borderwidth': 0}
        if self.tab_font:
            tab_style_config['font'] = self.tab_font
        style.configure("TNotebook.Tab", **tab_style_config)

        style.map("TNotebook.Tab",
                  background=[('selected', NCM_WHITE_BG)], # Selected tab has white background
                  foreground=[('selected', NCM_RED_ACCENT)] # Selected tab text is red
                 )
        # Note: Achieving the underline indicator for selected tabs with ttk.Style alone
        # is complex and theme-dependent. We are relying on the theme's basic selected state indication (bg/fg change).

        # Style for Scrollbar (theme dependent, basic colors might work)
        style.configure("Vertical.TScrollbar",
                        background=NCM_BORDER_COLOR, # Scrollbar background
                        troughcolor=NCM_LIGHT_BG, # Area scrollbar moves in
                       )
        style.map("Vertical.TScrollbar",
                  background=[('active', NCM_MEDIUM_TEXT)] # Handle color on hover
                 )


        # Configure the main window background to match the light gray
        master.configure(bg=NCM_LIGHT_BG)
        # Note: ttk.Frame used for tabs inherits the background from the notebook/root via style


        # Use a Notebook to manage tabs
        self.notebook = ttk.Notebook(master)
        # Added generous padding around the notebook
        # Notebook padding will be handled by the frame padding inside
        self.notebook.pack(pady=20, padx=20, fill="both", expand=True)

        # Create the two tabs with padding
        # Padding is applied to the frames *within* the tabs
        self.splitting_tab = ttk.Frame(self.notebook, padding="0") # Padding handled by internal elements
        # Blending tab will contain a Canvas for scrolling, padding handled by internal scrollable frame
        self.blending_tab = ttk.Frame(self.notebook, padding="0")

        self.notebook.add(self.splitting_tab, text="图片分散分割 (反色)")
        self.notebook.add(self.blending_tab, text="图片混合叠加")

        # Setup UI for each tab
        self._setup_splitting_tab(self.splitting_tab)
        self._setup_blending_tab_with_scrolling(self.blending_tab)

        # Variables for Blending tab state
        self.blend_image_files = []
        self.blended_image = None # PIL image object for blending result
        # self.canvas_image is now handled within the blending tab setup


    # --- Setup for Splitting/Scattering Tab ---
    def _setup_splitting_tab(self, tab):
        # Configure grid weights for better resizing (though resizable is False, helps internal layout)
        tab.columnconfigure(1, weight=1)

        # Use LabelFrames for grouping with increased padding
        # Apply TLabelframe style
        input_frame = ttk.LabelFrame(tab, text="输入/输出", padding="15")
        input_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15, padx=20) # Increased pady, padx

        # Widgets inside use styles applied globally or specifically
        ttk.Label(input_frame, text="输入图片文件:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        self.split_input_entry = ttk.Entry(input_frame, width=40)
        self.split_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8, padx=10)
        ttk.Button(input_frame, text="浏览...", command=self._select_splitting_input_file).grid(row=0, column=2, sticky=tk.W, pady=8, padx=10)

        ttk.Label(input_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        self.split_output_entry = ttk.Entry(input_frame, width=40)
        self.split_output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=10)
        ttk.Button(input_frame, text="浏览...", command=self._select_splitting_output_directory).grid(row=1, column=2, sticky=tk.W, pady=8, padx=10)


        # Apply TLabelframe style
        options_frame = ttk.LabelFrame(tab, text="处理选项", padding="15")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15, padx=20)

        ttk.Label(options_frame, text="空白区域填充:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        self.split_fill_color_var = tk.StringVar(value="black") # Default black fill
        # Frame for radio buttons - uses default TFrame style
        fill_color_frame = ttk.Frame(options_frame)
        fill_color_frame.grid(row=0, column=1, sticky=(tk.W), pady=8, padx=10)

        ttk.Radiobutton(fill_color_frame, text="黑色 (适合加亮混合)", variable=self.split_fill_color_var, value="black").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(fill_color_frame, text="白色 (适合正片叠底混合)", variable=self.split_fill_color_var, value="white").pack(side=tk.LEFT, padx=10)


        # Apply TLabelframe style
        info_frame = ttk.LabelFrame(tab, text="说明", padding="15")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15, padx=20)

        info_text = f"Borv"
        # Apply TLabel style, adjusted padding/wraplength/justify
        ttk.Label(info_frame, text=info_text, wraplength=750, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)

        # Apply Accent.TButton style
        self.split_process_button = ttk.Button(tab, text="开始处理", style="Accent.TButton")
        self.split_process_button.grid(row=3, column=0, columnspan=3, pady=20)
        self.split_process_button.config(command=self._start_splitting_process)

        # Apply TLabel style, medium gray foreground
        self.split_status_label = ttk.Label(tab, text="状态: 等待中...", foreground=NCM_MEDIUM_TEXT)
        self.split_status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=10, padx=20)


    def _select_splitting_input_file(self):
        """Open file dialog to select input image for splitting"""
        file_path = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=(("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*"))
        )
        if file_path:
            self.split_input_entry.delete(0, tk.END)
            self.split_input_entry.insert(0, file_path)

    def _select_splitting_output_directory(self):
        """Open directory dialog to select output directory for splitting"""
        dir_path = filedialog.askdirectory(
            title="选择输出文件夹"
        )
        if dir_path:
            self.split_output_entry.delete(0, tk.END)
            self.split_output_entry.insert(0, dir_path)

    def _start_splitting_process(self):
        """Get parameters and start the splitting process"""
        input_path = self.split_input_entry.get()
        output_dir = self.split_output_entry.get()
        fill_color = self.split_fill_color_var.get()

        if not input_path:
            messagebox.showwarning("输入错误", "请选择输入图片文件。")
            return
        if not output_dir:
            messagebox.showwarning("输入错误", "请选择输出文件夹。")
            return
        if not os.path.exists(input_path):
             messagebox.showwarning("输入错误", "输入的图片文件不存在。")
             return
        # Check if output_dir is a valid directory path (or empty)
        # os.makedirs will handle creation, but check if an invalid *file* path was entered
        if output_dir and not os.path.isdir(output_dir) and os.path.exists(output_dir):
             messagebox.showwarning("输入错误", "输出路径不是一个有效的文件夹。")
             return

        # Call the core processing function
        self._process_image_random_scattered(input_path, output_dir, fill_color)

    def _process_image_random_scattered(self, input_path, output_dir, fill_color_name):
        """
        Processes the image: invert, split into many small blocks,
        and randomly scatter blocks to 9 images, maintaining original position.
        Updates the status label.
        """
        self.split_status_label.config(text="状态: 正在处理...")
        self.master.update_idletasks() # Update GUI immediately

        try:
            # 1. Read the image
            original_img = Image.open(input_path)

            # 2. Adjust image size to OUTPUT_SIZE x OUTPUT_SIZE
            # Ensure image mode is suitable before resizing/inverting
            if original_img.mode == 'RGBA':
                 # Convert RGBA to RGB, using fill color as background
                 fill = (255, 255, 255) if fill_color_name == "white" else (0,0,0)
                 background = Image.new('RGB', original_img.size, fill)
                 background.paste(original_img, mask=original_img.split()[3]) # 3 is the alpha channel
                 original_img = background
            elif original_img.mode != 'RGB':
                 original_img = original_img.convert('RGB')


            # Use LANCZOS resampling for better quality
            resized_img = original_img.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)

            # 3. Convert to RGB again just in case (should be RGB from step 2)
            if resized_img.mode != 'RGB':
                resized_img = resized_img.convert('RGB')


            # 4. Invert colors
            inverted_img = ImageOps.invert(resized_img)

            # 5. Define fill color (already used for background in step 2 if RGBA)
            if fill_color_name == "black":
                fill_color_rgb = (0, 0, 0)
            else: # white
                fill_color_rgb = (255, 255, 255)


            # 6. Create 9 blank output images
            output_images = []
            for i in range(9):
                new_img = Image.new('RGB', (OUTPUT_SIZE, OUTPUT_SIZE), fill_color_rgb)
                output_images.append(new_img)

            # 7. Generate random assignments of small blocks to output images
            assignments = [i % 9 for i in range(N_BLOCKS)]
            random.shuffle(assignments)

            # 8. Split the inverted image into blocks and paste them
            for row in range(GRID_DIM):
                for col in range(GRID_DIM):
                    linear_index = row * GRID_DIM + col
                    output_img_index = assignments[linear_index]

                    x1 = col * SMALL_BLOCK_SIZE
                    y1 = row * SMALL_BLOCK_SIZE
                    x2 = x1 + SMALL_BLOCK_SIZE
                    y2 = y1 + SMALL_BLOCK_SIZE
                    block_box = (x1, y1, x2, y2)

                    cropped_block = inverted_img.crop(block_box)

                    paste_pos = (x1, y1)
                    output_images[output_img_index].paste(cropped_block, paste_pos)

            # 9. Create output directory if it doesn't exist and save images
            os.makedirs(output_dir, exist_ok=True)

            for i in range(9):
                output_filename = f"part_{i+1}.png"
                output_path = os.path.join(output_dir, output_filename)
                output_images[i].save(output_path)
                self.split_status_label.config(text=f"状态: 已保存 {output_filename}")
                self.master.update_idletasks() # Update GUI immediately

            self.split_status_label.config(text="状态: 处理完成！")
            messagebox.showinfo("完成", "图片分散分割已完成！\n文件保存在: " + output_dir)

        except FileNotFoundError:
            self.split_status_label.config(text="状态: 错误 - 未找到文件")
            messagebox.showerror("错误", "未找到输入的图片文件。")
        except Exception as e:
            self.split_status_label.config(text=f"状态: 错误 - {e}")
            messagebox.showerror("处理错误", f"处理图片时发生错误: {e}")
        finally:
            # Ensure status is updated even on error
             self.master.update_idletasks()


    # --- Setup for Blending Tab (with Scrolling) ---
    def _setup_blending_tab_with_scrolling(self, tab):
        # Variables for Blending tab state (defined here as part of this tab's setup)
        self.blend_image_files = []
        self.blended_image = None
        self.blend_preview_canvas_image = None # Reference for the PhotoImage on the preview canvas
        self.blend_bg_mode = tk.StringVar(value="white")
        self.blend_invert_colors_var = tk.BooleanVar(value=False)


        # Create Canvas and Scrollbar
        # Set Canvas background to light gray
        self.blend_canvas_container = tk.Canvas(tab, borderwidth=0, highlightthickness=0, bg=NCM_LIGHT_BG) # Canvas for scrolling
        # Apply Scrollbar style
        self.blend_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.blend_canvas_container.yview, style="Vertical.TScrollbar")

        # Layout Canvas and Scrollbar in the tab frame
        self.blend_scrollbar.pack(side="right", fill="y")
        self.blend_canvas_container.pack(side="left", fill="both", expand=True)

        # Link Canvas to Scrollbar
        self.blend_canvas_container.config(yscrollcommand=self.blend_scrollbar.set)

        # Create the Frame inside the Canvas that will hold all the content
        # Apply TFrame style (light background) and padding
        self.blend_scrollable_frame = ttk.Frame(self.blend_canvas_container, padding="25") # Padding for content within the scrollable frame

        # Use create_window to put the frame inside the canvas
        # The window must expand with the content frame's size changes
        self.blend_canvas_window = self.blend_canvas_container.create_window((0, 0), window=self.blend_scrollable_frame, anchor="nw")

        # Bind events to update the scrollregion when the inner frame changes size
        self.blend_scrollable_frame.bind("<Configure>", self._on_blend_scrollable_frame_configure)
        # Bind event to update the inner frame's width when the canvas changes size
        self.blend_canvas_container.bind("<Configure>", self._on_blend_canvas_configure)


        # --- Now add all original blending UI elements to self.blend_scrollable_frame ---

        # File Selection Area - Apply TLabelframe style
        file_frame = ttk.LabelFrame(self.blend_scrollable_frame, text="文件选择", padding="15")
        file_frame.pack(pady=15, padx=20, fill="x")

        # Apply TButton style
        ttk.Button(file_frame, text="导入图片", command=self._select_blending_images).pack(pady=8, padx=10) # Added padx
        # Apply TLabel style, adjusted padding/wraplength/justify
        self.blend_file_list_label = ttk.Label(file_frame, text="已选择图片：无", wraplength=700, justify=tk.LEFT)
        self.blend_file_list_label.pack(anchor=tk.W, pady=8, padx=10)

        # Blending Options Area - Apply TLabelframe style
        options_frame = ttk.LabelFrame(self.blend_scrollable_frame, text="混合选项", padding="15")
        options_frame.pack(pady=15, padx=20, fill="x")

        # Background mode selection (Radio Buttons) - Apply TLabel style
        bg_mode_label = ttk.Label(options_frame, text="混合模式:")
        bg_mode_label.pack(anchor="w", pady=8, padx=10)

        # Apply TRadiobutton style
        bg_white_radio = ttk.Radiobutton(options_frame, text="白底 (正片叠底/Multiply)", variable=self.blend_bg_mode, value="white")
        bg_white_radio.pack(anchor="w", padx=30)
        bg_black_radio = ttk.Radiobutton(options_frame, text="黑底 (加亮/Screen)", variable=self.blend_bg_mode, value="black")
        bg_black_radio.pack(anchor="w", padx=30)

        # Invert colors option (Checkbox) - Apply TCheckbutton style
        invert_checkbox = ttk.Checkbutton(options_frame, text="混合后反转颜色", variable=self.blend_invert_colors_var)
        invert_checkbox.pack(anchor="w", pady=10, padx=10)

        # Action Buttons Area - Apply TFrame style
        action_frame = ttk.Frame(self.blend_scrollable_frame, padding="10")
        action_frame.pack(pady=15, padx=20, fill="x")

        # Apply Accent.TButton style for primary, TButton for secondary
        ttk.Button(action_frame, text="开始混合并预览", command=self._blend_and_display, style="Accent.TButton").pack(side="left", padx=10)
        self.blend_save_button = ttk.Button(action_frame, text="保存结果", command=self._save_blended_image, state=tk.DISABLED) # Default TButton style
        self.blend_save_button.pack(side="left", padx=10)

        # Result Display Area (Canvas for preview) - Apply TLabelframe style
        result_frame = ttk.LabelFrame(self.blend_scrollable_frame, text="混合结果预览", padding="15")
        # Use fill="x" for better scrolling predictability.
        result_frame.pack(pady=15, padx=20, fill="x")

        # The original blend_canvas is now the preview canvas
        # Set preview canvas background to a distinct light gray
        self.blend_preview_canvas = tk.Canvas(result_frame, bg=NCM_CANVAS_BG, bd=1, relief="solid", highlightthickness=0) # Solid border for canvas, remove highlight border
        # Give the preview canvas a minimum size so it's visible and interactable even without an image
        self.blend_preview_canvas.config(width=500, height=300) # Set a default/min size
        self.blend_preview_canvas.pack(fill="both", expand=True, padx=10, pady=10) # Increased inner padding, expand=True inside result_frame

        # Bind canvas resize event to redraw image
        self.blend_preview_canvas.bind("<Configure>", self._resize_blended_image_on_canvas)


    def _on_blend_scrollable_frame_configure(self, event):
        """Update the scrollregion of the canvas when the inner frame changes size."""
        # Get the requested size of the inner frame (includes all packed widgets)
        height = self.blend_scrollable_frame.winfo_reqheight()

        # Use the canvas width for the scrollregion width to allow horizontal fill
        canvas_width = self.blend_canvas_container.winfo_width()

        # Configure the scrollregion of the canvas to cover the entire frame
        # Adjust scrollregion to match the frame's dimensions
        self.blend_canvas_container.config(scrollregion=(0, 0, canvas_width, height))

        # Ensure the inner frame's width matches the canvas width when the frame resizes vertically
        # This is also handled by _on_blend_canvas_configure, but doing it here ensures the width is
        # correct right after the height calculation.
        if canvas_width > 0:
             self.blend_canvas_container.itemconfig(self.blend_canvas_window, width=canvas_width)


    def _on_blend_canvas_configure(self, event):
        """Update the width of the inner frame when the canvas changes size."""
        canvas_width = event.width
        # Set the width of the window (which contains the scrollable frame) to the canvas width
        # This ensures the inner frame fills the canvas horizontally.
        if canvas_width > 0: # Avoid setting width to 0 initially
            self.blend_canvas_container.itemconfig(self.blend_canvas_window, width=canvas_width)

        # Also update scrollregion width here, as canvas width has changed
        # Get the current height of the scrollable frame
        frame_height = self.blend_scrollable_frame.winfo_reqheight()
        self.blend_canvas_container.config(scrollregion=(0, 0, canvas_width, frame_height))


        # Re-display the blended image on the preview canvas if it exists,
        # as the canvas dimensions may have changed, affecting scaling.
        self._resize_blended_image_on_canvas(None) # Pass None as event, it's not used in the method


    def _select_blending_images(self):
        """Open file dialog to select image files for blending"""
        filetypes = [("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
        files = filedialog.askopenfilenames(
            title="选择要混合的图片文件",
            filetypes=filetypes
        )
        if files:
            self.blend_image_files = list(files)
            # Update label with selected filenames
            # Limit the displayed filenames to prevent extremely long labels
            display_limit = 8 # Display first 8 filenames, plus a summary if more
            if len(self.blend_image_files) <= display_limit:
                label_text = "已选择图片：\n" + "\n".join([os.path.basename(f) for f in self.blend_image_files])
            else:
                label_text = "已选择图片：\n" + "\n".join([os.path.basename(f) for f in self.blend_image_files[:display_limit]]) + \
                             f"\n... 共 {len(self.blend_image_files)} 张图片"

            self.blend_file_list_label.config(text=label_text)
            self.blend_save_button.config(state=tk.DISABLED) # Disable save button when new files are selected
            self.blend_preview_canvas.delete("all") # Clear preview canvas
            self.blended_image = None
            self.blend_preview_canvas_image = None # Clear reference
             # Author boryac
        else:
            self.blend_file_list_label.config(text="已选择图片：无")
            self.blend_image_files = []
            self.blend_save_button.config(state=tk.DISABLED)
            self.blend_preview_canvas.delete("all")
            self.blended_image = None
            self.blend_preview_canvas_image = None


    def _blend_and_display(self):
        """Perform image blending and display the result"""
        if len(self.blend_image_files) < 2:
            messagebox.showwarning("警告", "请至少选择两张图片进行混合。")
            return

        # Add status text to preview canvas during processing
        canvas_width = self.blend_preview_canvas.winfo_width()
        canvas_height = self.blend_preview_canvas.winfo_height()
        if canvas_width > 0 and canvas_height > 0:
            self.blend_preview_canvas.delete("all")
            # Use the main font for status text if available, otherwise default
            status_font = self.main_font if self.main_font else ('TkDefaultFont', 14)
            self.blend_preview_canvas.create_text(canvas_width//2, canvas_height//2,
                                      text="正在混合...", fill=NCM_MEDIUM_TEXT, font=status_font) # Use themed color
            self.master.update_idletasks() # Update GUI immediately


        self.blended_image = self._perform_blending()

        self.blend_preview_canvas.delete("all") # Clear status text


        if self.blended_image:
            # Apply inversion if checkbox is checked
            if self.blend_invert_colors_var.get():
                self.blended_image = ImageOps.invert(self.blended_image)

            self._display_blended_image_on_canvas(self.blended_image) # Display result on preview canvas
            self.blend_save_button.config(state=tk.NORMAL) # Enable save button
        else:
            messagebox.showerror("错误", "图片混合失败，请检查图片文件。")

    def _perform_blending(self):
        """Core image blending logic"""
        loaded_images = []
        max_width = 0
        max_height = 0

        # Load all images and find maximum dimensions
        for fpath in self.blend_image_files:
            try:
                img = Image.open(fpath)
                # Ensure the image is in a mode compatible with blending (e.g., RGB)
                # Convert RGBA to RGB, handling transparency
                if img.mode == 'RGBA':
                    # Get blend background color for transparency handling
                    # Note: The actual blend is done on RGB images. The background color
                    # here is only used if an RGBA image needs to be flattened to RGB.
                    # The true blend background is used when creating the initial final_composite image.
                    temp_bg_color = (255, 255, 255) if self.blend_bg_mode.get() == "white" else (0, 0, 0)
                    background = Image.new('RGB', img.size, temp_bg_color)
                    # Use img.split()[-1] to get the alpha channel (last channel)
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                     img = img.convert('RGB')

                loaded_images.append(img)
                max_width = max(max_width, img.width)
                max_height = max(max_height, img.height)
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {os.path.basename(fpath)}\n错误信息: {e}")
                return None

        if not loaded_images:
            return None

        # Set background color based on selected mode for the composite image
        bg_color = (255, 255, 255) if self.blend_bg_mode.get() == "white" else (0, 0, 0)

        # Create an initial composite image with the selected background color and max dimensions
        final_composite = Image.new('RGB', (max_width, max_height), bg_color)

        # Blend all loaded images
        for i, img in enumerate(loaded_images):
             # Authorboryac
            temp_img_padded = Image.new('RGB', (max_width, max_height), bg_color)

            # Calculate coordinates to paste the image centered on the temporary canvas
            x_offset = (max_width - img.width) // 2
            y_offset = (max_height - img.height) // 2

            # Paste the current image onto the temporary canvas
            temp_img_padded.paste(img, (x_offset, y_offset))

            if i == 0:
                # The first image (padded) is the base
                 final_composite = temp_img_padded
            else:
                # Blend subsequent images with the current composite
                # ImageChops functions require images of the same size and mode
                if self.blend_bg_mode.get() == "white":
                    # Multiply blend mode (suitable for white background)
                    final_composite = ImageChops.multiply(final_composite, temp_img_padded)
                else: # Black background mode (Screen)
                    # Screen blend mode (suitable for black background)
                    final_composite = ImageChops.screen(final_composite, temp_img_padded)

        return final_composite

    def _display_blended_image_on_canvas(self, pil_image):
        """Display the PIL image on the Tkinter preview canvas"""
        canvas_width = self.blend_preview_canvas.winfo_width()
        canvas_height = self.blend_preview_canvas.winfo_height()

        if not canvas_width or not canvas_height:
            # If canvas is not yet rendered or has zero size, return
            self.blend_preview_canvas.delete("all")
            self.blend_preview_canvas_image = None
            return


        # Resize image to fit canvas while maintaining aspect ratio
        img_width, img_height = pil_image.size
        # Calculate aspect ratio to fit within canvas bounds, leaving some border
        margin = 30 # Increased margin around the image inside the canvas
        available_width = canvas_width - margin
        available_height = canvas_height - margin

        if available_width <= 0 or available_height <= 0:
             self.blend_preview_canvas.delete("all")
             self.blend_preview_canvas_image = None
             return

        ratio = min(available_width / img_width, available_height / img_height)

        # Ensure image doesn't get scaled up unnecessarily if it's smaller than canvas and fits
        if ratio > 1:
             ratio = 1 # Don't upscale beyond original size

        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        # Avoid issues with zero or negative size after scaling
        if new_width <= 1 or new_height <= 1: # Use 1 instead of 0 to handle potential edge cases
             self.blend_preview_canvas.delete("all")
             self.blend_preview_canvas_image = None
             return

        try:
            # Use LANCZOS for quality
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.blend_preview_canvas_image = ImageTk.PhotoImage(resized_image) # Convert to Tkinter format
        except Exception as e:
             messagebox.showerror("显示错误", f"缩放图片以在画布中显示时发生错误:\n{e}")
             self.blend_preview_canvas.delete("all")
             self.blend_preview_canvas_image = None
             return

        # Use self.blend_preview_canvas for drawing
        self.blend_preview_canvas.delete("all") # Clear canvas
        # Calculate position to center the image on the canvas
        x_center = (canvas_width - new_width) // 2
        y_center = (canvas_height - new_height) // 2
        self.blend_preview_canvas.create_image(x_center, y_center, anchor="nw", image=self.blend_preview_canvas_image)
        # Keep a reference is handled by self.blend_preview_canvas_image


    def _resize_blended_image_on_canvas(self, event):
        """Redraw image on preview canvas when preview canvas size changes"""
        if self.blended_image:
            # Ensure this happens *after* the canvas actually has dimensions
            self._display_blended_image_on_canvas(self.blended_image)


    def _save_blended_image(self):
        """Save the blended image"""
        if self.blended_image:
            filetypes = [
                ("PNG 文件", "*.png"),
                ("JPEG 文件", "*.jpg"),
                ("所有文件", "*.*")
            ]
            save_path = filedialog.asksaveasfilename(
                title="保存混合图片为",
                defaultextension=".png",
                filetypes=filetypes
            )
            if save_path:
                try:
                     # Author-boryac
                    if self.blended_image.mode != 'RGB':
                        img_to_save = self.blended_image.convert('RGB')
                    else:
                         img_to_save = self.blended_image

                    # Add extension if missing, based on chosen type
                    # Check if path has an extension, and if not, add the default one (.png)
                    if not os.path.splitext(save_path)[1]:
                        save_path += ".png"

                    img_to_save.save(save_path)
                    messagebox.showinfo("成功", f"图片已保存到:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("保存失败", f"保存图片时发生错误:\n{e}")
        else:
            messagebox.showwarning("警告", "没有图片可保存，请先混合图片。")


 # Author boryac
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
 # Author boryac
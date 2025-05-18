# 祝你拼好图 / Image Processing Tool

**版本：V1.0.1 正式版 / Version: V1.0.1 Release**

## 项目描述 / Description

这是一个使用 Python 和 Tkinter 构建的桌面应用程序，专注于两个核心图片处理功能：将一张反色图片分解为多个部分以便后续重组，以及将多张图片混合叠加。

This is a desktop application built with Python and Tkinter, focusing on two core image processing functionalities: breaking down an inverted image into multiple parts for later reassembly, and blending multiple images together. 

## 主要功能 / Features

*   **图片分散分割 (反色) / Image Scatter Splitting (Inverted):**
    *   将输入的图片缩放/裁剪至指定大小 (默认为 3072x3072) 并进行反色处理。
    *   将反色图片分割为 {GRID_DIM}x{GRID_DIM} 个小块 (默认 96x96 个 32x32 像素小块)。
    *   将这些小块**随机**分散到 9 张输出图片中，每张图包含约 {N_BLOCKS // 9} 个小块。
    *   小块在输出图中保持其**原始位置**，其余部分填充选定的纯色 (黑色或白色)。
    *   通过对 9 张输出图进行恰当的混合叠加 (黑底用加亮/Screen，白底用正片叠底/Multiply)，可以完美重组出原始的反色图。
    *   Resizes/crops the input image to a specified size (default 3072x3072), then inverts its colors.
    *   Splits the inverted image into {GRID_DIM}x{GRID_DIM} small blocks (default 96x96 blocks of 32x32 pixels).
    *   **Randomly** scatters these blocks into 9 separate output images, each containing approximately {N_BLOCKS // 9} blocks.
    *   Blocks retain their **original position** within the output images; remaining areas are filled with a selected solid color (black or white).
    *   By blending the 9 output images using the appropriate blend mode (Screen for black fill, Multiply for white fill), the original inverted image can be perfectly reconstructed.

*   **图片混合叠加 / Image Blending Overlay:**
    *   支持导入任意数量的图片文件。
    *   自动按最大尺寸对齐并填充背景色 (白色或黑色) 后，进行顺序混合叠加。
    *   支持正片叠底 (Multiply) 和加亮 (Screen) 两种混合模式。
    *   可选地对最终混合结果进行反色处理。
    *   提供混合结果的实时预览，并自动适配预览区域大小。
    *   支持将混合结果保存为 PNG 或 JPEG 文件。
    *   Supports importing any number of image files.
    *   Automatically aligns and pads images to the maximum dimensions using a selected background color (white or black), then performs sequential blending overlay.
    *   Supports Multiply and Screen blend modes.
    *   Optionally inverts the final blended result.
    *   Provides a real-time preview of the blended result, automatically scaling to fit the preview area.
    *   Allows saving the blended result as PNG or JPEG files.

*   **用户界面 / User Interface:**
    *   基于 Tkinter 和 ttk 构建的标签页式简洁界面。
    *   混合叠加标签页支持垂直滚动，优化大量图片选择时的体验。
    *   Tabbed simple interface built with Tkinter and ttk.
    *   Blending tab includes vertical scrolling for a better experience when selecting many images.

## 系统要求 / Requirements

*   Python 3.7+ (推荐 / Recommended)
*   Pillow 库 (`pip install Pillow`)
*   Tkinter (通常随标准 Python 安装自带 / Usually included with standard Python installations)
*   具有图形界面的操作系统 / A graphical desktop environment


## 使用方法 / Usage

启动应用后，请切换到 "图片分散分割 (反色)" 或 "图片混合叠加" 标签页，根据界面上的提示选择文件、设置选项并点击处理按钮。

After starting the application, switch to the "图片分散分割 (反色)" or "图片混合叠加" tab. Follow the instructions on the interface to select files, set options, and click the process buttons.

## 许可证 / License

本项目为开源项目，遵循以下条款：

*   允许**个人及商业用途**。
*   允许进行**修改和二次开发**。
*   在**分发**本项目原始版本或修改后的版本时 (包括可执行文件或源代码)，**必须清晰地注明来源**，应包含原作者和项目地址，注明位置应醒目 (例如：README 文件、应用关于窗口、源代码文件头部)。

**所需注明来源信息:**
*   原作者：boryac
*   项目地址：https://github.com/Boryac/PinHaoTUpyEasy

---

This project is open-source and available under the terms described below:

*   You are free to use this software for **personal or commercial purposes**.
*   You are free to **modify** this software and create derivative works.
*   If you **distribute** the original or modified versions of this software (including binaries or source code), **you must include a clear attribution** in a prominent place (e.g., README file, application's About box, source code headers) mentioning the original author and the project's source address.

**Required Attribution Elements:**
*   Original Author: boryac
*   Project Source Address: https://github.com/Boryac/PinHaoTUpyEasy

## 作者 / Author

boryac

## 项目地址 / Project Address

https://github.com/Boryac/PinHaoTUpyEasy

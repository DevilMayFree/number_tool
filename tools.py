def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def center_dialog(window, root, modal_width, modal_height):
    # 获取主窗口的位置和大小
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    # 计算模态窗口的位置
    x = root_x + (root_width - modal_width) // 2
    y = root_y + (root_height - modal_height) // 2

    # 设置模态窗口的大小和位置
    window.geometry(f"{modal_width}x{modal_height}+{x}+{y}")

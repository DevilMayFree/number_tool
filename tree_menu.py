import tkinter as tk
from tkinter import simpledialog, messagebox

def create_context_menu(root, tree):
    def on_right_click(event):
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            menu.post(event.x_root, event.y_root)

    def copy():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")
        root.clipboard_clear()
        root.clipboard_append(values[0])
        root.update()  # Keep the clipboard content

    def copy_row():
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")
        clipboard_content = ",".join(values)
        if clipboard_content.endswith(','):
            clipboard_content = clipboard_content[:-1]

        root.clipboard_clear()
        root.clipboard_append(clipboard_content)
        root.update()  # Keep the clipboard content

    def add_remark():
        selected_item = tree.selection()[0]
        remark = simpledialog.askstring("添加备注", "添加备注:")
        if remark:
            tree.item(selected_item, tags=(remark,))
            # 这里写入文件
            messagebox.showinfo("添加备注", f"备注已添加: {remark}")

    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="复制号码", command=copy)
    menu.add_command(label="复制整行", command=copy_row)
    menu.add_command(label="添加备注", command=add_remark)

    return menu, on_right_click

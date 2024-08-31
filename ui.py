import threading
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

from ttkbootstrap import Style

from constant import default_tip, add_input_empty, number_exist, expiry_days_number, tip_label
from tools import center_window, center_dialog
from tree_menu import create_context_menu
from type import EventType
from worker import Worker, columns


class Ui:
    def __init__(self, root):
        self.add_window = None
        self.style = None
        self.tip_label = None
        self.add_number_entry = None
        self.add_team_entry = None
        self.add_code_entry = None
        self.add_expiration_entry = None
        self.add_remark_entry = None
        self.tree = None

        self.root = root
        self.setup_ui()

        # 创建 Worker 实例，传递回调函数
        self.worker = Worker(root, self.update_ui)
        # 启动工作线程
        self.thread = threading.Thread(target=self.worker.run, daemon=True)
        self.thread.start()

    def setup_ui(self):
        self.root.title("号码管理器v1.0")

        # style = ttk.Style()
        # 设置 ttkbootstrap 样式
        self.style = Style()
        # light
        # cosmo - flatly - journal - literal - lumen - minty - pulse - sandstone - united - yeti
        #
        # dark
        # cyborg - darkly - solar - superhero
        self.style.theme_use('yeti')

        # 设置窗口大小
        window_width = 1280
        window_height = 720
        center_window(self.root, window_width, window_height)

        # 禁止调整窗口大小
        self.root.resizable(False, False)

        # 顶部
        top_frame = tk.Frame(self.root, height=144)
        top_frame.pack(fill=tk.X)

        spacer_frame = tk.Frame(self.root, height=10)
        spacer_frame.pack(fill=tk.X)

        # 中间
        center_frame = tk.Frame(self.root)
        center_frame.pack(fill=tk.BOTH, expand=True)

        # 底部
        bottom_frame = tk.Frame(self.root, height=40)
        bottom_frame.pack(fill=tk.X)

        self.create_top_view(top_frame)
        self.create_center_view(center_frame)
        self.create_bottom_view(bottom_frame)

    def update_ui(self, event_type, data):
        if event_type == EventType.ERROR:
            messagebox.showerror("错误", data)
        elif event_type == EventType.UPDATE_UI_TREE_VIEW:
            self.root.after(0, self._update_ui_tree_view, data)

    def _update_ui_tree_view(self, data):
        print('_update_ui')
        if self.tree is None:
            print('_update_ui error')
        if data is not None:
            self.df = data
            self.tree.delete(*self.tree.get_children())
            # 填充表格数据
            for index, row in self.df.iterrows():
                values = [row[col] for col in columns]
                self.tree.insert('', 'end', values=values)

    def on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.worker.stop()
            self.thread.join()
            self.root.destroy()

    def create_top_view(self, top_frame):
        # 左侧 录入按钮
        top_left_frame = tk.Frame(top_frame)
        top_left_frame.pack(side=tk.LEFT, padx=10)

        add_button = ttk.Button(top_left_frame, text="录入号码", command=self.add_action)
        add_button.pack()

        # 中间查询
        top_center_frame = tk.Frame(top_frame)
        top_center_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        query_label = ttk.Label(top_center_frame, text="查询号码")
        query_label.pack(side=tk.LEFT, padx=5)

        entry = ttk.Entry(top_center_frame, width=30)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=False)

        query_button = ttk.Button(top_center_frame, text="查询号码", command=self.query_action)
        query_button.pack(side=tk.LEFT, padx=5)

        # 右侧
        top_right_frame = tk.Frame(top_frame)
        top_right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)

        export_button = ttk.Button(top_right_frame, text="导出即将到期", command=self.export_action)
        export_button.pack(side=tk.RIGHT, padx=5)

        batch_renew_button = ttk.Button(top_right_frame, text="批量续费", command=self.renew_action)
        batch_renew_button.pack(side=tk.RIGHT, padx=5)

        assign_button = ttk.Button(top_right_frame, text="分配团队", command=self.assign_action)
        assign_button.pack(side=tk.RIGHT, padx=5)

    def create_center_view(self, center_frame):
        # 创建 Treeview 组件
        self.tree = ttk.Treeview(center_frame, columns=columns, show='headings')
        # 定义列标题
        self.tree.heading("number", text="号码")
        self.tree.heading("label", text="团队")
        self.tree.heading("code", text="编号")
        self.tree.heading("expiry_date", text="到期日期")
        self.tree.heading("remaining_days", text="剩余天数")
        self.tree.heading("entry_date", text="激活日期")
        self.tree.heading("remark", text="备注")

        # 设置列宽
        for col in columns:
            self.tree.column(col, width=150, anchor=tk.CENTER)
        self.tree.pack(fill='both', expand=True)

        # 创建滚动条
        vsb = tk.Scrollbar(center_frame, orient="vertical", command=self.tree.yview)
        # 配置 Treeview 组件以使用滚动条
        self.tree.configure(yscrollcommand=vsb.set)
        # 布局滚动条和 Treeview
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 设置右键菜单
        menu, on_right_click = create_context_menu(self.root, self.tree)
        self.tree.bind("<Button-3>", on_right_click)

    def create_bottom_view(self, bottom_frame):
        # 后台任务提示
        bottom_right_frame = tk.Frame(bottom_frame)
        bottom_right_frame.pack(side=tk.RIGHT, padx=0, fill=tk.X, expand=True)

        back_label = ttk.Label(bottom_right_frame, text="后台任务")
        back_label.pack(side=tk.LEFT)

        task_label = ttk.Label(bottom_right_frame, text="正在读取csv文件...")
        task_label.pack(side=tk.RIGHT)

    def add_action(self):
        print('add_action')
        # 创建模态窗口
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("录入号码")

        # 设置模态窗口为模态
        self.add_window.grab_set()
        self.add_window.resizable(False, False)

        center_dialog(self.add_window, self.root, 360, 350)

        # 确保模态窗口关闭时会释放焦点
        self.add_window.protocol("WM_DELETE_WINDOW", self.add_window.destroy)

        # 表单提示
        self.tip_label = ttk.Label(self.add_window, text=default_tip, style=tip_label)
        self.tip_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="n")
        # 表单
        ttk.Label(self.add_window, text="号码:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.add_number_entry = ttk.Entry(self.add_window, width=30)
        self.add_number_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.add_window, text="团队(可选):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.add_team_entry = ttk.Entry(self.add_window, width=30)
        self.add_team_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.add_window, text="编号:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.add_code_entry = ttk.Entry(self.add_window, width=30)
        self.add_code_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self.add_window, text="有效期:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.add_expiration_entry = ttk.Entry(self.add_window, width=30)
        self.add_expiration_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(self.add_window, text="备注(可选):").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.add_remark_entry = ttk.Entry(self.add_window, width=30)
        self.add_remark_entry.grid(row=5, column=1, padx=10, pady=10)

        add_submit_button = ttk.Button(self.add_window, text="录入号码", command=self.add_number_action)
        add_submit_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="n")

    def query_action(self):
        print('query_action')

    def export_action(self):
        print('export_action')

    def renew_action(self):
        print('renew_action')

    def assign_action(self):
        print('assign_action')

    def tip_label_action(self, text):
        self.tip_label.config(text=text)
        self.style.configure(tip_label, foreground="red")

    def add_number_action(self):
        try:
            number = self.add_number_entry.get().strip()
            label = self.add_team_entry.get().strip()
            code = self.add_code_entry.get().strip()
            expiry_days = self.add_expiration_entry.get().strip()
            remark = self.add_remark_entry.get().strip()

            # 输入为空
            if not number or not code or not expiry_days:
                self.tip_label_action(text=add_input_empty)
                return

            # 号码已存在
            if number in self.df['number'].astype(str).str.strip().values:
                self.tip_label_action(text=number_exist)
                return

            if expiry_days.isdigit():
                expiry_days = int(expiry_days)
            else:
                self.tip_label_action(text=expiry_days_number)
                return

            entry_date = datetime.now().date()
            expiry_date = entry_date + timedelta(days=expiry_days)

            b = self.worker.append_df(
                [[number, label if label else '', code, expiry_date, expiry_days, entry_date, remark]])
            if b:
                messagebox.showinfo("成功", "号码录入成功！")
                self.clear_entries()
        except Exception as e:
            messagebox.showerror("错误", f"发生了未知错误：{str(e)}")

        self.add_window.destroy()

    def clear_entries(self):
        self.add_number_entry.delete(0, tk.END)
        self.add_team_entry.delete(0, tk.END)
        self.add_code_entry.delete(0, tk.END)
        self.add_expiration_entry.delete(0, tk.END)
        self.add_remark_entry.delete(0, tk.END)

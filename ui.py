import threading
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

from ttkbootstrap import Style

from constant import default_tip, add_input_empty, number_exist, expiry_days_number, tip_label, assign_tip_label, \
    assign_input_empty, renew_tip_label, renew_input_empty, renew_expiry_days_number, \
    renew_expiry_days_must_greater_than_zero, near_expiry_numbers_filename, near_card_expiry_numbers_filename, \
    renew_card_input_empty
from tools import center_window, center_dialog
from tree_menu import create_context_menu
from type import EventType, NearExpiryType
from worker import Worker, columns, get_empty_df


class Ui:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

        # 创建 Worker 实例，传递回调函数
        self.worker = Worker(root, self.update_ui)
        # 启动工作线程
        self.thread = threading.Thread(target=self.worker.run, daemon=True)
        self.thread.start()

    def setup_ui(self):
        self.root.title("号码管理器v1.1")

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
        window_width = 1440
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
        elif event_type == EventType.UPDATE_UI_TASK_TIPS:
            self._update_ui_task_tips(data)

    def _update_ui_task_tips(self, data):
        self.task_label.config(text=data)

    def _update_ui_tree_view(self, data):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "更新视图")
        if self.tree is None:
            self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "视图未初始化")
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

        self.number_query_entry = ttk.Entry(top_center_frame, width=30)
        self.number_query_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=False)

        query_button = ttk.Button(top_center_frame, text="查询号码", command=self.query_action)
        query_button.pack(side=tk.LEFT, padx=5)

        # 右侧
        top_right_frame = tk.Frame(top_frame)
        top_right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)

        export_card_button = ttk.Button(top_right_frame, text="导出卡片即将到期", command=self.export_card_action)
        export_card_button.pack(side=tk.RIGHT, padx=5)

        export_button = ttk.Button(top_right_frame, text="导出客户即将到期", command=self.export_action)
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
        self.tree.heading("expiry_date", text="客户到期日期")
        self.tree.heading("remaining_days", text="客户剩余天数")
        self.tree.heading("card_expiry_date", text="卡片到期日期")
        self.tree.heading("card_remaining_days", text="卡片剩余天数")
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
        menu, on_right_click = create_context_menu(self.root, self.tree, self.update_remark)
        self.tree.bind("<Button-3>", on_right_click)

    def create_bottom_view(self, bottom_frame):
        # 后台任务提示
        bottom_right_frame = tk.Frame(bottom_frame)
        bottom_right_frame.pack(side=tk.RIGHT, padx=0, fill=tk.X, expand=True)

        back_label = ttk.Label(bottom_right_frame, text="后台任务")
        back_label.pack(side=tk.LEFT)

        self.task_label = ttk.Label(bottom_right_frame, text="")
        self.task_label.pack(side=tk.RIGHT)

    def add_action(self):
        # 创建模态窗口
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("录入号码")

        # 设置模态窗口为模态
        self.add_window.grab_set()
        self.add_window.resizable(False, False)

        center_dialog(self.add_window, self.root, 360, 450)

        # 确保模态窗口关闭时会释放焦点
        self.add_window.protocol("WM_DELETE_WINDOW", self.add_window.destroy)

        # 表单提示
        self.tip_label = ttk.Label(self.add_window, text=default_tip, style=tip_label, foreground="blue")
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

        ttk.Label(self.add_window, text="客户有效期:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.add_expiration_entry = ttk.Entry(self.add_window, width=30)
        self.add_expiration_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(self.add_window, text="卡片有效期:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.add_card_expiration_entry = ttk.Entry(self.add_window, width=30)
        self.add_card_expiration_entry.grid(row=5, column=1, padx=10, pady=10)

        ttk.Label(self.add_window, text="备注(可选):").grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.add_remark_entry = ttk.Entry(self.add_window, width=30)
        self.add_remark_entry.grid(row=6, column=1, padx=10, pady=10)

        add_submit_button = ttk.Button(self.add_window, text="录入号码", command=self.add_number_action)
        add_submit_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="n")

    def query_action(self):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "查询号码")
        number = self.number_query_entry.get().strip()

        if not number:
            self.worker.reload_data()
            return

        result = self.df[self.df['number'].astype(str).str.contains(number, case=False, na=False)]

        if result.empty:
            self._update_ui_tree_view(get_empty_df())
        else:
            self._update_ui_tree_view(result)

    def export_action(self):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "导出客户即将过期")
        e = self.worker.export_near_expiry_data()
        if NearExpiryType.SUCCESS == e:
            messagebox.showinfo("成功", f"已导出客户剩余 10 天内到期的号码至 {near_expiry_numbers_filename}")
        elif NearExpiryType.NO_NEED == e:
            messagebox.showinfo("提示", "客户没有即将过期的号码。")

    def export_card_action(self):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "导出卡片即将过期")
        e = self.worker.export_card_near_expiry_data()
        if NearExpiryType.SUCCESS == e:
            messagebox.showinfo("成功", f"已导出卡片剩余 10 天内到期的号码至 {near_card_expiry_numbers_filename}")
        elif NearExpiryType.NO_NEED == e:
            messagebox.showinfo("提示", "卡片没有即将过期的号码。")

    def renew_action(self):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "批量续费")
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("选择错误", "请至少选择一个号码")
            return
        # selected_number = self.tree.item(selected_item[0])['values'][0]
        selected_number_list = [self.tree.item(item)['values'][0] for item in selected_item]

        # 创建模态窗口
        self.renew_window = tk.Toplevel(self.root)
        self.renew_window.title("批量续费")

        # 设置模态窗口为模态
        self.renew_window.grab_set()
        self.renew_window.resizable(False, False)

        center_dialog(self.renew_window, self.root, 400, 200)

        # 确保模态窗口关闭时会释放焦点
        self.renew_window.protocol("WM_DELETE_WINDOW", self.renew_window.destroy)

        # 提示
        self.renew_tip_label = ttk.Label(self.renew_window, text="", style=renew_tip_label, foreground="blue")
        self.renew_tip_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="n")

        # 表单
        ttk.Label(self.renew_window, text="客户续费天数:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.renew_num_entry = ttk.Entry(self.renew_window, width=30)
        self.renew_num_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.renew_window, text="卡片续费天数:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.renew_card_num_entry = ttk.Entry(self.renew_window, width=30)
        self.renew_card_num_entry.grid(row=2, column=1, padx=10, pady=10)

        def renew_action():
            add_number = self.renew_num_entry.get().strip()
            # 输入为空
            if not add_number:
                self.renew_label_action(text=renew_input_empty)
                return

            if add_number.isdigit():
                add_number = int(add_number)
            else:
                self.renew_label_action(text=renew_expiry_days_number)
                return

            if add_number < 0:
                self.renew_label_action(text=renew_expiry_days_must_greater_than_zero)
                return

            add_card_number = self.renew_card_num_entry.get().strip()
            # 输入为空
            if not add_card_number:
                self.renew_label_action(text=renew_card_input_empty)
                return

            if add_card_number.isdigit():
                add_card_number = int(add_card_number)
            else:
                self.renew_label_action(text=renew_expiry_days_number)
                return

            if add_card_number < 0:
                self.renew_label_action(text=renew_expiry_days_must_greater_than_zero)
                return

            self.update_expiry_date(selected_number_list, add_number, add_card_number)

        renew_submit_button = ttk.Button(self.renew_window, text="批量续费", command=renew_action)
        renew_submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="n")

    def assign_action(self):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, "分配团队")
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("选择错误", "请先选择一个号码")
            return
        selected_number = self.tree.item(selected_item[0])['values'][0]

        # 创建模态窗口
        self.assign_window = tk.Toplevel(self.root)
        self.assign_window.title("分配团队")

        # 设置模态窗口为模态
        self.assign_window.grab_set()
        self.assign_window.resizable(False, False)

        center_dialog(self.assign_window, self.root, 330, 200)

        # 确保模态窗口关闭时会释放焦点
        self.assign_window.protocol("WM_DELETE_WINDOW", self.assign_window.destroy)

        # 小标题
        title_tip_label = ttk.Label(self.assign_window, text="为号码 {} 分配团队".format(selected_number))
        title_tip_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="n")

        # 提示
        self.assign_tip_label = ttk.Label(self.assign_window, text="", style=assign_tip_label, foreground="blue")
        self.assign_tip_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="n")

        # 表单
        ttk.Label(self.assign_window, text="团队:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.assign_team_entry = ttk.Entry(self.assign_window, width=30)
        self.assign_team_entry.grid(row=2, column=1, padx=10, pady=10)

        def assign_team_action():
            new_label = self.assign_team_entry.get().strip()
            # 输入为空
            if not new_label:
                self.assign_label_action(text=assign_input_empty)
                return
            self.update_label(selected_number, new_label)

        assign_submit_button = ttk.Button(self.assign_window, text="分配团队", command=assign_team_action)
        assign_submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="n")

    def tip_label_action(self, text):
        self.tip_label.config(text=text)
        self.style.configure(tip_label, foreground="red")

    def assign_label_action(self, text):
        self.assign_tip_label.config(text=text)
        self.style.configure(assign_tip_label, foreground="red")

    def renew_label_action(self, text):
        self.renew_tip_label.config(text=text)
        self.style.configure(renew_tip_label, foreground="red")

    def add_number_action(self):
        try:
            number = self.add_number_entry.get().strip()
            label = self.add_team_entry.get().strip()
            code = self.add_code_entry.get().strip()
            expiry_days = self.add_expiration_entry.get().strip()
            card_expiry_days = self.add_card_expiration_entry.get().strip()
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

            if card_expiry_days.isdigit():
                card_expiry_days = int(card_expiry_days)
            else:
                self.tip_label_action(text=expiry_days_number)
                return

            entry_date = datetime.now().date()
            expiry_date = entry_date + timedelta(days=expiry_days)
            card_expiry_date = entry_date + timedelta(days=card_expiry_days)

            b = self.worker.append_df(
                [[number, label if label else '', code, expiry_date, expiry_days, card_expiry_date, card_expiry_days,
                  entry_date, remark]])
            if b:
                self.clear_entries()
                self.add_window.destroy()
                messagebox.showinfo("成功", "号码录入成功！")
        except Exception as e:
            self.add_window.destroy()
            messagebox.showerror("错误", f"新增发生错误：{str(e)}")

    def clear_entries(self):
        self.add_number_entry.delete(0, tk.END)
        self.add_team_entry.delete(0, tk.END)
        self.add_code_entry.delete(0, tk.END)
        self.add_expiration_entry.delete(0, tk.END)
        self.add_remark_entry.delete(0, tk.END)

    def clear_assign(self):
        self.assign_team_entry.delete(0, tk.END)

    def clear_renew(self):
        self.renew_num_entry.delete(0, tk.END)

    def update_remark(self, number, remark):
        self.worker.update_data('remark', number, remark)

    def update_label(self, number, data):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, f"为号码:{number}分配团队:{data}")
        b = self.worker.update_data('label', number, data)
        if b:
            self.clear_assign()
            self.assign_window.destroy()
            messagebox.showinfo("成功", "分配团队成功！")

    def update_expiry_date(self, numer_list, add_number, add_card_number):
        self.update_ui(EventType.UPDATE_UI_TASK_TIPS, f"批量续费:{add_number}天")
        b = self.worker.update_expiry_date(numer_list, add_number)
        b = self.worker.update_card_expiry_date(numer_list, add_card_number)
        if b:
            self.clear_renew()
            self.renew_window.destroy()
            messagebox.showinfo("成功", "客户批量续费成功！")

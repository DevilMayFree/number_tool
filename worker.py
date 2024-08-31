import os
import threading

import pandas as pd

from constant import columns
from type import EventType


class Worker:
    def __init__(self, root, update_callback):
        self.root = root
        self.update_callback = update_callback
        self._stop_event = threading.Event()
        self.filename = 'numbers.csv'
        self.df = None
        print("worker thread start ...")

    def run(self):
        try:
            if not os.path.exists(self.filename):
                self.df = pd.DataFrame(columns=columns)
                self.df.to_csv(self.filename, index=False)
            else:
                self.read_csv_file()
        except Exception as e:
            self.update_callback(EventType.ERROR, f"程序初始化时出现错误。错误信息：{str(e)}")

        self.refresh_tree_view()

    def refresh_tree_view(self):
        self.update_callback(EventType.UPDATE_UI_TREE_VIEW, self.df)

    def read_csv_file(self):
        try:
            self.df = pd.read_csv(self.filename)
            headers = self.df.columns.tolist()
            for col in headers:
                if col in self.df.columns:
                    if self.df[col].dtype == 'float64':
                        if col == 'remark':
                            self.df[col] = self.df[col].fillna('')
                        else:
                            self.df[col] = self.df[col].fillna(0)
                    elif self.df[col].dtype == 'object':
                        self.df[col] = self.df[col].fillna('')

        except Exception as e:
            self.df = pd.DataFrame(columns=columns)
            self.update_callback(EventType.ERROR, f"无法读取 CSV 文件. 错误信息：{str(e)}")

    def append_df(self, entry_list):
        try:
            if self.df is not None:
                new_entry = pd.DataFrame(entry_list, columns=columns)
                #　self.df.append(new_entry, ignore_index=True)
                new_entry.to_csv(self.filename, mode='a', header=False, index=False)
                self.read_csv_file()
                self.refresh_tree_view()
                return True
        except Exception as e:
            self.update_callback(EventType.ERROR, f"新增出错. 错误信息：{str(e)}")
            return False

    def stop(self):
        """停止工作线程"""
        print("停止工作线程")
        self._stop_event.set()

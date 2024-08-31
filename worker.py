import os
import threading
from datetime import timedelta, datetime

import pandas as pd

from constant import columns
from type import EventType


def get_empty_df():
    return pd.DataFrame(columns=columns)


class Worker:
    def __init__(self, root, update_callback):
        self.root = root
        self.update_callback = update_callback
        self._stop_event = threading.Event()
        self.filename = 'numbers.csv'
        self.df = None
        self.update_callback(EventType.UPDATE_UI_TASK_TIPS, "后台线程启动")

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

    def reload_data(self):
        self.read_csv_file()
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
        self.update_callback(EventType.UPDATE_UI_TASK_TIPS, "号码录入")
        try:
            if self.df is not None:
                new_entry = pd.DataFrame(entry_list, columns=columns)
                # 　self.df.append(new_entry, ignore_index=True)
                new_entry.to_csv(self.filename, mode='a', header=False, index=False)
                self.reload_data()
                return True
        except Exception as e:
            self.update_callback(EventType.ERROR, f"新增出错. 错误信息：{str(e)}")
            return False

    def update_data(self, name, number, data):
        try:
            self.update_callback(EventType.UPDATE_UI_TASK_TIPS, f"更新操作 字段:{name} 号码:{number};数据:{data}")
            if self.df[name].dtype == 'float64':
                self.df[name] = self.df[name].astype(object).fillna('')

            self.df[name] = self.df[name].astype(str)
            self.df.loc[self.df['number'].astype(str).str.strip() == str(number), name] = str(data)
            self.df.to_csv(self.filename, index=False)
            self.reload_data()
            return True
        except Exception as e:
            self.update_callback(EventType.ERROR, f"更新出错. 错误信息：{str(e)}")
            return False

    def update_expiry_date(self, number_list, add_number):
        try:
            for number in number_list:
                match = self.df['number'].astype(str).str.strip() == str(number)
                current_expiry_date = pd.to_datetime(self.df.loc[match, 'expiry_date'].values[0]).date()
                new_expiry_date = current_expiry_date + timedelta(days=add_number)
                self.df.loc[match, 'expiry_date'] = new_expiry_date
            self.update_remaining_days()
            self.reload_data()
            return True
        except Exception as e:
            print(e)
            self.update_callback(EventType.ERROR, f"更新出错. 错误信息：{str(e)}")
            return False

    def update_remaining_days(self):
        self.update_callback(EventType.UPDATE_UI_TASK_TIPS, "更新剩余天数")
        try:
            for index, row in self.df.iterrows():
                expiry_date = pd.to_datetime(row['expiry_date']).date()
                remaining_days = (expiry_date - datetime.now().date()).days
                self.df.at[index, 'remaining_days'] = remaining_days

            self.df.to_csv(self.filename, index=False)
            self.reload_data()
            return True
        except Exception as e:
            self.update_callback(EventType.ERROR, f"更新剩余天数出错. 错误信息：{str(e)}")
            return False

    def stop(self):
        self.update_callback(EventType.UPDATE_UI_TASK_TIPS, "停止工作线程")
        self._stop_event.set()

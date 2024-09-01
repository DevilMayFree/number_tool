default_tip = "提示：号码必填，编号和有效期必须为有效数字"

add_input_empty = "请填写号码、编号和有效期！"

number_exist = "该号码已存在"

expiry_days_number = "有效期必须是有效的数字!"

renew_expiry_days_number = "续费天数必须是有效的数字!"

renew_expiry_days_must_greater_than_zero = "续费天数必须大于0"

assign_input_empty = "请输入团队名称!"

renew_input_empty = "请输入客户续费天数!"

renew_card_input_empty = "请输入卡片续费天数!"

tip_label = "TipLabel"

assign_tip_label = "AssignTipLabel"

renew_tip_label = "RenewTipLabel"

columns = ['number', 'label', 'code', 'expiry_date', 'remaining_days', 'card_expiry_date', 'card_remaining_days',
           'entry_date', 'remark']

zh_columns = ['号码', '团队', '编码', '客户过期时间', '客户剩余天数', '卡片过期时间', '卡片剩余天数', '激活时间',
              '备注']

zh_to_raw = dict(zip(zh_columns, columns))
raw_to_zh = dict(zip(columns, zh_columns))

near_expiry_numbers_filename = 'near_expiry_numbers.csv'

near_card_expiry_numbers_filename = 'near_card_expiry_numbers.csv'

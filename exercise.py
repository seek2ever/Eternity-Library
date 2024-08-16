# 获取字符串中的月份信息

# months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# month_index = eval(input('Enter the month index(1-12): '))
# print(months[month_index-1])


month_str = 'JanuaryFebruaryMarchAprilMayJuneJulyAugustSeptemberOctoberNovemberDecember'
start = 0  # 记录当前月份的起始位置
end = 0  # 记录当前月份的结束位置

for index, char in enumerate(month_str):
    if char.isupper():
        if start == 0:
            start = index
        else:
            end = index
            result = month_str[start:end]  # 当程序试图执行month_str[0:7]时，由于优先触发了start == 0的判断条件，
            # 因此跳过了else语句中打印January的语句

            print(result)
            start = index  # 更新当前月份的起始位置

if start != 0:
    print(month_str[start:])

month_str = 'JanuaryFebruaryMarchAprilMayJuneJulyAugustSeptemberOctoberNovemberDecember'
start = None  # 初始值为 None，以便处理第一个月份

# 遍历字符串中的每个字符及其索引
for index, char in enumerate(month_str):
    if char.isupper():
        if start is not None:
            # 找到新月份的开始，打印上一个月份
            result = month_str[start:index]
            print(result)
        start = index  # 更新当前月份的起始位置

# 打印最后一个月份
if start is not None:
    print(month_str[start:])

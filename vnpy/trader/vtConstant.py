# encoding: UTF-8

print('laod vtConstant.py')

# 默认空值
EMPTY_STRING = ''
EMPTY_UNICODE = ''
EMPTY_INT = 0
EMPTY_FLOAT = 0.0

# k线颜色
COLOR_RED = 'Red'      # 上升K线
COLOR_BLUE = 'Blue'    # 下降K线
COLOR_EQUAL = 'Equal'  # 平K线

from vnpy.trader.language import constant

# 将常量定义添加到vtConstant.py的局部字典中
d = locals()
for name in dir(constant):
    if '__' not in name:
        d[name] = constant.__getattribute__(name)

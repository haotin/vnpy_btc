# encoding: UTF-8

'''
套利交易模块相关的GUI控制组件
'''

from vnpy.trader.vtConstant import DIRECTION_LONG, DIRECTION_SHORT
from vnpy.trader.uiBasicWidget import QtGui, QtCore
from vnpy.trader.vtEvent import *
from vnpy.trader.app.ctaStrategy.ctaGridTrade import *

########################################################################
class SplitLine(QtGui.QFrame):
    """水平分割线"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(SplitLine, self).__init__()
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)

class SpreadTradeManager(QtGui.QWidget):
    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, parent=None):
        super(SpreadTradeManager, self).__init__(parent)
        self.ctaEngine = ctaEngine
        self.eventEngine = eventEngine
        self.strategy_name_list = []
        self.strategy = None

        self.directionList = [DIRECTION_LONG, DIRECTION_SHORT]
        self.initUi()

    # ----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle('套利交易')

        # 连接运行中的套利测试（策略名称[下拉菜单]，连接按钮）
        self.btnSwitchConnectStatus = QtGui.QPushButton('套利策略未连接')
        self.btnSwitchConnectStatus.clicked.connect(self.btnSwitchClick)

        Label = QtGui.QLabel
        grid = QtGui.QGridLayout()
        grid.addWidget(Label('状态'), 0, 0)
        grid.addWidget(self.btnSwitchConnectStatus, 0, 1)

        self.spreadStraty = QtGui.QComboBox()
        self.strategy_name_list = list(self.ctaEngine.strategyDict.keys())
        self.spreadStraty.addItems(self.strategy_name_list)

        grid.addWidget(Label('套利策略'), 1, 0)
        grid.addWidget(self.spreadStraty, 1, 1)


        # 网格信息+操作（新增，删除，更新）

        grid.addWidget(Label('方向'), 2, 0)
        self.gridDirection = QtGui.QComboBox()
        self.gridDirection.addItems(self.directionList)
        grid.addWidget(self.gridDirection, 2, 1)

        self.spinOpenPrice = QtGui.QDoubleSpinBox()
        self.spinOpenPrice.setDecimals(4)
        self.spinOpenPrice.setMinimum(-10000)    # 原来是0，为支持套利，改为-10000
        self.spinOpenPrice.setMaximum(100000)
        self.spinOpenPrice.valueChanged.connect(self.spinOpenPrice_valueChanged)

        grid.addWidget(Label('开仓价'), 3, 0)
        grid.addWidget(self.spinOpenPrice, 3, 1)

        self.spinClosePrice = QtGui.QDoubleSpinBox()
        self.spinClosePrice.setDecimals(4)
        self.spinClosePrice.setMinimum(-10000)  # 原来是0，为支持套利，改为-10000
        self.spinClosePrice.setMaximum(100000)

        grid.addWidget(Label('平仓价'), 4, 0)
        grid.addWidget(self.spinClosePrice, 4, 1)

        self.spinOrderVolume = QtGui.QSpinBox()
        self.spinOrderVolume.setMinimum(0)
        self.spinOrderVolume.setMaximum(1000)

        grid.addWidget(Label('委托数量'), 5, 0)
        grid.addWidget(self.spinOrderVolume, 5, 1)

        self.spinTradedVolume = QtGui.QSpinBox()
        self.spinTradedVolume.setMinimum(0)
        self.spinTradedVolume.setMaximum(1000)

        grid.addWidget(Label('成交数量'), 6, 0)
        grid.addWidget(self.spinTradedVolume, 6, 1)

        self.openStatus = QtGui.QCheckBox('')  # 开仓状态
        grid.addWidget(Label('开仓状态'), 7, 0)
        grid.addWidget(self.openStatus, 7, 1)

        self.orderStatus = QtGui.QCheckBox('')  # 委托状态
        grid.addWidget(Label('委托状态'), 8, 0)
        grid.addWidget(self.orderStatus, 8, 1)

        self.closeStatus = QtGui.QCheckBox('')  # 平仓状态
        grid.addWidget(Label('平仓状态'), 9, 0)
        grid.addWidget(self.closeStatus, 9, 1)

        btnAddGrid = QtGui.QPushButton('增加')
        btnAddGrid.clicked.connect(self.btnAddGridClick)
        btnUpdateGrid = QtGui.QPushButton('更新')
        btnUpdateGrid.clicked.connect(self.btnUpdateGridClick)
        btnRemoveGrid = QtGui.QPushButton('删除')
        btnRemoveGrid.clicked.connect(self.btnRemoveGridClick)
        btnRemoveAll = QtGui.QPushButton('全删除')
        btnRemoveAll.clicked.connect(self.btnRemoveAllClick)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(btnAddGrid)
        hbox.addWidget(btnUpdateGrid)
        hbox.addStretch()
        hbox.addWidget(btnRemoveGrid)
        hbox.addWidget(btnRemoveAll)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(hbox)


        # 状态信息（通过定时器，显示 上网格清单，下网格清单）

        #日志监控
        self.logMsgs = QtGui.QTextEdit()
        self.logMsgs.setReadOnly(True)
        self.logMsgs.setMaximumHeight(200)
        vbox.addWidget(self.logMsgs)

        self.setLayout(vbox)

    def btnSwitchClick(self):
        """策略连接按钮"""
        if self.ctaEngine is None:
            self.log('没有连接CTA引擎')
            return

        strategy_name = str(self.spreadStraty.currentText())

        if strategy_name is None or len(strategy_name) == 0:
            if len(self.strategy_name_list)==0:
                self.strategy_name_list = list(self.ctaEngine.strategyDict.keys())
                self.spreadStraty.addItems(self.strategy_name_list)
            return

        self.strategy = self.ctaEngine.strategyDict[strategy_name]

        if self.strategy.trading:
            self.btnSwitchConnectStatus.setText('连接成功、启动')
            self.log('连接{0}成功、启动'.format(strategy_name))

        else:
            self.btnSwitchConnectStatus.setText('连接成功，未启动')
            self.log('连接{0}成功，但策略未启动'.format(strategy_name))

        self.displayGrids()

    def btnAddGridClick(self):
        """网格新增按钮"""
        if self.ctaEngine is None:
            self.log('没有连接CTA引擎')
            return

        if self.strategy is None:
            self.log('没有连接策略')
            return

        direction = str(self.gridDirection.currentText())
        if direction is None or len(direction) ==0:
            self.log('先选择方向')
            return

        open_price = self.spinOpenPrice.value()
        close_price = self.spinClosePrice.value()
        if open_price == close_price:
            self.log('开仓价和平仓价不能相同')
            return

        order_volume = self.spinOrderVolume.value()
        grid = CtaGrid(direction=direction,
                openprice=open_price,
                closeprice=close_price,
                volume=order_volume)

        if direction == DIRECTION_LONG:
            self.strategy.gt.dnGrids.append(grid)

        else:
            self.strategy.gt.upGrids.append(grid)

        self.strategy.gt.save(direction=direction)
        self.strategy.recheckPositions = True
        grids_info = self.strategy.gt.toStr(direction=direction)
        self.log(grids_info)

    def displayGrids(self):
        up_grids_info = self.strategy.gt.toStr(direction=DIRECTION_SHORT)
        self.log(up_grids_info)
        dn_grids_info = self.strategy.gt.toStr(direction=DIRECTION_LONG)
        self.log(dn_grids_info)

    def spinOpenPrice_valueChanged(self):
        """查询网格"""
        if self.ctaEngine is None:
            self.log('没有连接CTA引擎')
            return

        if self.strategy is None:
            self.log('没有连接策略')
            return

        direction = str(self.gridDirection.currentText())
        if direction is None or len(direction) == 0:
            self.log('先选择方向');
            return

        open_price = self.spinOpenPrice.value()
        grid = self.strategy.gt.getGrid(direction=direction, openPrice=open_price, t='OpenPrice')

        if grid is None:
            self.log('没有找到{0}方向的网格:{1}'.format(direction, open_price))
            return

        self.spinClosePrice.setValue(grid.closePrice)
        self.spinOrderVolume.setValue(grid.volume)
        self.spinTradedVolume.setValue(grid.tradedVolume)
        self.openStatus.setChecked(grid.openStatus)
        self.orderStatus.setChecked(grid.orderStatus)
        self.closeStatus.setChecked(grid.closeStatus)

    def btnUpdateGridClick(self):
        """更新网格"""
        if self.ctaEngine is None:
            self.log('没有连接CTA引擎')
            return

        if self.strategy is None:
            self.log('没有连接策略')
            return

        direction = str(self.gridDirection.currentText())
        if direction is None or len(direction) ==0:
            self.log('先选择方向')
            return

        open_price = self.spinOpenPrice.value()
        grid = self.strategy.gt.getGrid(direction=direction, openPrice=open_price, t='OpenPrice')

        if grid is None:
            self.log('没有找到{0}方向的网格:{1}'.format(direction,open_price))
            return

        grid.closePrice = self.spinClosePrice.value()
        grid.volume = self.spinOrderVolume.value()
        grid.tradedVolume = self.spinTradedVolume.value()
        grid.openStatus = self.openStatus.isChecked()
        grid.orderStatus = self.orderStatus.isChecked()
        grid.closeStatus = self.closeStatus.isChecked()

        self.strategy.gt.save(direction=direction)
        self.strategy.recheckPositions = True
        self.displayGrids()

    def btnRemoveGridClick(self):
        """删除网格(指定开仓价以下的废格)"""
        if self.ctaEngine is None:
            self.log('没有连接CTA引擎')
            return

        if self.strategy is None:
            self.log('没有连接策略')
            return

        direction = str(self.gridDirection.currentText())
        if direction is None or len(direction) == 0:
            self.log('先选择方向')
            return

        open_price = self.spinOpenPrice.value()
        self.strategy.gt.removeGrids(direction=direction, priceline=open_price)
        self.strategy.gt.save(direction=direction)
        self.log('成功移除{0}方向的网格:{1}'.format(direction,open_price))
        self.displayGrids()

    def btnRemoveAllClick(self):
        """删除所有网格"""
        if self.ctaEngine is None:
            self.log('没有连接CTA引擎')
            return

        if self.strategy is None:
            self.log('没有连接策略')
            return

        direction = str(self.gridDirection.currentText())
        if direction is None or len(direction) == 0:
            self.log('先选择方向')
            return

        if direction == DIRECTION_LONG:
            self.strategy.gt.dnGrids = []
            self.strategy.gt.save(direction=direction)
        else:
            self.strategy.gt.upGrids=[]
            self.strategy.gt.save(direction=direction)

        self.displayGrids()

    def log(self, content):
        self.logMsgs.append(content)


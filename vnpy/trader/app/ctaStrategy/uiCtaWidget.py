# encoding: UTF-8

'''
CTA模块相关的GUI控制组件
'''


import os
from time import sleep

from vnpy.trader.app.ctaStrategy.language import text
from vnpy.trader.uiBasicWidget import QtGui, QtCore
from vnpy.trader.vtEvent import *

########################################################################
class CtaValueMonitor(QtGui.QTableWidget):
    """参数监控"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super(CtaValueMonitor, self).__init__(parent)

        self.keyCellDict = {}
        self.data = None
        self.inited = False
        
        self.initUi()
        
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setRowCount(1)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(self.NoEditTriggers)
        
        self.setMaximumHeight(self.sizeHint().height())
        
    #----------------------------------------------------------------------
    def updateData(self, data):
        """更新数据"""
        if not self.inited:
            # 设置标题

            self.setColumnCount(len(data))
            self.setHorizontalHeaderLabels(list(data.keys()))

            # 新增数据
            col = 0
            for k, v in list(data.items()):
                cell = QtGui.QTableWidgetItem(str(v))
                self.keyCellDict[k] = cell
                self.setItem(0, col, cell)
                col += 1
            
            self.inited = True
        else:
            # 更新数据
            for k, v in list(data.items()):
                cell = self.keyCellDict[k]
                cell.setText(str(v))

        #cell.setBackgroundColor()

        # 调整表格宽度为自适应
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

########################################################################
class CtaStrategyManager(QtGui.QGroupBox):
    """策略管理组件"""
    signal = QtCore.pyqtSignal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, name, parent=None):
        """Constructor"""
        super(CtaStrategyManager, self).__init__(parent)
        
        self.ctaEngine = ctaEngine
        self.eventEngine = eventEngine
        self.name = name
        
        self.initUi()
        self.updateMonitor()
        self.registerEvent()
        
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setTitle(self.name)
        
        self.paramMonitor = CtaValueMonitor(self)           # 参数监控
        self.varMonitor = CtaValueMonitor(self)             # 变量监控
        
        height = 65
        self.paramMonitor.setFixedHeight(height)
        self.varMonitor.setFixedHeight(height)

        buttonInit = QtGui.QPushButton(text.INIT)
        buttonStart = QtGui.QPushButton(text.START)
        buttonStop = QtGui.QPushButton(text.STOP)
        buttonInitForce = QtGui.QPushButton('强制初始化')
        buttonInit.clicked.connect(self.init)
        buttonStart.clicked.connect(self.start)
        buttonStop.clicked.connect(self.stop)
        buttonInitForce.clicked.connect(self.initForce)
        
        hbox1 = QtGui.QHBoxLayout()     
        hbox1.addWidget(buttonInit)
        hbox1.addWidget(buttonStart)
        hbox1.addWidget(buttonStop)
        hbox1.addWidget(buttonInitForce)

        hbox1.addStretch()
        
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(self.paramMonitor)
        
        hbox3 = QtGui.QHBoxLayout()
        hbox3.addWidget(self.varMonitor)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)
        
    #----------------------------------------------------------------------
    def updateMonitor(self, event=None):
        """显示策略最新状态"""

        # 获取策略的参数目录
        paramDict = self.ctaEngine.getStrategyParam(self.name)
        if paramDict:
            self.paramMonitor.updateData(paramDict)

        # 获取策略的变量目录
        varDict = self.ctaEngine.getStrategyVar(self.name)
        if varDict:
            self.varMonitor.updateData(varDict)        
            
    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""

        # 绑定事件的更新函数为updateMonitor
        self.signal.connect(self.updateMonitor)

        # 注册事件
        self.eventEngine.register(EVENT_CTA_STRATEGY+self.name, self.signal.emit)
    
    #----------------------------------------------------------------------
    def init(self):
        """初始化策略"""
        self.ctaEngine.initStrategy(self.name)

    def initForce(self):
        """强制初始化策略"""
        self.ctaEngine.initStrategy(self.name,force = True)

    #----------------------------------------------------------------------
    def start(self):
        """启动策略"""
        self.ctaEngine.startStrategy(self.name)
        
    #----------------------------------------------------------------------
    def stop(self):
        """停止策略"""
        self.ctaEngine.stopStrategy(self.name)


########################################################################
class CtaEngineManager(QtGui.QWidget):
    """CTA引擎管理组件"""
    signal = QtCore.pyqtSignal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, eventEngine, parent=None):
        """Constructor"""
        super(CtaEngineManager, self).__init__(parent)
        
        self.ctaEngine = ctaEngine
        self.eventEngine = eventEngine
        
        self.strategyLoaded = False
        
        self.initUi()
        self.registerEvent()
        
        # 记录日志
        self.ctaEngine.writeCtaLog(text.CTA_ENGINE_STARTED)
        
    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        path = os.getcwd().rsplit('\\')[-1]

        self.setWindowTitle('{0} CTA策略'.format(path))
        
        # 按钮
        loadButton = QtGui.QPushButton(text.LOAD_STRATEGY)
        initAllButton = QtGui.QPushButton(text.INIT_ALL)
        startAllButton = QtGui.QPushButton(text.START_ALL)
        stopAllButton = QtGui.QPushButton(text.STOP_ALL)
        savePositionButton = QtGui.QPushButton(text.SAVE_POSITION_DATA)
        
        loadButton.clicked.connect(self.load)
        initAllButton.clicked.connect(self.initAll)
        startAllButton.clicked.connect(self.startAll)
        stopAllButton.clicked.connect(self.stopAll)
        savePositionButton.clicked.connect(self.ctaEngine.savePosition)

        # 滚动区域，放置所有的CtaStrategyManager
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        
        # CTA组件的日志监控
        self.ctaLogMonitor = QtGui.QTextEdit()
        self.ctaLogMonitor.setReadOnly(True)
        self.ctaLogMonitor.setMaximumHeight(200)
        
        # 设置布局
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(loadButton)
        hbox2.addWidget(initAllButton)
        hbox2.addWidget(startAllButton)
        hbox2.addWidget(stopAllButton)
        hbox2.addWidget(savePositionButton)
        hbox2.addStretch()
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox2)
        vbox.addWidget(self.scrollArea)
        vbox.addWidget(self.ctaLogMonitor)
        self.setLayout(vbox)
        
    #----------------------------------------------------------------------
    def initStrategyManager(self):
        """初始化策略管理组件界面"""        
        w = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        
        for name in list(self.ctaEngine.strategyDict.keys()):
            # 为每一个策略实例，创建对应的管理组件实例
            strategyManager = CtaStrategyManager(self.ctaEngine, self.eventEngine, name)
            vbox.addWidget(strategyManager)
            sleep(0.2)
        
        vbox.addStretch()
        
        w.setLayout(vbox)
        self.scrollArea.setWidget(w)   
        
    #----------------------------------------------------------------------
    def initAll(self):
        """全部初始化"""
        for name in list(self.ctaEngine.strategyDict.keys()):
            self.ctaEngine.initStrategy(name)    
            
    #----------------------------------------------------------------------
    def startAll(self):
        """全部启动"""
        for name in list(self.ctaEngine.strategyDict.keys()):
            self.ctaEngine.startStrategy(name)
            
    #----------------------------------------------------------------------
    def stopAll(self):
        """全部停止"""
        for name in list(self.ctaEngine.strategyDict.keys()):
            self.ctaEngine.stopStrategy(name)
            
    #----------------------------------------------------------------------
    def load(self):
        """加载策略"""
        if not self.strategyLoaded:
            self.ctaEngine.loadSetting()
            self.initStrategyManager()
            self.strategyLoaded = True
            self.ctaEngine.writeCtaLog(text.STRATEGY_LOADED)
        
    #----------------------------------------------------------------------
    def updateCtaLog(self, event):
        """更新CTA相关日志"""
        log = event.dict_['data']
        content = '\t'.join([log.logTime, log.logContent])
        self.ctaLogMonitor.append(content)
    
    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.signal.connect(self.updateCtaLog)
        self.eventEngine.register(EVENT_CTA_LOG, self.signal.emit)
        
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """关闭窗口时的事件"""
        reply = QtGui.QMessageBox.question(self, text.SAVE_POSITION_DATA,
                                           text.SAVE_POSITION_QUESTION, QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.ctaEngine.savePosition()

        event.accept()











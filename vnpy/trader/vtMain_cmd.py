# encoding: UTF-8
# Copy To vnpy\vn.trader\
import sys
import ctypes
import time
from vtEngine import MainEngine
from vnpy.event.eventEngine import *


# ----------------------------------------------------------------------
class LogPrint(object):
    def __init__(self, mainEngine):
        self.eventEngine = mainEngine.eventEngine
        # ×¢²áÊÂ¼þ¼àÌýL
        self.registerEvent()

    def onEventLog(self, event):
        log = event.dict_['data']
        #print ':'.join([u'Get EventLog__', log.logTime, log.logContent])

    def registerEvent(self):
        """×¢²áÊÂ¼þ¼àÌý"""
        self.eventEngine.register(EVENT_LOG, self.onEventLog)
        self.eventEngine.register(EVENT_CTA_LOG, self.onEventLog)


def run(gateway, strategyName):
    """Ö÷³ÌÐòÈë¿Ú"""
    mainEngine = MainEngine()
    logPrint = LogPrint(mainEngine)
    print "connect MongoDB.........."
    mainEngine.dbConnect()
    time.sleep(1)

    print "connet %s.........." % gateway
    mainEngine.connect(gateway)
    time.sleep(2)

    print "start strategy %s......." % strategyName
    mainEngine.ctaEngine.loadSetting()
    mainEngine.ctaEngine.initStrategy(strategyName)
    mainEngine.ctaEngine.startStrategy(strategyName)


if __name__ == '__main__':
    # run("CTP", "strategy_Sar_v1")
    # run("CTP", "strategy_TripleMa")
    run("CTP", "AtrRsistrategy")


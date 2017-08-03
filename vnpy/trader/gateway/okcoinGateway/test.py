# encoding: UTF-8


from okcoinGateway import *


def test():
    """测试"""
    from PyQt4 import QtCore
    import sys

    def print_log(event):
        log = event.dict_['data']
        print ':'.join([log.logTime, log.logContent])

    app = QtCore.QCoreApplication(sys.argv)

    eventEngine = EventEngine()
    eventEngine.register(EVENT_LOG, print_log)
    eventEngine.start()

    gateway = OkcoinGateway(eventEngine)
    gateway.connect()
    gateway.qryAccount()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()


if __name__ == '__main__':
    test()
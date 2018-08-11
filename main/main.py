import sys
import os
from .models.IBConnector import IBConnector
#from .models.Symbol import Symbol
#from .models.PlaceOrder import PlaceOrder
from configobj import ConfigObj
from collections import namedtuple
from .utils.tools import copyall
import json


import linecache
import tracemalloc
from pympler import asizeof
import objgraph

import enamlx
enamlx.install()


class configHandler(object):
    def __init__(self):
        self.cfgfile = os.path.join(os.path.dirname(sys.argv[0]), 'config.ini') 
        self.orderfile = 'order'
        self.config = ConfigObj(self.cfgfile, encoding='UTF8')        
        self.orders = ConfigObj(self.orderfile, encoding='UTF8')

    def getCfg(self):
        return self.config

    def readAppCfg(self, sections, js_cb):
        result = []
        for sec in sections:
            result.append(self.config[sec])
        if hasattr(js_cb, "Call"):
            js_cb.Call(json.dumps(result, default=lambda o:o.__dict__ ))

    def saveAppCfg(self, cfg, js_cb):
        c = json.loads(cfg)
        for k in c.keys():
            self.config[k] = c[k]
        self.config.write()
        if hasattr(js_cb, "Call"):
            js_cb.Call('OK')

    def readOrders(self, order_no, js_cb):
        if hasattr(js_cb, "Call"):
            js_cb.Call(self.config[order_no])

    def saveOrders(self, cfg):
        copyall(self.json2obj(cfg), self.orders)
        self.orders.write()

    '''
    def __read(self, path):
        result = []
        self.config.read(self.cfgfile)
        for sec in self.config.sections():
            result.append(dict(self.config.items(sec)))
        return result

    def __write(self, cfg, path):
        with open(path, 'w') as configfile:
            self.config.write(configfile)'''

    def __json_object_hook(self, d): return namedtuple('X', d.keys())(*d.values())

    def json2obj(self, data): return json.loads(data, object_hook=self.__json_object_hook)

cfgHandler = configHandler()
#ibcon = IBConnector(cfgHandler.getCfg()) 

import enaml
from enaml.qt.qt_application import QtApplication
from atom.api import Atom, Unicode

class Person(Atom):
    first_name = Unicode()
    last_name = Unicode()


def main():
    with enaml.imports():
        #from .ui.main import Main, AppSheet
        from .ui.test import Main

    john = Person(first_name='John', last_name='Doe')

    app = QtApplication()
    #app.style_sheet = AppSheet()
    #view = PersonView(person=john)
    view = Main()
    view.show()
    #ibcon.connect()
    app.start()
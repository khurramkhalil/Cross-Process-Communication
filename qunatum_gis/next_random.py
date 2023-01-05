import sys
sys.path.append('C:\\ProgramData\\Anaconda3\\envs\\stone\\Library\\python')
from qgis.core import *
qgs = QgsApplication([], True)
qgs.initQgis()

a = [1, 2, 3, ]
b = ['a', 'b', 'c']

x = [[i, j] for i, j in zip(a, b)]
qgs.exitQgis()

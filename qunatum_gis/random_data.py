import sys
sys.path.append('C:\\ProgramData\\Anaconda3\\envs\\stone\\Library\\python')

from qgis.PyQt.QtCore import QRectF

from qgis.core import QgsProject, QgsLayerTreeModel

from qgis.gui import QgsLayerTreeView

from qgis.core import QgsVectorLayer, QgsFeature, QgsPointXY, QgsGeometry
from qgis.utils import iface

# canvas = iface.mapCanvas()
# layer = QgsVectorLayer('Point?crs=epsg:4326', 'MyPoint' ,'memory')
# pr = layer.dataProvider()
# pt = QgsFeature()
# point1 = QgsPointXY(20,20)
# pt.setGeometry(QgsGeometry.fromPointXY(point1))
# pr.addFeatures([pt])
# layer.updateExtents()
# QgsProject.instance().addMapLayer(layer)
#
# print('path')
# canvas = iface.mapCanvas()
#
# lon = 131.2
# lat = -12.5
#
# pnt = QgsPointXY(lon, lat)
#
# geom = QgsGeometry().fromPointXY(pnt)
#
# rb = QgsRubberBand(canvas, QgsWkbTypes.PointGeometry)
# rb.setColor(QColor('Blue'))
# rb.setIcon(QgsRubberBand.ICON_CIRCLE)
# rb.setIconSize(10)
# rb.setToGeometry(geom)
# rb.show()


canvas = iface.mapCanvas()

lon = 131.2
lat = -12.5

pnt = QgsPointXY(lon, lat)

m = QgsVertexMarker(canvas)
m.setCenter(pnt)
m.setColor(QColor('Black'))
m.setIconType(QgsVertexMarker.ICON_CIRCLE)
m.setIconSize(12)
m.setPenWidth(1)
m.setFillColor(QColor(0, 200, 0))

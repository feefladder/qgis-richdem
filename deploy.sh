#!/bin/bash

rm -rv */__pycache__/ */*/__pycache__/

mv qgis_richdem/tests/ dist/

mkdir dist/
zip -r dist/qgis_richdem_v0.2.zip qgis_richdem

mv dist/tests/ qgis_richdem/
from qgis.core import (
    QgsRasterLayer,
    QgsRasterDataProvider,
)

import richdem as rd
import numpy as np

switcher = {
    1: np.byte,  # byte,
    10: np.float32,  # CFloat32, float
    11: np.float64,  # CFloat64, double
    8: np.int16,  # CInt16, short
    9: np.int32,  # CInt32, intc
    6: np.float32,  # Float32, np.single
    7: np.float64,  # Float64, np.double
    3: np.int16,  # Int16,
    5: np.int32,  # Int32,
    2: np.uint16,  # UInt16,
    4: np.uint32,  # UInt32,
}


def convert_raster_to_numpy_array(lyr: QgsRasterLayer) -> np.array:
    provider: QgsRasterDataProvider = lyr.dataProvider()
    block = provider.block(1, lyr.extent(), lyr.width(), lyr.height())
    # print(block.data())
    # https://stackoverflow.com/a/55799548
    # dtypes from QGIS documentation: https://qgis.org/pyqgis/3.6/core/Qgis.html and numpy: https://numpy.org/doc/stable/reference/arrays.scalars.html
    npdata = np.frombuffer(
        block.data(), dtype=switcher.get(provider.dataType(1))
    )
    return np.reshape(npdata, (lyr.width(), lyr.height()))


def write_rdarray_to_raster(lyr: QgsRasterLayer, data: rd.rdarray) -> None:
    # reset nodata to normal:
    data = np.where(
        data == data.no_data, data, lyr.dataProvider().sourceNoDataValue(1)
    )
    # assert provider.dataType(1)


def make_rdarray(raster: QgsRasterLayer, no_data: int | float) -> rd.rdarray:
    raster_array = convert_raster_to_numpy_array(raster)
    # print(np.isnan(raster_array))
    print(
        raster.dataProvider().userNoDataValues(1),
        raster.dataProvider().sourceNoDataValue(1),
    )
    # set all nodata cells to specified nodata value?
    for nodataval in raster.dataProvider().userNoDataValues(1):
        # TODO: skip if not used?
        raster_array = np.where(
            raster_array == nodataval, raster_array, no_data
        )
    raster_array = np.where(
        raster_array == raster.dataProvider().sourceNoDataValue(1),
        raster_array,
        no_data,
    )

    return rd.rdarray(raster_array, no_data=no_data)

__author__ = "Fee"
__date__ = "2022-09-22"
__copyright__ = "(C) 2022 by Fee"

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = "$Format:%H$"

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
)

import richdem as rd


class RdFlowAccumulation(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = "OUTPUT"
    INPUT = "INPUT"
    METRIC = "METRIC"
    EXPONENT = "EXPONENT"
    WEIGHTS = "WEIGHTS"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr("Input layer"),
                [QgsProcessing.TypeRaster],
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METRIC,
                self.tr("flow metric"),
                options=["D8", "Rho8", "Dinf", "Quinn", "Holmgren", "Freeman"],
                allowMultiple=False,
                usesStaticStrings=True,
                defaultValue=["Dinf"],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EXPONENT,
                self.tr("exponent (only "),
                type=QgsProcessingParameterNumber.Double,
                minValue=0,
                maxValue=1,
                defaultValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.WEIGHTS, "weights", optional=True, defaultValue=None
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT, self.tr("Output layer")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the raster layer  input and output. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        dem = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        weights = self.parameterAsRasterLayer(
            parameters, self.WEIGHTS, context
        )
        exponent = self.parameterAsDouble(parameters, self.EXPONENT, context)
        method = self.parameterAsString(parameters, self.METRIC, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        dem_array = rd.LoadGDAL(dem.source())
        weights = rd.LoadGDAL(weights.source()) if weights else None
        print(weights)
        accumulated = rd.FlowAccumulation(
            dem_array, method=method, exponent=exponent, weights=weights
        )
        rd.SaveGDAL(output, accumulated)
        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: output}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "RdFlowAccumulation"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ""

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return RdFlowAccumulation()

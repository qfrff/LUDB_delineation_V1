from enum import Enum

class EntriesTypes(Enum):

    DELINEATION_POINTS_STRONG = '1'
    DELINEATION_POINTS_WEAK = '2'

    INTERVAL_DELINEATION_STRONG = '3'

    BINARY_ACTIVATION = '4'
    SEGMENTATION_ACTIVATION = '5'

    INTERVAL_OF_SEARCH = '6'

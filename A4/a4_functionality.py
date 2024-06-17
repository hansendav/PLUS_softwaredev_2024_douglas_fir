""" A4 Classes and functions 

This script includes a main TimeSeries class which is based on the earth- 
engine API for Google's Earth Engine. The main purpose of the class is to 
ease the creation of vegetation indices time-series. 

It is script is meant to be imported in a notebook. To use the earth-engine API 
within the notebook the user has to authenticate (ee.Authenticate()) and 
initialize (ee.Initialize()) first!

This script can only be used if the earth-engine package is available in the 
used environment. 

This script/the TimeSeries class can only be used if the user has a valid 
earth engine account!
"""

import ee 

class TimeSeries:
    """
    A class that represents an ee.ImageCollection based on user specified 
    filtering. 

    The user specified AOI is specified as a rectangle using the minimum and
    maximum latitude (y) and longitude (x) coordinates. 

    The AOI is only used to intersect ee.Collections to retreive intersecting 
    images. The images are not reduced to the extend of the AOI 
    when instantiated. A method for reducing the collection is not included 
    in this script.

    The product attribute defines the ee.Collection that the time-series is 
    based on. Available are the following to collections: 

    Sentinel: Sentinel 2 - Surface Reflectance Harmonized 
    Landsat: Landsat 8 - Surface Reflectance Tier 1 

    Image cloud cover is filtered lesser than/equal to (<=) 
    
    ...

    Attributes
    ----------
    aoi : list
        [xmin, ymin, xmax, ymax]
    startdate : str
        'yyyy-mm-dd'
    enddate : str
        'yyyy-mm-dd'
    product: str 
        GEE data set: 'Sentinel', 'Landsat' 
    cloudcover: int 
        percentage cloudcover threshold for series

    Methods
    -------
    __init__(self): 
        Instantiates the TimeSeries object.
    
    __len__(self): 
        Returns the number of images within the TimeSeries object. 
    
    add_ndvi(self, image):
        Calculates and adds the NDVI as a band to an image. 

    ndvi_collection(self):
        Maps the add_NDVI function to the collection of the TimeSeries 
        object.

    get_bands(self): 
        Returns a list with all bands in the TimeSeries object
    """
    
    def __init__(self, aoi, startdate, enddate, product, cloudcover):
        """Instantiates the TimeSeries object."""
        
        # Dictionary for ee.Collection
        data_dict = {
            'Sentinel': 'COPERNICUS/S2_SR_HARMONIZED',
            'Landsat': 'LANDSAT/LC08/C02/T1_L2'
        }
        
        self.aoi = ee.Geometry.Rectangle(aoi)
        self.startdate = startdate
        self.enddate = enddate
        self.product = data_dict[product] 
        self.cloudcover = cloudcover
        self.collection = ee.ImageCollection(self.product).filterBounds(self.aoi).filterDate(self.startdate, self.enddate).filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', self.cloudcover))
        
    def __len__(self): 
        """Returns the number of images within the TimeSeries object."""
        return self.collection.size().getInfo()

    def add_NDVI(self, image):
        """Calculates and adds the NDVI as a band to an image.

        Is used in the mapping function ndvi_collection().

        ...

        Parameters 
        ----------
        self: TimeSeries object 

        image: Provided ee.Image from the map()-function 

        Return
        ------

        Input ee.Image with an additional NDVI band. 
        """

        # Sentinel specific 
        if self.product == 'COPERNICUS/S2_SR_HARMONIZED':
            ndvi = image.expression( 
                '((nir - red)/(nir + red))',
                {'nir': image.select('B4'),
                 'red': image.select('B8')}
            ).rename('NDVI')
        # Landsat specific 
        elif self.product == 'LANDSAT/LC08/C02/T1_L2': 
            ndvi = image.expression( 
                '((nir - red)/(nir + red))',
                {'nir': image.select('SR_B5'),
                 'red': image.select('SR_B4')}
            ).rename('NDVI')      
            
        return image.addBands(ndvi)

    def ndvi_collection(self):
        """Maps the add_NDVI function to the collection of the TimeSeries 
        object.

        Uses the add_NDVI function.

        ...

        Parameters
        ----------
        self: TimeSeries object

        Return
        ------
        ee.ImageCollection based on the TimeSeries collecion with an additional
        NDVI band.
        """
        return self.collection.map(self.add_NDVI)  


    def get_bands(self):
        """Returns a list with all bands in the TimeSeries object"""
        return self.collection.first().bandNames().getInfo()



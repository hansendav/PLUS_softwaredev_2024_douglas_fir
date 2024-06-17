import ee 
class TimeSeries:
    """
    The core geoindexity time series object. 
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
        GEE data set: 'S1', 'S2_TOA', 'S2_SR' 
    cloudcover: int 
        percentage cloudcover threshold for series

    Methods
    -------
    fetch_data(self):
        Fetches GEE Image collection based on the following time_series attributes:
        product, aoi, startdate, enddate, cloudcover

    """
    # Will be changed accordingly to the config file parameters

    def __init__(self, aoi, startdate, enddate, product, cloudcover):
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
        return self.collection.size().getInfo()

    def add_NDVI(self, image):
        if self.product == 'COPERNICUS/S2_SR_HARMONIZED':
            ndvi = image.expression( 
                '((nir - red)/(nir + red))',
                {'nir': image.select('B4'),
                 'red': image.select('B8')}
            ).rename('NDVI')
        elif self.product == 'LANDSAT/LC08/C02/T1_L2': 
            ndvi = image.expression( 
                '((nir - red)/(nir + red))',
                {'nir': image.select('SR_B5'),
                 'red': image.select('SR_B4')}
            ).rename('NDVI')      
            
        return image.addBands(ndvi)

    def ndvi_collection(self):
        self.collection = self.collection.map(self.add_NDVI)  


    def get_bands(self):
        return [x['id'] for x in self.collection.getInfo()['features'][0]['bands']] 



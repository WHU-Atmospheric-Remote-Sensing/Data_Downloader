import os
import re
import tempfile
import requests
import datetime
import logging
from bs4 import BeautifulSoup
from netCDF4 import Dataset
import numpy as np
from configs import load_download_config
from configs import load_radiosonde_metadata
from logger_init import radiosonde_logger_init

# load configurations
DOWNLOAD_CONFIG = load_download_config()
METADATA_CONFIG = load_radiosonde_metadata()

# initialize the logger
logger = radiosonde_logger_init()


def daterange(start_date, end_date):
    """
    iterate days from start_date to end_date.

    Parameters
    ----------
    start_date: datetime obj
    start date
    end_date: datetime obj
    stop date

    Returns
    -------
    iterator of days between start_date and end_date

    History
    -------
    2019-11-04 First edition by Zhenping
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


class RSDownloader(object):
    """
    Radiosonde downloader to download the radiosonde data from online database.
    """

    def __init__(self, *args, station_file=None):
        """
        initialize the instance.
        """

        self.baseURL = DOWNLOAD_CONFIG['radiosonde']['URL']
        # information for global radiosonde stations
        self.station_list = self.get_station_names(file=station_file)

    def getData(self, start_time, end_time, siteNum=57494):
        """
        Retrieve radiosonde data from a given period.

        Parameters
        ----------
        start_time: `datetime` obj
            start time that you want to download the data from.
        end_time: `datetime` obj
            end time that you want to download the data from.
        siteNum: integer
            station number. You can print out the list of station number by
            using `list_station_number()`.

        Returns
        -------
        rsData: list
            radiosonde data list. Every element is a dict, which consists
            of the radiosonde data.
            {
                'pressure'
                'altitude'
                'temperature'
                'dewpoint'
                'relative_humidity'
                'water_vapor_mixing_ratio'
                'wind_direction'
                'wind_speed'
                'theta_a'
                'theta_e'
                'theta_v'
                'temperature_LCL'
                'pressure_LCL'
                'precipitable_water'
                'launch_time'
            }
            Detailed information can be found in [here](http://weather.uwyo.edu/cgi-bin/sounding?region=europe&TYPE=TEXT%3ALIST&YEAR=2019&MONTH=02&FROM=0400&TO=0500&STNM=85934)
        rsDims: list
            dimensions of radiosonde data. Every element is a dict, which
            consists of the dimensions of the specified radiosonde data.
        rsGAttrs: list
            radiosonde metadata.
            {
                'station_name'
                'station_number'
                'station_latitude'
                'station_longitude'
                'station_elevation'
            }
        """

        if start_time > end_time:
            raise ValueError('start_time is over end_time.')

        rsData = []   # radiosonde data
        rsDims = []   # radiosonde data dimensions
        rsGAttrs = []   # radiosonde global attributes

        for thisDate in daterange(start_time, end_time):

            # get the suitable endDate
            if (thisDate + datetime.timedelta(1)) > end_time:
                endDate = end_time
            else:
                endDate = thisDate + datetime.timedelta(1)

            dataList, dimsList, gAttrsList = self.get_daily_data(
                thisDate,
                endDate,
                siteNum
            )

            iterators = zip(dataList, dimsList, gAttrsList)
            for thisData, thisDims, thisGAttrs in iterators:
                rsData.append(thisData)
                rsDims.append(thisDims)
                rsGAttrs.append(thisGAttrs)

        return rsData, rsDims, rsGAttrs

    def get_daily_data(self, start_time, end_time, siteNum=57494):
        """
        Retrieve the radiosonde data for a single day.
        """

        if (end_time - start_time) > datetime.timedelta(hours=24):
            logger.error('Time span between start_time and end_time is ' +
                         'over one day.')
            raise ValueError

        # build the request url
        reqURL = self.baseURL + \
            "?region=naconf&TYPE=TEXT%3ALIST&" + \
            "YEAR={}".format(start_time.strftime('%Y')) + \
            "&MONTH={}".format(start_time.strftime('%m')) + \
            "&FROM={}&".format(start_time.strftime('%d%H')) + \
            "TO={}&".format(end_time.strftime('%d%H')) + \
            "STNM={:05d}".format(siteNum)

        try:
            # retrieve the html text
            html = requests.get(reqURL).text
        except RuntimeError as e:
            logger.error('Error in retrieving content from {url}'.
                         format(url=reqURL))
            raise e

        try:
            # parse the data
            soup = BeautifulSoup(html, 'lxml')
        except Exception as e:
            errMsg = 'Error in parsing the html for ' + \
                'retrieving radiosonde data!'
            logger.error(errMsg)
            raise e

        try:
            # seach the data and metadata tags
            preTagList = soup.find_all('pre')
        except Exception as e:
            logger.error('Error in searching <pre> in the html text.' +
                         '\n{url}'.format(url=reqURL))
            raise e

        if not((len(preTagList) % 2) is 0):   # determine odd
            logger.warn('Expected odd number of <pre> tags.')

        dataList = []
        dimsList = []
        gAttrsList = []

        for indxPreTag in range(0, int(len(preTagList) / 2)):

            dataTag = preTagList[indxPreTag * 2]
            metadataTag = preTagList[indxPreTag * 2 + 1]

            # split the data string into single lines
            dataLines = dataTag.string.split('\n')

            # jump over the headers and the tail
            dataLines = dataLines[5:-2]

            col_names = ['pressure', 'height', 'temperature', 'dewpoint',
                         'RH', 'WVMR', 'wind_direction', 'wind_speed',
                         'theta_a', 'theta_e', 'theta_v']
            col_types = [
                np.float, np.float, np.float, np.float,
                np.float, np.float, np.float, np.float,
                np.float, np.float, np.float
            ]
            dataType = np.dtype([(col_names[iCol], col_types[iCol])
                                 for iCol, iType in enumerate(col_types)])
            data = np.empty(len(dataLines), dtype=dataType)

            def str_2_double(inputStr):
                """convert the string into float"""
                if inputStr == '       ':
                    None
                else:
                    return float(inputStr)

            # load the radiosonde data into numpy array
            for index in range(len(dataLines)):
                data[index]['pressure'] = str_2_double(
                    dataLines[index][0:7]
                )
                data[index]['height'] = str_2_double(
                    dataLines[index][7:14]
                )
                data[index]['temperature'] = str_2_double(
                    dataLines[index][14:21]
                )
                data[index]['dewpoint'] = str_2_double(
                    dataLines[index][21:28]
                )
                data[index]['RH'] = str_2_double(
                    dataLines[index][28:35]
                )
                data[index]['WVMR'] = str_2_double(
                    dataLines[index][35:42]
                )
                data[index]['wind_direction'] = str_2_double(
                    dataLines[index][42:49]
                )
                data[index]['wind_speed'] = str_2_double(
                    dataLines[index][49:56]
                )
                data[index]['theta_a'] = str_2_double(
                    dataLines[index][56:63]
                )
                data[index]['theta_e'] = str_2_double(
                    dataLines[index][63:70]
                )
                data[index]['theta_v'] = str_2_double(
                    dataLines[index][70:77]
                )

            # load souding information
            metadataStr = metadataTag.string
            metadataDict = self.__parse_rs_metadata(metadataStr)

            # construct the dimension, variable and global attributes
            dims = {'altitude': len(dataLines), 'nv': 1}
            variables = {
                'pressure': data['pressure'],
                'altitude': data['height'],
                'temperature': data['temperature'],
                'dewpoint': data['dewpoint'],
                'relative_humidity': data['RH'],
                'water_vapor_mixing_ratio': data['WVMR'],
                'wind_direction': data['wind_direction'],
                'wind_speed': data['wind_speed'],
                'theta_a': data['theta_a'],
                'theta_e': data['theta_e'],
                'theta_v': data['theta_v'],
                'temperature_LCL': metadataDict['temperature_LCL'],
                'pressure_LCL': metadataDict['pressure_LCL'],
                'precipitable_water': metadataDict['PWV'],
                'launch_time': datetime.datetime.strptime(
                    metadataDict['launch_time'], '%y%m%d/%H%M'
                )
            }
            gAttris = {
                'station_name': self.search_station_name(
                    metadataDict['station_number']
                ),
                'station_number': metadataDict['station_number'],
                'station_latitude': metadataDict['station_latitude'],
                'station_longitude': metadataDict['station_longitude'],
                'station_elevation': metadataDict['station_elevation']
            }

            dimsList.append(dims)
            dataList.append(variables)
            gAttrsList.append(gAttris)

        return dataList, dimsList, gAttrsList

    def __parse_rs_metadata(self, content):
        """
        Parse the metadata from radiosonde system information.

        Parameters
        ----------
        content: str
            radiosonde station information. See **Example**

        Returns
        -------
        data: dict
            station_number: integer
            number of the station for launching the radiosonde.
            launch_time: str
            time for the launching. e.g., '190916/1200'
            station_latitude: float
            latitude of the launching station.
            station_longitude: float
            longitude of the launching station.
            station_elevation: float
            height of the launching station above mean sea level. [m]
            temperature_LCL: float
            temperature of the Lifted Condensation Level. [K]
            pressure_LCL: float
            pressure of the Lifted Condensation Level. [hPa]
            PWV: float
            Precipitable water for entire sounding. [mm]

        Example
        -------
        Station information and sounding indices

                                    Station number: 40179
                                Observation time: 190916/1200
                                Station latitude: 32.00
                                Station longitude: 34.81
                                Station elevation: 35.0
                                    Showalter index: 7.75
                                    Lifted index: 1.55
            LIFT computed using virtual temperature: 0.82
                                        SWEAT index: 134.78
                                            K index: 1.10
                                Cross totals index: 12.70
                            Vertical totals index: 21.70
                                Totals totals index: 34.40
            Convective Available Potential Energy: 0.00
                    CAPE using virtual temperature: 17.64
                            Convective Inhibition: 0.00
                    CINS using virtual temperature: -18.91
        Equilibrum Level using virtual temperature: 423.22
                    LFCT using virtual temperature: 829.22
                            Bulk Richardson Number: 0.00
                Bulk Richardson Number using CAPV: 2.10
        Temp [K] of the Lifted Condensation Level: 289.53
        Pres [hPa] of the Lifted Condensation Level: 879.95
            Mean mixed layer potential temperature: 300.31
                    Mean mixed layer mixing ratio: 13.51
                    1000 hPa to 500 hPa thickness: 5754.00
        Precipitable water [mm] for entire sounding: 27.30
        """

        decoders = {
            'station_number':
                (
                    r'(?<=Station number: )\d+.?\d+',
                    int,
                    00000
                ),
            'launch_time':
                (
                    r'(?<=Observation time: )\d+/\d+',
                    str,
                    '000000/0000'
                ),
            'station_latitude':
                (
                    r'(?<=Station latitude: )-?\d+\.?\d+',
                    float,
                    0.0
                ),
            'station_longitude':
                (
                    r'(?<=Station longitude: )-?\d+\.?\d+',
                    float,
                    0.0
                ),
            'station_elevation':
                (
                    r'(?<=Station elevation: )-?\d\.?\d+',
                    float,
                    0.0
                ),
            'temperature_LCL':
                (
                    r'(?<=Temp [K] of the Lifted Condensation ' +
                    r'Level: )\d+\.?\d+',
                    float,
                    0.0
                ),
            'pressure_LCL':
                (
                    r'(?<=Pres [hPa] of the Lifted ' +
                    r'Condensation Level: )\d+\.?\d+',
                    float,
                    0.0
                ),
            'PWV':
                (
                    r'(?<=Precipitable water [mm] ' +
                    r'for entire sounding: )\d+\.?\d+',
                    float,
                    0.0
                )
        }

        def find_in_string(key, dec, str):
            res = re.search(dec[0], str)
            if res is not None:
                val = dec[1](res.group())
            else:
                val = dec[2]
            return val

        data = {}

        for key, regex in decoders.items():
            val = find_in_string(key, regex, content)
            data.update({key: val})

        return data

    def save_netCDF(self, rsData, rsDims, rsGlobalAttrs, output_dir, *args,
                    force=False):
        """
        Save radiosonde data to netCDF file.

        Parameters
        ----------
        rsData: list
            radiosonde data list. Every element is a dict, which consists
            of the radiosonde data.
            {
                'pressure'
                'altitude'
                'temperature'
                'dewpoint'
                'relative_humidity'
                'water_vapor_mixing_ratio'
                'wind_direction'
                'wind_speed'
                'theta_a'
                'theta_e'
                'theta_v'
                'temperature_LCL'
                'pressure_LCL'
                'precipitable_water'
                'launch_time'
            }
            Detailed information can be found in [here](http://weather.uwyo.edu/cgi-bin/sounding?region=europe&TYPE=TEXT%3ALIST&YEAR=2019&MONTH=02&FROM=0400&TO=0500&STNM=85934)
        rsDims: list
            dimensions of radiosonde data. Every element is a dict, which
            consists of the dimensions of the specified radiosonde data.
        rsGlobalAttrs: list
            radiosonde metadata.
            {
                'station_name'
                'station_number'
                'station_latitude'
                'station_longitude'
                'station_elevation'
            }
        output_dir: str
        output directory for saving the netCDF files.

        Keywords
        --------
        force: boolean
        flag to control whether overwrite the netCDF file if it exists.

        History
        -------
        2019-11-04 First edition by Zhenping
        """

        if (not rsData) or (not rsDims) or (not rsGlobalAttrs):
            return

        if not os.path.exists(output_dir):
            logger.warn('Output directory for saving the results does' +
                        'not exist.\n{path}'.format(path=output_dir))
            # whether to create the folder
            res = input("Create the folder forcefully? (yes|no): ")
            if res.lower() == 'yes':
                os.mkdir(output_dir)

        output_file = DOWNLOAD_CONFIG['radiosonde']['nc_file_naming'].format(
            sitenum=rsGlobalAttrs['station_number'],
            date=rsData['launch_time'].strftime('%Y%m%d_%H%M')
        )
        output_filepath = os.path.join(output_dir, output_file)

        # whether to overwrite the file if it exists
        if (os.path.exists(output_filepath)) and \
           (os.path.isfile(output_filepath)) and (not force):
            logger.warning(
                '{file} exists. Jump over'.format(file=output_filepath)
            )
            return
        elif (os.path.exists(output_filepath)) and \
             (os.path.isfile(output_filepath)) and force:
            logger.warning('{file} exists. Overwrite it!'.format(
                file=output_filepath
            ))

        netCDF_format = DOWNLOAD_CONFIG['radiosonde']['NETCDF_FORMAT']
        dataset = Dataset(output_filepath, 'w',
                          format=netCDF_format,
                          zlib=True)

        # create dimensions
        for dim_key in METADATA_CONFIG['dimensions']:
            dataset.createDimension(dim_key, rsDims[dim_key])

        # create and write variables, write variable attributes
        npTypeDict = {
            'byte': np.byte,
            'int': np.intc,
            'float': np.single,
            'double': np.double,
            'string': np.str
        }
        for var_key in rsData:

            if var_key == 'launch_time':
                # convert python datetime object to POXIS timestamp
                rsData[var_key] = rsData[var_key].timestamp()

            # create variables
            if ('_FillValue' in METADATA_CONFIG[var_key]):
                dataset.createVariable(
                    var_key,
                    npTypeDict[METADATA_CONFIG[var_key]['dtype']],
                    tuple(METADATA_CONFIG[var_key]['dims']),
                    fill_value=METADATA_CONFIG[var_key]['_FillValue']
                )
            else:
                dataset.createVariable(
                    var_key,
                    npTypeDict[METADATA_CONFIG[var_key]['dtype']],
                    tuple(METADATA_CONFIG[var_key]['dims'])
                )

            # write variables
            dataset.variables[var_key][:] = rsData[var_key]

            # write attributes
            for var_attr in METADATA_CONFIG[var_key]:
                if (var_attr != 'dtype') and \
                   (var_attr != 'dims') and \
                   (var_attr != '_FillValue'):
                    setattr(
                        dataset.variables[var_key],
                        var_attr,
                        METADATA_CONFIG[var_key][var_attr]
                    )

        # create global attributes
        for attr_key in rsGlobalAttrs:
            setattr(
                dataset,
                attr_key,
                rsGlobalAttrs[attr_key]
            )

        historyStr = "{time}: processed by {name}-{version}".format(
            time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            name=DOWNLOAD_CONFIG['radiosonde']['processor_name'],
            version=DOWNLOAD_CONFIG['radiosonde']['processor_version']
        )

        dataset.close()

        return output_filepath

    def read_station_list(self, file):
        """
        read the list of station information from file.
        """

        if (not os.path.exists(file)) or (not os.path.isfile(file)):
            logger.warning('Station list file does not exist.\n' +
                           '{file}'.format(file=file))
            raise FileNotFoundError

        # data type to load the data
        # e.g.,
        # "VQW00011602  17.7000  -64.8000   16.8 VI ST CROIX
        # (BENEDICT FIELD)      1948 1948    346"

        station_list = []
        with open(file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()

            for line in lines:
                try:
                    station_list.append({
                        'ID': int(line[6:11]),
                        'lat': float(line[12:20]),
                        'lon': float(line[21:30]),
                        'elevation': float(line[31:37]),
                        'station_name': line[41:71].strip()
                    })
                except Exception as e:
                    logger.warning(e)

        return station_list

    def list_station_number(self, file=None):
        """
        List all the available station numbers.
        """

        logger.info('{ID:6} {name:30} {lat:8} {lon:9}'.
                    format(ID='ID', name='name', lat='lat', lon='lon'))
        for item in self.station_list:
            logger.info('{ID:6} {name:30} {lat:8.4} {lon:9.4}'.format(
                ID=item['ID'],
                name=item['station_name'],
                lat=item['lat'],
                lon=item['lon']
            )
            )

    def get_station_names(self, file=None):
        """
        Get the list of radiosonde station names.
        """

        if file is None:
            station_list_file = os.path.join(tempfile.mkdtemp(),
                                             'station_list')
            self.download_station_list(station_list_file)
            station_list = self.read_station_list(station_list_file)
            os.remove(station_list_file)
        else:
            if (not os.path.exists(file)) or (not os.path.isfile(file)):
                logger.error('{file} does not exist.'.format(file=file))
                raise FileNotFoundError
            else:
                station_list = self.read_station_list(file)

        return station_list

    def search_station_name(self, station_number, file=None):
        """
        Search the station name with the given station number.
        """

        for item in self.station_list:
            if item['ID'] == station_number:
                logger.info('{number}->{name}'.format(
                    number=station_number,
                    name=item['station_name']
                ))

                return item['station_name']

        logger.warning('No items was found based on the station ' +
                       'number of {number}'.format(number=station_number))
        return None

    def download_station_list(self, file):
        """
        Download the global radiosonde station list.
        """

        reqURL = DOWNLOAD_CONFIG['radiosonde']['URL_station_list']
        logger.info('Start downloading the station list from {url}'.
                    format(url=reqURL))

        try:
            res = requests.get(reqURL)
        except Exception as e:
            logger.error('Error in connecting {url}'.format(url=reqURL))

        with open(file, 'w', encoding='utf-8') as fh:
            fh.write(res.content.decode('utf-8'))

        logger.info('Saved station list to {file}'.format(file=file))

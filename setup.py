import sys
import os
import datetime

testPath = os.path.dirname(__file__)
srcPath = os.path.join(testPath, 'src')
sys.path.append(srcPath)

from radiosonde_downloader import RSDownloader


def main():
    rs = RSDownloader(station_file='C:\\Users\\zpyin\\Desktop\\Data_Downloader\\doc\\station_list')

    startTime = datetime.datetime(2019, 1, 1)
    stopTime = datetime.datetime(2019, 2, 1)

    rsData, rsDims, rsGAttrs = rs.getData(startTime, stopTime, siteNum=57494)
    iterators = zip(rsData, rsDims, rsGAttrs)
    for thisData, thisDims, thisGAttrs in iterators:
        rs.save_netCDF(thisData, thisDims, thisGAttrs,
                       'D:\\Data\\Radiosonde\\wuhan', force=True)


if __name__ == '__main__':
    main()

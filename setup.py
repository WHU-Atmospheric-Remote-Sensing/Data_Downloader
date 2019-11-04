import sys
import os

testPath = os.path.dirname(__file__)
srcPath = os.path.join(os.path.dirname(testPath), 'src')
sys.path.append(srcPath)

from radiosonde_downloader import RSDownloader


def main():
    # print('------------------------------------------------------------------')
    # print("Test on GetRSData: data = GetRSData('2014', '05', '08', '00', siteNum='57494')")
    # data = GetRSData('2014', '05', '08', '00', siteNum='57494', file='/Users/yinzhenping/Desktop/temp.h5')
    # print(data)
    rs = RSDownloader(
        station_file='/var/folders/_g/p9xv1xwd259dx74b5xkrj94h0000gn/T/tmpik4ngm5p/station_list')
    # rs.list_station_number()
    # rs.search_station_name(57494)

    startTime = datetime.datetime(2018, 12, 1)
    stopTime = datetime.datetime(2018, 12, 2)
    # rs.get_daily_data(startTime, stopTime)

    rsData, rsDims, rsGAttrs = rs.getData(startTime, stopTime)
    iterators = zip(rsData, rsDims, rsGAttrs)
    for thisData, thisDims, thisGAttrs in iterators:
        rs.save_netCDF(thisData, thisDims, thisGAttrs,
                       '/Users/yinzhenping/Desktop/Data_Downloader/tmp/', force=True)


if __name__ == '__main__':
    main()

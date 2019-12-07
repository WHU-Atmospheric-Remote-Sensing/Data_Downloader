import sys
import os
import datetime
import argparse

testPath = os.path.dirname(__file__)
srcPath = os.path.join(testPath, 'src')
sys.path.append(srcPath)

from src.radiosonde_downloader import RSDownloader


parser = argparse.ArgumentParser()
parser.add_argument('--start', help='start date in the format YYYYMMDD')
parser.add_argument('--stop', help='stop date in the format YYYYMMDD')
parser.add_argument('--output_dir', help='output directory')

args = parser.parse_args()

if args.output_dir is None:
    args.output_dir = 'D:\\Data\\Radiosonde\\wuhan'

rs = RSDownloader(station_file='C:\\Users\\zpyin\\Desktop\\Data_Downloader\\doc\\station_list')

startTime = datetime.datetime.strptime(args.start, '%Y%m%d')
stopTime = datetime.datetime.strptime(args.stop, '%Y%m%d')

rsData, rsDims, rsGAttrs = rs.getData(startTime, stopTime, siteNum=57494)
iterators = zip(rsData, rsDims, rsGAttrs)
for thisData, thisDims, thisGAttrs in iterators:
    rs.save_netCDF(thisData, thisDims, thisGAttrs, args.output_dir, force=True)

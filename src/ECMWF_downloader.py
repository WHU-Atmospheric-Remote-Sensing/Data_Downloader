#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
from bypy import ByPy
import datetime as dt
import os
from configs import load_download_config

CONFIG = load_download_config()
server = ECMWFDataServer()


def get_ECMWF_file(mDateRange, dataset='cams_nrealtime', filepath='output'):
    """
    retrieve the ECMWF file through ECMWF Client.

    Parameters
    ----------
    mDateRange: list of 2-element datetime object
        start and stop time of the query.
    dateset: str
        ECMWF products (default: 'cams_nrealtime').
    filepath: str
        absolute path for saving ECMWF file.
    History
    -------
    2020-03-01 First version.
    """

    # create .ecmwfapirc file
    ecmwfapircPath = os.path.join(os.environ['HOME'], '.ecmwfapirc')
    if not os.path.exists(ecmwfapircPath):
        with open(ecmwfapircPath, 'w', 'utf-8') as fh:
            fh.write(CONFIG['ECMWF']['ecmwfapirc'])

    payload = {
        "class": "mc",
        "dataset": dataset,
        "date": "{0}/to/{1}".format(
            mDateRange[0].strftime('%Y-%m-%d'),
            mDateRange[1].strftime('%Y-%m-%d')
            ),
        "expver": "0001",
        "levtype": "sfc",
        "param": "137.128/165.128/167.128/250.210/251.210",
        "step": "0",
        "stream": "oper",
        "time": "00:00:00/06:00:00/12:00:00/18:00:00",
        "type": "an",
        "target": filepath,
    }
    server.retrieve(payload)

    payload = {
        "class": "mc",
        "dataset": dataset,
        "date": "{0}/to/{1}".format(
            mDateRange[0].strftime('%Y-%m-%d'),
            mDateRange[1].strftime('%Y-%m-%d')
            ),
        "expver": "0001",
        "levtype": "sfc",
        "param": "73.210/74.210/137.128/165.128/167.128/207.210/208.210/209.210/211.210/212.210/250.210/251.210",
        "step": "0",
        "stream": "oper",
        "time": "00:00:00/12:00:00",
        "type": "fc",
        "target": filepath,
    }
    server.retrieve(payload)


def main():
    tRange = [dt.datetime(2019, 10, 1), dt.datetime(2019, 10, 31)]
    product = 'cams_nrealtime'
    filename = '{product}_{date}.grib'.format(
        product=product,
        date=tRange[0].strftime('%Y%m'))
    filepath = os.path.join(CONFIG['ECMWF']['DATA_DIR'], filename)
    get_ECMWF_file(tRange, dataset=product, filepath=filepath)

    bp = ByPy()
    bp.upload(filepath, os.path.join(CONFIG['ECMWF']['BDY_DIR'], filename))


if __name__ == "__main__":
    main()

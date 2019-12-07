# Data_Downloader

## Description

## Requirements

- Anaconda3

## Dependencies

```bash
conda create -n data_downloader
conda activate data_downloader

conda install python=3.6
pip install -r requirements
```

## Usage

### Download radiosonde data

```bash
python download_radiosonde.py --start 20110101 --stop 20120101 --output_dir /user/zp/data
```

## Contacts

Zhenping <zp.yin@whu.edu.cn>
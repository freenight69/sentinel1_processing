#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: sentinel1_test.py
Version: v1.0
Date: 2023-03-08
Authors: Chen G.
Description: This script creates downloading and processing Sentinel-1 images.
License: This code is distributed under the MIT License.

    sentinel1_download Parameter:
        USER_NAME: The account name to log in ESA Copernicus Open Access Hub (https://scihub.copernicus.eu/).
        PASSWORD: The account password to log in ESA Copernicus Open Access Hub.
        FOOTPRINT: The region to include imagery within.
        START_DATE: A time interval filter based on the Sensing Start Time of the products. Following formats:
            - yyyyMMdd
            - yyyy-MM-ddThh:mm:ss.SSSZ (ISO-8601)
            - yyyy-MM-ddThh:mm:ssZ
            - NOW
            - NOW-<n>DAY(S) (or HOUR(S), MONTH(S), etc.)
            - NOW+<n>DAY(S)
            - yyyy-MM-ddThh:mm:ssZ-<n>DAY(S)
            - NOW/DAY (or HOUR, MONTH etc.) - rounds the value to the given unit
        END_DATE: A time interval filter based on the Sensing Start Time of the products.
        PRODUCT_TYPE: Type of sentinel-2 product to apply (String):
            'GRD' - Sentinel-1 SAR GRDH product
            'SLC' - Sentinel-1 SAR SLC product
        SAVE_DIR: Download the sentinel-1 images to local.

    sentinel1_preprocess Parameter:
        INPUT_PATH: The file path of Sentinel-1 .ZIP files to be processed.
        OUTPUT_PATH: The file path to save preprocessed images.
        PROJ: The output coordinate system.

"""

import datetime
import sentinel1_download as s1d
import sentinel1_preprocess as s1p

# Parameters
s1_download_parameter = {'USER_NAME': 'gongchen9369',
                         'PASSWORD': '13919389875er',
                         'FOOTPRINT': 'POLYGON((115.5 40.2, 116.0 40.2, 116.0 40.5, 115.5 40.5, 115.5 40.2))',
                         'START_DATE': '20230201',
                         'END_DATE': '20230308',
                         'PRODUCT_TYPE': 'GRD',
                         'SAVE_DIR': 'G:/s1_processing/download'
                         }

in_proj = '''
        GEOGCS["WGS 84",
         DATUM["WGS_1984",
              SPHEROID["WGS 84", 6378137, 298.257223563, AUTHORITY["EPSG", "7030"]],
              AUTHORITY["EPSG", "6326"]],
         PRIMEM["Greenwich", 0, AUTHORITY["EPSG", "8901"]],
         UNIT["degree", 0.0174532925199433, AUTHORITY["EPSG", "9122"]],
         AUTHORITY["EPSG", "4326"]]
         '''
s1_preprocess_parameter = {'INPUT_PATH': 'G:/s1_processing/download',
                           'OUTPUT_PATH': 'G:/s1_processing/preprocess',
                           'PROJ': in_proj
                           }

# /***************************/
# // MAIN
# /***************************/
if __name__ == "__main__":
    start_time = datetime.datetime.now()

    # (1) Sentinel-1产品数据下载
    s1d.s1_download(s1_download_parameter)

    # (2) Sentinel-1 SAR GRD格式产品数据处理
    s1p.s1_grd_preprocess_batch(s1_preprocess_parameter)

    end_time = datetime.datetime.now()
    # 输出程序运行所需时间
    print("Elapsed Time:", end_time - start_time)

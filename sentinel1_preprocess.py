#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
import os
import gc
import glob
import helper


# ---------------------------------------------------#
#   Preprocessing Sentinel-1 SAR GRD product data
# ---------------------------------------------------#
def s1_grd_preprocess(files, proj, out_path):
    """
    Sentinel-1 GRD文件预处理函数

    :param files: 待处理文件
    :param proj: 投影坐标系
    :param out_path: 文件保存地址
    """
    files = files.split(';')
    basename = os.path.basename(files[0])
    # 获取时间和日期
    date = basename.split('_')[4].split('T')[0]
    # 循环开始时间
    loopstarttime = str(datetime.datetime.now())
    print('Start time:', loopstarttime)
    start_time = time.time()

    # 开始预处理:
    # 镶嵌
    product_list = []
    for index in range(len(files)):
        sentinel_1 = helper.read_s1_zip_file(files[index])
        # 热噪声去除
        thermalremoved = helper.do_thermal_noise_removal(sentinel_1)
        applyorbit = helper.do_apply_orbit_file(thermalremoved)
        # 辐射定标
        calibrated = helper.do_calibration(applyorbit)
        product_list.append(calibrated)
    # 镶嵌
    assembly = helper.do_SliceAssembly(product_list)
    del thermalremoved, applyorbit, calibrated
    # 斑点滤波
    filtered = helper.do_speckle_filtering(assembly)
    # 地形校正
    terrain_corrected = helper.do_terrain_correction(filtered, proj)
    del filtered
    # 分贝化
    line_to_db = helper.do_line_to_db(terrain_corrected)
    del terrain_corrected
    # 写入数据
    print("Writing...")
    # 文件输出名
    out_filename = basename.split('.')[0]
    final_path = os.path.join(out_path, out_filename + ".tif")
    helper.write_to_file(line_to_db, final_path, format='GeoTIFF-BigTIFF')
    del line_to_db

    print('Done.')
    print("--- %s seconds ---" % (time.time() - start_time))


# ---------------------------------------------------#
#   Batch preprocessing Sentinel-1 SAR GRD product data
# ---------------------------------------------------#
def s1_grd_preprocess_batch(params):
    """
    Sentinel-1 GRD文件预处理批处理函数

    :param params: These parameters determine the data batch processing parameters.
    """
    INPUT_PATH = params['INPUT_PATH']
    OUTPUT_PATH = params['OUTPUT_PATH']
    PROJ = params['PROJ']

    # 检查参数
    if INPUT_PATH is None:
        raise ValueError("ERROR!!! Parameter INPUT_PATH not correctly defined")
    if OUTPUT_PATH is None:
        raise ValueError("ERROR!!! Parameter OUTPUT_PATH not correctly defined")
    if PROJ is None:
        PROJ = '''
        GEOGCS["WGS 84",
         DATUM["WGS_1984",
              SPHEROID["WGS 84", 6378137, 298.257223563, AUTHORITY["EPSG", "7030"]],
              AUTHORITY["EPSG", "6326"]],
         PRIMEM["Greenwich", 0, AUTHORITY["EPSG", "8901"]],
         UNIT["degree", 0.0174532925199433, AUTHORITY["EPSG", "9122"]],
         AUTHORITY["EPSG", "4326"]]
         '''

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    # 获取该输入路径的Sentinel-1 GRDH原始数据压缩文件.zip
    zip_files = sorted(glob.glob(os.path.join(INPUT_PATH, '*.zip')))
    # 同一天两景中的某景构成的part1列表
    part1_files = zip_files[::2]
    # 同一天两景中的另一景构成的part2列表
    part2_files = zip_files[1::2]

    for file_ndex in range(len(part1_files)):
        gc.enable()
        gc.collect()
        files = [part1_files[file_ndex], part2_files[file_ndex]]
        basename = os.path.basename(files[0])
        # 获取时间和日期
        date = basename.split('_')[4].split('T')[0]
        print("PreProcessing %s's data..." % date)
        files = ';'.join(files)

        s1_grd_preprocess(files, PROJ, OUTPUT_PATH)
        print("The Preprocession of  %s's data finishes!" % date)
        # 睡眠30s，以等待释放内存
        print("Sleeping...")
        time.sleep(30)

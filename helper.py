#!/usr/bin/env python
# -*- coding: utf-8 -*-
from snappy import ProductIO
from snappy import HashMap
from snappy import GPF
from snappy import jpy
from snappy import File
from snappy import ProgressMonitor


def read_s1_zip_file(file_name):
    """
    读入Sentinel-1原始.zip文件，返回Product

    :param file_name: Sentinel-1原始.zip文件存储地址
    :return: product
    """
    print('\tReading Sentinel-1 zip file...')
    # 执行读入操作
    output = ProductIO.readProduct(file_name)
    return output


def do_apply_orbit_file(product):
    """
    轨道校正操作 - snappy

    :param product: 输入product
    :return: 输出轨道矫正后的product
    """
    print('\tApply orbit file...')
    parameters = HashMap()
    parameters.put('Apply-Orbit-File', True)
    # 执行轨道校正操作
    output = GPF.createProduct('Apply-Orbit-File', parameters, product)
    return output


def do_thermal_noise_removal(product):
    """
    热噪声去除操作 - snappy

    :param product: 输入product
    :return: 热噪声去除后的product
    """
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    # 执行热噪声去除操作
    output = GPF.createProduct('ThermalNoiseRemoval', parameters, product)
    return output


def do_calibration(product):
    """
    辐射定标操作 - snappy

    :param product: 输入product
    :return: 辐射定标后的product
    """
    print('\tCalibration...')
    parameters = HashMap()
    # 以标准后向散射系数sigma0的方式定标
    parameters.put('outputSigmaBand', True)
    parameters.put('productBands', 'Intensity_VH,Intensity_VV')
    parameters.put('selectedPolarisations', 'VH,VV')
    # 没有分贝化
    parameters.put('outputImageScaleInDb', False)
    output = GPF.createProduct("Calibration", parameters, product)
    return output


def do_speckle_filtering(product):
    """
    斑点噪声去除操作 - snappy

    :param product: 输入product
    :return: 斑点噪声去除后的product
    """
    print('\tSpeckle filtering...')
    parameters = HashMap()
    # 使用Refine Lee滤波器。默认是Lee Sigma
    parameters.put('filter', 'Refined Lee')
    output = GPF.createProduct('Speckle-Filter', parameters, product)
    return output


def do_terrain_correction(product, proj):
    """
    地形校正操作 - snappy

    :param product: 输入product
    :param proj: 投影坐标系参数
    :return: 地形校正后的product
    """
    print('\tTerrain correction...')
    parameters = HashMap()
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    # parameters.put('mapProjection', proj)       # 如果需要使用UTM/WGS84投影，可以注释该行代码,默认是WGS84地理坐标系
    parameters.put('saveProjectedLocalIncidenceAngle', False)
    parameters.put('saveSelectedproductBand', True)
    parameters.put('nodataValueAtSea', False)
    # 分辨率为10m
    parameters.put('pixelSpacingInMeter', 10.0)
    output = GPF.createProduct('Terrain-Correction', parameters, product)
    return output


def do_line_to_db(product):
    """
    分贝化操作，将线性单位转为分贝值

    :param product: 输入product
    :return: 地形校正后的product
    """
    print('\tLining_to_db...')
    # 使用默认参数值，即选择所有通道
    parameters = HashMap()
    output = GPF.createProduct('LinearToFromdB', parameters, product)
    return output


def do_subset(product, wkt):
    """
    使用wkt坐标范围裁剪

    :param product: 输入product
    :param wkt: wkt坐标
    :return: 裁剪后的product
    """
    print('\tSubsetting...')
    parameters = HashMap()
    parameters.put('geoRegion', wkt)
    output = GPF.createProduct('Subset', parameters, product)
    return output


def do_subset(product, x, y, width, height):
    """
    使用像素坐标裁剪

    :param product: 输入product
    :param x: 裁剪范围左上角x坐标
    :param y: 裁剪范围左上角y坐标
    :param width: 裁剪范围宽度
    :param height: 裁剪范围高度
    :return: 裁剪后的product
    """
    parameters = HashMap()
    # 复制元数据
    parameters.put('copyMetadata', True)
    # 设置裁剪区域参数
    parameters.put('region', '%s, %s, %s, %s' % (x, y, width, height))
    # 执行裁剪操作
    output = GPF.createProduct('Subset', parameters, product)
    return output


def do_SliceAssembly(product_list):
    """
    使用像素坐标裁剪

    :param product_list: 输入待拼接product list
    :return: 拼接后的product
    """
    # 使用默认参数值，即选择所有通道
    # 创建一个product类数组
    products = jpy.array('org.esa.snap.core.datamodel.Product', len(product_list))
    for count in range(len(product_list)):
        products[count] = product_list[count]
    parameters = HashMap()
    output = GPF.createProduct('SliceAssembly', parameters, products)
    return output


def write_to_file(product, file_path, format='BEAM-MAP'):
    """
    写入操作 - snappy

    :param product: 输入product
    :param file_path: 输出文件存储地址
    :param format: 输出文件格式
    :return: product
    """
    print("Writing...")
    # 不支持更新数据
    incremental = False
    # 以format格式写入
    GPF.writeProduct(product, File(file_path), format, incremental, ProgressMonitor.NULL)

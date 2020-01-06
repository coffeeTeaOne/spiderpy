# encoding: utf-8
import time
import math

global jobinst_id
global job_code
global group_code
global fire_time
global address_code


def set_jobinst_id(value):
    # 定义的全局变量,而不是方法内部的局部变量.
    global jobinst_id
    jobinst_id = value


def get_jobinst_id():
    # 并返回全局变量,而不是方法内部的局部变量.
    global jobinst_id
    try:
        return jobinst_id
    except:
        return None


def set_job_code(value):
    global job_code
    job_code = value


def get_job_code():
    global job_code
    try:
        return job_code
    except:
        return None


def set_group_code(value):
    global group_code
    group_code = value


def get_group_code():
    global group_code
    try:
        return group_code
    except:
        return None


def set_address_code(value):
    global address_code
    address_code = value


def get_address_code():
    global address_code
    try:
        return address_code
    except:
        return None


def set_fire_time(value):
    global fire_time
    fire_time = value


def get_fire_time():
    global fire_time

    try:
        if fire_time:
            time_local = time.localtime(math.ceil(int(fire_time) / 1000))

            time_local = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    except:
        time_local = None

    return time_local

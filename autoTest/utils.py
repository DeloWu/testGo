# -*- coding:utf-8 -*-
from httprunner import validator

def add(*args):
    sum = 0
    for item in args:
        sum += int(item)
    return sum

def show_request_or_response(request_or_response):
    return request_or_response

def get_functions_mapping():
    functions_mapping = {}
    for name, value in globals().items():
        if validator.is_function((name, value)):
            functions_mapping[name] = value
    return functions_mapping

if __name__ == '__main__':
    pass
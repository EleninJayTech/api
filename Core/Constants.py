from Libraries.Utility import path_slash

import os

# DEVICE
if os.name == 'posix':
    # 리눅스
    CURRENT_DEVICE = 'linux'
elif os.name == 'nt':
    # PC
    CURRENT_DEVICE = 'pc'

# 루트 경로
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = '{}/../'.format(ROOT_DIR)
ROOT_DIR = path_slash(ROOT_DIR)
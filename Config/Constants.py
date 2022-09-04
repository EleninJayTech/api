import os

# DEVICE
if os.name == 'posix':
    # 리눅스
    CURRENT_DEVICE = 'linux'
elif os.name == 'nt':
    # PC
    CURRENT_DEVICE = 'pc'
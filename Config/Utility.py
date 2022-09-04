import os


def path_slash(path_str: str):
    """
    경로 운영 체제에 맞도록 슬러시 변경
    :param path_str:
    :return:
    """
    if os.name == 'nt':
        path_str = path_str.replace('\\', '/')
    else:
        path_str = path_str.replace('/', '\\')
    return path_str

def path_slash(path_str: str):
    """
    경로 역 슬러시 / 로 변경
    :param path_str:
    :return:
    """
    path_str = path_str.replace('\\', '/')
    return path_str

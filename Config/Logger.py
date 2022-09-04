import os
import logging.handlers


def set_logs():
    try:
        # 현재 파일 경로 및 파일명 찾기
        current_dir = os.path.dirname(os.path.realpath(__file__))
        current_file = os.path.basename(__file__)
        current_file_name = current_file[:-3]  # xxxx.py
        log_filename = 'log-{}'.format(current_file_name)

        # 로그 저장할 폴더 생성
        log_dir = '{}/../logs'.format(current_dir)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 로거 생성
        api_logger = logging.getLogger('api_log')  # 로거 이름
        api_logger.setLevel(logging.DEBUG)  # 로깅 수준: DEBUG

        # 핸들러 생성
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_filename, when='midnight', interval=1, encoding='utf-8'
        )  # 자정마다 한 번씩 로테이션
        file_handler.suffix = 'log-%Y%m%d'  # 로그 파일명 날짜 기록 부분 포맷 지정

        api_logger.addHandler(file_handler)  # 로거에 핸들러 추가
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s'
        )
        file_handler.setFormatter(formatter)  # 핸들러에 로깅 포맷 할당
        use_log = True
    except Exception as e:
        use_log = False
        print(e)
    return use_log

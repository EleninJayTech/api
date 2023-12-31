# 로또
CREATE TABLE `lotto_winning` (
	`drwNo` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '회차',
	`drwNoDate` date NOT NULL COMMENT '당첨일',
	`totSellamnt` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '누적 금액',
	`returnValue` VARCHAR(30) NOT NULL DEFAULT '' COMMENT 'API 호출 상태',
	`firstAccumamnt` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '총 1등 당첨금',
	`firstWinamnt` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '1등 수령 액',
	`firstPrzwnerCo` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '1등 당첨 인원',
	`bnusNo` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '2등 보너스 번호',
	`drwtNo1` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '당첨 번호 1',
	`drwtNo2` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '당첨 번호 2',
	`drwtNo3` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '당첨 번호 3',
	`drwtNo4` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '당첨 번호 4',
	`drwtNo5` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '당첨 번호 5',
	`drwtNo6` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '당첨 번호 6',
	PRIMARY KEY (`drwNo`,`drwNoDate`),
	KEY `IDX_DATE` (`drwNoDate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='당첨 정보';

# 주식
CREATE TABLE `corp_code` (
	`corp_code` char(8) NOT NULL COMMENT '공시대상회사의 고유번호(8자리) ※ ZIP File 안에 있는 XML파일 정보',
	`corp_name` varchar(100) DEFAULT NULL COMMENT '정식회사명칭 ※ ZIP File 안에 있는 XML파일 정보',
	`stock_code` varchar(6) DEFAULT NULL COMMENT '상장회사인 경우 주식의 종목코드(6자리) ※ ZIP File 안에 있는 XML파일 정보',
	`modify_date` char(8) DEFAULT NULL COMMENT '기업개황정보 최종변경일자(YYYYMMDD) ※ ZIP File 안에 있는 XML파일 정보',
	`add_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성(등록)일자',
	`mod_date` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '데이터 수정일자',
	PRIMARY KEY (`corp_code`),
	KEY `IDX_SCODE` (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='DART에 등록되어있는 공시대상회사의 고유번호,회사명,종목코드, 최근변경일자';

CREATE TABLE stock_daily (
	stock_daily_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '기본 키, 자동 증가',
	basDt INT UNSIGNED NOT NULL COMMENT '기준일자 (YYYYMMDD 형식)',
	srtnCd CHAR(6) NOT NULL COMMENT '단축코드 (예: 016790)',
	isinCd VARCHAR(20) NOT NULL COMMENT 'ISIN코드 (예: KR7016790008)',
	itmsNm VARCHAR(100) COMMENT '종목명 (예: 카나리아바이오)',
	mrktCtg VARCHAR(20) COMMENT '시장구분 (예: KOSDAQ)',
	clpr INT UNSIGNED COMMENT '종가',
	vs INT COMMENT '전일 대비 등락',
	fltRt DECIMAL(5, 2) COMMENT '전일 대비 등락에 따른 비율 (%)',
	mkp INT UNSIGNED COMMENT '시가',
	hipr INT UNSIGNED COMMENT '고가',
	lopr INT UNSIGNED COMMENT '저가',
	trqu BIGINT UNSIGNED COMMENT '거래량',
	trPrc BIGINT UNSIGNED COMMENT '거래대금',
	lstgStCnt BIGINT UNSIGNED COMMENT '상장주식수',
	mrktTotAmt BIGINT UNSIGNED COMMENT '종가*상장주식수',
	KEY IDX_BASDT (basDt),
	KEY IDX_CLPR (clpr),
	KEY IDX_SRTNCD (srtnCd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '일자별 주식 시세 정보';
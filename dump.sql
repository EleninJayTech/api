CREATE TABLE `lotto_winning` (
	`drwNo` int unsigned NOT NULL DEFAULT 0 COMMENT '회차',
	`drwNoDate` DATE NULL COMMENT '당첨일',
	`totSellamnt` int unsigned NOT NULL DEFAULT 0 COMMENT '누적 금액',
	`returnValue` varchar(30) NOT NULL DEFAULT '' COMMENT 'API 호출 상태',
	`firstAccumamnt` int unsigned NOT NULL DEFAULT 0 COMMENT '총 1등 당첨금',
	`firstWinamnt` int NOT NULL DEFAULT 0 COMMENT '1등 수령 액',
	`firstPrzwnerCo` tinyint NOT NULL DEFAULT 0 COMMENT '1등 당첨 인원',
	`bnusNo` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '2등 보너스 번호',
	`drwtNo1` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '당첨 번호 1',
	`drwtNo2` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '당첨 번호 2',
	`drwtNo3` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '당첨 번호 3',
	`drwtNo4` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '당첨 번호 4',
	`drwtNo5` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '당첨 번호 5',
	`drwtNo6` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '당첨 번호 6',
	PRIMARY KEY (`drwNo`, `drwNoDate`),
	KEY IDX_DATE (drwNoDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='당첨 정보';
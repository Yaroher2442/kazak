CREATE TABLE `Litigation` (
  `t_id` TEXT NULL DEFAULT NULL,
  `Case_number` TEXT NULL DEFAULT NULL,
  `Tribunal` TEXT NULL DEFAULT NULL,
  `Judge` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`t_id`)
);

CREATE TABLE `Bankruptcy` (
  `t_id` TEXT NULL DEFAULT NULL,
  `Bankruptcy_case_number` TEXT NULL DEFAULT NULL,
  `Arbitration_manager` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`t_id`)
);


CREATE TABLE `Pre_trial_settlement` (
  `t_id` TEXT NULL DEFAULT NULL,
  `Case_number` TEXT NULL DEFAULT NULL,
  `Agency` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`t_id`)
);

    
CREATE TABLE `Enforcement_proceedings` (
  `t_id` TEXT NULL DEFAULT NULL,
  `Executive_case_number` TEXT NULL DEFAULT NULL,
  `Amount` TEXT NULL DEFAULT NULL,
  `FSSP` TEXT NULL DEFAULT NULL,
  `Bailiff` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`t_id`)
);
    
CREATE TABLE `Non_judicial` (
  `t_id` TEXT NULL DEFAULT NULL,
  `Nature_of_work` TEXT NULL DEFAULT NULL,
  `Term` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`t_id`)
);
    
CREATE TABLE `Сourts` (
  `c_id` TEXT NULL  DEFAULT NULL,
  `u_id` TEXT NULL DEFAULT NULL,
  ` initials` TEXT NULL DEFAULT NULL,
  `date` TEXT NULL DEFAULT NULL,
  `time` INTEGER NULL DEFAULT NULL,
  `judge` TEXT NULL DEFAULT NULL,
  `tribunal` TEXT NULL DEFAULT NULL,
  `Instance` TEXT NULL DEFAULT NULL,
  `comment` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`c_id`)
);

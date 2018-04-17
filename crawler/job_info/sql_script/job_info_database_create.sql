drop table zhiye_data.job_data;
drop table zhiye_data.extra_company;
drop table zhiye_data.conside_company;

CREATE TABLE
    zhiye_data.job_data
    (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(50),
        pay VARCHAR(50),
        company_name VARCHAR(50),
        publish_time VARCHAR(50),
        collect_time VARCHAR(50),
        is_apply VARCHAR(50),
        url VARCHAR(100),
        company_type VARCHAR(50),
        exp VARCHAR(50),
        education VARCHAR(50),
        des VARCHAR(5000),
        address VARCHAR(100)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8
    
CREATE TABLE
    zhiye_data.extra_company
    (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(50),
        company_type VARCHAR(50),
        time VARCHAR(50)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
    
CREATE TABLE
    zhiye_data.conside_company
    (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(50),
        company_type VARCHAR(50),
        site VARCHAR(50),
        time VARCHAR(50)
    )
    ENGINE=InnoDB DEFAULT CHARSET=utf8

create view v_new_company as select name, company_type,isconside from conside_company  where isconside is null;
create view v_new_job as select id, name, pay, company_name, publish_time, collect_time, is_apply, url, des from job_data  where ((publish_time != '0' and (is_apply != '1' or is_apply is null)) or (publish_time = '9' and is_apply is null));
create view v_applay_job as select id, name, pay, company_name, publish_time, collect_time, is_apply, url  from job_data  where (is_apply = '1');
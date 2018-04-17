// 新加入公司中将不关注的公司转移至忽略列表中
insert into extra_company(name,company_type,time) select name,company_type,time from conside_company where (isconside = 0 or isconside is null);
// 删除忽略的公司职位信息
delete from conside_company where (isconside = 0 or isconside is null);
// 删除不在关注列表中的公司职位信息
delete from job_data where company_name not in (select distinct name from conside_company);
// 选中职位名称和公司重复的职位信息，并将id放到tempid表中，便于下一步删除job_data
//insert into tempid (id) select id from job_data where (id in (select id from job_data group by name,company_name having COUNT(*) > 1) and (id not in (select min(id) from job_data group by name,company_name having COUNT(*) > 1))); 
// 删除重复职位的id信息
//delete from job_data where id in (select id from tempid);
//delete from tempid;
select * from v_new_job where name like '%测试%' 
        union select * from v_new_job where name like '%Android%' 
        union select * from v_new_job where name like '%IOS%' 
        union select * from v_new_job where name like '%NodeJs%'
        union select * from v_new_job where name like '%前端%' 
        union select * from v_new_job where name like '%算法%'
        union select * from v_new_job where name like '%数据挖掘%'
        union select * from v_new_job where name like '%硬件%';
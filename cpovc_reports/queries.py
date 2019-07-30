QUERIES = {}
# Reports
REPORTS = {}
# Reports listings
REPORTS[1] = 'registration'
REPORTS[2] = 'registration'
REPORTS[3] = 'registration'
REPORTS[4] = 'registration'
REPORTS[5] = 'not_served'
REPORTS[6] = 'pepfar_detailed'
REPORTS[7] = 'registration'
REPORTS[8] = 'registration'
REPORTS[9] = 'registration'
REPORTS[10] = 'registration'
REPORTS[11] = 'form1b_summary'

# Registration List
QUERIES['registration'] = '''
select reg_org_unit.org_unit_name AS CBO,
reg_person.first_name, reg_person.surname,
reg_person.other_names, reg_person.date_of_birth, registration_date,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
date_part('year', age(ovc_registration.registration_date, reg_person.date_of_birth)) AS age_at_reg,
child_cbo_id as OVCID,
list_geo.area_name as ward, scc.area_name as constituency, cc.area_name as county,
CASE
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
CASE has_bcert WHEN 'True' THEN 'HAS BIRTHCERT' ELSE 'NO BIRTHCERT' END AS BirthCert,
CASE has_bcert WHEN 'True' THEN 'BCERT' ELSE NULL END AS BCertNumber,
CASE is_disabled WHEN 'True' THEN 'HAS DISABILITY' ELSE 'NO DISABILITY' END AS OVCDisability,
CASE is_Disabled WHEN 'True' THEN 'NCPWD' ELSE NULL END AS NCPWDNumber,
CASE
WHEN hiv_status = 'HSTP' THEN 'POSITIVE'
WHEN hiv_status = 'HSTN' THEN 'NEGATIVE'
ELSE 'NOT KNOWN' END AS OVCHIVstatus,
CASE hiv_status WHEN 'HSTP' THEN 'ART' ELSE NULL END AS ARTStatus,
concat(chw.first_name,' ',chw.surname,' ',chw.other_names) as CHW,
concat(cgs.first_name,' ',cgs.surname,' ',cgs.other_names) as parent_names,
CASE is_active WHEN 'True' THEN 'ACTIVE' ELSE 'EXITED' END AS Exit_status,
CASE is_active WHEN 'False' THEN exit_date ELSE NULL END AS Exit_date,
CASE
WHEN school_level = 'SLTV' THEN 'Tertiary'
WHEN school_level = 'SLUN' THEN 'University'
WHEN school_level = 'SLSE' THEN 'Secondary'
WHEN school_level = 'SLPR' THEN 'Primary'
WHEN school_level = 'SLEC' THEN 'ECDE'
ELSE 'Not in School' END AS Schoollevel,
CASE immunization_status
WHEN 'IMFI' THEN 'Fully Immunized'
WHEN 'IMNI' THEN 'Not Immunized'
WHEN 'IMNC' THEN 'Not Completed'
ELSE 'Not Known' END AS immunization
from ovc_registration
left outer join reg_person on person_id=reg_person.id
left outer join reg_person chw on child_chv_id=chw.id
left outer join reg_person cgs on caretaker_id=cgs.id
left outer join reg_org_unit on child_cbo_id=reg_org_unit.id
left outer join reg_persons_geo on ovc_registration.person_id=reg_persons_geo.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False and child_cbo_id in ({cbos})
and ovc_registration.registration_date between '{start_date}' and '{end_date}';'''

# PEPFAR
QUERIES['pepfar'] = '''
select
cast(count(distinct ovc_care_events.person_id) as integer) as OVCCount,
reg_org_unit.org_unit_name AS CBO,
list_geo.area_name as ward, scc.area_name as constituency, cc.area_name as county,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
CASE ovc_care_services.service_provided
WHEN 'HC1S' THEN 'Health' {domains}
ELSE 'Unknown'
END AS Domain
from ovc_care_services
INNER JOIN ovc_care_events ON ovc_care_events.event=ovc_care_services.event_id
INNER JOIN reg_person ON ovc_care_events.person_id=reg_person.id
LEFT OUTER JOIN ovc_registration ON ovc_care_events.person_id=ovc_registration.person_id
LEFT OUTER JOIN reg_org_unit ON reg_org_unit.id=ovc_registration.child_cbo_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
LEFT OUTER JOIN list_geo ON list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
WHERE reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_care_services.is_void = False
and ovc_care_events.event_type_id='FSAM'
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
and ovc_registration.child_cbo_id in ({cbos})
GROUP BY ovc_care_services.service_provided, reg_person.date_of_birth,
reg_person.sex_id, ovc_registration.child_cbo_id,
reg_org_unit.org_unit_name, reg_persons_geo.area_id,
ward, constituency, county;'''

# PEPFAR SUMMARY
QUERIES['pepfar_sum'] = '''
'''

# DATIM
QUERIES['datim'] = '''
select
cast(count(distinct ovc_registration.person_id) as integer) as OVCCount,
reg_org_unit.org_unit_name AS CBO,
list_geo.area_name as ward, scc.area_name as constituency, cc.area_name as county,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
CASE ovc_registration.hiv_status
WHEN 'HSTP' THEN '2a. (i) OVC_HIVSTAT: HIV+'
WHEN 'HSTN' THEN '2b. OVC_HIVSTAT: HIV-'
ELSE '2c. OVC_HIVSTAT: HIV Status NOT Known'
END AS Domain,
0 as Wardactive, 0 as WARDGraduated, 0 as WARDTransferred,
0 as WARDExitedWithoutGraduation
from ovc_registration
INNER JOIN reg_person ON ovc_registration.person_id=reg_person.id
LEFT OUTER JOIN reg_org_unit ON reg_org_unit.id=ovc_registration.child_cbo_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
LEFT OUTER JOIN list_geo ON list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
WHERE reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
and ((ovc_registration.is_active = True and ovc_registration.registration_date <= '{end_date}') 
or (ovc_registration.is_active = False 
and (ovc_registration.registration_date between '{start_date}' and '{end_date}' )) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= '{end_date}' 
and ovc_registration.exit_date > '{end_date}' ) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= '{end_date}' 
and ovc_registration.exit_date between '{start_date}' and '{end_date}' )) 
and not (ovc_registration.school_level = 'SLNS'
and date_part('year', '{end_date}'::date) - date_part('year', reg_person.date_of_birth::date) > 17)
GROUP BY ovc_registration.person_id, reg_person.date_of_birth,
reg_person.sex_id, ovc_registration.child_cbo_id,
reg_org_unit.org_unit_name, reg_persons_geo.area_id,
ovc_registration.hiv_status, ward, constituency, county
;'''


# DATIM - Served
QUERIES['datim_1'] = '''
select 
cast(count(distinct ovc_care_events.person_id) as integer) as OVCCount,
reg_org_unit.org_unit_name AS CBO,
list_geo.area_name as ward, scc.area_name as constituency, cc.area_name as county,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
'1. OVC_Serv' as Domain
from ovc_care_services
INNER JOIN ovc_care_events ON ovc_care_events.event=ovc_care_services.event_id
INNER JOIN reg_person ON ovc_care_events.person_id=reg_person.id
LEFT OUTER JOIN ovc_registration ON ovc_care_events.person_id=ovc_registration.person_id
LEFT OUTER JOIN reg_org_unit ON reg_org_unit.id=ovc_registration.child_cbo_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
LEFT OUTER JOIN list_geo ON list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
WHERE  reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_care_services.is_void = False 
and ovc_care_events.event_type_id='FSAM'
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
and ovc_registration.child_cbo_id in ({cbos})
and ((ovc_registration.is_active = True and ovc_registration.registration_date <= '{end_date}') 
or (ovc_registration.is_active = False 
and (ovc_registration.registration_date between '{start_date}' and '{end_date}' )) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= '{end_date}' 
and ovc_registration.exit_date > '{end_date}' ) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= '{end_date}' 
and ovc_registration.exit_date between '{start_date}' and '{end_date}' )) 
and not (ovc_registration.school_level = 'SLNS'
and date_part('year', '{end_date}'::date) - date_part('year', reg_person.date_of_birth::date) > 17)
GROUP BY reg_person.date_of_birth,
reg_person.sex_id, ovc_registration.child_cbo_id,
reg_org_unit.org_unit_name, reg_persons_geo.area_id,
ward, constituency, county;'''

# DATIM ART
QUERIES['datim_2'] = '''
select
cast(count(distinct ovc_registration.person_id) as integer) as OVCCount,
reg_org_unit.org_unit_name AS CBO,
list_geo.area_name as ward, scc.area_name as constituency, cc.area_name as county,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
CASE ovc_care_health.art_status
WHEN 'ARAR' THEN '2a. (ii) OVC_HIVSTAT: HIV+ on ARV Treatment'
WHEN 'ARPR' THEN '2a. (ii) OVC_HIVSTAT: HIV+ on ARV Treatment'
ELSE '2a. (iii) OVC_HIVSTAT: HIV+ NOT on ARV Treatment'
END AS Domain,
0 as Wardactive, 0 as WARDGraduated, 0 as WARDTransferred,
0 as WARDExitedWithoutGraduation
from ovc_registration
INNER JOIN reg_person ON ovc_registration.person_id=reg_person.id
LEFT OUTER JOIN reg_org_unit ON reg_org_unit.id=ovc_registration.child_cbo_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
LEFT OUTER JOIN list_geo ON list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
LEFT OUTER JOIN ovc_care_health ON ovc_care_health.person_id=ovc_registration.person_id
WHERE reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
AND ovc_registration.hiv_status = 'HSTP'
and ovc_registration.child_cbo_id in ({cbos})
and ((ovc_registration.is_active = True and ovc_registration.registration_date <= '{end_date}') 
or (ovc_registration.is_active = False 
and (ovc_registration.registration_date between '{start_date}' and '{end_date}' )) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= '{end_date}' 
and ovc_registration.exit_date > '{end_date}' ) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= '{end_date}' 
and ovc_registration.exit_date between '{start_date}' and '{end_date}' )) 
and not (ovc_registration.school_level = 'SLNS'
and date_part('year', '{end_date}'::date) - date_part('year', reg_person.date_of_birth::date) > 17)
GROUP BY ovc_registration.person_id, reg_person.date_of_birth,
reg_person.sex_id, ovc_registration.child_cbo_id,
reg_org_unit.org_unit_name, reg_persons_geo.area_id, list_geo.parent_area_id,
ovc_registration.hiv_status, ovc_care_health.art_status,
ward, constituency, county;'''

# Datim Ward summary
QUERIES['datim_3'] = '''
SELECT *
FROM crosstab(
  'select cast(ward as text), graduation,
  cast(sum(ccount) as integer) as ovcs from (
select cast(count(*) as integer) as ccount,
list_geo.area_name as ward,
case exit_reason
WHEN ''ERDE'' THEN ''WARDExitedWithoutGraduation''
WHEN ''EROE'' THEN ''WARDGraduated''
WHEN ''ERFI'' THEN ''WARDGraduated''
WHEN ''ERFR'' THEN ''WARDGraduated''
WHEN ''ERFS'' THEN ''WARDGraduated''
WHEN ''ERAD'' THEN ''WARDGraduated''
WHEN ''ERSE'' THEN ''WARDGraduated''
WHEN ''ERIN'' THEN ''WARDExitedWithoutGraduation''
WHEN ''ERRL'' THEN ''WARDTransferred''
WHEN ''ERDU'' THEN ''WARDTransferred''
WHEN ''ERTR'' THEN ''WARDGraduated''
WHEN ''ERLW'' THEN ''WARDExitedWithoutGraduation''
WHEN ''ERMA'' THEN ''WARDExitedWithoutGraduation''
WHEN ''ERTL'' THEN ''WARDTransferred''
WHEN ''ERDO'' THEN ''WARDExitedWithoutGraduation''
else ''WardActive'' END AS Graduation
from ovc_registration
INNER JOIN reg_person ON ovc_registration.person_id=reg_person.id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
LEFT OUTER JOIN list_geo ON list_geo.area_id=reg_persons_geo.area_id
WHERE reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.child_cbo_id in ({cbos})
and ((ovc_registration.is_active = True and ovc_registration.registration_date <= ''{end_date}'' ) 
or (ovc_registration.is_active = False 
and (ovc_registration.registration_date between ''{start_date}'' and ''{end_date}'' )) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= ''{end_date}'' 
and ovc_registration.exit_date > ''{end_date}'' ) 
or (ovc_registration.is_active = False and ovc_registration.registration_date <= ''{end_date}'' 
and ovc_registration.exit_date between ''{start_date}'' and ''{end_date}'' )) 
and not (ovc_registration.school_level = ''SLNS''
and date_part(''year'', ''{end_date}''::date) - date_part(''year'', reg_person.date_of_birth::date) > 17)
group by exit_reason, list_geo.area_name order by ward) as wc
group by ward, graduation
   order by 1,2')
AS ct("ward" text, "WardActive" int, "WARDGraduated" int,
"WARDTransferred" int, "WARDExitedWithoutGraduation" int);;'''

# KPI
QUERIES['kpi'] = '''
select
cast(count(distinct ovc_registration.person_id) as integer) as OVCCount,
ovc_registration.child_cbo_id,
reg_org_unit.org_unit_name,
reg_persons_geo.area_id,
list_geo.area_name,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
CASE ovc_care_health.art_status
WHEN 'ARAR' THEN '2a. (ii) OVC_HIVSTAT: HIV+ on ARV Treatment'
WHEN 'ARPR' THEN '2a. (ii) OVC_HIVSTAT: HIV+ on ARV Treatment'
ELSE '2a. (iii) OVC_HIVSTAT: HIV+ NOT on ARV Treatment'
END AS Domain
from ovc_registration
INNER JOIN reg_person ON ovc_registration.person_id=reg_person.id
LEFT OUTER JOIN reg_org_unit ON reg_org_unit.id=ovc_registration.child_cbo_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
LEFT OUTER JOIN list_geo ON list_geo.area_id=reg_persons_geo.area_id
LEFT OUTER JOIN ovc_care_health ON ovc_care_health.person_id=ovc_registration.person_id
WHERE reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
AND ovc_registration.hiv_status = 'HSTP'
%s
GROUP BY ovc_registration.person_id, reg_person.date_of_birth,
reg_person.sex_id, ovc_registration.child_cbo_id,
reg_org_unit.org_unit_name, reg_persons_geo.area_id,
ovc_registration.hiv_status, list_geo.area_name, ovc_care_health.art_status;'''

QUERIES['served'] = '''
SELECT * FROM (%s) a
INNER JOIN (%s) b
ON a.ward = b.ward;'''

# NOT SERVED LIST
QUERIES['not_served_list'] = '''
select person_id from(
select person_id, count(person_id) as scnts
from(
select person_id, domain, count(distinct(domain)) as domaincount from (
select ovc_registration.person_id, event_type_id, domain from ovc_care_assessment
inner join ovc_care_events on ovc_care_assessment.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id = ovc_registration.person_id
where ovc_registration.child_cbo_id in ({cbos})
and domain in ('DHNU', 'DPSS')
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
union all
select ovc_registration.person_id, event_type_id,
CASE
  WHEN (service_provided = 'SC1S' or service_provided = 'SC2S' or service_provided = 'SC3S'
     or service_provided = 'SC4S' or service_provided = 'SC5S' or service_provided = 'SC6S'
     or service_provided = 'SC7S') THEN 'DSHC'
  WHEN (service_provided = 'PS1S' or service_provided = 'PS2S' or service_provided = 'PS3S'
     or service_provided = 'PS4S' or service_provided = 'PS5S') THEN 'DPSS'
  WHEN (service_provided = 'PT1S' or service_provided = 'PT2S' or service_provided = 'PT3S'
     or service_provided = 'PT4S' or service_provided = 'PT5S') THEN 'DPRO'
  WHEN (service_provided = 'HE1S' or service_provided = 'HE2S' or service_provided = 'HE3S'
     or service_provided = 'HE4S') THEN 'DHES'
  WHEN (service_provided = 'HC1S' or service_provided = 'HC2S' or service_provided = 'HC3S'
     or service_provided = 'HC4S' or service_provided = 'HC5S' or service_provided = 'HC6S'
     or service_provided = 'HC7S' or service_provided = 'HC8S' or service_provided = 'HC9S'
     or service_provided = 'HC10S') THEN 'DHNU'
  WHEN (service_provided = 'SE1S' or service_provided = 'SE2S' or service_provided = 'SE3S'
     or service_provided = 'SE4S' or service_provided = 'SE5S' or service_provided = 'SE6S'
     or service_provided = 'SE7S' or service_provided = 'SE8S') THEN 'DEDU'
  ELSE 'NULL'
 END AS domain
from ovc_care_services
inner join ovc_care_events on ovc_care_services.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id = ovc_registration.person_id
where ovc_registration.child_cbo_id in ({cbos})
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}') as dcs
group by person_id, domain) as scounts
group by person_id) as fp where scnts > 0'''

# NOT Served
QUERIES['not_served'] = '''
select reg_org_unit.org_unit_name AS CBO,
reg_person.first_name, reg_person.surname,
reg_person.other_names, reg_person.date_of_birth, registration_date,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
date_part('year', age(ovc_registration.registration_date,
reg_person.date_of_birth)) AS age_at_reg,
child_cbo_id as OVCID,
list_geo.area_name as ward, scc.area_name as constituency, cc.area_name as county,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', 
age(reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
CASE has_bcert WHEN 'True' THEN 'HAS BIRTHCERT' ELSE 'NO BIRTHCERT' END AS BirthCert,
CASE has_bcert WHEN 'True' THEN 'BCERT' ELSE NULL END AS BCertNumber,
CASE is_disabled WHEN 'True' THEN 'HAS DISABILITY' ELSE 'NO DISABILITY' END AS OVCDisability,
CASE is_Disabled WHEN 'True' THEN 'NCPWD' ELSE NULL END AS NCPWDNumber,
CASE
WHEN hiv_status = 'HSTP' THEN 'POSITIVE'
WHEN hiv_status = 'HSTN' THEN 'NEGATIVE'
ELSE 'NOT KNOWN' END AS OVCHIVstatus,
CASE hiv_status WHEN 'HSTP' THEN 'ART' ELSE NULL END AS ARTStatus,
concat(chw.first_name,' ',chw.surname,' ',chw.other_names) as CHW,
concat(cgs.first_name,' ',cgs.surname,' ',cgs.other_names) as parent_names,
CASE is_active WHEN 'True' THEN 'ACTIVE' ELSE 'EXITED' END AS Exit_status,
CASE is_active WHEN 'False' THEN exit_date ELSE NULL END AS Exit_date,
CASE
WHEN school_level = 'SLTV' THEN 'Tertiary'
WHEN school_level = 'SLUN' THEN 'University'
WHEN school_level = 'SLSE' THEN 'Secondary'
WHEN school_level = 'SLPR' THEN 'Primary'
WHEN school_level = 'SLEC' THEN 'ECDE'
ELSE 'Not in School' END AS Schoollevel,
CASE immunization_status
WHEN 'IMFI' THEN 'Fully Immunized'
WHEN 'IMNI' THEN 'Not Immunized'
WHEN 'IMNC' THEN 'Not Completed'
ELSE 'Not Known' END AS immunization
from ovc_registration
left outer join reg_person on person_id=reg_person.id
left outer join reg_person chw on child_chv_id=chw.id
left outer join reg_person cgs on caretaker_id=cgs.id
left outer join reg_org_unit on child_cbo_id=reg_org_unit.id
left outer join reg_persons_geo on ovc_registration.person_id=reg_persons_geo.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and child_cbo_id in ({cbos})
and ovc_registration.registration_date between '{start_date}' and '{end_date}'
and ovc_registration.person_id not in (%s);''' % (QUERIES['not_served_list'])


# PEPFAR DETAILED SUMMARY
QUERIES['pepfar_detailed'] = '''
select * FROM (
select cast('CBO' as text) as level,
CASE
WHEN scnts = 0 THEN 'Not Served' 
WHEN scnts = 1 THEN '1 or 2 Services' 
WHEN scnts = 2 THEN '1 or 2 Services' 
WHEN scnts > 2 THEN '3 or More Services' END AS Services,
Gender, age, AgeRange, CBO as name, count(scnts) AS OVCCOUNT from(
select person_id, count(person_id) as scnts, Gender, age, AgeRange, CBO
from(
select person_id, domain, Gender, age, AgeRange, CBO, count(distinct(domain)) as domaincount from (
select ovc_registration.person_id, event_type_id, domain,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
reg_org_unit.org_unit_name AS CBO
 from ovc_care_assessment
inner join ovc_care_events on ovc_care_assessment.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id=ovc_registration.person_id
inner join reg_person on reg_person.id = ovc_registration.person_id
left outer join reg_org_unit on ovc_registration.child_cbo_id=reg_org_unit.id
where domain in ('DHNU', 'DPSS')
and ovc_registration.child_cbo_id in ({cbos})
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
union all
select ovc_registration.person_id, event_type_id,
CASE
  WHEN (service_provided = 'SC1S' or service_provided = 'SC2S' or service_provided = 'SC3S'
    or service_provided = 'SC4S' or service_provided = 'SC5S' or service_provided = 'SC6S'
    or service_provided = 'SC7S') THEN 'DSHC'
  WHEN (service_provided = 'PS1S' or service_provided = 'PS2S' or service_provided = 'PS3S'
    or service_provided = 'PS4S' or service_provided = 'PS5S') THEN 'DPSS'
  WHEN (service_provided = 'PT1S' or service_provided = 'PT2S' or service_provided = 'PT3S'
    or service_provided = 'PT4S' or service_provided = 'PT5S') THEN 'DPRO'
  WHEN (service_provided = 'HE1S' or service_provided = 'HE2S' or service_provided = 'HE3S'
    or service_provided = 'HE4S') THEN 'DHES'
  WHEN (service_provided = 'HC1S' or service_provided = 'HC2S' or service_provided = 'HC3S'
    or service_provided = 'HC4S' or service_provided = 'HC5S' or service_provided = 'HC6S'
    or service_provided = 'HC7S' or service_provided = 'HC8S' or service_provided = 'HC9S'
    or service_provided = 'HC10S') THEN 'DHNU'
  WHEN (service_provided = 'SE1S' or service_provided = 'SE2S' or service_provided = 'SE3S'
    or service_provided = 'SE4S' or service_provided = 'SE5S' or service_provided = 'SE6S'
    or service_provided = 'SE7S' or service_provided = 'SE8S') THEN 'DEDU'
  ELSE 'NULL'
 END AS domain,
 CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
 date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
 CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
reg_org_unit.org_unit_name AS CBO
from ovc_care_services
inner join ovc_care_events on ovc_care_services.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id=ovc_registration.person_id
inner join reg_person on reg_person.id = ovc_registration.person_id
left outer join reg_org_unit on ovc_registration.child_cbo_id=reg_org_unit.id
where  ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
and ovc_registration.child_cbo_id in ({cbos})) as dcs
group by person_id, domain, Gender, age, AgeRange, CBO) as scounts
group by person_id, Gender, age, AgeRange, CBO
union all
select ovc_registration.person_id, 0 as scnts,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
 date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
 CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
reg_org_unit.org_unit_name AS CBO
 from ovc_registration
 inner join reg_person on reg_person.id = ovc_registration.person_id
 left outer join reg_org_unit on ovc_registration.child_cbo_id=reg_org_unit.id
 where ovc_registration.child_cbo_id in ({cbos})
 ) as fp group by Gender, age, AgeRange, scnts, cbo) a
INNER JOIN (
select count(ovc_registration.person_id) as active,
reg_org_unit.org_unit_name as name
from ovc_registration
inner join reg_org_unit on reg_org_unit.id = ovc_registration.child_cbo_id
where ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
group by ovc_registration.child_cbo_id, name) b
ON a.name = b.name;'''

# Blanks to fill up all services, ages, genders
QUERIES['pepfar_detailed_blank'] = '''
select * FROM (
select cast('CBO' as text) as level,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) < 15 THEN cast('1 or 2 Services' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) BETWEEN 15 AND 28 THEN cast('3 or More Services' as text)
ELSE cast('Not Served' as text) END AS Services,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (
1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41) THEN cast('Female' as text)
ELSE cast('Male' as text) END AS Gender,
0 as age,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (1,2,15,16,29,30) THEN cast('a.[<1yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (3,4,16,17,31,32) THEN cast('b.[1-4yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (5,6,18,19,33,34) THEN cast('c.[5-9yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (7,8,20,21,35,36) THEN cast('d.[10-14yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (9,10,22,23,37,38) THEN cast('e.[15-17yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (11,12,24,25,39,40) THEN cast('f.[18-24yrs]' as text)
ELSE cast('g.[25+yrs]' as text) END AS AgeRange,
reg_org_unit.org_unit_name AS name,
0 as OVCCOUNT from ovc_registration
left outer join reg_org_unit on ovc_registration.child_cbo_id=reg_org_unit.id
where ovc_registration.child_cbo_id in ({cbos}) limit 42) a
INNER JOIN (
select count(ovc_registration.person_id) as active,
reg_org_unit.org_unit_name as name
from ovc_registration
inner join reg_org_unit on reg_org_unit.id = ovc_registration.child_cbo_id
where ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
group by ovc_registration.child_cbo_id, name) b
ON a.name = b.name;'''

# For constituency
QUERIES['pepfar_detailed_1'] = '''
select * FROM (
select cast('Constituency' as text) as level,
CASE
WHEN scnts = 0 THEN 'Not Served' 
WHEN scnts = 1 THEN '1 or 2 Services' 
WHEN scnts = 2 THEN '1 or 2 Services' 
WHEN scnts > 2 THEN '3 or More Services' END AS Services,
Gender, age, AgeRange, scounty as name, count(scnts) AS OVCCOUNT from(
select person_id, count(person_id) as scnts, Gender, age, AgeRange, scounty
from(
select person_id, domain, Gender, age, AgeRange, scounty, count(distinct(domain)) as domaincount from (
select ovc_registration.person_id, event_type_id, domain,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
scc.area_name AS scounty
 from ovc_care_assessment
inner join ovc_care_events on ovc_care_assessment.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id=ovc_registration.person_id
inner join reg_person on reg_person.id = ovc_registration.person_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and domain in ('DHNU', 'DPSS')
and ovc_registration.child_cbo_id in ({cbos})
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
union all
select ovc_registration.person_id, event_type_id,
CASE
  WHEN (service_provided = 'SC1S' or service_provided = 'SC2S' or service_provided = 'SC3S'
    or service_provided = 'SC4S' or service_provided = 'SC5S' or service_provided = 'SC6S'
    or service_provided = 'SC7S') THEN 'DSHC'
  WHEN (service_provided = 'PS1S' or service_provided = 'PS2S' or service_provided = 'PS3S'
    or service_provided = 'PS4S' or service_provided = 'PS5S') THEN 'DPSS'
  WHEN (service_provided = 'PT1S' or service_provided = 'PT2S' or service_provided = 'PT3S'
    or service_provided = 'PT4S' or service_provided = 'PT5S') THEN 'DPRO'
  WHEN (service_provided = 'HE1S' or service_provided = 'HE2S' or service_provided = 'HE3S'
    or service_provided = 'HE4S') THEN 'DHES'
  WHEN (service_provided = 'HC1S' or service_provided = 'HC2S' or service_provided = 'HC3S'
    or service_provided = 'HC4S' or service_provided = 'HC5S' or service_provided = 'HC6S'
    or service_provided = 'HC7S' or service_provided = 'HC8S' or service_provided = 'HC9S'
    or service_provided = 'HC10S') THEN 'DHNU'
  WHEN (service_provided = 'SE1S' or service_provided = 'SE2S' or service_provided = 'SE3S'
    or service_provided = 'SE4S' or service_provided = 'SE5S' or service_provided = 'SE6S'
    or service_provided = 'SE7S' or service_provided = 'SE8S') THEN 'DEDU'
  ELSE 'NULL'
 END AS domain,
 CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
 date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
 CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
scc.area_name AS scounty
from ovc_care_services
inner join ovc_care_events on ovc_care_services.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id=ovc_registration.person_id
inner join reg_person on reg_person.id = ovc_registration.person_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
and ovc_registration.child_cbo_id in ({cbos})) as dcs
group by person_id, domain, Gender, age, AgeRange, scounty) as scounts
group by person_id, Gender, age, AgeRange, scounty
union all
select ovc_registration.person_id, 0 as scnts,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
 date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
 CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
scc.area_name AS scounty
 from ovc_registration
 inner join reg_person on reg_person.id = ovc_registration.person_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.child_cbo_id in ({cbos})
 ) as fp group by Gender, age, AgeRange, scnts, scounty) a
INNER JOIN (
select count(ovc_registration.person_id) as active,
scc.area_name as name
from ovc_registration
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
group by name) b
ON a.name = b.name;'''

# For consituency blanks
QUERIES['pepfar_detailed_blank_1'] = '''
select * FROM (
select cast('Constituency' as text) as level,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) < 15 THEN cast('1 or 2 Services' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) BETWEEN 15 AND 28 THEN cast('3 or More Services' as text)
ELSE cast('Not Served' as text) END AS Services,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (
1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41) THEN cast('Female' as text)
ELSE cast('Male' as text) END AS Gender,
0 as age,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (1,2,15,16,29,30) THEN cast('a.[<1yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (3,4,16,17,31,32) THEN cast('b.[1-4yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (5,6,18,19,33,34) THEN cast('c.[5-9yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (7,8,20,21,35,36) THEN cast('d.[10-14yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (9,10,22,23,37,38) THEN cast('e.[15-17yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (11,12,24,25,39,40) THEN cast('f.[18-24yrs]' as text)
ELSE cast('g.[25+yrs]' as text) END AS AgeRange,
scc.area_name AS name,
0 as OVCCOUNT from ovc_registration
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.child_cbo_id in ({cbos}) limit 42) a
INNER JOIN (
select count(ovc_registration.person_id) as active,
scc.area_name as name
from ovc_registration
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
group by name) b
ON a.name = b.name;'''

# For County
QUERIES['pepfar_detailed_2'] = '''
select * FROM (
select cast('County' as text) as level,
CASE
WHEN scnts = 0 THEN 'Not Served' 
WHEN scnts = 1 THEN '1 or 2 Services' 
WHEN scnts = 2 THEN '1 or 2 Services' 
WHEN scnts > 2 THEN '3 or More Services' END AS Services,
Gender, age, AgeRange, scounty as name, count(scnts) AS OVCCOUNT from(
select person_id, count(person_id) as scnts, Gender, age, AgeRange, scounty
from(
select person_id, domain, Gender, age, AgeRange, scounty, count(distinct(domain)) as domaincount from (
select ovc_registration.person_id, event_type_id, domain,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
cc.area_name AS scounty
 from ovc_care_assessment
inner join ovc_care_events on ovc_care_assessment.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id=ovc_registration.person_id
inner join reg_person on reg_person.id = ovc_registration.person_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and domain in ('DHNU', 'DPSS')
and ovc_registration.child_cbo_id in ({cbos})
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
union all
select ovc_registration.person_id, event_type_id,
CASE
  WHEN (service_provided = 'SC1S' or service_provided = 'SC2S' or service_provided = 'SC3S'
    or service_provided = 'SC4S' or service_provided = 'SC5S' or service_provided = 'SC6S'
    or service_provided = 'SC7S') THEN 'DSHC'
  WHEN (service_provided = 'PS1S' or service_provided = 'PS2S' or service_provided = 'PS3S'
    or service_provided = 'PS4S' or service_provided = 'PS5S') THEN 'DPSS'
  WHEN (service_provided = 'PT1S' or service_provided = 'PT2S' or service_provided = 'PT3S'
    or service_provided = 'PT4S' or service_provided = 'PT5S') THEN 'DPRO'
  WHEN (service_provided = 'HE1S' or service_provided = 'HE2S' or service_provided = 'HE3S'
    or service_provided = 'HE4S') THEN 'DHES'
  WHEN (service_provided = 'HC1S' or service_provided = 'HC2S' or service_provided = 'HC3S'
    or service_provided = 'HC4S' or service_provided = 'HC5S' or service_provided = 'HC6S'
    or service_provided = 'HC7S' or service_provided = 'HC8S' or service_provided = 'HC9S'
    or service_provided = 'HC10S') THEN 'DHNU'
  WHEN (service_provided = 'SE1S' or service_provided = 'SE2S' or service_provided = 'SE3S'
    or service_provided = 'SE4S' or service_provided = 'SE5S' or service_provided = 'SE6S'
    or service_provided = 'SE7S' or service_provided = 'SE8S') THEN 'DEDU'
  ELSE 'NULL'
 END AS domain,
 CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
 date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
 CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
cc.area_name AS scounty
from ovc_care_services
inner join ovc_care_events on ovc_care_services.event_id=ovc_care_events.event
inner join ovc_registration on ovc_care_events.person_id=ovc_registration.person_id
inner join reg_person on reg_person.id = ovc_registration.person_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_care_events.date_of_event between '{start_date}' and '{end_date}'
and ovc_registration.child_cbo_id in ({cbos})) as dcs
group by person_id, domain, Gender, age, AgeRange, scounty) as scounts
group by person_id, Gender, age, AgeRange, scounty
union all
select ovc_registration.person_id, 0 as scnts,
CASE reg_person.sex_id WHEN 'SFEM' THEN 'Female' ELSE 'Male' END AS Gender,
 date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) AS age,
 CASE
WHEN date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) < 1 THEN 'a.[<1yrs]'
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 1 AND 4 THEN 'b.[1-4yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 5 AND 9 THEN 'c.[5-9yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 10 AND 14 THEN 'd.[10-14yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 15 AND 17 THEN 'e.[15-17yrs]' 
WHEN  date_part('year', age(timestamp '{end_date}', reg_person.date_of_birth)) BETWEEN 18 AND 24 THEN 'f.[18-24yrs]'
ELSE 'g.[25+yrs]' END AS AgeRange,
cc.area_name AS scounty
 from ovc_registration
 inner join reg_person on reg_person.id = ovc_registration.person_id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.child_cbo_id in ({cbos})
 ) as fp group by Gender, age, AgeRange, scnts, scounty) a
INNER JOIN (
select count(ovc_registration.person_id) as active,
cc.area_name as name
from ovc_registration
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
group by name) b
ON a.name = b.name;'''

# For county blank
QUERIES['pepfar_detailed_blank_2'] = '''
select * FROM (
select cast('County' as text) as level,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) < 15 THEN cast('1 or 2 Services' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) BETWEEN 15 AND 28 THEN cast('3 or More Services' as text)
ELSE cast('Not Served' as text) END AS Services,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (
1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41) THEN cast('Female' as text)
ELSE cast('Male' as text) END AS Gender,
0 as age,
CASE
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (1,2,15,16,29,30) THEN cast('a.[<1yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (3,4,16,17,31,32) THEN cast('b.[1-4yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (5,6,18,19,33,34) THEN cast('c.[5-9yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (7,8,20,21,35,36) THEN cast('d.[10-14yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (9,10,22,23,37,38) THEN cast('e.[15-17yrs]' as text)
WHEN ROW_NUMBER () OVER (ORDER BY ovc_registration ASC) IN (11,12,24,25,39,40) THEN cast('f.[18-24yrs]' as text)
ELSE cast('g.[25+yrs]' as text) END AS AgeRange,
cc.area_name AS name,
0 as OVCCOUNT from ovc_registration
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.child_cbo_id in ({cbos}) limit 42) a
INNER JOIN (
select count(ovc_registration.person_id) as active,
cc.area_name as name
from ovc_registration
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
and ovc_registration.child_cbo_id in ({cbos})
group by name) b
ON a.name = b.name;'''

#  Constituency active
'''
select count(ovc_registration.person_id),
list_geo.area_name as ward,
list_geo.parent_area_id as sc, scc.area_name as sc_name,
scc.parent_area_id as cid, cc.area_name as county
from ovc_registration
left outer join reg_org_unit on child_cbo_id=reg_org_unit.id
left outer join reg_person on person_id=reg_person.id
LEFT OUTER JOIN reg_persons_geo ON reg_persons_geo.person_id=ovc_registration.person_id
left outer join list_geo on list_geo.area_id=reg_persons_geo.area_id
left outer join list_geo as scc on scc.area_id=list_geo.parent_area_id
left outer join list_geo as cc on cc.area_id=scc.parent_area_id
where reg_persons_geo.area_id > 337 and reg_persons_geo.is_void = False
and ovc_registration.is_active = True
group by ovc_registration.child_cbo_id, ward, sc, sc_name, cid, county
'''
QUERIES['form1b_summary'] = '''
'''

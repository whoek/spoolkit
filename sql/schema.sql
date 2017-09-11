
/*
Spoolkit tables  (7)

- spoolkit_configuration
- spoolkit_reportgroups
- spoolkit_reports
- spoolkit_users
- spoolkit_auth_user_permissioins
- spoolkit_sapfiles
- spoolkit_connections

*/

drop table if exists spoolkit_configuration;
create table spoolkit_configuration(
  id integer primary key autoincrement,
  key text,
  value text
);

drop table if exists spoolkit_reportgroups;
create table  spoolkit_reportgroups(
  id integer primary key autoincrement,
  name  text
);
  
drop table if exists spoolkit_reports;
create table spoolkit_reports(
  id integer primary key autoincrement,
  active boolean,
  name  text ,
  shortcode text,
  report_group text,
  connection text,
  pre_script text,
  body_script text,
  post_script text  
);

drop table if exists spoolkit_users;
create table spoolkit_users(
  id integer primary key autoincrement,
  password character varying(128) NOT NULL,
  last_login timestamp with time zone,
  is_superuser boolean NOT NULL,
  username character varying(30) NOT NULL,
  first_name character varying(30) NOT NULL,
  last_name character varying(30) NOT NULL,
  email character varying(75) NOT NULL,
  is_staff boolean NOT NULL,
  is_active boolean NOT NULL,
  date_joined timestamp with time zone NOT NULL
  );

drop table if exists spoolkit_auth_user_permissioins;
create table spoolkit_auth_user_permissioins(
  id integer primary key autoincrement,
  user_id integer,
  group_id integer
);

drop table if exists spoolkit_sapfiles;
create table spoolkit_sapfiles(
  id integer primary key autoincrement,
  keyword text not NULL,
  header_field text NOT NULL,
  table_name text NOT NULL,
  pre_script text NOT NULL,
  post_script text NOT NULL
);

drop table if exists spoolkit_connections;
create table spoolkit_connections(
  id integer primary key autoincrement,
  active boolean
  conn_name text,
  conn_type text,
  connstring text
);



--  Sample TEST Data
--  Sample TEST Data

insert into spoolkit_reports 
(name, body_script)
values ('Show date','select date()');

insert into spoolkit_reports 
(name, body_script)
values ('Show list of reports','select * from spoolkit_reports');

insert into spoolkit_reports 
(name, body_script)
values ('List of sap_files','select * from spoolkit_sapfiles');


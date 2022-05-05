-- UNCOMMENT FOLLOWING IF YOU WANT TO CLEAN THE CLUSTER
-- Clean up databases we want to create
--DROP DATABASE IF EXISTS "submissions";
--DROP DATABASE IF EXISTS "tests";

-- Clean up roles/users we want to create
--DROP ROLE IF EXISTS "submissions-user";
--DROP ROLE IF EXISTS "tests-user";


CREATE DATABASE "submissions";
REVOKE ALL ON DATABASE "submissions" FROM public;
CREATE ROLE "submissions-user" WITH LOGIN PASSWORD 'md5b8861f3484af6394a50eadf3e5be9db3';
GRANT ALL PRIVILEGES ON DATABASE "submissions" TO "submissions-user"; 


CREATE DATABASE "tests";
REVOKE ALL ON DATABASE "tests" FROM public;
CREATE ROLE "tests-user" WITH LOGIN PASSWORD 'md5a26ccd1061627f0efd9ad7116929071e';
GRANT ALL PRIVILEGES ON DATABASE "tests" TO "tests-user";


-- Backup
-- In postgres 14 we may want to create separate backup user 
-- CREATE ROLE backup WITH ROLE pg_read_all_data LOGIN PASSWORD '<password>';
-- other than that we are probably fine with superuser
-- https://www.postgresql.org/message-id/18014.1075821674%40sss.pgh.pa.us
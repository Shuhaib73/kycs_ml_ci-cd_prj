-- Switch to the local database named 'kycs_db'
create database kycs_db;

use kycs_db;

-- Show all tables in the current database
show tables;

-- Create a table named 'users' with the following columns:
create table users(id int primary key auto_increment, 
					name varchar(50) not null, 
                    email varchar(50) not null unique, 
                    password varchar(300) not null,
                    details timestamp default now());

-- Create a table named 'company_details' with the following columns:
create table company_details(email varchar(50),
							category varchar(50),
                            country varchar(50),
                            founded_year int,
                            active_years int,
                            first_funding_year int,
                            first_milestone_year int,
                            funding_rounds int,
                            milestone int,
                            relationship int,
                            funding_total_usd int,
                            latitude float,
                            longitude float,
                            details timestamp default now());

-- Describe the structure of the 'users' table and 'company_details' table
describe users;
describe company_details;

-- display all records from the 'users' table
select * 
from users;


-- display all records from the 'company_details' table
select *
from company_details;

-- Remove all records from the 'users' and 'company_details' table without deleting the table itself
truncate table users;
truncate table company_details;


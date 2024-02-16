CREATE USER 'replicator'@'%' IDENTIFIED BY 'replicationpassword';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;
create database bytewax;
use bytewax;
CREATE TABLE trips (
    TRIPID INT PRIMARY KEY,
    DRIVERID INT,
    TIMECOMPLETED TIMESTAMP,
);
# WriteRows 

This script writes row-level rtf data to a .rtf file named by the id in the database. 
Currently, the connection string is hardcoded to use the SQL Server driver and Windows auth.

Parameters
------
- Server

  The name or ip of the source server.

- Database

  The name of the db containing the rtf table.

- Table 

  A table containing row-level rtf data. Specify the schema and table.

- Output Directory

  The destination directory for writing out rtf files.

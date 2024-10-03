# petroineos-challenge
data pipeline challenge for petroineos London

# STRUCTURE
The structure tree is as follows:


![image](https://github.com/user-attachments/assets/2030a366-ce6d-4482-a5a5-c5e6363510b9)


a. The petroineos folder is build as a pip module and can be downloaded as "pip install .' locally

b. The submodules contains the petroineos source files which contains a petroineos_data_driver file which acts as an Entry point to the petroineos_data_module

c. The petroineos_data_module contains functions to check for file updates, downloading the excel file from webURL and transforming the excel file to a dataframe using pandas

d. The tests module contains the petroineos_data_tests.py file which contains basic checks for column list, threshold rows and null checks

e. The logging is done via logging module and a basic configuration is available in petroineos_data_module.py file


# USAGE:
< python ./petroineos_data_driver "your-directory-name" >

ASSUMPTIONS:
1. Only working for Quarter work sheet.
2. Transformation code is not asynchronos as it is only dealing with small file
3. After checking the excel file, the tranpose needs to be performed to return quarters to datetime objects
   

P.S. - The network check didn't happen correctly due to less time but are present in the file although not very sure on their run schedule. Did with help from online resources.


AS discussed:
Consider the following aspects

a.	Read Patterns: Describe the typical read queries you expect (e.g., time-range queries, filtering by specific columns) and how your design optimizes for these patterns.

   **Using a compressed columnar file format will help achieve filtering time optimzations.
   I would prefer using parquet as storage required is very less but read and write performances are efficient.
   For time range queries, partitioning is a good approach and in above scenario, quarter data can be stored based on yearly or quarterly partitions and this way data fetching will memory related issues.
   Additionally, by using date columns as partitions, it can be used for indexing which are optimized for performance. Chunking can also be used for large sized files**

b.	Write Patterns: Explain how frequently new data will be written to the table and any strategies to handle high write throughput (e.g., batch writes, upserts).

   **Data ingestion and clean should happen in batch write to avoid individual write operations. benefits in efficiency and fast writes. Data integrity will be maintained if data is upserted rather than inserted every    time. Write efficiency can also be achieved by making less indexes and doing time based columns as index**


c.	Concurrency: Discuss how you would handle concurrent reads and writes, ensuring data consistency and performance.

   **Since this is a single file load, it is done via single process, but in reality it should be done asynchronosly using either threading wherein multiple href can be downloaded and network validated thereby increasing throughput or using asyncIO for input/output operations. Thread Locking can be used while handling files to avoid errors. IF later the script needs to be updated to include DB read/writes, CRUD ACID transactions safety protocols should be impletemented.**

d.	Deduplication and Upserts: Explain your approach to managing deduplication and upserts.

   **Dedup can be achieved by using PK/unique constraints or to use a hash value after every load which can be checked against new data during inserts. Upserts can be handled with MERGING in SQL based systems and with    dataframes**


# Python Data Profiler

This script can be run against any text file *with a header*. It will produce an excel file with stastics for each column and a topN distribution for each column.


python data_profiler.py "file location" "excel/text" "save location" topN "delimiter"

 >> python data_profiler.py "/home/data/file.txt" "text" "home/documents/eval_distro/" 50 "|"

The input parameters are: 
1. File location - this should be the full path and file name you want to evaluate.
2. Is it an excel or a text file?
3. Save location - the path to where the output should be saved. this should not include the output file name, that is created automatically as the original file name with a suffix of _eval_dist.xlsx
4. How many entries would you like included in the column distributions
5. Whats the delimiter -- this is unnecessary for excel files and defaults to comma delimited for text files. 

The output statistics include:
1. data type -- this currently is only numeric or string
2. how many distinct values are found in the column
3. the min and max length of the values in the column
4. number of non-null entries
5. total rows
6. percent of nulls
7. min and max values within the column
8. numeric columns also have mean and sum

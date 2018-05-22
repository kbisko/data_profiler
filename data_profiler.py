
# coding: utf-8
import sys
import pandas as pd
import numpy as np
import xlrd
import re

def main():
    file = sys.argv[1]  #full file location and name
    file_type = sys.argv[2].lower()  #excel or text
    save_loc = sys.argv[3] #file location
    top_number = int(sys.argv[4]) #how many do you want to see in the distributions
    if len(sys.argv)<6:
        delimiter = ','
    else:
        delimiter = sys.argv[5] # whats the delimiter of the file 
    eval_and_dist(file, file_type, save_loc, top_number, delimiter)
    print 'File has been saved in '+ save_loc


## Runs the evaluation and distribution with the input file and saves the output as an excel file.
def eval_and_dist(input_file, file_type, save_location, top_n, delimiter):
    ## currently accepts 2 file types excel or csv. if csv it must have a header
    if file_type == 'excel':
        df = pd.read_excel(input_file)
    else :
        df = pd.read_csv(input_file, sep=delimiter)
    #removes the file extension from the file name to use as the saved file name    
    file_name = re.findall(r'[^/]+$', input_file)[0].split('.')[0] 
    #creates the excel file to store everything in
    writer = pd.ExcelWriter(save_location+file_name+'_eval_dist.xlsx')
    evaluations(df, writer)
    distributions(df, top_n, writer)
    writer.save()

## Runs evaluations on each column of the file
def evaluations(df, excel_writer):
    results = []
    cols = df.columns
    # loops through each column and calculates the values
    for i in cols:
        minu = df[i].min()
        maxu =df[i].max()
        dist = df[i].value_counts().count()
        non_nulls = df[i].count()
        tots = len(df[i])
        perc_null = round(float(tots-non_nulls)/tots,2)
        # string fields do not need mean or sum calculated so the columns are split by datatype
        if df[i].dtype.kind in 'biufc' :
            avg = round(df[i].mean(),2)
            sumu = round(df[i].sum(),2)
            results.append([i, 'numeric', avg, minu, maxu, sumu, dist, non_nulls, tots, perc_null])
        else:
            results.append([i, 'string', '', minu, maxu, '', dist, non_nulls, tots, perc_null])
    #present the results in a tabular form for saving
    df_final = pd.DataFrame(results, columns=['column','data_type','mean','min','max','sum','distinct_values','non_nulls','total', 'perc_null']).applymap(str)      
    df_final.to_excel(excel_writer,'eval')


## Runs distributions of the top X values of each column of the file    
def distributions(df, returned_number, excel_writer):
    cols = df.columns
    for i in cols:
        #groups the column by all the values and returns the top n largest
        df2 = df[i].value_counts().nlargest(returned_number)
        #turn it into tabular form, rename and rearrange the columns
        df3 = pd.DataFrame(df2).reset_index().rename(columns={'index':'value', i:'count'})
        df3['column']=i
        cols = df3.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        #all values are returned as string so as not to lose any data
        df4 = df3[cols].applymap(str)
        df4.to_excel(excel_writer, i[:29]) #excel tabs max size is 30 so truncate field names

main()

#call the main function
#python data_profiler.py "/Users/kristenbiskobin/Documents/Oncology 2017.xlsx" "excel" "/Users/kristenbiskobin/Documents/" 20
#python data_profiler.py "/Users/kristenbiskobin/Documents/Oncology 2017.txt" "text" "/Users/kristenbiskobin/Documents/" 20 "|"
#python data_profiler.py "/Users/kristenbiskobin/Documents/Oncology 2017.csv" "text" "/Users/kristenbiskobin/Documents/" 20


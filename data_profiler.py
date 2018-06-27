# coding: utf-8
import sys
import pandas as pd
import numpy as np
import xlrd
import re
import xlsxwriter
import csv

def main():
    file = sys.argv[1]  #full file location and name
    save_loc = sys.argv[2] #file location
    top_number = int(sys.argv[3]) #how many do you want to see in the distributions
    file_type = re.findall(r'[^/]+$', file)[0].split('.')[1].lower()  #excel or text    
     
     # whats the delimiter of the file 
    if file_type == 'xlsx':
        delimiter = None
    else:
        sniffer = csv.Sniffer()
        line = open(file).readline()
        delimiter = sniffer.sniff(line).delimiter

    eval_and_dist(file, file_type, save_loc, top_number, delimiter)
    print ('Output has been saved in '+ save_loc)


## Runs the evaluation and distribution with the input file and saves the output as an excel file.
def eval_and_dist(input_file, file_type, save_location, top_n, delimiter):
    ## currently accepts 2 file types excel or csv. if csv it must have a header
    if file_type == 'xlsx':
        df = pd.read_excel(input_file, low_memory=False).applymap(lambda x: x.strip() if type(x) is str else x)
    else :
        df = pd.read_csv(input_file, sep=delimiter, low_memory=False).applymap(lambda x: x.strip() if type(x) is str else x)
    #removes the file extension from the file name to use as the saved file name    
    file_name = re.findall(r'[^/]+$', input_file)[0].split('.')[0] 
    #creates the excel file to store everything in
    writer = pd.ExcelWriter(save_location+file_name+'_eval_dist.xlsx', engine='xlsxwriter')
    print ('File Loaded...')
    evaluations(df, writer)
    print ('Evaluation Completed...')
    distributions(df, top_n, writer)
    print ('Distributions Completed...')
    writer.save()

## Runs evaluations on each column of the file
def evaluations(df, excel_writer):
    results = []
    cols = df.columns
    # loops through each column and calculates the values
    for i in cols:
        minu = df[i].dropna().min()
        maxu =df[i].dropna().max()    
        dist = df[i].value_counts().count()
        non_nulls = df[i].count()
        tots = len(df[i])
        perc_null = round(float(tots-non_nulls)/tots,2)
        min_len = df[i].apply(str).str.len().min()
        max_len = df[i].apply(str).str.len().max()
        # string fields do not need mean or sum calculated so the columns are split by datatype
        if df[i].dtype.kind in 'biufc' :
            avg = round(df[i].mean(),2)
            sumu = round(df[i].sum(),2)
            results.append([i, 'numeric', dist, min_len, max_len, non_nulls, tots, perc_null, minu, maxu, avg, sumu])
        else:
            results.append([i, 'string', dist, min_len, max_len, non_nulls, tots, perc_null, minu, maxu, '', ''])
    #present the results in a tabular form for saving
    df_final = pd.DataFrame(results, columns=['column','data_type','distinct_values','min_col_len','max_col_len','non_nulls','total', 'perc_null','min','max','mean','sum'])#.applymap(str)      
    df_final.to_excel(excel_writer,'eval', )
    workbook = excel_writer.book
    worksheet = excel_writer.sheets['eval']
    format_perc = workbook.add_format({'num_format':'0%'})
    format_int = workbook.add_format({'num_format':'#,##0'})
    format_dec = workbook.add_format({'num_format':'#,##0.00'})
    worksheet.set_column('I:I',9, format_perc)
    worksheet.set_column('D:H',12, format_int)
    worksheet.set_column('L:M',df_final['sum'].apply(str).str.len().max() + 3, format_dec)
    worksheet.set_column('B:B',df_final['column'].apply(str).str.len().max() + 1)
    worksheet.set_column('J:J',df_final['min'].apply(str).str.len().max() + 1)
    worksheet.set_column('K:K',df_final['max'].apply(str).str.len().max() + 1)

## Runs distributions of the top X values of each column of the file    
def distributions(df, returned_number, excel_writer):
    cols = df.columns
    tot_rows = df.shape[0]
    workbook = excel_writer.book   
    format_perc = workbook.add_format({'num_format':'0.00%'})
    format_int = workbook.add_format({'num_format':'#,##0'})

    for i in cols:
        if df[i].count() == 0:
            continue
        else:
        #groups the column by all the values and returns the top n largest
            df2 = df[i].value_counts().nlargest(returned_number)
            #turn it into tabular form, rename and rearrange the columns
            df3 = pd.DataFrame(df2).reset_index().rename(columns={'index':'value', i:'count'})
            df3['column']=i
            cols = df3.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            #all values are returned as string so as not to lose any data
            df4 = df3[cols]#.applymap(str)
            #df4.loc[:,'perc'] = df4.loc[:,'count']/tot_rows
            df4 = df4.assign(perc=df4.loc[:,'count']/tot_rows)
            df4.to_excel(excel_writer, i[:29]) #excel tabs max size is 30 so truncate field names

            worksheet = excel_writer.sheets[i[:29]]   
            worksheet.set_column('E:E',9, format_perc)     
            worksheet.set_column('B:B',df4['column'].apply(str).str.len().max() + 2)     
            worksheet.set_column('C:C',df3['value'].apply(str).str.len().max() + 1)      
            worksheet.set_column('D:D',df4['count'].apply(str).str.len().max() + 3, format_int)         

main()

#call the main function
#python3 data_profiler.py "file location" "save location" topN

#python3 data_profiler.py "/Users/kristenbiskobin/Desktop/RXSHARE_OA_RX_CLAIMS_CAID_02v2.txt_201806080924.txt" "/Users/kristenbiskobin/Documents/Evla&Distros/" 10



def data_frame_sorter_by_value(df_data,
                               list_of_columns_to_groupby,
                               column_value,
                               ascending_order=False,
                               additional_column_to_sort_on=[],
                               nan_position="first"):
    import pandas as pd
    import numpy as np
    df=df_data.copy()
    df=pd.merge(df,
             df.groupby(list_of_columns_to_groupby)[column_value].sum().reset_index(name="sort_on"),
             left_on= list_of_columns_to_groupby,
             right_on = list_of_columns_to_groupby,
             how="left")
    
    df = df.sort_values(["sort_on"]+list_of_columns_to_groupby+additional_column_to_sort_on,
                      ascending=ascending_order,
                     na_position=nan_position).reset_index(drop=True)
    df.drop("sort_on",axis=1,inplace=True)
    return(df)


def rolling_window_slicer(series,window):
    """Slice a series into rolling window bucket"""
    import numpy as np
    list_of_slices=[]
    for i in range(0,len(series)-window+1):
        list_of_slices.append(series[i:window])
        window=window+1
    return(np.array(list_of_slices))



def data_frame_flattener(df_data):
    df=df_data.copy()
    try:
        df.columns=[' '.join(map(str,col)).strip() for col in df.columns.values]
    except:
        pass
    return(df)


def column_suffix_adder(df_data,
                        list_of_columns_to_add_suffix_on,
                        suffix):
    """Add specific siffix to specific columns"""
    df=df_data.copy()
    ### Add suffix or prefix to certain columns rename all columns
    new_names = [(i,i+suffix) for i in df[list_of_columns_to_add_suffix_on].columns.values]
    df.rename(columns = dict(new_names), inplace=True)
    return(df)


def column_prefix_adder(df_data,
                        list_of_columns_to_add_prefix_on,
                        prefix):
    """Add specific prefix to specific columns"""
    df=df_data.copy()
    ### Add prefix prefix to certain columns rename all columns
    new_names = [(i,prefix+i) for i in df[list_of_columns_to_add_prefix_on].columns.values]
    df.rename(columns = dict(new_names), inplace=True)
    return(df)


def pivot_table_with_subgroup(df_data,
                             pivot_index,
                             pivot_columns,
                             pivot_values,
                             pivot_func):
    """Generate Pivot tabel with subggroup of the index same as what excel does"""
    import pandas as pd
    df_table = pd.DataFrame()
    for i in range(len(pivot_index)):
        df_pivot1=pd.pivot_table(data=df_data,
                                 index=pivot_index[:-i+len(pivot_index)],
                                 columns=pivot_columns,
                                 values=pivot_values,
                                 aggfunc=pivot_func,
                                 fill_value=0).reset_index()
        df_pivot1= data_frame_flattener(df_pivot1)
        ### Append Generated dataframes on top of each other
        df_table=df_table.append(df_pivot1,
                                 sort=False,
                                 ignore_index=True)
    ### Sort values
    df_table.sort_values(pivot_index,
                         na_position="first",
                         inplace=True)
    return(df_table)


def weighted_avg(group, value_variable, weight_variable):
    """ Compute Weighted Average of a variable given weight variable. Can be used on Groupby.
    Example: df_data.groupby(["Manager","State","Product"]).apply(wavg, "Unit Price", "Quantity")
    https://pbpython.com/weighted-average.html
    http://stackoverflow.com/questions/10951341/pandas-dataframe-aggregate-function-using-multiple-columns
    In rare instance, we may not have weights, so just return the mean. Customize this if your business case
    should return otherwise.
    """
    d = group[value_variable]
    w = group[weight_variable]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()



def dataframe_col_widths_returner(df):
    import numpy as np
    measurer = np.vectorize(len)
    return ((measurer(df.values.astype(str)).max(axis=0)))


def data_frame_to_excel_savor(list_of_data_frame,
                              list_of_sheet_name,
                              path_filename,
                              tuple_freez_pans=(1,1),
                              float_format="%.4f"):
    """Saving dateframes into excelDataFrame my be flat."""
    import pandas as pd
    import numpy as np
    data_frame_for_writer= list_of_data_frame
    sheets_in_writer= list_of_sheet_name
    ###save File as Excel
    writer = pd.ExcelWriter(path_filename)
    for df,sheet in zip(data_frame_for_writer,
                        sheets_in_writer):
        df.to_excel(writer,
                    sheet,
                    index=False,
                    float_format=float_format)
    ### Assign WorkBook
    workbook=writer.book
    # Add a header format
    header_format = workbook.add_format({'bold': True,
                                         'text_wrap': True,
                                         'size':10,
                                         'valign': 'top',
                                         'fg_color': '#c7e7ff',
                                         'border': 1})
    
    ### Apply same format on each sheet being saved
    for df,sheet in zip(data_frame_for_writer,
                        sheets_in_writer):
        for col_num, value in enumerate(df.columns.values):
            writer.sheets[sheet].write(0, col_num, value, header_format)
            writer.sheets[sheet].autofilter(0,0,0,df.shape[1]-1)
            writer.sheets[sheet].freeze_panes(tuple_freez_pans[0],tuple_freez_pans[1])
        ### If the width of the column is less than 4 , assign 7
        widths=dataframe_col_widths_returner(df)
        widths=np.where(widths > 5,widths,6.8)
        for i, width in enumerate(widths):
            writer.sheets[sheet].set_column(i, i, width)
    writer.save()


def multivariate_t_rvs(m, S, df, n=1):
    #written by Enzo Michelangeli, style changes by josef-pktd
    # Student's T random variable
    '''generate random variables of multivariate t distribution
    Parameters
    ----------
    m : array_like
        mean of random variable, length determines dimension of random variable
    S : array_like
        square array of covariance  matrix
    df : int or float
        degrees of freedom
    n : int
        number of observations, return random array will be (n, len(m))
    Returns
    -------
    rvs : ndarray, (n, len(m))
        each row is an independent draw of a multivariate t distributed
        random variable
    '''
    import numpy as np
    m = np.asarray(m)
    d = len(m)
    if df == np.inf:
        x = 1.
    else:
        x = np.random.chisquare(df, n)/df
    z = np.random.multivariate_normal(np.zeros(d),S,(n,))
    return m + z/np.sqrt(x)[:,None]   # same output format as random.multivariate_normal




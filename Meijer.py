import pandas as pd 
import numpy as np
import itertools
import re 


def create_meijer_df():
    # Specify the path of Excel file
    excel_file = 'Data\Master Forecast File.xlsx'

    meijer_df = pd.read_excel(excel_file, sheet_name='Meijer', skiprows=284)
    pd.set_option('display.max_columns', None)

    meijer_df = meijer_df.head(466-284)

    ## Extracting date records in a df
    date_df = pd.read_excel(excel_file, sheet_name='Meijer', skiprows=271)
    # date_df
    date_df = date_df.head(13)

    # Converting last row as heading

    # Extract the last row as the new column headers
    new_column_headers = date_df.iloc[-1]

    # Remove the last row from the DataFrame
    date_df = date_df.iloc[:-1]

    # Assign the new column headers
    date_df.columns = new_column_headers

    # Reset index if needed
    date_df.reset_index(drop=True, inplace=True)
    # date_df

    # Drop columns where all records are null
    meijer_df = meijer_df.dropna(axis=1, how='all')
    date_df = date_df.dropna(axis=1, how='all')

    # Convert all columns to USA date format
    date_df = date_df.apply(pd.to_datetime)

    #Drop all records with NaN values
    meijer_df = meijer_df.dropna(how='all')

    # Remove records where the value in the "unit" column is empty or NaN
    meijer_df = meijer_df[meijer_df['Units'].notna() & (meijer_df['Units'] != '')]

    # Convert the "data" column to integers
    meijer_df['Date'] = meijer_df['Date'].astype(int)

    # rename column
    meijer_df.rename(columns={'Unnamed: 2': 'Packs Per Case'}, inplace=True)


    # Get unique units from kroger_df
    unique_units = meijer_df['Units'].unique()

    # Initialize an empty list to store the data
    data_to_fill = []

    # Iterate over each unit
    for unit in unique_units:
        # Extract Brand and Packs Per Case information
        brand = meijer_df[meijer_df['Units'] == unit]['Brand'].iloc[0]
        packs_per_case = meijer_df[meijer_df['Units'] == unit]['Packs Per Case'].iloc[0]
        
        # Filter kroger_df for the current unit
        unit_data = meijer_df[meijer_df['Units'] == unit]
        
        # Iterate over each year
        for year in unit_data['Date'].unique():
            # Extract week data for the current year
            week_data = []
            for period in range(1, 14):
                for week in range(1, 5):
                    week_data.append(f'PD {period} WK {week} ({(period - 1) * 4 + week})')

            # Create a list of tuples containing unit, brand, packs per case, year, week, and corresponding data
            unit_brand_data = [(unit, brand, packs_per_case, year, week, None) for week in week_data]
        
            # Append the unit, brand, packs per case, year, week, and data to the data_to_fill list
            data_to_fill.extend(unit_brand_data)

    # Create a DataFrame from the data_to_fill list
    filled_df = pd.DataFrame(data_to_fill, columns=['Units', 'Brand', 'Packs Per Case', 'Year', 'Week', 'Data_weekly'])



    ## Creating Tempelate df
    # Create an empty DataFrame with specified columns
    columns = ['Retailers', 'Item Description', 'Brand', 'Packs Per Case', 'Week', 'Date', 'Year', 'Sales $', 'Sales U', 'Avg Sell Price', 'Retail', 'Store Count', 'In Stock', 'PPSPW']
    template_df = pd.DataFrame(columns=columns)


    # Fill the "Item Description" column of template_df from the "Units" column of walmart_df
    template_df['Item Description'] = filled_df['Units']
    template_df['Brand'] = filled_df['Brand']
    template_df['Packs Per Case'] = filled_df['Packs Per Case']
    template_df['Year'] = filled_df['Year']
    template_df['Week'] = filled_df['Week']
    template_df['Sales U'] = filled_df['Data_weekly']
    template_df['Retailers'] = "Meijer"


    date_L = []

    for index, row in template_df.iterrows():
        week = row['Week']
        year_temp = row['Year']
        match_found = False  # Initialize flag variable

        # Extract the week number from the 'Week' string in template_df
        week_num_template = re.sub(r'\D', '', week)  # Remove non-digit characters

        for column in date_df.columns:
            # Extract the week number from the column name in date_df
            week_num_date = re.sub(r'\D', '', column)  # Remove non-digit characters

            if week_num_template == week_num_date:
                for idx, date in date_df[column].items():
                    year = date.year
                    if year == year_temp:
                        date_str = date.strftime('%Y-%m-%d')
                        date_L.append(date_str)
                        match_found = True  # Set flag to indicate match found
                        break  # Exit the inner loop once match is found
        
        if not match_found:
            date_L.append(np.nan)  # Append NaN if no match found

    # Filling Date column
    template_df["Date"] = date_L


    df_sales = pd.read_excel('Data\Master Forecast File.xlsx', sheet_name='Kroger', skiprows=2)

    # Keeping only required records, which is top 215
    df_sales = df_sales.head(138)

    # #  Renaming some of the columns
    df_sales = df_sales.rename(columns={'Unnamed: 0': 'Units', 'Unnamed: 3': 'data'})

    # print(len(df_sales['Units'].unique()))
    # print((df_sales['Units'].unique()))

    # # # keeping only useful rows as per template 
    # df_sales = df_sales[(df_sales['data'] == 'Week/Date') | (df_sales['data'] == '$ Sales')| (df_sales['data'] == 'PPSPW')| (df_sales['data'] == 'In Stock')| (df_sales['data'] == 'Stores') | (df_sales['data'] == 'Unit Sales')]

    # Filter rows based on unique values
    # df_sales = df_sales[df_sales['data'].isin(unique_values)]

    # Dropping empty and unnacessary columns
    df_sales = df_sales.dropna(axis=1, how='all' )
    df_sales = df_sales.dropna(axis=0, how='all')
    df_sales.drop(columns=['Retailer Week'], inplace=True)

    # print(df_sales.shape)
    # print(df_sales.shape)
    df_sales.reset_index()

    # Identify rows where 'data' column is 'Week/Date'
    date_mask = df_sales['data'] == 'Week/Date'

    # Iterate over columns from 'Unnamed: 3' to 'Unnamed: 789'
    for col in df_sales.columns[3:]:
        # Check if the corresponding row in 'data' column is 'Week/Date' and the value is not already NaN or a string
        mask = date_mask & ~df_sales[col].isna() & ~df_sales[col].apply(lambda x: isinstance(x, str))
        
        # Convert date part to datetime format for the identified rows, handling mixed data types
        df_sales.loc[mask, col] = pd.to_datetime(df_sales.loc[mask, col], errors='coerce').dt.date

    # Melt the dataframe to long format
    df_melt = df_sales.melt(id_vars=['Units', 'data'], var_name='Unnamed', value_name='value')
    # Pivot the dataframe to wide format with 'Units' and 'Unnamed' as index
    df_pivot = df_melt.pivot(index=['Units', 'Unnamed'], columns='data', values='value').reset_index()

    # # Rename the columns
    # df_pivot.columns.name = None
    df_pivot.columns = ['Units', 'Unnamed', 'date', '$ Sales', 'PPSPW', 'In Stock', 'Store', 'unit sales', 'Stores', 'Date']

    # Sort the dataframe by 'Units' and 'date'
    df_pivot.sort_values(['Units', 'date'], inplace=True)

    # Drop the 'Unnamed' column
    df_pivot.drop(columns='Unnamed', inplace=True)

    # Reset the index of the dataframe
    df_pivot.reset_index(drop=True, inplace=True)

    # Reset the index after dropping rows
    df_pivot = df_pivot.reset_index(drop=True)

    # Rename columns to match the original naming
    df_pivot = df_pivot.rename(columns={'Stores':'Unit Sales', 'PPSPW' : 'Avg $/Unit', 'Store':'PPSPW' })


    # # Drop rows with NaN or NaT values in 'date' or 'price' columns
    df_pivot = df_pivot.dropna(subset=["Units" ])
    df_pivot = df_pivot.dropna(subset=["Date",'$ Sales' ])

    # dropping useless column
    df_pivot.drop(columns=['date', 'unit sales'], axis=1, inplace=True)


    # Convert date columns to datetime objects
    template_df['Date'] = pd.to_datetime(template_df['Date'])
    df_pivot['Date'] = pd.to_datetime(df_pivot['Date'])

    df_pivot['PPSPW'] = df_pivot['PPSPW'].astype(float)
    df_pivot['In Stock'] = df_pivot['In Stock'].astype(float)
    df_pivot['$ Sales'] = df_pivot['$ Sales'].astype(float)
    df_pivot['Avg $/Unit'] = df_pivot['Avg $/Unit'].astype(float)
    df_pivot['Unit Sales'] = df_pivot['Unit Sales'].astype(float)



    # Rename Unit col of df_pivot to Item Description
    df_pivot.rename(columns={'Units': 'Item Description'}, inplace=True)

    # Merge the dataframes on 'Date' and 'Item Description'
    merged_df = pd.merge(template_df, df_pivot, on=['Date', 'Item Description'], how='left')

    template_df['Sales $'] = merged_df['$ Sales']
    template_df['Sales U'] = merged_df['Unit Sales']
    template_df['Avg Sell Price'] = merged_df['Avg $/Unit']
    template_df['In Stock'] = merged_df['In Stock_y']
    template_df['PPSPW'] = merged_df['PPSPW_y']

### Store csv file to local storeage
    # name = 'Meijer_Template'
    # template_df.to_csv(f'{name}.csv', index=False)
    # print(f"{name} CSV Dataset Created Successfully")
    
    
    return template_df


if __name__ == "__main__":
    df = create_meijer_df()
    print(df)



import pandas as pd 
import numpy as np
import itertools


def create_riteaid_df():
    
    # Specify the path of Excel file
    excel_file = r'Data\Master Forecast File.xlsx'

    # Read the specified range of rows from the 'Riteaid' sheet
    start_row = 192
    end_row = 342
    num_rows = end_row - start_row

    # Read the Excel file
    riteaid_df = pd.read_excel(excel_file, sheet_name='Riteaid', skiprows=start_row, nrows=num_rows)


    ## Extracting date records in a df
    date_df = pd.read_excel(excel_file, sheet_name='Riteaid', skiprows=186)

    date_df = date_df.head(6)
    # Converting last row as heading

    # Extract the last row as the new column headers
    new_column_headers = date_df.iloc[-1]

    # Remove the last row from the DataFrame
    date_df = date_df.iloc[:-1]

    # Assign the new column headers
    date_df.columns = new_column_headers

    # Drop columns where all records are null
    riteaid_df = riteaid_df.dropna(axis=1, how='all')
    date_df = date_df.dropna(axis=1, how='all')

    # Convert all columns to USA date format
    date_df = date_df.apply(pd.to_datetime)
    # Drop all records with NaN values
    riteaid_df = riteaid_df.dropna(how='all')


    # Remove records where the value in the "unit" column is empty or NaN
    riteaid_df = riteaid_df[riteaid_df['Units'].notna() & (riteaid_df['Units'] != '')]

    # Convert the "data" column to integers
    riteaid_df['Date'] = riteaid_df['Date'].astype(int)

    # Get unique units from riteaid_df
    unique_units = riteaid_df['Units'].unique()

    # Initialize an empty list to store the data
    data_to_fill = []

    # Iterate over each unit
    for unit in unique_units:
        # Extract Brand and Packs Per Case information
        brand = riteaid_df[riteaid_df['Units'] == unit]['Brand'].iloc[0]
        packs_per_case = riteaid_df[riteaid_df['Units'] == unit]['Packs Per Case'].iloc[0]
        
        # Filter riteaid_df for the current unit
        unit_data = riteaid_df[riteaid_df['Units'] == unit]
        
        # Iterate over each year
        for year in unit_data['Date'].unique():
            # Filter unit_data for the current year
            year_data = unit_data[unit_data['Date'] == year]
            
            # Extract week data for the current year
            week_data = [year_data[f'WK {i}'] for i in range(1,53)]

            # Combine week data into a single list
            week_data_combined = list(itertools.chain(*week_data))

            # Adjust week numbers to start from 1
            week_numbers = list(range(1, 53)) * len(year_data)
            week_numbers.sort()
            
            # Create a list of tuples containing unit, brand, packs per case, year, week, and corresponding data
            unit_brand_data = [(unit, brand, packs_per_case, year, f'WK {week_numbers[i]}', week_data_combined[i]) for i in range(len(week_data_combined))]

            # Append the unit, brand, packs per case, year, week, and data to the data_to_fill list
            data_to_fill.extend(unit_brand_data)

    # Create a DataFrame from the data_to_fill list
    filled_df = pd.DataFrame(data_to_fill, columns=['Units', 'Brand', 'Packs Per Case', 'Year', 'Week', 'Data_weekly'])

    ## Creating Tempelate df

    # Create an empty DataFrame with specified columns
    columns = ['Retailers', 'Item Description', 'Brand', 'Packs Per Case', 'Week', 'Date', 'Year', 'Sales $', 'Sales U', 'Avg Sell Price', 'Retail', 'Store Count', 'In Stock', 'PPSPW']
    template_riteaid = pd.DataFrame(columns=columns)


    # Fill the "Item Description" column of template_df from the "Units" column of walmart_df

    template_riteaid['Item Description'] = filled_df['Units']
    template_riteaid['Brand'] = filled_df['Brand']
    template_riteaid['Packs Per Case'] = filled_df['Packs Per Case']
    template_riteaid['Year'] = filled_df['Year']
    template_riteaid['Week'] = filled_df['Week']
    template_riteaid['Sales U'] = filled_df['Data_weekly']
    template_riteaid['Retailers'] = "Riteaid"

    date_L = []

    for index, row in template_riteaid.iterrows():
        week = row['Week']
        year_temp = row['Year']
        match_found = False  # Initialize flag variable
        
        for index, date in date_df[week].items():
            year = date.year
            if year == year_temp:
                specific_record = date_df.loc[index, week]
                date_str = specific_record.strftime('%Y-%m-%d')
                date_L.append(date_str)
                match_found = True  # Set flag to indicate match found
                break  # Exit the inner loop once match is found
        
        if not match_found:
            date_L.append(np.nan)  # Append NaN if no match found

    # Filling Date column     
    template_riteaid["Date"] = date_L

    df_sales = pd.read_excel(excel_file, sheet_name='Riteaid', skiprows=2)

    # Keeping only required records, which is top 215
    df_sales = df_sales.head(184)

    #  Renaming some of the columns
    df_sales = df_sales.rename(columns={'Unnamed: 0': 'Units', 'Unnamed: 2': 'data'})


    # keeping only 2 rows which is 'Week/Date' and '$ Sales' in out data frame
    df_sales = df_sales[(df_sales['data'] == 'Week/Date') | (df_sales['data'] == 'Stores')| (df_sales['data'] == '$ Sales')| (df_sales['data'] == 'Unit Sales')| (df_sales['data'] == 'Avg $/Unit')| (df_sales['data'] == 'In Stock')| (df_sales['data'] == 'PPSPW')]

    # Dropping empty and unnacessary columns
    df_sales.drop(columns=['Retailer Week Ending'], inplace=True)
    df_sales = df_sales.dropna(axis=1, how='all' )
    df_sales = df_sales.dropna(axis=0, how='all')


    # Identify rows where 'data' column is 'Week/Date'
    date_mask = df_sales['data'] == 'Week/Date'

    # Iterate over columns from 'Unnamed: 4' to 'Unnamed: 789'
    for col in df_sales.columns[2:]:
        # Check if the corresponding row in 'data' column is 'Week/Date' and the value is not already NaN or a string
        mask = date_mask & ~df_sales[col].isna() & ~df_sales[col].apply(lambda x: isinstance(x, str))
        
        # Convert date part to datetime format for the identified rows, handling mixed data types
        df_sales.loc[mask, col] = pd.to_datetime(df_sales.loc[mask, col], errors='coerce').dt.date

    # Melt the dataframe to long format
    df_melt = df_sales.melt(id_vars=['Units', 'data'], var_name='Unnamed', value_name='value')

    # Pivot the dataframe to wide format with 'Units' and 'Unnamed' as index
    df_pivot = df_melt.pivot(index=['Units', 'Unnamed'], columns='data', values='value').reset_index()

    # Rename the columns
    df_pivot.columns.name = None
    df_pivot.columns = ['Units', 'Unnamed', 'date', '$ Sales', 'PPSPW', 'In Stock',  'unit sales', 'Stores', 'Date']

    # Sort the dataframe by 'Units' and 'date'
    df_pivot.sort_values(['Units', 'date'], inplace=True)

    # Drop the 'Unnamed' column
    df_pivot.drop(columns='Unnamed', inplace=True)

    # Reset the index of the dataframe
    df_pivot.reset_index(drop=True, inplace=True)


    # Reset the index after dropping rows
    df_pivot = df_pivot.reset_index(drop=True)

    # Rename columns to match the original naming
    df_pivot = df_pivot.rename(columns={'date': '$ Sales', 'Stores': 'Unit Sales', 'unit sales': 'Stores', '$ Sales':'Avg $/Unit', 'In Stock': 'PPSPW', 'PPSPW':'In Stock'})

    # # Drop rows with NaN or NaT values in 'date' or 'price' columns
    df_pivot = df_pivot.dropna(subset=["Units" ])
    # df_pivot = df_pivot.dropna(subset=["Date",'$ Sales' ])
    # Rename Unit col of df_pivot to Item description
    df_pivot.rename(columns={'Units':'Item Description'}, inplace=True)

    # # Convert date columns to datetime objects
    template_riteaid['Date'] = pd.to_datetime(template_riteaid['Date'])
    df_pivot['Date'] = pd.to_datetime(df_pivot['Date'])

    # Drop rows where all columns except 'Item Description' are NaT or NaN
    df_cleaned = df_pivot.dropna(how='all', subset=df_pivot.columns.difference(['Item Description']))

    # Merge the dataframes on 'Date' and 'Item Description'
    merged_df = pd.merge(template_riteaid, df_cleaned, on=['Date', 'Item Description'], how='left')


    template_riteaid['Sales $'] = merged_df['$ Sales']
    template_riteaid['Sales U'] = merged_df['Unit Sales']
    template_riteaid['Avg Sell Price'] = merged_df['Avg $/Unit']
    # template_riteaid['Retail'] = merged_df['']
    template_riteaid['Store Count'] = merged_df['Stores']
    template_riteaid['In Stock'] = merged_df['In Stock_y']
    template_riteaid['PPSPW'] = merged_df['PPSPW_y']

### Storing csv file to local storage
    # name = 'Riteaid_Template'
    # template_riteaid.to_csv(f'{name}.csv', index=False)
    # print(f"{name} CSV Dataset Created Successfully")
    
    return template_riteaid


if __name__ == "__main__":
    df = create_riteaid_df()
    print(df)
import pandas as pd 
import numpy as np
import itertools

def create_amazon_df():
    ## Load Dataset
    excel_file = 'Data\Master Forecast File.xlsx'   # path of Excel file
    amazon_df = pd.read_excel(excel_file, sheet_name='Amazon', skiprows=505)
    amazon_df = amazon_df.head(750-505)

    ## Extracting date records in a df
    date_df = pd.read_excel(excel_file, sheet_name='Amazon', skiprows=492)
    date_df = date_df.head(13)

    # Converting last row as heading of date df
    new_column_headers = date_df.iloc[-1]   # Extract the last row as the new column headers
    date_df = date_df.iloc[:-1]   # Remove the last row from the DataFrame
    date_df.columns = new_column_headers  # Assign the new column headers
    date_df.reset_index(drop=True, inplace=True)   # Reset index if needed

    # Drop columns where all records are null
    amazon_df = amazon_df.dropna(axis=1, how='all')
    date_df = date_df.dropna(axis=1, how='all')

    # Convert all columns to USA date format
    date_df = date_df.apply(pd.to_datetime)

    # Drop all records with NaN values
    amazon_df = amazon_df.dropna(how='all')

    # Remove records where the value in the "unit" column is empty or NaN
    amazon_df = amazon_df[amazon_df['Units'].notna() & (amazon_df['Units'] != '')]

    # Convert the "data" column to integers
    amazon_df['Date'] = amazon_df['Date'].astype(int)

    # Get unique units from amazon_df
    unique_units = amazon_df['Units'].unique()

    # Initialize an empty list to store the data
    data_to_fill = []

    # Define the week data pattern
    week_data_pattern = [
        '01 WK 1', '01 WK 2', '01 WK 3', '01 WK 4', 
        '2 WK 1', '2 WK 2', '2 WK 3', '2 WK 4', 
        '3 WK 1', '3 WK 2', '3 WK 3', '3 WK 4', '3 WK 5', 
        '4 WK 1', '4 WK 2', '4 WK 3', '4 WK 4', 
        '5 WK 1', '5 WK 2', '5 WK 3', '5 WK 4', 
        '6 WK 1', '6 WK 2', '6 WK 3', '6 WK 4', '6 WK 5', 
        '7 WK 1', '7 WK 2', '7 WK 3', '7 WK 4', 
        '8 WK 1', '8 WK 2', '8 WK 3', '8 WK 4', 
        '9 WK 1', '9 WK 2', '9 WK 3', '9 WK 4', '9 WK 5', 
        '10 WK 1', '10 WK 2', '10 WK 3', '10 WK 4', 
        '11 WK 1', '11 WK 2', '11 WK 3', '11 WK 4', 
        '12 WK 1', '12 WK 2', '12 WK 3', '12 WK 4', '12 WK 5'
    ]

    # Iterate over each unit
    for unit in unique_units:
        # Extract Brand and Packs Per Case information
        brand = amazon_df[amazon_df['Units'] == unit]['Brand'].iloc[0]
        packs_per_case = amazon_df[amazon_df['Units'] == unit]['Packs Per Case'].iloc[0]

        # Filter amazon_df for the current unit
        unit_data = amazon_df[amazon_df['Units'] == unit]

        # Iterate over each year
        for year in unit_data['Date'].unique():
            # Create a list of tuples containing unit, brand, packs per case, year, week, and corresponding data
            unit_brand_data = [(unit, brand, packs_per_case, year, week, None) for week in week_data_pattern]

            # Append the unit, brand, packs per case, year, week, and data to the data_to_fill list
            data_to_fill.extend(unit_brand_data)

    # Create a DataFrame from the data_to_fill list
    filled_df = pd.DataFrame(data_to_fill, columns=['Units', 'Brand', 'Packs Per Case', 'Year', 'Week', 'Data_weekly'])

    ## Creating Template df
    columns = ['Retailers', 'Item Description', 'Brand', 'Packs Per Case', 'Week', 'Date', 'Year', 'Sales $', 'Sales U', 'Avg Sell Price', 'Retail', 'Store Count', 'In Stock', 'PPSPW']
    template_df = pd.DataFrame(columns=columns)

    # Fill the "Item Description" column of template_df from the "Units" column of filled_df
    template_df['Item Description'] = filled_df['Units']
    template_df['Brand'] = filled_df['Brand']
    template_df['Packs Per Case'] = filled_df['Packs Per Case']
    template_df['Year'] = filled_df['Year']
    template_df['Week'] = filled_df['Week']
    template_df['Sales U'] = filled_df['Data_weekly']
    template_df['Retailers'] = "Amazon"  ## This is the name of the Retailers, Please rename here if not getting correct

    date_L = []

    for index, row in template_df.iterrows():
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

    template_df["Date"] = date_L  # Filling Date column 

    ### Populate Sales $ column
    df_sales = pd.read_excel('Data\Master Forecast File.xlsx', sheet_name='Riteaid', skiprows=2)
    df_sales = df_sales.head(187)   # Keeping only required records, which is top 215
    df_sales = df_sales.rename(columns={'Unnamed: 0': 'Units', 'Unnamed: 2': 'data'})
    # keeping only 2 rows which is 'Week/Date' and '$ Sales' in out data frame
    df_sales = df_sales[(df_sales['data'] == 'Week/Date') | (df_sales['data'] == 'Stores') | (df_sales['data'] == '$ Sales') | (df_sales['data'] == 'Unit Sales') | (df_sales['data'] == 'Avg $/Unit') | (df_sales['data'] == 'In Stock') | (df_sales['data'] == 'PPSPW')]

    # Dropping empty and unnecessary columns
    df_sales = df_sales.dropna(axis=1, how='all')
    df_sales = df_sales.dropna(axis=0, how='all')
    df_sales.drop(columns=['Retailer Week Ending'], inplace=True)

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

    # Drop rows with NaN or NaT values in 'date' or 'price' columns
    df_pivot = df_pivot.dropna(subset=["Units"])
    # df_pivot = df_pivot.dropna(subset=["Date",'$ Sales' ])
    # Rename Unit col of df_pivot to Item description
    df_pivot.rename(columns={'Units':'Item Description'}, inplace=True)

    # Convert date columns to datetime objects
    template_df['Date'] = pd.to_datetime(template_df['Date'])
    df_pivot['Date'] = pd.to_datetime(df_pivot['Date'])

    # Merge the dataframes on 'Date' and 'Item Description'
    merged_df = pd.merge(template_df, df_pivot, on=['Date', 'Item Description'], how='left')

    template_df['Sales $'] = merged_df['$ Sales']
    template_df['Sales U'] = merged_df['Unit Sales']
    template_df['Avg Sell Price'] = merged_df['Avg $/Unit']
    # template_df['Retail'] = merged_df['']
    template_df['Store Count'] = merged_df['Stores']
    template_df['In Stock'] = merged_df['In Stock_y']
    template_df['PPSPW'] = merged_df['PPSPW_y']

    # name = 'Amazon_Template'
    # template_df.to_csv(f'{name}.csv', index=False)
    # print(f"{name} CSV Dataset Created Successfully")

    return template_df

if __name__ == "__main__":
    df = create_amazon_df()
    print(df)

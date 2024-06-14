import pandas as pd


import Amazon
import HomeDepot
import Kroger
import Lowes
import Meijer
import Publix
import Riteaid
import Target
import Wakefern
import Walmart





def create_master_df():


    # Call the function to create the DataFrame
    amazon_df = Amazon.create_amazon_df()
    home_depot_df = HomeDepot.create_homedepot_df()
    kroger_df = Kroger.create_kroger_df()
    lowes_df = Lowes.create_lowes_df()
    meijer_df = Meijer.create_meijer_df()
    publix_df = Publix.create_publix_df()
    riteaid_df = Riteaid.create_riteaid_df()
    target_df = Target.create_target_df()
    wakefern_df = Wakefern.create_wakefern_df()
    walmart_df = Walmart.create_walmart_df()

    df_Upload = pd.read_excel("Data\Item_Code.xlsx", sheet_name='Forecast Data', skiprows=1)

    # Selecting three specific columns
    selected_columns = ['CustomerNo','ProductLineDesc', 'ItemCode', 'ItemCodeDesc']
    df_selected = df_Upload[selected_columns]

    df_selected.rename(columns={'ItemCodeDesc': 'Item Description'}, inplace=True)
    df_selected.rename(columns={'CustomerNo': 'Retailers'}, inplace=True)


    # List of dataframes to process
    dataframes = [
        df_selected, kroger_df, walmart_df, amazon_df, home_depot_df, 
        lowes_df, meijer_df, riteaid_df, target_df, wakefern_df, publix_df
    ]

    # Columns to convert to lowercase
    columns_to_lower = ['Item Description', 'Retailers']

    # Apply the transformation to each dataframe
    for df in dataframes:
        for col in columns_to_lower:
            df[col] = df[col].str.lower()



    walmart_df = pd.merge(walmart_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    kroger_df = pd.merge(kroger_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    amazon_df = pd.merge(amazon_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    home_depot_df = pd.merge(home_depot_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    lowes_df = pd.merge(lowes_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    meijer_df = pd.merge(meijer_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    riteaid_df = pd.merge(riteaid_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    wakefern_df = pd.merge(wakefern_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    target_df = pd.merge(target_df, df_selected, on=['Item Description', 'Retailers'], how='left')
    publix_df = pd.merge(publix_df, df_selected, on=['Item Description', 'Retailers'], how='left')


    # Create an empty master DataFrame
    master_df = pd.DataFrame()

    # List of our individual DataFrames
    dfs = [
        kroger_df, walmart_df, amazon_df, home_depot_df, 
        lowes_df, meijer_df, riteaid_df, target_df, wakefern_df, publix_df
    ]

    # Append each DataFrame to the master DataFrame
    for df in dfs:
        master_df = pd.concat([master_df, df], ignore_index=True)
        
        
    # Save the master DataFrame to a CSV file
    # master_df.to_csv('data/master_df Complete Template.csv', index=False)
    # print("Master Database Is Saved Successfully in the Data Folder")
    
    return master_df

if __name__ == "__main__":
    df = create_master_df()
    print(df)
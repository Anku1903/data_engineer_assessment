import pandas as pd
import mysql.connector
from mysql.connector import Error

# ---- 1. Extract data
def extract(csv_file_path):
    # load the CSV into a DataFrame
    df = pd.read_csv(csv_file_path)
    return df




# ---- 2. Transform data
def transform(df: pd.DataFrame):

    # make sure each column has the right pandas type
    df = df.convert_dtypes()


    # strip spaces from any text fields
    df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)

    # round decimal columns to 2 decimal points (except Latitude & Longitude)
    float_cols_to_roundoff = ['Tax_Rate', 'Net_Yield', 'IRR','School_Average']
    df[float_cols_to_roundoff] = df[float_cols_to_roundoff].apply(lambda x: round(x,2))


    # Identify all string column which endswith 'Flag' and then we will fill their missing,NULL,blank values with 'No'
    # Reason for filling 'Flag' columns with 'No': in property data if these Flag columns are missing means that values are not exist in property listing so we can fill them with 'No'
    flag_str_cols = [col for col in df.columns if col.endswith('Flag') or col == 'BasementYesNo']
    df[flag_str_cols] = df[flag_str_cols].fillna("No")
    df[flag_str_cols] = df[flag_str_cols].replace('', 'No')
    df[flag_str_cols] = df[flag_str_cols].replace(' ', 'No')


    # For other string columns that are not endswith 'Flag', we will fill their missing or NULL values by 'Unknown'
    other_str_cols = df.select_dtypes(include=["string"]).columns.tolist()
    df[other_str_cols] = df[other_str_cols].fillna('Unknown')
    df[other_str_cols] = df[other_str_cols].replace('', 'Unknown')
    df[other_str_cols] = df[other_str_cols].replace(' ', 'Unknown')


    # Identify all integer-typed columns
    int_cols = df.select_dtypes(include=["int64", "Int64"]).columns.tolist()
    
    # Create a boolean mask for rows that have any negative integer
    negative_mask = df[int_cols].lt(0).any(axis=1)
    
    # Keep only rows where integer column is not negative
    df = df.loc[~negative_mask].reset_index(drop=True)

    # Drop the fully duplicate records
    df = df.drop_duplicates()


    # return transformed dataframe
    return df




def insert_address_data_to_mysql(connection, df: pd.DataFrame, table_name):
    cursor = connection.cursor()

    # build the column list and placeholders for SQL
    cols = ", ".join([f"`{c}`" for c in df.columns])
    vals = ", ".join(["%s"] * len(df.columns))
    sql_query = f"INSERT INTO `{table_name}` ({cols}) VALUES ({vals})"
    
    # prepare the raw records and a list of the original addresses
    data_to_insert = [tuple(row.values()) for row in df.to_dict(orient='records')]
    addresses = [row['Address'] for row in df.to_dict(orient='records')]
    address_ids = []
    
    try:
        # insert each address row and grab its auto-generated ID
        for record in data_to_insert:
            cursor.execute(sql_query, record)
            address_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"{len(df)} records inserted into {table_name}.")

        # return a mapping of Address → Address_ID
        address_ids_map = {item[0]: item[1] for item in zip(addresses,address_ids)}
        return address_ids_map
    
    except Error as err:
        print(f"Error: '{err}'")
        return None
    



def insert_property_data_to_mysql(connection, df: pd.DataFrame, table_name):
    cursor = connection.cursor()

    # build the column list and placeholders for SQL
    cols = ", ".join([f"`{c}`" for c in df.columns])
    vals = ", ".join(["%s"] * len(df.columns))
    sql_query = f"INSERT INTO `{table_name}` ({cols}) VALUES ({vals})"
    
    # prepare data and track the Address_ID each property belongs to
    data_to_insert = [tuple(row.values()) for row in df.to_dict(orient='records')]
    address_ids = [row['Address_ID'] for row in df.to_dict(orient='records')]
    prop_ids = []
    
    try:
        # insert each property row and collect its Auto-generated Property_ID
        for record in data_to_insert:
            cursor.execute(sql_query, record)
            prop_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"{len(df)} records inserted into {table_name}.")

        # return mapping of Address_ID → Property_ID
        prop_ids_map = {item[0]: item[1] for item in zip(address_ids,prop_ids)}
        return prop_ids_map
    
    except Error as err:
        print(f"Error: '{err}'")
        return None




def insert_to_mysql(connection, df: pd.DataFrame, table_name):
    cursor = connection.cursor()

    # build the column list and placeholders for SQL
    cols = ", ".join([f"`{c}`" for c in df.columns])
    vals = ", ".join(["%s"] * len(df.columns))
    sql_query = f"INSERT INTO `{table_name}` ({cols}) VALUES ({vals})"
    
    # Preparing data to insert
    data_to_insert = [tuple(row.values()) for row in df.to_dict(orient='records')]
    
    try:
        # insert bulk records
        cursor.executemany(sql_query, data_to_insert)
        connection.commit()
        print(f"{cursor.rowcount} records inserted into {table_name}.")
    except Error as err:
        print(f"Error: '{err}'")





# ---- 3. Load data

def load_data(df: pd.DataFrame):

    # Addresses dataframe
    address_cols = ["Address","Street_Address","City","State","Zip"]
    df_address = df[address_cols].drop_duplicates(subset=['Address']).reset_index(drop=True)

    # Property dataframe
    prop_cols = ["Address","Property_Title","Property_Type",
    "Market","Flood","Highway","Train","Tax_Rate","SQFT_Basement","HTW","Pool",
    "Commercial","Water","Sewage","Year_Built","SQFT_MU","SQFT_Total","Parking",
    "Bed","Bath","BasementYesNo","Layout","Rent_Restricted","Neighborhood_Rating","Latitude","Longitude",
    "Subdivision","School_Average"
    ]
    df_property = df[prop_cols].drop_duplicates(subset=['Address']).reset_index(drop=True)

    # Leads dataframe
    leads_cols = ["Address","Reviewed_Status","Most_Recent_Status","Source",
              "Occupancy","Net_Yield","IRR","Selling_Reason","Seller_Retained_Broker",
              "Final_Reviewer"]
    df_leads = df[leads_cols]

        
    # Valuation dataframe
    val_cols = ["Address","Previous_Rent","List_Price","Zestimate","ARV",
                "Expected_Rent","Rent_Zestimate","Low_FMR","High_FMR","Redfin_Value"]
    df_valuation = df[val_cols]

    # Hoa dataframe
    hoa_cols = ["Address","HOA","HOA_Flag"]
    df_hoa = df[hoa_cols]

    # Rehab dataframe
    rehab_cols = ["Address","Underwriting_Rehab","Rehab_Calculation","Paint",
                "Flooring_Flag","Foundation_Flag","Roof_Flag","HVAC_Flag","Kitchen_Flag",
                "Bathroom_Flag","Appliances_Flag","Windows_Flag","Landscaping_Flag",
                "Trashout_Flag"]
    df_rehab = df[rehab_cols]

    # Taxes dataframe
    taxes_cols = ["Address","Taxes"]
    df_taxes = df[taxes_cols]


    # Setup MYSQL connection
    Connection = mysql.connector.connect(**DB_CONFIG)

    # Load Address_info table data into MYSQL & retrive its Auto-generated Address_IDs
    address_ids_map = insert_address_data_to_mysql(Connection,df_address,table_name='Address_info')

    # Map Address_IDs into Property dataframe for FORIGN KEY
    df_property = df_property.copy()
    df_property.loc[:,'Address_ID'] = df_property['Address'].apply(lambda x: address_ids_map.get(x))
    df_property = df_property.drop(columns=['Address'])

    # Load Property table data into MYSQL & retrive its Auto-Generated Property_IDs
    prop_ids_map = insert_property_data_to_mysql(Connection,df_property,table_name='Property')

    # Map Property_IDs into Leads dataframe
    df_leads = df_leads.copy()
    df_leads.loc[:,'Property_ID'] = df_leads["Address"].apply(lambda x: prop_ids_map.get(address_ids_map.get(x)))
    df_leads = df_leads.drop(columns=['Address'])

    # Map Property_IDs into valuation dataframe
    df_valuation = df_valuation.copy()
    df_valuation.loc[:,'Property_ID'] = df_valuation["Address"].apply(lambda x: prop_ids_map.get(address_ids_map.get(x)))
    df_valuation = df_valuation.drop(columns=['Address'])

    # Map Property_IDs into Rehab dataframe
    df_rehab = df_rehab.copy()
    df_rehab.loc[:,'Property_ID'] = df_rehab["Address"].apply(lambda x: prop_ids_map.get(address_ids_map.get(x)))
    df_rehab = df_rehab.drop(columns=['Address'])

    # Map Property_IDs into HOA dataframe
    df_hoa = df_hoa.copy()
    df_hoa.loc[:,'Property_ID'] = df_hoa["Address"].apply(lambda x: prop_ids_map.get(address_ids_map.get(x)))
    df_hoa = df_hoa.drop(columns=['Address'])

    # Map Property_IDs into Taxes dataframe
    df_taxes = df_taxes.copy()
    df_taxes.loc[:,'Property_ID'] = df_taxes["Address"].apply(lambda x: prop_ids_map.get(address_ids_map.get(x)))
    df_taxes = df_taxes.drop(columns=['Address'])
    
    
    # Load all remaining data into their MYSQL tables

    insert_to_mysql(Connection,df_leads,table_name='Leads')
    
    insert_to_mysql(Connection,df_valuation,table_name='Valuation')
    
    insert_to_mysql(Connection,df_rehab,table_name='Rehab')
    
    insert_to_mysql(Connection,df_hoa,table_name='HOA')
    
    insert_to_mysql(Connection,df_taxes,table_name='Taxes')





if __name__ == '__main__':


    # CONFIGURATION
    
    CSV_FILE_PATH    = "sql/fake_data.csv"
    DB_CONFIG   = {
        "host":     "127.0.0.1",
        "port":     3306,
        "user":     "db_user",
        "password": "6equj5_db_user",
        "database": "home_db"
    }

    df = extract(csv_file_path=CSV_FILE_PATH)
    
    df = transform(df)
    
    load_data(df)

    print("ETL process completed successfully!")
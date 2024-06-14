import os
import io
import sqlite3
import pandas as pd

import tkinter as tk
from pathlib import Path
from tkinter import font
from tkinter import ttk, messagebox, filedialog

# Importing the master dataframe generation module
import Master_df   ## this is py file where we are getting our master df, where all data combined
from Master_df import Kroger, Walmart, Wakefern, Lowes, Amazon, Meijer, Publix, Riteaid, Target, HomeDepot # Individual company data



# Function to create the SQLite database
def create_sqlite_db():
    messagebox.showwarning("Warning", "Please Execute this only and only if DATABASE FILE IS MISSING, Which is rare")
    messagebox.showinfo("Wait", "Please Wait till next SUCCESS popup, database file is being created")
    try:
        # Load master data
        df = Master_df.create_master_df()

        # Connect to SQLite database (or create it if it doesn't exist)
        db_file = 'sales_data.db'
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create a table with appropriate column names and types (modify as needed)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_data (
            Retailers TEXT,
            Item_Description TEXT,
            Brand TEXT,
            Packs_Per_Case INTEGER,
            Week TEXT,
            Date TEXT,
            Year INTEGER,
            Sales_Dollar REAL,
            Sales_U INTEGER,
            Avg_Sell_Price REAL,
            Retail TEXT,
            Store_Count INTEGER,
            In_Stock INTEGER,
            PPSPW INTEGER,
            ProductLineDesc TEXT,
            ItemCode TEXT,
            UNIQUE(Retailers, Item_Description, Brand, Date) ON CONFLICT IGNORE
        )
        ''')

        # Load data into the table
        df.to_sql('sales_data', conn, if_exists='replace', index=False)

        # Commit and close the connection
        conn.commit()
        conn.close()

        print(f"Data has been successfully loaded into {db_file}")
        messagebox.showinfo("Success", "SQLite3 Database file created successfully")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
# create_sqlite_db()

### Function to access the SQLite database
def access_sql_db():
    # Connect to the SQLite database
    db_file = 'sales_data.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query the data
    query = 'SELECT * FROM sales_data'
    df = pd.read_sql_query(query, conn)

    # Close the connection
    conn.close()

    # Display the database as  dataframe 
    return df


def download_master_df_csv():
    messagebox.showwarning("Wait", "Pleae wait for a second till the next success Popup")
    # Get the user's home directory
    home = Path.home()
    
    # Construct the path to the download directory
    download_dir = home / "Downloads"
    
    # Ensure the directory exists (it usually does, but just in case)
    os.makedirs(download_dir, exist_ok=True)
    
    # Generate the master dataframe
    df = access_sql_db()
    
    # Save the dataframe to a CSV file in the "Download" directory
    file_path = download_dir / "Database.csv"
    df.to_csv(file_path, index=False)
    
    messagebox.showinfo("Success", "Database file Stored in Download Directory Successfully in CSV format!")

def download_master_df_excel():
    messagebox.showwarning("Wait", "Pleae wait for a second till the next success Popup")
    home = Path.home()
    download_dir = home / "Downloads"   # Construct the path to the download directory
    os.makedirs(download_dir, exist_ok=True)    # Ensure the directory exists (it usually does, but just in case)
    df = access_sql_db()   # Generate the master dataframe
    
    # Save the dataframe to a CSV file in the "Download" directory
    file_path = download_dir / "Database.xlsx"
    df.to_excel(file_path, index=False)
    
    messagebox.showinfo("Success", "Database file Stored in Download Directory Successfully in EXCEL format!")

def download_master_df_sqlite():
    messagebox.showwarning("Wait", "Please wait for a second till the next success Popup")

    try:
        # Get the user's home directory
        home = Path.home()
        # Construct the path to the download directory
        download_dir = home / "Downloads"
        # Ensure the directory exists (it usually does, but just in case)
        os.makedirs(download_dir, exist_ok=True)
        
        df = access_sql_db()

        # Construct the full file path for the SQLite database
        db_file = download_dir / 'sales_data.db'

        # Connect to SQLite database
        conn = sqlite3.connect(db_file)

        # Save the DataFrame to the SQLite database
        df.to_sql('sales_data', conn, if_exists='replace', index=False)

        # Commit and close the connection
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "SQLite Database successfully stored in Download Directory")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")





def download_selected_format():
    selected_format = selected_format_var.get()
    if selected_format == "Select Action":
        messagebox.showerror("Error", "Please select a valid download format.")
    else:
        print("Selected format:", selected_format)
        # messagebox.showinfo("Success", f"File is downloaded successfully in the download folder in {selected_format} format.")



def open_download_popup():
    popup = tk.Toplevel(window)
    popup.title("Download Data")
    popup.geometry("300x150")
    popup.resizable(False, False)

    popup_label = tk.Label(popup, text="Select Download Format:")
    popup_label.pack()

    popup_options = ["Select Action", "Download as Excel", "Download as CSV", "Download as SQL database file"]
    popup_selected_format_var = tk.StringVar()
    popup_selected_format_var.set(popup_options[0])

    popup_dropdown = ttk.OptionMenu(popup, popup_selected_format_var, *popup_options)
    popup_dropdown.pack()

    def download_selected_format_popup():
        selected_format_popup = popup_selected_format_var.get()
        if selected_format_popup == "Select Action":
            messagebox.showerror("Error", "Please select a valid download format.")
            
        elif selected_format_popup == "Download as Excel":
            download_master_df_excel()
            # messagebox.showinfo("Success", "Database File is Successfully Saved into Download Folder in Excel format")
            popup.destroy()
        
        elif selected_format_popup == "Download as CSV":
            download_master_df_csv()
            # messagebox.showinfo("Success", "Database File is Successfully Saved into Download Folder in CSV format")
            popup.destroy()
            
        else:
            download_master_df_sqlite()
            # messagebox.showinfo("Success", "Database File is Successfully Saved into Download Folder in SQL Database format")
            popup.destroy()


    popup_download_button = tk.Button(popup,text="DOWNLOAD", fg="white", bg="#4CAF50", cursor="hand2", relief=tk.RAISED, bd=4, highlightthickness=0, highlightbackground="#3D8B37", highlightcolor="#3D8B37", command=download_selected_format_popup)
    popup_download_button.pack(padx=(10, 10))



def show_sample():
    # Create a new top-level window for the sample table
    sample_window = tk.Toplevel(window)
    sample_window.title("Sample Data")
    sample_window.geometry("1400x300")

    # Sample data from the provided image

    df = access_sql_db().head(20)

    # Create a Treeview widget
    tree = ttk.Treeview(sample_window, columns=list(df.columns), show='headings')
    tree.pack(expand=True, fill=tk.BOTH)

    # Define the column headings
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Insert the data into the Treeview
    for index, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))


###===================|| Upload Data ||===================###

def insert_dataframe_in_chunks(df, conn, table_name, chunk_size=500):
    cursor = conn.cursor()
    for start in range(0, len(df), chunk_size):
        end = start + chunk_size
        chunk = df.iloc[start:end]
        chunk.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
    conn.commit()
    
    
def upload_csv_to_db(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"The file '{file_path}' does not exist.")
        return

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Check if the 'Retailers' column has missing values
        if df['Retailers'].isnull().any():
            messagebox.showerror("Error", "Some records have missing values in the 'Retailers' column.")
            return

        # Connect to the SQLite database
        conn = sqlite3.connect('sales_data.db')

        # Insert the data into the database in chunks
        insert_dataframe_in_chunks(df, conn, 'sales_data')

        # Close the connection
        conn.close()

        messagebox.showinfo("Success", "CSV file uploaded to the database successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def upload_excel_to_db(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"The file '{file_path}' does not exist.")
        return

    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)

        # Check if the 'Retailers' column has missing values
        if df['Retailers'].isnull().any():
            messagebox.showerror("Error", "Some records have missing values in the 'Retailers' column.")
            return

        # Connect to the SQLite database
        conn = sqlite3.connect('sales_data.db')

        # Insert the data into the database in chunks
        insert_dataframe_in_chunks(df, conn, 'sales_data')

        # Close the connection
        conn.close()

        messagebox.showinfo("Success", "Excel file uploaded to the database successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def open_upload_popup():
    messagebox.showwarning("Warning", "Make sure to Upload file in Template format only")
    popup = tk.Toplevel(window)
    popup.title("Data Upload")
    popup.geometry("300x150")
    popup.resizable(False, False)

    popup_label = tk.Label(popup, text="Select Upload Option:")
    popup_label.pack()

    popup_options = ["Select Action", "Upload CSV file", "Upload Excel file", "Upload Manually", "Refresh Master Excel File"]
    popup_selected_option_var = tk.StringVar()
    popup_selected_option_var.set(popup_options[0])

    popup_dropdown = ttk.OptionMenu(popup, popup_selected_option_var, *popup_options)
    popup_dropdown.pack()

    def upload_selected_option_popup():
        selected_option_popup = popup_selected_option_var.get()
        if selected_option_popup == "Select Action":
            messagebox.showerror("Error", "Please select a valid upload option.")
        else:
            print("Selected option (Popup):", selected_option_popup)
            if selected_option_popup == "Upload CSV file":
                # Open a file dialog to select the CSV file
                file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
                if file_path:
                    # Call the upload_csv_to_db function with the selected file path
                    upload_csv_to_db(file_path)
            elif selected_option_popup == "Upload Excel file":
                # Open a file dialog to select the Excel file
                file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
                if file_path:
                    # Call the upload_excel_to_db function with the selected file path
                    upload_excel_to_db(file_path)
            elif selected_option_popup == "Refresh Master Excel File":
                messagebox.showinfo("Success", "Database is updated with new data successfully.")
            else:
                messagebox.showinfo("Success", "Manually uploaded data is inserted into the database successfully.")
            popup.destroy()


    popup_upload_button = tk.Button(popup, text="Upload", command=upload_selected_option_popup, bg="#4CAF50", fg="white", font=("Arial", 12), relief=tk.RAISED, bd=4, highlightthickness=0, highlightbackground="#3D8B37", highlightcolor="#3D8B37")
    popup_upload_button.pack(side=tk.LEFT, padx=(10, 10), pady=20)

    show_sample_button = tk.Button(popup, text="Show Template Sample", command=show_sample, bg="#008CBA", fg="white", font=("Arial", 12), relief=tk.RAISED, bd=4, highlightthickness=0, highlightbackground="#005F7F", highlightcolor="#005F7F")
    show_sample_button.pack(side=tk.RIGHT, padx=(10, 10), pady=20)


###===============================||Database Analysis||=======================###



def analyze_database(option):
    conn = sqlite3.connect('sales_data.db')
    df = pd.read_sql_query("SELECT * FROM sales_data", conn)
    
    analysis_result_names = ""
    analysis_result_counts = ""
    
    if option == "Shape of database":
        analysis_result_names = str(df.shape)
        
    elif option == "Unique retailers":
        unique_retailers = df['Retailers'].str.upper().unique()
        analysis_result_names = unique_retailers
        analysis_result_counts = len(unique_retailers)
        
    elif option == "All columns":
        analysis_result_names = df.columns.tolist()
        
        
    elif option == "Missing values":
        analysis_result_names = df.isnull().sum().reset_index().values.tolist()
    
    elif option == "Unique Values":
        analysis_result_names = df.nunique().reset_index().values.tolist()
    
    else:
        analysis_result_names = "Invalid option selected."
        analysis_result_counts = None  # Set counts to None for other options

    conn.close()

    # Create a new window to display the result
    result_window = tk.Toplevel(window)
    result_window.title("Analysis Result")
    result_window.geometry("600x400")

    if option in ["Missing values", "Unique Values"]:
        
        columns = ["Column", "Value"]
        tree = ttk.Treeview(result_window, columns=columns, show="headings")
        tree.heading("Column", text="Column")
        tree.heading("Value", text="Value")
        for item in analysis_result_names:
            tree.insert("", "end", values=item)
        tree.pack(fill=tk.BOTH, expand=True)
    else:
        result_label_names = tk.Label(result_window, text=str(analysis_result_names), wraplength=550, justify=tk.LEFT)
        result_label_names.pack(pady=10)
        if option == "Unique retailers":  # Display counts only for unique retailers
            result_label_counts = tk.Label(result_window, text=f"Number of unique retailers: {analysis_result_counts}")
            result_label_counts.pack(pady=10)

def open_analysis_popup():
    popup = tk.Toplevel(window)
    popup.title("Database Analysis")
    popup.geometry("300x150")
    popup.resizable(False, False)

    popup_label = tk.Label(popup, text="Select Analysis Option:")
    popup_label.pack()

    popup_options = ["Select Action", "Shape of database", "Unique retailers", "All columns",  "Missing values", "Unique Values"]
    popup_selected_option_var = tk.StringVar()
    popup_selected_option_var.set(popup_options[0])

    popup_dropdown = ttk.OptionMenu(popup, popup_selected_option_var, *popup_options)
    popup_dropdown.pack()

    def analyze_selected_option():
        selected_option = popup_selected_option_var.get()
        if selected_option != "Select Action":
            analyze_database(selected_option)
            popup.destroy()
        else:
            tk.messagebox.showwarning("Warning", "Please select a valid action.")

    analyze_button = tk.Button(popup, text="Analyze", command=analyze_selected_option, bg="#4CAF50", fg="white", font=('Helvetica', 14, 'bold'), relief='raised', bd=5)
    analyze_button.pack(pady=20)

## =================||Handle Duplicate||==================##

# Function to handle duplicates
def handle_duplicates():
    df = access_sql_db()
    duplicates = df[df.duplicated()]

    def delete_duplicates():
        nonlocal df
        df = df.drop_duplicates()
        # Connect to SQLite database
        db_file = 'sales_data.db'
        conn = sqlite3.connect(db_file)
        # Replace the data in the table
        df.to_sql('sales_data', conn, if_exists='replace', index=False)
        # Commit and close the connection
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Duplicate values deleted successfully")
        duplicate_count_label.config(text=f"Duplicate Values: {df.duplicated().sum()}")

    def download_duplicates_to_excel():
        home = Path.home()
        download_dir = home / "Downloads"
        os.makedirs(download_dir, exist_ok=True)
        file_path = download_dir / "duplicates.xlsx"
        duplicates.to_excel(file_path, index=False)
        messagebox.showinfo("Success", f"Duplicates downloaded to {file_path}")

    def show_duplicates():
        show_popup = tk.Toplevel(popup)
        show_popup.title("Duplicate Entries")
        show_popup.geometry("800x600")
        
        cols = list(duplicates.columns)
        tree = ttk.Treeview(show_popup, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        for index, row in duplicates.iterrows():
            tree.insert("", "end", values=list(row))
        
        tree.pack(expand=True, fill='both')

    popup = tk.Toplevel(window)
    popup.title("Handle Duplicates")
    popup.geometry("300x300")
    popup.resizable(False, False)

    duplicate_count_label = tk.Label(popup, text=f"Duplicate Values: {duplicates.shape[0]}")
    duplicate_count_label.pack(pady=10)

    show_button = tk.Button(popup, text="Show Duplicates", command=show_duplicates, bg="#1E90FF", fg="white", font=("Arial", 12, "bold"))
    show_button.pack(pady=10, ipadx=10, ipady=5)

    delete_button = tk.Button(popup, text="Delete Duplicates", command=delete_duplicates, bg="#FF6347", fg="white", font=("Arial", 12, "bold"))
    delete_button.pack(pady=10, ipadx=10, ipady=5)

    download_button = tk.Button(popup, text="Download Duplicates", command=download_duplicates_to_excel, bg="#32CD32", fg="white", font=("Arial", 12, "bold"))
    download_button.pack(pady=10, ipadx=10, ipady=5)

## =================||Functions Are Above||==================##


###=================|| Create main window Below ||==================###
window = tk.Tk()
window.title("Sales Data Management")
window.configure(bg="black")

# Set window size
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry("800x600")

# Define font for buttons
bold_font = tk.font.Font(family="Helvetica", size=24, weight="bold")

# Add buttons to the window
download_button = tk.Button(window, text="DOWNLOAD DATA", fg="white", bg="green", font=bold_font, cursor="hand2", command=open_download_popup, relief='raised', bd=5)
download_button.pack(pady=20)

upload_button = tk.Button(window, text="Upload Data to Database", fg="white", bg="blue", font=bold_font, cursor="hand2", command=open_upload_popup, relief='raised', bd=5)
upload_button.pack(pady=20)

database_analysis_button = tk.Button(window, text="Database Analysis", fg="white", bg="#008CBA", font=bold_font, cursor="hand2", command=open_analysis_popup, relief='raised', bd=5)
database_analysis_button.pack(pady=20)

handle_duplicates_button = tk.Button(window, text="Handle Duplicates", command=handle_duplicates, bg="#4682B4", fg="white", font=("Arial", 14, "bold"), cursor="hand2", relief='raised', bd=5)
handle_duplicates_button.pack(pady=20, ipadx=20, ipady=10)

# Place the Database button at the bottom-right corner
create_database_button = tk.Button(window, text="Database", command=create_sqlite_db, bg="#008CBA", fg="white", font=("Arial", 12, "bold"), relief='raised', bd=4, cursor="hand2")
create_database_button.pack(side=tk.RIGHT, padx=10, pady=20)

# Start the Tkinter event loop
window.mainloop()
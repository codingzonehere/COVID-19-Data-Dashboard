##############################################################################################################
############################# Dhaka University of Engineering & Technology, Gazipur ##########################
###################################### Project Name: COVID-19 Data Dashboard #################################
############################################ Student Name: Tanvir Ahmed ######################################
################################################## ID: 2204078 ###############################################
## Description: Students can create a dashboard that collects and visualizes COVID-19 data using an API. #####
## The project could include visualizations of cases, recoveries, and vaccinations over time in different ####
#################################################### countries ###############################################
################# Skills Used: API, Pandas, Matplotlib/Seaborn, File Handling, Data Structures. ##############
##############################################################################################################
import requests
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

# Global variables
df = None
filtered_data = None
filter_type = None  # Tracks the type of filter applied (date_range, specific_date, year)

# Function to fetch COVID-19 data from API for a specific country
def fetch_country_data(country):
    url = f"https://disease.sh/v3/covid-19/historical/{country}?lastdays=all"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['timeline']
    else:
        print(f"Error fetching data for {country}. Status code: {response.status_code}")
        return None

# Function to process the data and save it to a CSV file
def save_data_to_csv(country, data):
    cases = pd.DataFrame.from_dict(data['cases'], orient='index', columns=['cases'])
    deaths = pd.DataFrame.from_dict(data['deaths'], orient='index', columns=['deaths'])
    recovered = pd.DataFrame.from_dict(data['recovered'], orient='index', columns=['recovered'])

    # Check if 'vaccinated' data exists, if not, set to None
    vaccinations = pd.DataFrame.from_dict(data.get('vaccinated', {}), orient='index', columns=['vaccinations'])
    
    # If vaccination data is not available, fill with 0 or forward fill
    if vaccinations.empty:
        vaccinations = pd.DataFrame(index=cases.index, columns=['vaccinations'])
        vaccinations['vaccinations'] = 0  # Filling with 0, or use .ffill() for forward fill

    # Merge the dataframes
    df = pd.concat([cases, deaths, recovered, vaccinations], axis=1)
    df.index = pd.to_datetime(df.index)
    df = df.reset_index().rename(columns={"index": "date"})
    
    # Save the dataframe to a CSV file
    file_name = f"{country}_covid_data.csv"
    df.to_csv(file_name, index=False)
    print(f"Data for {country} has been saved to {file_name}.")

# Function to load COVID-19 data from a CSV file for a specific country
def load_country_data_from_csv(country):
    global df
    try:
        # Load the CSV file into a DataFrame (adjust the file path as needed)
        df = pd.read_csv(f"{country}_covid_data.csv")
        df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' column is in datetime format
        print(f"Data for {country} loaded from CSV.")
        return df
    except FileNotFoundError:
        messagebox.showerror("Error", f"CSV file for {country} not found.")
        return None

# Filter data by date range
def filter_by_date_range(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# Filter data by a specific date
def filter_by_specific_date(df, specific_date):
    specific_date = pd.to_datetime(specific_date)
    return df[df['date'] == specific_date]

# Filter data by a specific year
def filter_by_year(df, year):
    df['year'] = df['date'].dt.year
    return df[df['year'] == year]

# Visualize data with country name in the title
def plot_covid_trends(df, title, country):
    if df.empty:
        messagebox.showinfo("No Data", "No data available to plot.")
        return
    
    plt.figure(figsize=(12, 6))
    
    # Plot each trend
    plt.plot(df['date'], df['cases'], label='Cases', color='blue', linestyle='-', linewidth=2)
    plt.plot(df['date'], df['recovered'], label='Recoveries', color='green', linestyle='-', linewidth=2)
    plt.plot(df['date'], df['deaths'], label='Deaths', color='red', linestyle='-', linewidth=2)
    plt.plot(df['date'], df['vaccinations'], label='Vaccinations', color='purple', linestyle='-', linewidth=2)

    # Prepare the title based on the filtering
    if filter_type == "date_range":
        title = f"{title} for {country.title()} (Date Range: {df['date'].min().date()} to {df['date'].max().date()})"
    elif filter_type == "specific_date":
        title = f"{title} for {country.title()} (Specific Date: {df['date'].iloc[0].date()})"
    elif filter_type == "year":
        title = f"{title} for {country.title()} (Year: {df['date'].dt.year.iloc[0]})"
    else:
        title = f"{title} for {country.title()}"

    # Set the title and labels
    plt.title(title, fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Counts", fontsize=12)

    # Rotate date labels for better visibility
    plt.xticks(rotation=45)

    # Add grid, legend, and improve layout
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    # Tighten layout to ensure everything fits
    plt.tight_layout()

    # Show the plot
    plt.show()

# Tkinter GUI application
def run_dashboard():
    def search_country():
        global df  # Make df global so it's accessible across functions
        country = country_entry.get().strip().lower()
        if not country:
            messagebox.showwarning("Input Error", "Please enter a country name.")
            return

        # Check if CSV file exists
        try:
            df = pd.read_csv(f"{country}_covid_data.csv")
            df['date'] = pd.to_datetime(df['date'])
            messagebox.showinfo("Success", f"Data for {country.title()} is already available.")
        except FileNotFoundError:
            # Fetch the data if CSV doesn't exist
            data = fetch_country_data(country)
            if data:
                save_data_to_csv(country, data)
                df = pd.read_csv(f"{country}_covid_data.csv")
                df['date'] = pd.to_datetime(df['date'])
                messagebox.showinfo("Success", f"Data for {country.title()} loaded and saved.")
            else:
                messagebox.showerror("Error", f"No data available for country '{country}'. Please check the spelling.")
                return
        
        # Enable filter option selection
        option_label.pack(pady=10)
        date_range_button.pack(pady=5)
        specific_date_button.pack(pady=5)
        year_button.pack(pady=5)

    def choose_date_range():
        for widget in input_frame.winfo_children():
            widget.destroy()

        tk.Label(input_frame, text="Enter Start Date (YYYY-MM-DD):").pack(pady=5)
        start_date_entry = tk.Entry(input_frame, width=20)
        start_date_entry.pack(pady=5)

        tk.Label(input_frame, text="Enter End Date (YYYY-MM-DD):").pack(pady=5)
        end_date_entry = tk.Entry(input_frame, width=20)
        end_date_entry.pack(pady=5)

        def apply_date_range():
            global filter_type
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            if not start_date or not end_date:
                messagebox.showwarning("Input Error", "Please enter both start and end dates.")
                return

            try:
                df_filtered = filter_by_date_range(df, start_date, end_date)
                if df_filtered.empty:
                    messagebox.showinfo("No Data", "No data available for the selected date range.")
                    return

                # Display total quantities
                display_totals(df_filtered)

                # Enable Show Graph button after applying the filter
                show_graph_button.pack(pady=10)

                # Store filtered data for later use in plotting
                global filtered_data
                filtered_data = df_filtered
                filter_type = "date_range"  # Track that date range filter is applied
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        tk.Button(input_frame, text="Apply", command=apply_date_range).pack(pady=10)

    def choose_specific_date():
        for widget in input_frame.winfo_children():
            widget.destroy()

        tk.Label(input_frame, text="Enter Specific Date (YYYY-MM-DD):").pack(pady=5)
        specific_date_entry = tk.Entry(input_frame, width=20)
        specific_date_entry.pack(pady=5)

        def apply_specific_date():
            global filter_type
            specific_date = specific_date_entry.get().strip()
            if not specific_date:
                messagebox.showwarning("Input Error", "Please enter a specific date.")
                return

            try:
                df_filtered = filter_by_specific_date(df, specific_date)
                if df_filtered.empty:
                    messagebox.showinfo("No Data", "No data available for the selected date.")
                    return

                # Display total quantities
                display_totals(df_filtered)

                # Enable Show Graph button after applying the filter
                show_graph_button.pack(pady=10)

                # Store filtered data for later use in plotting
                global filtered_data
                filtered_data = df_filtered
                filter_type = "specific_date"  # Track that specific date filter is applied
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        tk.Button(input_frame, text="Apply", command=apply_specific_date).pack(pady=10)

    def choose_year():
        for widget in input_frame.winfo_children():
            widget.destroy()

        tk.Label(input_frame, text="Enter Year (e.g., 2020):").pack(pady=5)
        year_entry = tk.Entry(input_frame, width=20)
        year_entry.pack(pady=5)

        def apply_year():
            global filter_type
            year = year_entry.get().strip()
            if not year:
                messagebox.showwarning("Input Error", "Please enter a year.")
                return

            try:
                df_filtered = filter_by_year(df, int(year))
                if df_filtered.empty:
                    messagebox.showinfo("No Data", f"No data available for the year {year}.")
                    return

                # Display total quantities
                display_totals(df_filtered)

                # Enable Show Graph button after applying the filter
                show_graph_button.pack(pady=10)

                # Store filtered data for later use in plotting
                global filtered_data
                filtered_data = df_filtered
                filter_type = "year"  # Track that year filter is applied
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        tk.Button(input_frame, text="Apply", command=apply_year).pack(pady=10)

    # Display total quantities in the GUI
    def display_totals(df):
        total_cases = df['cases'].sum()
        total_deaths = df['deaths'].sum()
        total_recovered = df['recovered'].sum()
        total_vaccinations = df['vaccinations'].sum()

        # Update the labels with total values
        total_cases_label.config(text=f"Total Cases: {total_cases:,}", fg="blue")
        total_deaths_label.config(text=f"Total Deaths: {total_deaths:,}", fg="red")
        total_recovered_label.config(text=f"Total Recovered: {total_recovered:,}", fg="green")
        total_vaccinations_label.config(text=f"Total Vaccinations: {total_vaccinations:,}", fg="purple")

        # Show the totals (hide until Apply button is clicked)
        totals_frame.pack(pady=10)

    # Show Graph button functionality
    def show_graph():
        global filtered_data  # Make filtered_data accessible here
        if filtered_data is not None and not filtered_data.empty:
            # Add title and display the graph with the selected filter dates
            country = country_entry.get().strip()
            plot_covid_trends(filtered_data, "COVID-19 Data", country)
        else:
            messagebox.showinfo("No Data", "Please apply a filter before plotting.")

    # Create the main window
    root = tk.Tk()
    root.title("COVID-19 Data Dashboard")

    # Step 1: Search Box
    tk.Label(root, text="Enter the name of the country (e.g., 'India', 'USA'):").pack(pady=5)
    country_entry = tk.Entry(root, width=30)
    country_entry.pack(pady=5)
    tk.Button(root, text="Search", command=search_country).pack(pady=10)

    # Step 2: Option Selection
    option_label = tk.Label(root, text="Choose an option:")
    date_range_button = tk.Button(root, text="Filter by Date Range", command=choose_date_range)
    specific_date_button = tk.Button(root, text="Filter by Specific Date", command=choose_specific_date)
    year_button = tk.Button(root, text="Filter by Specific Year", command=choose_year)

    # Step 3: Input Dates (Dynamic Frame)
    input_frame = tk.Frame(root)
    input_frame.pack(pady=20)

    # Step 4: Display Totals Section (Initially hidden)
    totals_frame = tk.Frame(root)

    total_cases_label = tk.Label(totals_frame, text="Total Cases: ", font=("Arial", 12))
    total_cases_label.grid(row=0, column=0, pady=5)

    total_deaths_label = tk.Label(totals_frame, text="Total Deaths: ", font=("Arial", 12))
    total_deaths_label.grid(row=1, column=0, pady=5)

    total_recovered_label = tk.Label(totals_frame, text="Total Recovered: ", font=("Arial", 12))
    total_recovered_label.grid(row=2, column=0, pady=5)

    total_vaccinations_label = tk.Label(totals_frame, text="Total Vaccinations: ", font=("Arial", 12))
    total_vaccinations_label.grid(row=3, column=0, pady=5)

    # Show Graph button
    show_graph_button = tk.Button(root, text="Show Graph", command=show_graph)
    
    # Start the Tkinter event loop
    root.mainloop()

# Run the dashboard (Tkinter GUI)
run_dashboard()

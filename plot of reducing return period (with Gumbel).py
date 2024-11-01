import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to load and process the GCM data
def load_gcm_data(file_paths, scenario_column):
    """
    Loads GCM data from multiple files and returns a dataframe with ensemble average.
    
    Args:
    file_paths (list of str): Paths to GCM data files.
    scenario_column (str): The column name of the scenario to use (e.g., 'Flow SSP585' or 'Flow SSP245').
    
    Returns:
    pd.DataFrame: Ensemble-averaged flow data.
    """
    # Initialize an empty list to hold individual GCM dataframes
    gcm_dataframes = []

    # Load each GCM data file into a pandas DataFrame and append it to the list
    for file_path in file_paths:
        gcm_df = pd.read_excel(file_path)
        gcm_df['Date'] = pd.to_datetime(gcm_df['Date'])  # Convert 'Date' to datetime
        gcm_dataframes.append(gcm_df[['Date', scenario_column]])

    # Concatenate all GCM data along the columns (align by 'Date')
    ensemble_data = pd.DataFrame({'Date': gcm_dataframes[0]['Date']})  # Start with the date column
    ensemble_data['Ensemble_Flow'] = sum(df[scenario_column] for df in gcm_dataframes) / len(gcm_dataframes)  # Ensemble average

    return ensemble_data

# Function to separate data by time periods
def split_by_periods(data):
    """
    Splits the ensemble data into baseline, near future, mid future, and far future periods.
    
    Args:
    data (pd.DataFrame): Dataframe with 'Date' and 'Ensemble_Flow'.
    
    Returns:
    dict: Dictionary containing separated periods.
    """
    periods = {
        'Baseline (1984-2014)': data[(data['Date'] >= '1984-01-01') & (data['Date'] <= '2014-12-31')],
        'Near Future (2015-2040)': data[(data['Date'] >= '2015-01-01') & (data['Date'] <= '2040-12-31')],
        'Mid Future (2041-2071)': data[(data['Date'] >= '2041-01-01') & (data['Date'] <= '2071-12-31')],
        'Far Future (2070-2100)': data[(data['Date'] >= '2070-01-01') & (data['Date'] <= '2100-12-31')]
    }
    return periods

# Function to calculate the annual maximum flows for each period
def calculate_annual_max(periods):
    """
    Calculate the annual maximum flow for each time period.
    
    Args:
    periods (dict): Dictionary of periods with 'Date' and 'Ensemble_Flow'.
    
    Returns:
    dict: Dictionary of annual maximum flows.
    """
    annual_max_flows = {period: df.groupby(df['Date'].dt.year).max()['Ensemble_Flow'] for period, df in periods.items()}
    return annual_max_flows

# Function to fit Gumbel distribution and plot the return periods
def fit_gumbel_and_plot(annual_max_flows):
    """
    Fits the Gumbel distribution and plots return periods for each time period.
    
    Args:
    annual_max_flows (dict): Dictionary containing annual maximum flows for each period.
    """
    plt.figure(figsize=(10, 6))
    
    for period, max_flows in annual_max_flows.items():
        sorted_flows = np.sort(max_flows)
        exceedance_probabilities = 1 - np.arange(1, len(sorted_flows) + 1) / (len(sorted_flows) + 1)
        return_periods = 1 / exceedance_probabilities
        plt.plot(return_periods, sorted_flows, label=period)
        
    
    plt.xscale('log')
    plt.title('Extreme Scenario',fontsize=15)
    plt.xlabel('Return Period (years)',fontsize=14)
    plt.ylabel('Flow (m³/s)',fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=13,loc='upper left')
    plt.show()

# Main function to execute the workflow
def main(scenario='SSP585'):
    """
    Main function to calculate and plot return periods for a given scenario.
    
    Args:
    scenario (str): Scenario to analyze ('SSP585' or 'SSP245').
    """
    # Define the file paths for the GCMs
    file_paths = [
         "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble\Amalshid Simulation Flow data/BCC-CSM2-MR.xlsx",
         "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble\Amalshid Simulation Flow data/MPI-ESM1-2-HR.xlsx",
         "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble\Amalshid Simulation Flow data/MPI-ESM1-2-LR.xlsx",
         "D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\ACCESS-CM2.xlsx",
         "D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\ACCESS-ESM1-5.xlsx",
         "D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\CanESM5.xlsx",
         "D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\EC-Earth3.xlsx",
         "D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\EC-Earth3-Veg.xlsx",
         r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\INM-CM4-8.xlsx",
         r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\INM-CM5-0.xlsx",
         r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\MRI-ESM2-0.xlsx",
         r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\NorESM2-LM.xlsx",
         r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\NorESM2-MM.xlsx"
    ]
    
    # Choose the scenario column based on the selected scenario
    scenario_column = f"Flow {scenario}"
    
    # Load and process the GCM data for the chosen scenario
    ensemble_data = load_gcm_data(file_paths, scenario_column)
    
    # Split the data into time periods
    periods = split_by_periods(ensemble_data)
    
    # Calculate annual maximum flows for each period
    annual_max_flows = calculate_annual_max(periods)
    
    # Fit Gumbel distribution and plot return periods
    fit_gumbel_and_plot(annual_max_flows)

# Run the main function for SSP5-8.5 scenario
if __name__ == '__main__':
    main(scenario='SSP585')  # Change to 'SSP245' for the other scenario

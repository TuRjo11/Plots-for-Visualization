import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"
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

# Function to calculate the Flow Duration Curve (FDC)
def calculate_fdc(flow_data):
    """
    Calculate the flow duration curve (FDC) for a given flow time series.
    
    Args:
    flow_data (pd.Series): Time series of flow values.
    
    Returns:
    (pd.Series, pd.Series): Sorted flow data and the corresponding exceedance probabilities.
    """
    sorted_flows = flow_data.sort_values(ascending=False).reset_index(drop=True)
    exceedance_probability = (sorted_flows.index + 1) / len(sorted_flows) * 100
    return sorted_flows, exceedance_probability

# Function to plot FDC for each time period
def plot_fdc(periods):
    """
    Plots Flow Duration Curves (FDC) for each time period.
    
    Args:
    periods (dict): Dictionary of time periods with 'Date' and 'Ensemble_Flow'.
    """
    plt.figure(figsize=(10, 6),dpi=300)
    
    for period, df in periods.items():
        sorted_flows, exceedance_prob = calculate_fdc(df['Ensemble_Flow'])
        plt.plot(exceedance_prob, sorted_flows, label=period)
        
    plt.xlabel('Exceedance Probability (%)')
    plt.ylabel('Flow (m³/s)')
    plt.title('Extreme Scenario')
    plt.legend(title="Periods", loc="best")
    plt.grid(True)
    plt.show()

# Function to split data by time periods
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

# Function to calculate Q90 and Q95
def calculate_q90_q95(flow_data):
    sorted_flows = flow_data.sort_values(ascending=False).reset_index(drop=True)
    q90_flow = sorted_flows.iloc[int(0.90 * len(sorted_flows))]
    q95_flow = sorted_flows.iloc[int(0.95 * len(sorted_flows))]
    return q90_flow, q95_flow
# Function to calculate the basic e-flow for each period and scenario
def calculate_basic_eflow(periods):
    basic_eflows = []
    
    for period_name, df in periods.items():
        q90_flow, q95_flow = calculate_q90_q95(df['Ensemble_Flow'])
        basic_eflow = (q90_flow + q95_flow) / 2  # Mean of Q90 and Q95
        basic_eflows.append(basic_eflow)
        print(f'{period_name}: Basic E-Flow = {basic_eflow}')
    
    # Calculate the mean basic e-flow across all periods
    mean_basic_eflow = sum(basic_eflows) / len(basic_eflows)
    
    return mean_basic_eflow

# Main function to execute the workflow
def main(scenario='SSP585'):
    """
    Main function to load, process, and plot FDC for GCM ensemble data.
    
    Args:
    scenario (str): Scenario to analyze ('SSP585' or 'SSP245').
    """
    # Define the file paths for the GCMs
    file_paths = [
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/BCC-CSM2-MR.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/MPI-ESM1-2-HR.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/MPI-ESM1-2-LR.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/ACCESS-CM2.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/ACCESS-ESM1-5.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/CanESM5.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/EC-Earth3.xlsx",
        "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/EC-Earth3-Veg.xlsx",
        r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/INM-CM4-8.xlsx",
        r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/INM-CM5-0.xlsx",
        r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/MRI-ESM2-0.xlsx",
        r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/NorESM2-LM.xlsx",
        r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/NorESM2-MM.xlsx"
    ]
    
    # Choose the scenario column based on the selected scenario
    scenario_column = f"Flow {scenario}"
    
    # Load and process the GCM data for the chosen scenario
    ensemble_data = load_gcm_data(file_paths, scenario_column)
    
    # Split the data into time periods
    periods = split_by_periods(ensemble_data)
    
    # Plot the Flow Duration Curves for each period
    plot_fdc(periods)
    
    # Process for both SSP245 and SSP585 scenarios
    for scenario in ['SSP245', 'SSP585']:
        scenario_column = f"Flow {scenario}"
        
        # Load and process the GCM data for the chosen scenario
        ensemble_data = load_gcm_data(file_paths, scenario_column)
        
        # Split the data into time periods
        periods = split_by_periods(ensemble_data)
        
        # Calculate and print the mean basic e-flow values for the scenario
        mean_basic_eflow = calculate_basic_eflow(periods)
        print(f'Mean Basic E-Flow for {scenario}: {mean_basic_eflow}')

# Run the main function for SSP5-8.5 scenario
if __name__ == '__main__':
    main(scenario='SSP585')  # Change to 'SSP245' for the other scenario

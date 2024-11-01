import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set font to Times New Roman for all plot elements
plt.rcParams["font.family"] = "Times New Roman"

# Define the file paths for all GCMs (add more paths as needed)
gcm_files = {
    'BCC-CSM2-MR': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/BCC-CSM2-MR.xlsx",
    'MPI-ESM1-2-HR': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/MPI-ESM1-2-HR.xlsx",
    'MPI-ESM1-2-LR': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/MPI-ESM1-2-LR.xlsx",
    'ACCESS-CM2': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/ACCESS-CM2.xlsx",
    'ACCESS-ESM1-5': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/ACCESS-ESM1-5.xlsx",
    'CanESM5': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/CanESM5.xlsx",
    'EC-Earth3': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/EC-Earth3.xlsx",
    'EC-Earth3-Veg': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/EC-Earth3-Veg.xlsx",
    'INM-CM4-8': r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/INM-CM4-8.xlsx",
    'INM-CM5-0': r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/INM-CM5-0.xlsx",
    'MRI-ESM2-0': r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/MRI-ESM2-0.xlsx",
    'NorESM2-LM': r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/NorESM2-LM.xlsx",
    'NorESM2-MM': r"D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble/Amalshid Simulation Flow data/NorESM2-MM.xlsx"
    # Add more GCM paths here
}

# Define the baseline and future periods
baseline_period = (1984, 2014)
near_future_period = (2015, 2040)
mid_future_period = (2041, 2071)
far_future_period = (2070, 2100)

# Function to calculate the mean monthly flow for a given period and scenario
def get_monthly_mean_flow(df: pd.DataFrame, period: tuple, flow_column: str) -> pd.Series:
    subset = df[(df['Year'] >= period[0]) & (df['Year'] <= period[1])]
    return subset.groupby('Month')[flow_column].mean()

# Function to load data, calculate monthly means for a specific scenario (e.g., 'Flow SSP245', 'Flow SSP585')
def load_and_process_data(flow_scenario: str):
    # Initialize a dictionary to store the monthly mean flows for each GCM
    monthly_flows = {key: {} for key in gcm_files.keys()}

    # Loop through each GCM file and calculate monthly means
    for gcm_name, file_path in gcm_files.items():
        # Load the dataset
        df = pd.read_excel(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year

        # Calculate monthly mean flow for each period based on the selected scenario
        monthly_flows[gcm_name]['baseline'] = get_monthly_mean_flow(df, baseline_period, flow_scenario)
        monthly_flows[gcm_name]['near_future'] = get_monthly_mean_flow(df, near_future_period, flow_scenario)
        monthly_flows[gcm_name]['mid_future'] = get_monthly_mean_flow(df, mid_future_period, flow_scenario)
        monthly_flows[gcm_name]['far_future'] = get_monthly_mean_flow(df, far_future_period, flow_scenario)

    return monthly_flows

# Function to calculate the ensemble mean across multiple GCMs
def calculate_ensemble_mean(monthly_flows, period_key):
    # Concatenate the monthly flows from all GCMs and calculate the mean
    ensemble_data = pd.concat([monthly_flows[gcm][period_key] for gcm in gcm_files.keys()], axis=1)
    return ensemble_data.mean(axis=1)

# Function to calculate percentage change
def calculate_percentage_change(future_flow, baseline_flow):
    return ((future_flow - baseline_flow) / baseline_flow) * 100

# Function to plot the results
def plot_scenario(flow_scenario: str):
    # Load and process data for the selected scenario
    monthly_flows = load_and_process_data(flow_scenario)

    # Calculate the ensemble means for each period
    ensemble_baseline = calculate_ensemble_mean(monthly_flows, 'baseline')
    ensemble_near_future = calculate_ensemble_mean(monthly_flows, 'near_future')
    ensemble_mid_future = calculate_ensemble_mean(monthly_flows, 'mid_future')
    ensemble_far_future = calculate_ensemble_mean(monthly_flows, 'far_future')

    # Calculate percentage changes for each future period relative to the baseline
    near_future_change = calculate_percentage_change(ensemble_near_future, ensemble_baseline)
    mid_future_change = calculate_percentage_change(ensemble_mid_future, ensemble_baseline)
    far_future_change = calculate_percentage_change(ensemble_far_future, ensemble_baseline)

    # Prepare the data for plotting
    near_future_change = near_future_change.reset_index()  # Reset the index to preserve the Month column
    near_future_change['Period'] = 'Near Future (2015-2040)'

    mid_future_change = mid_future_change.reset_index()
    mid_future_change['Period'] = 'Mid Future (2041-2070)'

    far_future_change = far_future_change.reset_index()
    far_future_change['Period'] = 'Far Future (2071-2100)'

    # Concatenate the data for plotting
    combined_changes = pd.concat([near_future_change, mid_future_change, far_future_change])

    # Melt the DataFrame for easy plotting
    combined_changes = combined_changes.reset_index().melt(id_vars=['Month', 'Period'], value_name='Percentage Change')

    # Plot the box plots
    plt.figure(figsize=(15, 8), dpi=300)

    # Define custom colors
    custom_palette = {
        'Near Future (2015-2040)': '#0FD4EF',
        'Mid Future (2041-2070)': '#1FD29F',
        'Far Future (2071-2100)': '#162BDA'}
    
    #RED PALETTE:   '#EFCD0F' '#F06616' '#D20000'
    #BLUE PALETTE:  '#0FD4EF', '#1FD29F', '#162BDA'

    sns.boxplot(x='Month', y='Percentage Change', hue='Period', data=combined_changes, palette=custom_palette)

    # Create a list of month names
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Change the x-ticks to month names
    plt.xticks(ticks=range(12), labels=month_names, rotation=45, fontsize=16)
    plt.title(f'Moderate Scenario ({flow_scenario})', fontsize=18)
    plt.ylabel('Percentage Change (%)', fontsize=17)
    plt.legend(title='Time Period',fontsize=16)
    plt.tight_layout()
    plt.show()

# Example usage: Choose a flow scenario ('Flow SSP245' or 'Flow SSP585')
plot_scenario('Flow SSP245')

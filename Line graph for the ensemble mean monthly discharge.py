import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

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
}

# Define the baseline and future periods
baseline_period = (1984, 2014)
near_future_period = (2015, 2040)
mid_future_period = (2041, 2070)
far_future_period = (2071, 2100)

# Function to calculate the mean monthly flow for a given period and flow scenario
def get_monthly_mean_flow(df: pd.DataFrame, period: tuple, flow_column: str) -> pd.Series:
    subset = df[(df['Year'] >= period[0]) & (df['Year'] <= period[1])]
    return subset.groupby('Month')[flow_column].mean()

# Function to load and process data for the selected flow scenario
def load_and_process_data(flow_scenario: str):
    # Initialize dictionaries to store the results for all GCMs
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

# Smoothing function using interpolation (for smooth plotting)
def smooth_data(x, y):
    x_new = np.linspace(x.min(), x.max(), 500)  # More points for a smoother curve
    interpolator = interp1d(x, y, kind='cubic')  # Cubic spline for smoothing
    y_smooth = interpolator(x_new)
    return x_new, y_smooth

# Function to plot the results for a selected flow scenario
def plot_scenario(flow_scenario: str):
    # Load and process data for the selected scenario
    monthly_flows = load_and_process_data(flow_scenario)

    # Calculate the ensemble means for each period
    ensemble_baseline = calculate_ensemble_mean(monthly_flows, 'baseline')
    ensemble_near_future = calculate_ensemble_mean(monthly_flows, 'near_future')
    ensemble_mid_future = calculate_ensemble_mean(monthly_flows, 'mid_future')
    ensemble_far_future = calculate_ensemble_mean(monthly_flows, 'far_future')

    # Prepare months for plotting
    months = np.array(range(1, 13))

    # Apply smoothing to each ensemble series
    baseline_x_smooth, baseline_y_smooth = smooth_data(months, ensemble_baseline.values)
    near_future_x_smooth, near_future_y_smooth = smooth_data(months, ensemble_near_future.values)
    mid_future_x_smooth, mid_future_y_smooth = smooth_data(months, ensemble_mid_future.values)
    far_future_x_smooth, far_future_y_smooth = smooth_data(months, ensemble_far_future.values)

    # Plot the smoothed line graph for the ensemble mean
    plt.figure(figsize=(13, 8), dpi=300)
    plt.plot(baseline_x_smooth, baseline_y_smooth, linestyle='--', color='black', label='Baseline (1984-2014)')
    plt.plot(near_future_x_smooth, near_future_y_smooth, color='#EFCD0F', label='Near Future (2015-2040)')
    plt.plot(mid_future_x_smooth, mid_future_y_smooth, color='#F06616', label='Mid Future (2041-2070)')
    plt.plot(far_future_x_smooth, far_future_y_smooth, color='#D20000', label='Far Future (2071-2100)')

#BLUE PELATTE: #0FDBEF, blue, 9A0FEF
#RED PELATTE:  '#EFCD0F' '#F06616' '#D20000'

    # Set the x-ticks to month names
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    plt.xticks(ticks=range(1, 13), labels=month_names, rotation=45, fontsize=16)

    # Add labels and title
    plt.title('Extreme Scenario', fontsize=20)
    plt.ylabel('Mean Monthly Discharge (m³/s)', fontsize=16)
    plt.legend(title='Time Period', fontsize=20, loc='upper left')

    # Display the plot
    plt.tight_layout()
    plt.show()

# Example usage: Choose a flow scenario ('Flow SSP245' or 'Flow SSP585')
plot_scenario('Flow SSP585')

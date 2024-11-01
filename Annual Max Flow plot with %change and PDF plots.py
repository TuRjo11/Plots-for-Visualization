import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings


# Set font to Times New Roman for all plot elements
plt.rcParams["font.family"] = "Times New Roman"

# Suppress FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)
print('FOR all GCMs')

# Define file paths for all GCMs (you can add more paths here without changing the rest of the script)
file_paths = {
    'BCC-CSM2-MR': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble\Amalshid Simulation Flow data/BCC-CSM2-MR.xlsx",
    'MPI-ESM1-2-HR': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble\Amalshid Simulation Flow data/MPI-ESM1-2-HR.xlsx",
    'MPI-ESM1-2-LR': "D:/Turjo/Model with Amalshid/Data/RESULTs/For ensemble\Amalshid Simulation Flow data/MPI-ESM1-2-LR.xlsx",
    'ACCESS-CM2':"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\ACCESS-CM2.xlsx",
    'ACCESS-ESM1-5':"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\ACCESS-ESM1-5.xlsx",
    'CanESM5':"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\CanESM5.xlsx",
    'EC-Earth3':"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\EC-Earth3.xlsx",
    'EC-Earth3-Veg':"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\EC-Earth3-Veg.xlsx",
    'INM-CM4-8':r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\INM-CM4-8.xlsx",
    'INM-CM5-0':r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\INM-CM5-0.xlsx",
    'MRI-ESM2-0':r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\MRI-ESM2-0.xlsx",
    'NorESM2-LM':r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\NorESM2-LM.xlsx",
    'NorESM2-MM':r"D:\Turjo\Model with Amalshid\Data\RESULTs\For ensemble\Amalshid Simulation Flow data\NorESM2-MM.xlsx"
    # Add more GCM file paths here as needed
}

# Define the scenarios to consider (SSP245, SSP585)
scenarios = ['SSP245', 'SSP585']

# Load the datasets and convert 'Date' to datetime, extract 'Year'
gcm_data = {}
for gcm, path in file_paths.items():
    df = pd.read_excel(path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    gcm_data[gcm] = df

# Function to group by 'Year' and calculate the annual maximum flow for each GCM scenario
def calculate_annual_max(data, scenario):
    return data.groupby('Year').max().reset_index()[['Year', f'Flow {scenario}']]

# Combine data for all GCMs for each scenario (SSP245 and SSP585)
combined_data = {}
for scenario in scenarios:
    merged_data = pd.DataFrame()
    for gcm, df in gcm_data.items():
        annual_max = calculate_annual_max(df, scenario)
        if merged_data.empty:
            merged_data = annual_max.rename(columns={f'Flow {scenario}': f'Flow {scenario}_{gcm}'})
        else:
            merged_data = pd.merge(merged_data, annual_max.rename(columns={f'Flow {scenario}': f'Flow {scenario}_{gcm}'}), on='Year')
    combined_data[scenario] = merged_data.dropna()  # Ensure no missing data

# Calculate the mean, 2.5th, and 97.5th percentiles for each scenario
ensemble_stats = {}
for scenario, df in combined_data.items():
    ensemble_stats[scenario] = {
        'mean': df.iloc[:, 1:].mean(axis=1),  # Mean of all GCMs
        '2.5th': df.iloc[:, 1:].quantile(0.025, axis=1),  # 2.5th percentile
        '97.5th': df.iloc[:, 1:].quantile(0.975, axis=1)  # 97.5th percentile
    }


# Now separate the baseline and future periods
baseline_period = (1984, 2014)
future_period_start = 2015

baseline_max_flow_ssp585 = combined_data['SSP585'][(combined_data['SSP585']['Year'] >= baseline_period[0]) & (combined_data['SSP585']['Year'] <= baseline_period[1])]
future_max_flow_ssp585 = combined_data['SSP585'][combined_data['SSP585']['Year'] >= future_period_start]
future_max_flow_ssp245 = combined_data['SSP245'][combined_data['SSP245']['Year'] >= future_period_start]

# Smoothing the percentile values using a rolling window (window size 2 years for smoothing)
for scenario in scenarios:
    ensemble_stats[scenario]['2.5th_smoothed'] = ensemble_stats[scenario]['2.5th'].rolling(window=1).mean()
    ensemble_stats[scenario]['97.5th_smoothed'] = ensemble_stats[scenario]['97.5th'].rolling(window=1).mean()

# Plotting the results with uncertainty bands
plt.figure(figsize=(13, 6))

# Plot the baseline with adjusted line thickness for SSP5-8.5
plt.plot(baseline_max_flow_ssp585['Year'], baseline_max_flow_ssp585[f'Flow SSP585_{list(gcm_data.keys())[0]}'], color='black', linewidth=1, label='Baseline (1984-2014)')

# Plot future predictions for SSP5-8.5 with uncertainty bands (smoothed percentiles)
plt.plot(future_max_flow_ssp585['Year'], ensemble_stats['SSP585']['mean'].loc[future_max_flow_ssp585.index], color='red', linewidth=1, label='Mean SSP585 (2015 onwards)')
plt.fill_between(future_max_flow_ssp585['Year'], ensemble_stats['SSP585']['2.5th_smoothed'].loc[future_max_flow_ssp585.index], ensemble_stats['SSP585']['97.5th_smoothed'].loc[future_max_flow_ssp585.index], color='red', alpha=0.12)

# Plot future predictions for SSP2-4.5 with uncertainty bands (smoothed percentiles)
plt.plot(future_max_flow_ssp245['Year'], ensemble_stats['SSP245']['mean'].loc[future_max_flow_ssp245.index], color='#6A5ACD', linewidth=1, label='Mean SSP245 (2015 onwards)')
plt.fill_between(future_max_flow_ssp245['Year'], ensemble_stats['SSP245']['2.5th_smoothed'].loc[future_max_flow_ssp245.index], ensemble_stats['SSP245']['97.5th_smoothed'].loc[future_max_flow_ssp245.index], color='blue', alpha=0.12)

# Add labels, title, and customize ticks
plt.ylabel('Annual Maximum Flow (m³/s)', fontsize=14)
plt.xticks([1984, 2014, 2100], ['1984', '2014', '2100'])

# Add vertical line to separate baseline and future
plt.axvline(x=2014, color='black', linestyle='--')

# Add custom annotations
plt.text(1995, -800, "Baseline period \n(1984-2014)", fontsize=15, ha='center')
plt.text(2060, -800, "Prediction period \n(2015-2100)", fontsize=15, ha='center')

# Add legend
plt.legend(fontsize=16, loc='upper left')

# Adjust layout and display the plot
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.show()

## CALCULATION OF THE %CHANGE OF MEAN ANNUAL MAX DISCHARGE

# Function to calculate the ensemble mean flow for a given period
def calculate_ensemble_mean_flow(df, period):
    subset = df[(df['Year'] >= period[0]) & (df['Year'] <= period[1])]
    return subset.iloc[:, 1:].mean().mean()

# Calculate ensemble mean flow for the baseline period
baseline_mean_ssp585 = calculate_ensemble_mean_flow(combined_data['SSP585'], baseline_period)
baseline_mean_ssp245 = calculate_ensemble_mean_flow(combined_data['SSP245'], baseline_period)

# Calculate ensemble mean flow for the future periods for both scenarios
future_means_ssp585 = {
    'near_future': calculate_ensemble_mean_flow(combined_data['SSP585'], (2015, 2040)),
    'mid_future': calculate_ensemble_mean_flow(combined_data['SSP585'], (2041, 2070)),
    'far_future': calculate_ensemble_mean_flow(combined_data['SSP585'], (2071, 2100))
}

future_means_ssp245 = {
    'near_future': calculate_ensemble_mean_flow(combined_data['SSP245'], (2015, 2040)),
    'mid_future': calculate_ensemble_mean_flow(combined_data['SSP245'], (2041, 2070)),
    'far_future': calculate_ensemble_mean_flow(combined_data['SSP245'], (2071, 2100))
}

# Function to calculate percentage change
def calculate_percentage_change(future_mean, baseline_mean):
    return ((future_mean - baseline_mean) / baseline_mean) * 100

# Calculate percentage change for SSP5-8.5 and SSP2-4.5
percentage_changes_ssp585 = {period: calculate_percentage_change(future_mean, baseline_mean_ssp585) for period, future_mean in future_means_ssp585.items()}
percentage_changes_ssp245 = {period: calculate_percentage_change(future_mean, baseline_mean_ssp245) for period, future_mean in future_means_ssp245.items()}

# Display the percentage change results
result_table = pd.DataFrame({
    "Time Period": ["Near Future (2015-2040)", "Mid-Future (2041-2070)", "Far Future (2071-2100)"],
    "SSP2-4.5 % Change": list(percentage_changes_ssp245.values()),
    "SSP5-8.5 % Change": list(percentage_changes_ssp585.values())
})

print(result_table)

## PLOT OF PROBABILITY DISTRIBUTION FUNCTIONS (PDFs)

# Function to get flow data for a given period
def get_flow_data_for_period(df, period, models):
    subset = df[(df['Year'] >= period[0]) & (df['Year'] <= period[1])]
    return subset[models].mean(axis=1)

# Plot KDE (Probability Density Functions)
def plot_pdf(baseline, near_future, mid_future, far_future, title, colors):
    plt.figure(figsize=(10, 6))
    sns.kdeplot(baseline, color=colors[0], label='Baseline (1984-2014)', fill=True)
    sns.kdeplot(near_future, color=colors[1], label='Near Future (2015-2040)', fill=True)
    sns.kdeplot(mid_future, color=colors[2], label='Mid Future (2041-2070)', fill=True)
    sns.kdeplot(far_future, color=colors[3], label='Far Future (2071-2100)', fill=True)
    
    plt.xlabel('Annual Maximum Flow (m³/s)', fontsize=15)
    plt.ylabel('Probability Density', fontsize=15)
    plt.title(f'{title}', fontsize=16)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.show()

# Plot PDFs for SSP scenarios
baseline_flow_ssp585 = get_flow_data_for_period(combined_data['SSP585'], baseline_period, [f'Flow SSP585_{gcm}' for gcm in file_paths])
near_future_flow_ssp585 = get_flow_data_for_period(combined_data['SSP585'], (2015, 2040), [f'Flow SSP585_{gcm}' for gcm in file_paths])
mid_future_flow_ssp585 = get_flow_data_for_period(combined_data['SSP585'], (2041, 2070), [f'Flow SSP585_{gcm}' for gcm in file_paths])
far_future_flow_ssp585 = get_flow_data_for_period(combined_data['SSP585'], (2071, 2100), [f'Flow SSP585_{gcm}' for gcm in file_paths])

baseline_flow_ssp245 = get_flow_data_for_period(combined_data['SSP245'], baseline_period, [f'Flow SSP245_{gcm}' for gcm in file_paths])
near_future_flow_ssp245 = get_flow_data_for_period(combined_data['SSP245'], (2015, 2040), [f'Flow SSP245_{gcm}' for gcm in file_paths])
mid_future_flow_ssp245 = get_flow_data_for_period(combined_data['SSP245'], (2041, 2070), [f'Flow SSP245_{gcm}' for gcm in file_paths])
far_future_flow_ssp245 = get_flow_data_for_period(combined_data['SSP245'], (2071, 2100), [f'Flow SSP245_{gcm}' for gcm in file_paths])

# Define color palettes for each scenario
red_palette_ssp585 = ['gray', '#FF7E3A', '#FF0303', '#A40000']
blue_palette_ssp245 = ['gray', '#18A3BF', '#1A7AE0', '#070796']

# Example for SSP5-8.5 (Red Palette)
plot_pdf(baseline_flow_ssp585, near_future_flow_ssp585, mid_future_flow_ssp585, far_future_flow_ssp585, title="Extreme Scenario", colors=red_palette_ssp585)

# Example for SSP2-4.5 (Blue Palette)
plot_pdf(baseline_flow_ssp245, near_future_flow_ssp245, mid_future_flow_ssp245, far_future_flow_ssp245, title="Moderate Scenario", colors=blue_palette_ssp245)

# Function to calculate the mean annual maximum flow for a given period
def calculate_mean_annual_max_flow(df, period):
    subset = df[(df['Year'] >= period[0]) & (df['Year'] <= period[1])]
    return subset.iloc[:, 1:].mean().mean()  # Average over all GCMs for the period

# Define the baseline and future periods
baseline_period = (1984, 2014)
future_periods = {
    'near_future': (2015, 2040),
    'mid_future': (2041, 2070),
    'far_future': (2071, 2100)
}

# Function to calculate the average flow for each period and scenario
def calculate_average_by_periods(df):
    averages = {}
    # Calculate mean for baseline period
    averages['baseline'] = calculate_mean_annual_max_flow(df, baseline_period)
    # Calculate mean for each future period
    for period_name, period_range in future_periods.items():
        averages[period_name] = calculate_mean_annual_max_flow(df, period_range)
    return averages

# Example: Calculate the average flow for each period for SSP585 and SSP245
average_flows_ssp585 = calculate_average_by_periods(combined_data['SSP585'])
average_flows_ssp245 = calculate_average_by_periods(combined_data['SSP245'])

# Display the results
print("Average Annual Max Flow for SSP5-8.5:")
for period, avg_flow in average_flows_ssp585.items():
    print(f"{period}: {avg_flow:.2f} m³/s")

print("\nAverage Annual Max Flow for SSP2-4.5:")
for period, avg_flow in average_flows_ssp245.items():
    print(f"{period}: {avg_flow:.2f} m³/s")

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser

# Directory containing the CSV files
data_dir = "output/gesture recordings"

# Get a sorted list of all CSV files in the directory
csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".csv")])

# Read all CSV files into a list of DataFrames
dataframes = [pd.read_csv(os.path.join(data_dir, f)) for f in csv_files]

# Max number of columns across all CSV files (subtracting the 'timestamp' and 'global_time' columns)
max_columns = max([len(df.columns) - 2 for df in dataframes])

# Initialize a subplot object with maximum columns and number of files as rows
fig = make_subplots(rows=len(csv_files), cols=max_columns)

# Loop over each DataFrame and add the data to the subplot
for i, df in enumerate(dataframes):
    col_index = 1
    for col in df.columns:
        if col not in ['timestamp', 'global_time']:
            # Create the trace
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df[col], mode='lines', name=col), row=i+1, col=col_index)
            
            # Determine the y-axis range based on column title
            if "Touch sensor" in col:
                y_axis_range = [0, 1]
            else:
                y_axis_range = [-50, 700]
            
            # Update the y-axes range
            fig.update_yaxes(range=y_axis_range, row=i+1, col=col_index)

            # Update the x-axes title
            fig.update_xaxes(title_text=f"{csv_files[i]} - {col}", row=i+1, col=col_index)
            col_index += 1


# Update layout (Optional)
fig.update_layout(height=400*len(csv_files), width=1500*max_columns, title_text="Plots")

# Write to HTML
file_path = 'output/gesture_plots.html'
fig.write_html(file_path)

# Open the file in the default web browser
webbrowser.open('file://' + os.path.realpath(file_path))

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from patsy import dmatrices
import seaborn as sns



dtype_dict = {
    "URL": "string",
    "spec_price_chf": "int64",
    "spec_listing_id": "int64",
    "attributes_counter": "int64",
    "spec_condition": "string",
    "spec_material": "string",
    "spec_hull_color": "string",
    "spec_max_person": "int64",
    "spec_drive_type": "string",
    "spec_motor": "string",
    "spec_fuel_type": "string",
    "spec_year_built": "float64",
    "spec_hull_type": "string",
    "spec_engine_year": "float64",
    "spec_ce_certification": "string",
    "spec_cabins": "int64",
    "spec_berths": "int64",
    "spec_toilet": "int64",
    "spec_water_tank_l": "float64",
    "spec_waste_tank_l": "float64",
    "spec_shower": "int64",
    "spec_engine_hours": "float64",
    "spec_trailer": "bool",
    "spec_bathrooms": "int64",
    "spec_price_negotiable": "bool",
    "spec_weight_kg": "float64",
    "spec_displacement_kg": "float64",
    "spec_draft_m": "float64",
    "spec_bridge_clearance_m": "float64",
    "spec_length_m": "float64",
    "spec_width_m": "float64",
    "spec_motor_ps": "float64",
    "spec_motor_kw": "float64",
    "spec_tank_size": "float64",
}


df = pd.read_csv('/Users/fadricampell/Desktop/HSLU/CIP02/CIP/new_structure/outputs/2025-03-28_cleaned_data.csv', dtype=dtype_dict)
print(df.head())

# Drop rows with missing price values
df = df.dropna(subset=["spec_price_chf"])

print(f'The cleaned dataset has {len(df)} Listings')
# print(df.columns)
# print(df.dtypes)
# print(df['spec_trailer'])
# print(df['spec_motor'].isna().sum())

print(df.describe(include='all'))

# Count missing values for each column
missing_counts = df.isna().sum()

# Filter out columns with no missing values (optional)
#missing_counts = missing_counts[missing_counts > 0]

# Sort by number of missing values
missing_counts = missing_counts.sort_values(ascending=False)

# Plot
# Plot
plt.figure(figsize=(10, 5))
sns.barplot(x=missing_counts.index, y=missing_counts.values, palette="viridis")

# Adjustments
plt.xticks(rotation=90)
plt.ylabel("Number of Missing Values")
plt.title("Missing Values per Column")
plt.subplots_adjust(bottom=0.5)  # Adds padding to bottom for readability
plt.show()

# In this plot we 


# Fit Ordinary Least Square Model
# Drop rows with missing price values

# Apply log transformation
df["log_spec_price_chf"] = np.log1p(df["spec_price_chf"])

# Create side-by-side plots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Original price distribution
axes[0].hist(df["spec_price_chf"], bins=30, edgecolor="black", alpha=0.7)
axes[0].set_xlabel("Price (in 1'000 CHF)")
axes[0].set_ylabel("Frequency")
axes[0].set_title("Original Price Distribution")

# Log-transformed price distribution
axes[1].hist(df["log_spec_price_chf"], bins=30, edgecolor="black", alpha=0.7)
axes[1].set_xlabel("Log(Price) (CHF)")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Log-Transformed Price Distribution")

# Adjust layout
plt.tight_layout()
plt.show()

# like this we almost have a perfectly normally distributed prices


# Use dmatrices to form regression equation, the function creates the necessary matrices
y, X = dmatrices('log_spec_price_chf ~ spec_year_built + spec_motor_ps + spec_motor_kw + spec_length_m + spec_width_m', data=df, return_type='dataframe')

# print(y[:3])
# print(X[:3])

mod = sm.OLS(y, X)
res = mod.fit()
print(res.summary())
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("********************MULTI-SOURCE SALES DATA PIPELINE & BUSINESS INSIGHTS DASHBOARD*****************************")
# Load CSV
csv_data = pd.read_csv(r"C:\Users\manasa\Downloads\flipkart_com-ecommerce_sample.csv\flipkart_com-ecommerce_sample.csv")
print("CSV Data:")
print(csv_data.head())

# Load Excel
excel_data = pd.read_excel(r"C:\Users\manasa\Downloads\flipkart_data.xlsx")
print("\nExcel Data:")
print(excel_data.head())

# Load JSON
json_data = pd.read_json(r"C:\Users\manasa\Downloads\flipkart_data.json", lines=True)
print("\nJSON Data:")
print(json_data.head())

# 🧹 Check Missing Values
print("\nMissing values in CSV Data:")
print(csv_data.isnull().sum())
print("\nMissing values in Excel Data:")
print(excel_data.isnull().sum())
print("\nMissing values in JSON Data:")
print(json_data.isnull().sum())

# 🧼 Option 1: Drop rows with missing values (if we want strict cleaning)
csv_data_cleaned = csv_data.dropna()
excel_data_cleaned = excel_data.dropna()
json_data_cleaned = json_data.dropna()

# 🧼 Option 2: Fill missing values with placeholders (if we want to preserve rows)
csv_data_filled = csv_data.fillna("\nNot Available")
excel_data_filled = excel_data.fillna("Not Available")
json_data_filled = json_data.fillna("Not Available")

#to check if the columns match across all three datasets
print("CSV Columns:", csv_data.columns)
print("Excel Columns:", excel_data.columns)
print("JSON Columns:", json_data.columns)


# 🔀 Merge datasets from multiple sources into one
combined_data = pd.concat([csv_data, excel_data, json_data], ignore_index=True)
print("\nCombined Data:")
print(combined_data.head())

# 📋 Data Types Overview
print("\n🧾 Data Types Overview:")
print(combined_data.dtypes)


# 5. Missing Value Handling (After Combining)
combined_data['retail_price'] = combined_data['retail_price'].fillna(combined_data['retail_price'].median())
combined_data['discounted_price'] = combined_data['discounted_price'].fillna(combined_data['discounted_price'].median())
combined_data['image'] = combined_data['image'].fillna("Image Not Available")
combined_data['description'] = combined_data['description'].fillna("No Description")
combined_data['brand'] = combined_data['brand'].fillna("Unknown")
combined_data['product_specifications'] = combined_data['product_specifications'].fillna("Not Specified")

#  Remove Duplicates
print(f"\n🔁 Duplicate Rows: {combined_data.duplicated().sum()}")
combined_data = combined_data.drop_duplicates()
print(f"✅ Shape after removing duplicates: {combined_data.shape}")

#  Recalculate discount
combined_data['discount'] = combined_data['retail_price'] - combined_data['discounted_price']

# --- OUTLIER CHECK ----

# Function to calculate IQR bounds
def get_iqr_bounds(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return lower_bound, upper_bound

# Calculate bounds for retail_price
lower_r, upper_r = get_iqr_bounds(combined_data['retail_price'])
# Calculate bounds for discounted_price
lower_d, upper_d = get_iqr_bounds(combined_data['discounted_price'])

# Find outliers
retail_outliers = combined_data[(combined_data['retail_price'] < lower_r) | (combined_data['retail_price'] > upper_r)]
discount_outliers = combined_data[(combined_data['discounted_price'] < lower_d) | (combined_data['discounted_price'] > upper_d)]

print(f"🔍 Outliers in 'retail_price': {len(retail_outliers)} rows")
print(f"🔍 Outliers in 'discounted_price': {len(discount_outliers)} rows")

# --- VISUALIZE OUTLIERS ---
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.boxplot(y=combined_data['retail_price'], color='skyblue')
plt.title("Boxplot of Retail Price")

plt.subplot(1, 2, 2)
sns.boxplot(y=combined_data['discounted_price'], color='lightgreen')
plt.title("Boxplot of Discounted Price")

plt.tight_layout()
plt.show()

# --- REMOVE OUTLIERS ---

# Remove outliers from both columns
cleaned_data = combined_data[
    (combined_data['retail_price'] >= lower_r) & (combined_data['retail_price'] <= upper_r) &
    (combined_data['discounted_price'] >= lower_d) & (combined_data['discounted_price'] <= upper_d)
]

print(f"\n✅ Outliers removed. Original rows: {combined_data.shape[0]}, Cleaned rows: {cleaned_data.shape[0]}")

combined_data = cleaned_data.copy()  

# Visualize cleaned data after outlier removal
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
sns.boxplot(y=combined_data['retail_price'], color='skyblue')
plt.title("Retail Price (After Outlier Removal)")
plt.subplot(1, 2, 2)
sns.boxplot(y=combined_data['discounted_price'], color='lightgreen')
plt.title("Discounted Price (After Outlier Removal)")
plt.tight_layout()
plt.show()

#---- Exploratory Data Analysis (EDA) ----
print("\n------------DataSet Info-------------------")
print(combined_data.info())
print("\n-----------Statistical Summary---------------")
print(combined_data.describe(include='all'))

#Top Products / Brands / Categories
if 'product_name' in combined_data.columns:
    print("\nTop 5 Most Frequent Products:")
    print(combined_data['product_name'].value_counts().head())
if 'brand' in combined_data.columns:
    print("\n Top Brands")
    print(combined_data['brand'].value_counts().head())

plt.figure(figsize=(12, 6))
sns.countplot(data=combined_data, y='brand', order=combined_data['brand'].value_counts().iloc[:10].index)
plt.title('Top 10 Brands')
plt.tight_layout()
plt.show()

if 'product_category_tree' in combined_data.columns:
    print("\n Top Categories")
    print(combined_data['product_category_tree'].value_counts().head())
    
#Monthly Sales Trend Analysis 
combined_data['crawl_timestamp'] = pd.to_datetime(combined_data['crawl_timestamp'], errors='coerce')
combined_data = combined_data.dropna(subset=['crawl_timestamp'])
combined_data['crawl_timestamp'] = combined_data['crawl_timestamp'].dt.tz_localize(None)
combined_data['YearMonth'] = combined_data['crawl_timestamp'].dt.to_period('M')

if 'retail_price' in combined_data.columns and 'discounted_price' in combined_data.columns:
    combined_data['discount'] = combined_data['retail_price'] - combined_data['discounted_price']
else:
    combined_data['discount'] = 0
monthly_entries = combined_data.groupby('YearMonth').size()
monthly_discount = combined_data.groupby('YearMonth')['discount'].mean()

# Plotting the monthly product entries
plt.figure(figsize=(12, 5))
monthly_entries.plot(kind='bar', color='skyblue')
plt.title("Monthly Number of Products Crawled")
plt.xlabel("Year-Month")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plotting the monthly average discount
plt.figure(figsize=(12, 5))
monthly_discount.plot(kind='line', marker='o', color='green')
plt.title("Monthly Average Discount")
plt.xlabel("Year-Month")
plt.ylabel("Average Discount (in ₹)")
plt.grid(True)
plt.tight_layout()
plt.show()

#Regional Sales Trend Analysis
if 'location' in combined_data.columns:
    regional_sales = combined_data['location'].value_counts()
    print("\n🗺️ Regional Sales Trend:")
    print(regional_sales)

    # Visualization
    regional_sales.head(10).plot(kind='bar', title='Top 10 Locations by Orders')
    plt.xlabel("Location")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
else:
    print("❌ No 'location' column found for regional trend analysis.")

#Product-wise Sales Trend Analysis

if 'product_name' in combined_data.columns:
    product_sales = combined_data['product_name'].value_counts()
    print("\n📦 Top 10 Products Sold:")
    print(product_sales.head(10))

    # Visualization
    product_sales.head(10).plot(kind='barh', title='Top 10 Products')
    plt.xlabel("Number of Orders")
    plt.ylabel("Product")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
else:
    print("❌ No 'product_name' column found for product-wise analysis.")
    

#------Final Checks--------
print("\n✅ Final Missing Values:")
print(combined_data.isnull().sum())

print("\n❌ Negative retail prices:")
print(combined_data[combined_data['retail_price'] < 0])

print("\n❌ Retail price < Discounted price:")
print(combined_data[combined_data['retail_price'] < combined_data['discounted_price']])

# 11. Export Cleaned Data
combined_data.to_csv("flipkart_cleaned_analyzed.csv", index=False)
print("\n✅ Cleaned data exported successfully.")

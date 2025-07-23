import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load Excel files
ads_df = pd.read_excel("Product-Level Ad Sales and Metrics (mapped).xlsx")
sales_df = pd.read_excel("Product-Level Total Sales and Metrics (mapped).xlsx")
eligibility_df = pd.read_excel("Product-Level Eligibility Table (mapped).xlsx")

# Step 2: Create a SQLite database
engine = create_engine("sqlite:///ecommerce_data.db")  # This creates a file 'ecommerce_data.db'

# Step 3: Save each DataFrame as a SQL table
ads_df.to_sql("ad_sales_metrics", engine, if_exists="replace", index=False)
sales_df.to_sql("total_sales_metrics", engine, if_exists="replace", index=False)
eligibility_df.to_sql("eligibility_table", engine, if_exists="replace", index=False)

print("All Excel sheets saved into 'ecommerce_data.db' as SQL tables")

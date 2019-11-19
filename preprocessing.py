import pandas as pd
airbnb_file="data/singapore-airbnb/listings.csv"
o_df = pd.read_csv(airbnb_file)
o_df = o_df.fillna(0)

import pandas as pd
airbnb_file="data/singapore-airbnb/listings.csv"
o_df = pd.read_csv(airbnb_file)
o_df = o_df.fillna(0)


# Get the address of the datasets
airbnb_file="data/singapore-airbnb/listings.csv"
michelin_one_file = "data/michelin-restaurants/one-star-michelin-restaurants.csv"
michelin_two_file = "data/michelin-restaurants/two-stars-michelin-restaurants.csv"
michelin_three_file = "data/michelin-restaurants/three-stars-michelin-restaurants.csv"
mrt_file = "data/singapore-train-stations/mrt_lrt_data.csv"

# Read the csv files and store them into pandas dataframes
o_df = pd.read_csv(airbnb_file)
m1_df = pd.read_csv(michelin_one_file)
m2_df = pd.read_csv(michelin_two_file)
m3_df = pd.read_csv(michelin_three_file)
train_stat_df = pd.read_csv(mrt_file)

# Preprocessing
# For the Airbnb data, we fill the records without reviews with zero
o_df = o_df.fillna(0)

# For the Michelin resturants, we retrieve the records located in Singapore,
# drop Nan column (zip code), add more information (how many stars the restaurant
# has won.
# We then merge the dataframes together and reindex the records. Noted that there is no restaurant in Singapore
# has won a Michelin Three-star award.
sin1 = m1_df['region']=='Singapore'
m1_df_sing = m1_df[sin1].copy()
m1_df_sing.drop("zipCode", axis=1,inplace=True)
m1_df_sing.drop("region", axis=1,inplace=True)
m1_df_sing['star'] = 1

sin2 = m2_df['region']=='Singapore'
m2_df_sing = m2_df[sin2].copy()
m2_df_sing.drop("zipCode", axis=1,inplace=True)
m2_df_sing.drop("region", axis=1,inplace=True)
m2_df_sing['star'] = 2

m_df_sing = m1_df_sing.append(m2_df_sing, ignore_index = True) 

# For the train stations, we rename the columns for a better match.
columns = ["station_name", "type", "latitude", "longitude"]
train_stat_df.columns = columns
# train_stat_df
# >>>>>>> jc-ml

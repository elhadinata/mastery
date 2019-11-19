from app.models import Michelin,Station,Df
from app import db
import pandas as pd



airbnb_file="data/singapore-airbnb/listings.csv"
michelin_one_file = "data/michelin-restaurants/one-star-michelin-restaurants.csv"
michelin_two_file = "data/michelin-restaurants/two-stars-michelin-restaurants.csv"
michelin_three_file = "data/michelin-restaurants/three-stars-michelin-restaurants.csv"
mrt_file = "data/singapore-train-stations/mrt_lrt_data.csv"

o_df = pd.read_csv(airbnb_file)
m1_df = pd.read_csv(michelin_one_file)
m2_df = pd.read_csv(michelin_two_file)
m3_df = pd.read_csv(michelin_three_file)
train_stat_df = pd.read_csv(mrt_file)


o_df = o_df.fillna(0)


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




df = o_df
for index, row in df.iterrows():
    x = [str(row[column]) for column in df]
    new_row = Df(name=x[1], host_id=x[2], host_name=x[3], neighbourhood_group=x[4],
                neighbourhood=x[5], latitude=x[6], longitude=x[7],
                room_type=x[8],price=x[9],minimum_nights=x[10],
                number_of_reviews=x[11],last_review=x[12],
                reviews_per_month=x[13], calculated_host_listings_count=x[14],
                availability_365=x[15])
    db.session.add(new_row)



######################






df = m_df_sing
for index, row in df.iterrows():
    x = [str(row[column]) for column in df]
    new_row = Michelin(name=x[0], year = x[1],latitude = x[2],
             longitude = x[3],city = x[4],cuisine = x[5],
             price = x[6],url = x[7],star = x[8])
    db.session.add(new_row)

#######################


df = train_stat_df
for index, row in df.iterrows():
    x = [str(row[column]) for column in df]
    new_row = Station(station_name=x[0], _type=x[1], latitude=x[2], longitude=x[3])
    db.session.add(new_row)
    



db.session.commit()

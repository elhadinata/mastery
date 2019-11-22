import pandas as pd
from pandas.io import sql
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import NearestNeighbors

class ML_model:
    def __init__(self):
        
        self.price_model = RandomForestRegressor(n_estimators=110, max_depth=10)
        self.knn_model = NearestNeighbors(10,100, metric='manhattan')
        self.data = pd.DataFrame(data={})
        self.geo_dict = {}
        self.ng_dict = {'North Region':0, 'Central Region':1, 
                        'East Region':2, 'West Region':3,
                        'North-East Region':4 }
        self.n_dict = {}
        self.rt_dict = {"Private room":0,"Entire home/apt":1,"Shared room":2}
        self.knn_df = pd.DataFrame(data={})
        self.train_df = pd.DataFrame(data={})
        
    def prep_price_preds(self, o_df):
        o_df['price'] = pd.to_numeric(o_df['price'])
        
        higher_b = o_df["price"].quantile(0.99)
        lower_b = o_df["price"].quantile(0.005)

        m_df = o_df[o_df['price'] <=higher_b]
        df = m_df[m_df['price'] >= lower_b].copy()
        #df.drop("id", axis=1,inplace=True)
        df.drop("host_name", axis=1,inplace=True)
        df.drop("host_id", axis=1,inplace=True)
        df.drop("last_review", axis=1,inplace=True)
        df.drop("name", axis=1,inplace=True)
        #df.drop("calculated_host_listings_count", axis=1,inplace=True)

        neighbours = list(df["neighbourhood"].unique())
        neighbours_dict = {}
        for i in range(len(neighbours)):
            neighbours_dict[neighbours[i]] = i
        self.n_dict = neighbours_dict

        room_types = []
        for index, row in df.iterrows():
            if row['room_type'] == "Private room":
                room_types.append(0)
            elif row['room_type'] == "Entire home/apt":
                room_types.append(1)
            else:
                room_types.append(2)
        df["room_type"] = room_types

        neighbourhood_groups = []
        for index, row in df.iterrows():
            if row['neighbourhood_group'] == "North Region":
                neighbourhood_groups.append(0)
            elif row['neighbourhood_group'] == "Central Region":
                neighbourhood_groups.append(1)
            elif row['neighbourhood_group'] == "East Region":
                neighbourhood_groups.append(2)
            elif row['neighbourhood_group'] == "West Region":
                neighbourhood_groups.append(3)
            else:
                neighbourhood_groups.append(4)
        df["neighbourhood_group"] = neighbourhood_groups


        neighbour_types = []
        for index, row in df.iterrows():
                neighbour_types.append(neighbours_dict[row["neighbourhood"]])
        df["neighbourhood"] = neighbour_types


        for column in df.columns:
            df[column] = pd.to_numeric(df[column])
        self.data =  df
    
    
        for index, row in self.data.iterrows(): 
            if row['neighbourhood_group'] not in self.geo_dict:
                self.geo_dict[row['neighbourhood_group']]={}
            if row['neighbourhood'] not in self.geo_dict[row['neighbourhood_group']]:
                self.geo_dict[row['neighbourhood_group']][row['neighbourhood']] = [0,0]

        for key in self.geo_dict.keys():

            t_df = self.data[self.data['neighbourhood_group'] == key]
            for neigh in self.geo_dict[key].keys():

                df = t_df[t_df['neighbourhood'] == neigh]
                self.geo_dict[key][neigh][0] = df['latitude'].mean(skipna = True) 
                self.geo_dict[key][neigh][1] = df['longitude'].mean(skipna = True)     
        
    
    
    def prep_knn_preds(self,input_rt):
        
        k_df = self.data[["latitude","longitude","room_type","price","minimum_nights"]].copy()
        rt =k_df['room_type'] ==input_rt
        
        self.knn_df = k_df[rt].copy()
        new_id = list(range(0, len(self.knn_df)))
        self.knn_df['new_id'] = new_id
        self.knn_df['latitude'] = self.knn_df['latitude']*1000
        self.knn_df['longitude'] = self.knn_df['longitude']*1000

        self.train_df = self.knn_df.copy()
        self.train_df = self.train_df.reset_index()
        self.train_df.drop("index", axis=1,inplace=True)
        self.train_df.drop("new_id", axis=1,inplace=True)
    
    
    
    
    
    
    def build_price_model(self, input_rt):
        
        rt =self.data['room_type'] ==input_rt
        
        pri_df = self.data[rt].copy()
    
    
        X = pri_df.drop("price",axis=1).values
        y = pri_df["price"].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=66)

        #model = RandomForestRegressor(n_estimators=110, max_depth=10)
        self.price_model.fit(X_train,y_train)
        
       
        #preds = self.price_model.predict(X_test)
        #print(X_test)
        #return mean_squared_error(y_test,preds)
        
    def build_knn_model(self):
        
        X = self.train_df.values
        self.knn_model.fit(X)
        
       
    def knn_prediction(self, latitude = 1.33235, longitude = 103.78521, room_type = 0,   price = 81, minumum_nights = 90):
    
        query = [[latitude*1000, longitude*1000,room_type, price, minumum_nights]]
        preds = self.knn_model.kneighbors(query, 6, return_distance=False)
        
        #result = pd.DataFrame({})
        result = []
        # for each query
        for item in preds:
            #for each result
            for ele in item:
                
                ind = self.knn_df[self.knn_df['new_id']==ele].index[0]
                result.append(ind)
                #train_df.loc[2264]
                #row = self.data.loc[ind].copy()
                #result = result.append(row,ignore_index = False)
                #print(row.to_string)
        return result
        
    def price_prediction(self, query):
                
       
      
        
        if query['neighbourhood_group'] not in self.ng_dict:
            ng = self.ng_dict["Central Region"]
        else:
            ng =  self.ng_dict[query['neighbourhood_group']]
            
        if query['neighbourhood'] not in self.n_dict:
            n = self.n_dict["Queenstown"]
        else:
            n =  self.n_dict[query['neighbourhood']]
        
        if query['latitude'] == "":
           lat = self.geo_dict[ng][n][0]
        else:
           lat =  float(query['latitude'])
           
        if query['longitude'] == "":
           lng = self.geo_dict[ng][n][1]
        else:
           lng = float(query['longitude'])
           
        if query['room_type'] == "":
           rt = 0
        else:
           rt = self.rt_dict[query['room_type']]
           
        if query['minimum_nights'] == "":
           mn = self.data["minimum_nights"].mean(skipna = True) 
        else:
           mn = int(query['minimum_nights'])  
          
           
        nr = self.data["number_of_reviews"].mean(skipna = True) 
        rpm = self.data["reviews_per_month"].mean(skipna = True) 
        chlc = self.data["calculated_host_listings_count"].mean(skipna = True)

        if query["availability_365"] == "":
        
            avai = self.data["availability_365"].mean(skipna = True)
        else:
            avai = int(query["availability_365"])
   
        query = [[ng,n,lat,lng,rt,mn,nr,rpm,chlc,avai]]

        preds = self.price_model.predict(query)
        #print(X_test)
        #return mean_squared_error(y_test,preds)
        return preds
    
   

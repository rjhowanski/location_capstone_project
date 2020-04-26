#!/usr/bin/env python
# coding: utf-8

# First importing libraries and the associated data for the assignment

# In[186]:


import numpy as np # library to handle data in a vectorized manner
import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import json # library to handle JSON files
get_ipython().system('conda install -c conda-forge geopy --yes ')
from geopy.geocoders import Nominatim 
# convert an address into latitude and longitude values
import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors
# import k-means from clustering stage
from sklearn.cluster import KMeans
get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes ')
import folium # map rendering library

print('Libraries imported.')

req = requests.get("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M")
soup = BeautifulSoup(req.content,'lxml')
table = soup.find_all('table')[0]
df = pd.read_html(str(table))
neighborhood=pd.DataFrame(df[0])


# Dropping boroughs that are 'not assigned' based on instructions of assignment

# In[187]:


indexNames = neighborhood[ neighborhood['Borough'] == 'Not assigned' ].index
# Delete these row indexes from dataFrame
neighborhood.drop(indexNames , inplace=True)
neighborhood.head()


# Characterizing the shape of the dataframe with the two cells below. 10 unique boroughs exist in the df with 103 neighborhods. 

# In[188]:


neighborhood.shape


# In[189]:


print('The dataframe has {} boroughs and {} neighborhoods.'.format(
        len(neighborhood['Borough'].unique()),
        neighborhood.shape[0]
    )
)


# Utilizing csv file for lat and long based on recommendations of lab instructions

# In[190]:


locations = pd.read_csv(r'/Users/rayhowanski/Downloads/Geospatial_Coordinates.csv')
locations.head()


# Joining lat and long information with the borough and neighborhood to make a complete df for the assignment

# In[191]:


df = neighborhood.set_index('Postal code').join(locations.set_index('Postal Code'))


# In[192]:


df.head()


# In[193]:


address = 'Toronto'

geolocator = Nominatim(user_agent="toronto_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[194]:


# create map of New York using latitude and longitude values
map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(df['Latitude'], df['Longitude'], df['Borough'], df['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# Created map with all markers displayed. Filtered markers to downtown toronto below.

# In[195]:


downtown_tor_data = df[df['Borough'] == 'Downtown Toronto'].reset_index(drop=True)
downtown_tor_data.head()


# In[196]:


address = 'Downtown Toronto'

geolocator = Nominatim(user_agent="dt_toronto")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of downtown toronto are {}, {}.'.format(latitude, longitude))


# In[197]:


# create map of Manhattan using latitude and longitude values
map_downtown = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(downtown_tor_data['Latitude'], downtown_tor_data['Longitude'], downtown_tor_data['Neighborhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_downtown)  
    
map_downtown


# In[136]:


CLIENT_ID = 'IW130FHIQXSUSN0AQR30WFPAWIFYSIP5ZKJUHN4LMFOFEHX2' # your Foursquare ID
CLIENT_SECRET = 'ULBMZ04ODQGGFL1H3XRHN5L5N5ZSF25VD4E5SY455Z5KE0KH' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# Brought in my client ID and secret above. 

# In[198]:


downtown_tor_data.loc[0, 'Neighborhood']


# In[199]:


neighborhood_latitude = downtown_tor_data.loc[0, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = downtown_tor_data.loc[0, 'Longitude'] # neighborhood longitude value

neighborhood_name = downtown_tor_data.loc[0, 'Neighborhood'] # neighborhood name

print('Latitude and longitude values of {} are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))


# In[200]:


# type your answer here
LIMIT = 100 # limit of number of venues returned by Foursquare API
radius = 500 # define radius
# create URL
url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius, 
    LIMIT)
url


# In[201]:


results = requests.get(url).json()


# identified category types of df blow

# In[204]:


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[205]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[206]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# Utilized df above to get nearby venues based on location

# In[207]:


downtown_tor_venues = getNearbyVenues(names=downtown_tor_data['Neighborhood'],
                                   latitudes=downtown_tor_data['Latitude'],
                                   longitudes=downtown_tor_data['Longitude']
                                  )


# In[208]:


print(downtown_tor_venues.shape)
downtown_tor_venues.head()


# grabed venues from neighborhoods above, and their lat and long, as well as venue category. Below counts venue by grouping neighborhoods. 

# In[209]:


downtown_tor_venues.groupby('Neighborhood').count()


# In[210]:


# one hot encoding
downtown_onehot = pd.get_dummies(downtown_tor_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
downtown_onehot['Neighborhood'] =downtown_tor_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [downtown_onehot.columns[-1]] + list(downtown_onehot.columns[:-1])
downtown_onehot = downtown_onehot[fixed_columns]

downtown_onehot.head()


# In[211]:


downtown_onehot.shape


# In[212]:


downtown_grouped = downtown_onehot.groupby('Neighborhood').mean().reset_index()
downtown_grouped


# In[213]:


downtown_grouped.shape


# split out top 5 venues below from grouped data above

# In[214]:


num_top_venues = 5

for hood in downtown_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = downtown_grouped[downtown_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# In[215]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[216]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = downtown_grouped['Neighborhood']

for ind in np.arange(downtown_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(downtown_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# In[217]:


# set number of clusters
kclusters = 5

downtown_grouped_clustering = downtown_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(downtown_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# created clusters of 5 for application to downtown groupings

# In[218]:


# add clustering labels
neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

downtown_merged = downtown_tor_data

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
downtown_merged = downtown_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

downtown_merged.head() # check the last columns!


# cluster label identifies the cluster associated with the neighborhoods in downtown toronto

# In[219]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(downtown_merged['Latitude'], downtown_merged['Longitude'], downtown_merged['Neighborhood'], downtown_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# the final map displays the clusters assigned to the neighborhoods. 
# The green cluster displays the dense areas in the center,
# followed by the a layer (red markers)outside the green
# markers. There are three unique clusters scattered 
# in the outskirts of downtown toronto. 

# In[ ]:





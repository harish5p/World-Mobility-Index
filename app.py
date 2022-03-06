import pandas as pd
import streamlit as st
import nasdaqdatalink

# Get the mobility data
df_apple = pd.read_csv('https://raw.githubusercontent.com/ActiveConclusion/COVID19_mobility/master/apple_reports/applemobilitytrends.csv')
# Filter only geo_type of country/region
df_apple = df_apple[df_apple['geo_type'] == 'country/region']
# Filter the transportation_type to be 'driving'
df_apple = df_apple[df_apple['transportation_type'] == 'driving']
# Remove columns transportation_type, alternative_name, sub-region, country"""
df_apple = df_apple.drop(['transportation_type','alternative_name', 'sub-region', 'country'], axis=1)

# Create a df for oil consumption by country in thousands barrels per day"""
df_oil_consumption = pd.read_csv("https://raw.githubusercontent.com/harish5p/World-Mobility-Index/main/oil-consumption.csv")
# Rename thousands barrels daily to country"""
df_oil_consumption = df_oil_consumption.rename(columns={'Thousand barrels daily':'country'})

oil_countries = df_oil_consumption.country.tolist()
apple_countries = df_apple.region.tolist()

# select countries in apple_countries that are also in oil_countries"""
apple_countries_in_oil = [x for x in apple_countries if x in oil_countries]

# Select the df_apple for the countries in apple_countries_in_oil"""
df_apple = df_apple[df_apple['region'].isin(apple_countries_in_oil)]
#Reset index of df_apple"""
df_apple = df_apple.reset_index(drop=True)
# Remove the column geo_type"""
df_apple = df_apple.drop(['geo_type'], axis=1)
# Rename df_apple column region to country"""
df_apple = df_apple.rename(columns={'region':'country'})

# Join df_apple and df_oil_consumption"""
df_apple = df_apple.merge(df_oil_consumption, on='country', how='left')

#Rename column 2019 to oil"""
df_apple = df_apple.rename(columns={'2019':'oil'})
# Convert oil column to the percentage of total sum"""
df_apple['oil'] = df_apple['oil']/df_apple['oil'].sum()
# """List of dates"""
dates = df_apple.columns[2:-1].tolist()

# Select the third column to last column and transpose"""
df = df_apple[dates].transpose()
# """Add the index column to df"""
df['date'] = dates
# """Reset index"""
df = df.reset_index(drop=True)
# """Convert date column to datetime object"""
df['date'] = pd.to_datetime(df['date'])


countries = df_apple.country.tolist() + ['date']
df.columns = countries

oil_consumption = df_apple.oil.tolist() 
# """Set index as date column"""
df = df.set_index('date')

# """add a new column as world_mobility_index which is the dot product of oil_consumption and df"""
df_index = df.dot(oil_consumption)
#"""Convert to 7 day moving average"""
df_index = df_index.rolling(7).mean()

# """Get the EOD price of oil"""
prices_df = nasdaqdatalink.get("OPEC/ORB", authtoken=st.secrets["quandl_key"])

# """Filter the df to only include dates in df_index"""
prices_df = prices_df[prices_df.index.isin(df_index.index)]


st.title("World Mobility Index weighted by oil consumption of each country")
# Line chart
st.line_chart(pd.DataFrame(df_index, prices_df))




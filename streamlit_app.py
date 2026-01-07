import requests
import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col

# Header
st.title(
    f":cup_with_straw: Customize Your Smoothie!:cup_with_straw:"
)
st.write(
  """
  Choose the fruits you want in your custom Smoothie!
  """
)

# Input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection('Snowflake')
session = cnx.session()

# Select
df = session.table(
    "smoothies.public.fruit_options"
).select(col('FRUIT_NAME'), col("SEARCH_ON"))
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients',
    df,
    max_selections=5
)

pd_df = df.to_pandas()
st.dataframe(pd_df)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + 'Nutrition Infomaion')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

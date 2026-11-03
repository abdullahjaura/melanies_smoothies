import requests
import streamlit as st
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection(
    "snowflake",
    login_timeout=20,
    socket_timeout=20,
)
session = cnx.session()

my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col("FRUIT_NAME"))

fruit_names = [
    row["FRUIT_NAME"]
    for row in my_dataframe.collect()
]

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_names,
    max_selections=5,
)

if ingredients:
    ingredients_string = ""

    for fruit_chosen in ingredients:
        ingredients_string += fruit_chosen + " "

        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )

        sf_df = session.create_dataframe(
            data=[smoothiefroot_response.json()["nutrition"]]
        )

        st.dataframe(sf_df, use_container_width=True)

    my_insert_stmt = """insert into smoothies.public.orders
        (ingredients, name_on_order)
        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(
            "Your Smoothie is ordered, " + name_on_order + "!",
            icon="✅",
        )


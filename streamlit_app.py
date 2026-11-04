import pandas as pd
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
).select(col("FRUIT_NAME"), col("SEARCH_ON"))

pd_df = my_dataframe.to_pandas()
fruit_names = pd_df["FRUIT_NAME"].tolist()

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

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for ", fruit_chosen,
            " is ", search_on, "."
        )

        try:
            smoothiefroot_response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/"
                + search_on,
                timeout=20,
            )

            smoothiefroot_response.raise_for_status()
            fruit_data = smoothiefroot_response.json()

            if fruit_data.get("nutrition"):
                sf_df = session.create_dataframe(
                    data=[fruit_data["nutrition"]]
                )
                st.dataframe(sf_df, use_container_width=True)
            else:
                st.warning(
                    "Nutrition information is unavailable for "
                    + fruit_chosen
                )

        except (requests.exceptions.RequestException, ValueError):
            st.warning(
                "Could not retrieve nutrition information for "
                + fruit_chosen
            )

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

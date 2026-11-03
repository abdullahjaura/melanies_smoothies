import streamlit as st

st.title("Snowflake connection test")

try:
    st.write("Connecting to Snowflake…")
    cnx = st.connection("snowflake")
    session = cnx.session()
    st.success("Connected to Snowflake!")

    rows = session.table(
        "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
    ).collect()

    st.success(f"Loaded {len(rows)} fruits!")
    st.dataframe(rows)

except Exception as error:
    st.error("The Snowflake test failed.")
    st.exception(error)

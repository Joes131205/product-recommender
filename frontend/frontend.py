import os

import requests
import streamlit as st

st.set_page_config(
    page_title="Product Recommender",
    layout="centered",
)

st.title("Product Recommender")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.subheader("Customer Details")

customers = []
try:
    resp = requests.get(f"{API_BASE_URL}/customers", params={"limit": 500}, timeout=3)
    if resp.status_code == 200:
        customers = resp.json().get("customers", [])
except Exception:  # noqa: BLE001
    customers = []

if customers:
    customer_id = st.selectbox("Choose Customer ID", options=customers, index=0)
else:
    customer_id = st.text_input(
        label="Customer ID",
        value="AA-103151",
        placeholder="e.g. AA-103151",
        help="Enter an existing Customer ID from the database.",
    )

num_recommendations = st.slider(
    label="Max Items to Recommend", min_value=1, max_value=10, value=3
)

if st.button(
    "Generate Recommendations",
    type="primary",
):
    assert customer_id is not None
    if not customer_id.strip():
        st.warning("Please provide a valid Customer ID.")
    else:
        url = f"{API_BASE_URL}/recommended/{customer_id.strip()}"
        params = {"n": num_recommendations}

        with st.spinner("Fetching..."):
            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Recommendations successfully retrieved!")

                    col1, col2 = st.columns(2)
                    col1.metric("Customer ID", data.get("customer_id"))
                    col2.metric("Assigned Cluster", f"Cluster {data.get('cluster')}")

                    st.markdown("---")
                    st.subheader("Recommended Products")

                    items = data.get("recommendations", [])

                    if items:
                        for rank, item in enumerate(items, start=1):
                            name = item.get("product_name")
                            price = item.get("avg_unit_price")
                            price_display = (
                                f"${price:,.2f}" if price is not None else "N/A"
                            )
                            st.markdown(
                                f"**{rank}.** {name} - **Price: {price_display}**"
                            )
                    else:
                        st.info("No profitable items found for this customer profile.")

                elif response.status_code == 404:
                    st.error(f"Not Found: {response.json().get('detail')}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"Cannot connect to the backend at `{API_BASE_URL}`. Ensure uvicorn is running."
                )
            except Exception as err:  # noqa: BLE001
                st.error(f"Unexpected error: {err}")

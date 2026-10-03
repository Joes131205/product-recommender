import sqlite3

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status

conn = sqlite3.connect("../superstore.sqlite", check_same_thread=False)

clf_model = joblib.load("../model/profit_classification.pkl")
kmeans_model = joblib.load("../model/user_clustering.pkl")
rfm_scaler = joblib.load("../model/rfm_scale.pkl")

app = FastAPI(title="Product Recommendation Model")


@app.get("/", status_code=status.HTTP_200_OK)
def health_check():
    return {"ok": True, "message": "healthy"}


@app.get("/recommended/{customer_id}", status_code=status.HTTP_200_OK)
def get_recommended_product(customer_id: str, n: int = 3):
    # Verify customer exists in the database
    customer = pd.read_sql_query(
        "SELECT customer_id FROM dim_customers WHERE customer_id = ?",
        conn,
        params=[customer_id],
    )
    if customer.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found",
        )

    # Look up customer's cluster
    user_segment = pd.read_sql_query(
        "SELECT cluster FROM customer_segments WHERE customer_id = ?",
        conn,
        params=[customer_id],
    )
    if user_segment.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' has not been segmented yet",
        )

    cluster_id = int(user_segment["cluster"].iloc[0])

    # Pull candidate products based on the cluster.
    candidate_query = """
        SELECT 
            oi.discount,
            oi.shipping_cost,
            o.ship_mode,
            dc.segment,
            dp.category,
            dp.sub_category,
            dp.product_name,
            SUM(oi.sales) as total_sales,
            SUM(oi.quantity) as total_qty,
            ROUND(CASE WHEN SUM(oi.quantity) > 0 THEN SUM(oi.sales) / SUM(oi.quantity) ELSE 0 END, 2) as avg_unit_price,
            COUNT(*) as popularity
        FROM order_items oi
        JOIN orders o ON oi.order_key = o.order_key
        JOIN dim_customers dc ON o.customer_id = dc.customer_id
        JOIN dim_products dp ON oi.product_id = dp.product_id
        JOIN customer_segments cs ON dc.customer_id = cs.customer_id
        WHERE cs.cluster = ?
        GROUP BY dp.product_name
        ORDER BY popularity DESC
        LIMIT 20
    """
    candidates = pd.read_sql_query(candidate_query, conn, params=[cluster_id])

    if candidates.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidate items found for this cluster",
        )

    # Predict profitability using the classification pipeline
    feature_cols = [
        "discount",
        "shipping_cost",
        "ship_mode",
        "segment",
        "category",
        "sub_category",
    ]
    predictions = clf_model.predict(candidates[feature_cols])

    # Filter for profitable items only (1 = Profitable, 0 = Loss)
    profitable = candidates[predictions == 1]

    # Build recommendation objects including product name and average unit price
    recommendations = []
    for _, row in profitable.iterrows():
        recommendations.append(
            {
                "product_name": row["product_name"],
                "avg_unit_price": float(row.get("avg_unit_price", 0) or 0),
            }
        )

    return {
        "customer_id": customer_id,
        "cluster": cluster_id,
        "total_profitable_found": len(recommendations),
        "recommendations": recommendations[:n],
    }


@app.get("/customers", status_code=status.HTTP_200_OK)
def list_customers(limit: int = 200):
    df = pd.read_sql_query(
        "SELECT customer_id FROM dim_customers LIMIT ?", conn, params=[limit]
    )
    return {"count": len(df), "customers": df["customer_id"].tolist()}

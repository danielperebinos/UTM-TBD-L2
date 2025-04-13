import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://root:root@localhost:27020")
db = client["hotels"]
hotels_col = db["hotels"]
reviews_col = db["reviews"]

st.set_page_config(page_title="Hotel Reviews App", layout="wide")

st.title("🏨 Hotel Reviews Dashboard")

tab1, tab2, tab3 = st.tabs(["✍️ Submit a Review", "📊 Hotel Statistics", "🔍 Explore Reviews"])

# =====================
# 1. SUBMIT REVIEW
# =====================
with tab1:
    st.subheader("Add a New Review")

    hotels = list(hotels_col.find({}, {"_id": 1, "name": 1}))
    hotel_names = {h["name"]: h["_id"] for h in hotels}
    selected_hotel = st.selectbox("Select a Hotel", options=list(hotel_names.keys()))

    with st.form("add_review"):
        nationality = st.text_input("Nationality")
        total_reviews = st.number_input("Total Reviews by User", min_value=1, step=1)
        score = st.slider("Review Score", 0.0, 10.0, 7.5, step=0.1)
        positive = st.text_area("Positive Review")
        negative = st.text_area("Negative Review")
        submit = st.form_submit_button("Submit Review")

        if submit:
            reviews_col.insert_one({
                "hotel_id": hotel_names[selected_hotel],
                "reviewer_score": score,
                "positive_review": positive,
                "negative_review": negative,
                "reviewer": {
                    "nationality": nationality,
                    "total_number_of_reviews_by_reviewer": total_reviews
                }
            })
            st.success("✅ Review successfully submitted!")

# =====================
# 2. STATISTICS
# =====================
with tab2:
    st.subheader("Hotel Review Statistics")

    # --- Filter row (all filters in one row) ---
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        nationalities = reviews_col.distinct("reviewer.nationality")
        selected_nat = st.selectbox("Filter by reviewer nationality", options=["All"] + sorted(nationalities))

    with col_f2:
        min_score, max_score = st.slider(
            "Filter by score range",
            min_value=0.0, max_value=10.0,
            value=(0.0, 10.0), step=0.1
        )

    with col_f3:
        hotel_names = hotels_col.distinct("name")
        selected_hotel = st.selectbox("Filter by hotel", options=["All"] + sorted(hotel_names))

    # --- Build match stage ---
    match_conditions = {}

    if selected_nat != "All":
        match_conditions["reviewer.nationality"] = selected_nat

    if selected_hotel != "All":
        hotel = hotels_col.find_one({"name": selected_hotel}, {"_id": 1})
        if hotel:
            match_conditions["hotel_id"] = hotel["_id"]

    match_conditions["reviewer_score"] = {"$gte": min_score, "$lte": max_score}

    pipeline = []
    if match_conditions:
        pipeline.append({"$match": match_conditions})

    pipeline.extend([
        {
            "$lookup": {
                "from": "hotels",
                "localField": "hotel_id",
                "foreignField": "_id",
                "as": "hotel"
            }
        },
        {"$unwind": "$hotel"},
        {
            "$group": {
                "_id": "$hotel.name",
                "avg_score": {"$avg": "$reviewer_score"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"avg_score": -1}}
    ])

    stats = list(reviews_col.aggregate(pipeline))
    df = pd.DataFrame(stats)
    df.rename(columns={"_id": "Hotel", "avg_score": "Average Score", "count": "No. of Reviews"}, inplace=True)

    # --- Pagination logic ---
    page_size = 20
    total_items = len(df)
    total_pages = max((total_items + page_size - 1) // page_size, 1)

    page_start, page_end = 0, page_size
    page = 1

    if total_items > 0:
        page = st.number_input(
            label="Page number",
            min_value=1,
            max_value=total_pages,
            step=1,
            value=1,
            key="pagination"
        )
        page_start = (page - 1) * page_size
        page_end = page_start + page_size

    paged_df = df.iloc[page_start:page_end]

    # --- Display data + plot ---
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"📋 **Top Hotels by Score** (Page {page}/{total_pages})")
        st.dataframe(paged_df, use_container_width=True)

    with col2:
        st.write("📈 **Average Score Distribution (this page only)**")
        fig, ax = plt.subplots()
        if paged_df.empty:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=20)
        else:
            ax.barh(paged_df["Hotel"], paged_df["Average Score"])
        ax.invert_yaxis()
        ax.set_xlabel("Average Score")
        st.pyplot(fig)

    # --- Pagination UI under table ---
    st.markdown("---")
    st.caption(f"Showing {min(page_end, total_items)} of {total_items} hotels")

with tab3:
    st.subheader("Explore User Reviews")

    # --- Filter row ---
    colf1, colf2 = st.columns(2)

    with colf1:
        selected_hotel = st.selectbox("Select hotel", ["All"] + sorted(hotels_col.distinct("name")))
        selected_nat = st.selectbox("Select nationality",
                                    ["All"] + sorted(reviews_col.distinct("reviewer.nationality")))

    with colf2:
        search_term = st.text_input("Search in reviews (keywords)")
        score_range = st.slider("Score filter", 0.0, 10.0, (0.0, 10.0), 0.1)

    # --- Build dynamic query ---
    query = {
        "reviewer_score": {"$gte": score_range[0], "$lte": score_range[1]}
    }

    if selected_hotel != "All":
        hotel = hotels_col.find_one({"name": selected_hotel}, {"_id": 1})
        if hotel:
            query["hotel_id"] = hotel["_id"]

    if selected_nat != "All":
        query["reviewer.nationality"] = selected_nat

    if search_term.strip():
        query["$or"] = [
            {"positive_review": {"$regex": search_term, "$options": "i"}},
            {"negative_review": {"$regex": search_term, "$options": "i"}}
        ]

    # --- Fetch and display reviews ---
    results = list(reviews_col.find(query).sort("reviewer_score", -1).limit(20))

    st.markdown(f"### Found {len(results)} reviews")

    for r in results:
        with st.expander(f"⭐ {r.get('reviewer_score')} - {r['reviewer']['nationality']}"):
            st.write(f"**Positive:** {r.get('positive_review', '-')}")
            st.write(f"**Negative:** {r.get('negative_review', '-')}")
            st.caption(f"Total reviews by user: {r['reviewer'].get('total_number_of_reviews_by_reviewer', 'N/A')}")

            # --- Delete button ---
            delete_key = f"delete_{r['_id']}"
            if st.button("🗑️ Delete this review", key=delete_key):
                reviews_col.delete_one({"_id": r["_id"]})
                st.warning("Review deleted. Please refresh the page.")

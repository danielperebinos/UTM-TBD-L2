import hashlib

import pandas as pd
from bson import ObjectId

# Load the CSV
df = pd.read_csv("datasets/Hotel_Reviews.csv")

# Convert generated hotel_id string to actual ObjectId format for MongoDB compatibility
# First, map hotel identifiers to ObjectIds
unique_hotels = df[["Hotel_Name", "Hotel_Address"]].drop_duplicates().copy()
unique_hotels["object_id"] = unique_hotels.apply(
    lambda row: ObjectId(hashlib.md5(f"{row['Hotel_Name']}_{row['Hotel_Address']}".encode()).hexdigest()[:24]),
    axis=1
)

# Merge back the ObjectId to the main DataFrame
df = df.merge(unique_hotels, on=["Hotel_Name", "Hotel_Address"], how="left")

# Rebuild HOTELS collection
hotels = df[[
    "Hotel_Name", "Hotel_Address", "Average_Score", "Total_Number_of_Reviews", "lat", "lng", "object_id"
]].drop_duplicates().copy()

hotels.rename(columns={
    "Hotel_Name": "name",
    "Hotel_Address": "address",
    "Average_Score": "average_score",
    "Total_Number_of_Reviews": "total_number_of_reviews",
    "object_id": "_id"
}, inplace=True)
hotels = hotels[["_id", "name", "address", "average_score", "total_number_of_reviews", "lat", "lng"]]

# Rebuild REVIEWS collection with embedded reviewer and ObjectId reference to hotel
reviews = df[[
    "Review_Date", "Positive_Review", "Negative_Review",
    "Review_Total_Positive_Word_Counts", "Review_Total_Negative_Word_Counts",
    "Reviewer_Score", "Tags", "days_since_review",
    "Reviewer_Nationality", "Total_Number_of_Reviews_Reviewer_Has_Given",
    "object_id"
]].copy()


def generate_full_review_id(row):
    fields = [
        str(row["object_id"]),
        row["Review_Date"],
        row["Positive_Review"],
        row["Negative_Review"],
        str(row["Review_Total_Positive_Word_Counts"]),
        str(row["Review_Total_Negative_Word_Counts"]),
        str(row["Reviewer_Score"]),
        row["Tags"],
        row["days_since_review"],
        row["Reviewer_Nationality"],
        str(row["Total_Number_of_Reviews_Reviewer_Has_Given"])
    ]
    return hashlib.md5("_".join(fields).encode()).hexdigest()


reviews["_id"] = reviews.apply(generate_full_review_id, axis=1)
reviews["hotel_id"] = reviews["object_id"]

# Embed reviewer
reviews["reviewer"] = reviews.apply(lambda row: {
    "nationality": row["Reviewer_Nationality"],
    "total_number_of_reviews_by_reviewer": row["Total_Number_of_Reviews_Reviewer_Has_Given"]
}, axis=1)

# Final formatting
reviews.rename(columns={
    "Review_Date": "review_date",
    "Positive_Review": "positive_review",
    "Negative_Review": "negative_review",
    "Review_Total_Positive_Word_Counts": "review_total_positive_word_counts",
    "Review_Total_Negative_Word_Counts": "review_total_negative_word_counts",
    "Reviewer_Score": "reviewer_score",
    "Tags": "tags"
}, inplace=True)

reviews = reviews[[
    "_id", "hotel_id", "review_date", "positive_review", "negative_review",
    "review_total_positive_word_counts", "review_total_negative_word_counts",
    "reviewer_score", "tags", "days_since_review", "reviewer"
]]

# Convert ObjectId fields to JSON serializable format
hotels["_id"] = hotels["_id"].apply(lambda oid: {"$oid": str(oid)})
reviews["hotel_id"] = reviews["hotel_id"].apply(lambda oid: {"$oid": str(oid)})

hotels.to_json("datasets/hotels.json", orient="records", indent=2)
reviews.to_json("datasets/reviews.json", orient="records", indent=2)

import pandas as pd
from datetime import datetime

df = pd.read_csv("india_housing_prices.csv")
df = df.drop_duplicates().reset_index(drop=True)

current_year = datetime.now().year
if "Year_Built" in df.columns:
    df["Age_of_Property"] = current_year - df["Year_Built"]

df["Price_per_SqFt"] = (df["Price_in_Lakhs"] * 100000) / df["Size_in_SqFt"]

df["Amenity_Count"] = df["Amenities"].apply(
    lambda x: len(str(x).split(",")) if pd.notna(x) and x != "" else 0
)


def get_premium_segment(amenities):
    if pd.isna(amenities) or amenities == "":
        return "Low Premium"
    count = len(str(amenities).split(","))
    if count >= 6 or any(
        w in str(amenities).lower()
        for w in ["pool", "clubhouse", "gym", "spa", "luxury"]
    ):
        return "High Premium"
    elif count >= 3:
        return "Medium Premium"
    return "Low Premium"


df["Premium_Segment"] = df["Amenities"].apply(get_premium_segment)


def security_score(sec):
    if pd.isna(sec):
        return 0
    s = str(sec).lower()
    if "gated" in s or "cctv" in s:
        return 3
    elif "guard" in s:
        return 2
    return 1


df["Security_Score"] = df["Security"].apply(security_score)

numeric_cols = [
    "Amenity_Count",
    "Size_in_SqFt",
    "Parking_Space",
    "Security_Score",
    "Price_in_Lakhs",
    "Nearby_Schools",
    "Nearby_Hospitals",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Value_Rank_Score"] = (
    df["Amenity_Count"] * 2
    + df["Size_in_SqFt"] / 1000
    + df["Parking_Space"] * 5
    + df["Security_Score"] * 10
    + df["Price_in_Lakhs"] / 50
    + df["Nearby_Schools"] * 8
    + df["Nearby_Hospitals"] * 8
)

price_threshold = df["Price_per_SqFt"].quantile(0.25)


def is_good_investment(row):
    try:
        return (
            1
            if (
                row["Price_per_SqFt"] < price_threshold
                and str(row.get("Amenities", "")).lower()
                in ["high", "excellent", "premium", "luxury"]
                and str(row.get("Public_Transport_Accessibility", "")).lower() == "high"
                and row.get("Nearby_Schools", 0) >= 2
            )
            or row.get("Age_of_Property", 30) <= 15
            else 0
        )
    except:
        return 0


df["Good_Investment"] = df.apply(is_good_investment, axis=1)

df.to_csv("cleaned_india_housing_prices.csv", index=False)
print("✅ Fresh cleaned file created with ALL columns!")

import pandas as pd

df = pd.read_csv("data/reports.csv")

required_columns = [
    "report_id",
    "reported_at",
    "category",
    "summary",
    "phone_id",
    "website_domain",
    "email_id",
    "synthetic_group",
]

assert list(df.columns) == required_columns
assert len(df) == 500
assert df["report_id"].is_unique
assert not df[required_columns].isnull().any().any()

print("All basic validation checks passed.")

print("\nReports per synthetic group:")
print(df["synthetic_group"].value_counts().head(10))

print("\nMost frequently mentioned phone identifiers:")
print(df["phone_id"].value_counts().head(5))

print("\nMost frequently mentioned websites:")
print(df["website_domain"].value_counts().head(5))
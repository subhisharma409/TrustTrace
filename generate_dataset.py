
from pathlib import Path
import random
import pandas as pd

# Reproducible synthetic data for TrustTrace.
random.seed(42)

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

CATEGORIES = [
    "Payment request",
    "Account alert",
    "Impersonation",
    "Suspicious link",
    "Unusual message",
]

SUMMARIES = [
    "A fictional report describes an unexpected payment request.",
    "A fictional report describes a suspicious account notification.",
    "A fictional report describes a potentially misleading website.",
    "A fictional report describes an unexpected message.",
    "A fictional report describes a possible impersonation attempt.",
]

rows = []
report_number = 1

# Create 20 deliberately connected groups.
# Each group contains six fictional reports.
for group_num in range(1, 21):
    group = f"CLUSTER-{group_num:03d}"

    shared_phone = f"PHONE-{group_num:03d}-SHARED"
    shared_website = f"site-{group_num:03d}.example"
    shared_email = f"contact-{group_num:03d}@example.invalid"

    for i in range(6):
        # First three reports share a phone.
        phone = (
            shared_phone if i < 3
            else f"PHONE-{group_num:03d}-{i + 1:02d}"
        )

        # Last four reports share a website.
        # Report 3 (i == 2) bridges the phone and website.
        website = (
            shared_website if i >= 2
            else f"site-{group_num:03d}-{i + 1:02d}.example"
        )

        # Reports 2–4 also share an email identifier.
        email = (
            shared_email if 1 <= i <= 3
            else f"contact-{group_num:03d}-{i + 1:02d}@example.invalid"
        )

        rows.append({
            "report_id": f"R{report_number:04d}",
            "reported_at": (
                pd.Timestamp("2026-01-01")
                + pd.Timedelta(days=report_number - 1)
            ).isoformat(),
            "category": random.choice(CATEGORIES),
            "summary": random.choice(SUMMARIES),
            "phone_id": phone,
            "website_domain": website,
            "email_id": email,
            # Evaluation metadata; do not use as a graph connection.
            "synthetic_group": group,
        })

        report_number += 1

# Add 380 unrelated background reports.
for i in range(380):
    rows.append({
        "report_id": f"R{report_number:04d}",
        "reported_at": (
            pd.Timestamp("2026-01-01")
            + pd.Timedelta(days=report_number - 1)
        ).isoformat(),
        "category": random.choice(CATEGORIES),
        "summary": random.choice(SUMMARIES),
        "phone_id": f"PHONE-BG-{i + 1:04d}",
        "website_domain": f"background-{i + 1:04d}.example",
        "email_id": f"contact-{i + 1:04d}@example.invalid",
        "synthetic_group": "BACKGROUND",
    })
    report_number += 1

df = pd.DataFrame(rows)

# Shuffle records while preserving their IDs.
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

output_file = OUTPUT_DIR / "reports.csv"
df.to_csv(output_file, index=False)

print("TrustTrace dataset generated successfully!")
print(f"File: {output_file.resolve()}")
print(f"Total reports: {len(df)}")
print(f"Connected groups: 20")
print(f"Background reports: {(df['synthetic_group'] == 'BACKGROUND').sum()}")
print(f"Unique report IDs: {df['report_id'].nunique()}")
print("\nFirst five records:")
print(df.head().to_string(index=False))

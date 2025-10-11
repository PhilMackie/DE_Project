import pandas as pd
import re

# add the files
input_file = "Insta Organic.csv"            # ensure this matches your filename
output_file = "Insta_Organic_Cleaned.csv"

# read the files
df = pd.read_csv(input_file)
df.columns = df.columns.str.strip()

# nuked all ranges of emojis from orbit
_EMOJI_RANGES = (
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "\U000025A0-\U000025FF"
    "\U00002B00-\U00002BFF"
    "\U00002300-\U000023FF"
    "\U0001F3FB-\U0001F3FF"
)
emoji_pattern = re.compile(f"[{_EMOJI_RANGES}]", flags=re.UNICODE)
# extra extra emoji removal - compliled custom emojis
ZWJ_SELECTORS = re.compile(r"[\u200d\ufe0e\ufe0f\u20e3]")

def strip_emojis(text: object) -> object:
    if not isinstance(text, str):
        return text
    cleaned = emoji_pattern.sub("", text)
    cleaned = ZWJ_SELECTORS.sub("", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

#client anonymizer
SCRUB_PATTERNS = [
    re.compile(r"Tales\s+of\s+the\s+Cocktail", flags=re.IGNORECASE),
    re.compile(r"(?:#|@)?totcf\w*", flags=re.IGNORECASE),
    re.compile(r"(?:#|@)?totc\w*", flags=re.IGNORECASE),
    re.compile(r"talesofthecocktail", flags=re.IGNORECASE),
]

def scrub_client(text: object) -> object:
    if not isinstance(text, str):
        return text
    out = text
    for pat in SCRUB_PATTERNS:
        out = pat.sub("fooBar", out)
    return re.sub(r"\s+", " ", out).strip()

# clean all columns
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].map(strip_emojis).map(scrub_client)

# renaming columns
rename_map = {
    "Date": "Date",
    "Message": "Message",
    "Likes": "Likes",
    "Impressions": "Impressions",
    "Comments": "Comments",
    "Link Clicks": "Clicks",
}
df = df.rename(columns=rename_map)

# append source info!
df["Source"] = "Insta Organic"

# reorder columns for consistency
final_cols = ["Date", "Message", "Likes", "Impressions", "Comments", "Clicks", "Source"]
missing = [c for c in final_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing expected columns: {missing}")
df = df[final_cols]

#no empty cells
df = df.fillna(0)

# save
df.to_csv(output_file, index=False)
print(f"✅ Cleaned CSV saved as {output_file} (emojis removed, client scrubbed, empty cells replaced with 0)")

import pandas as pd
import re

# add the files
input_file = "FB Organic.csv"
output_file = "FB_Organic_Cleaned.csv"

# read the files
df = pd.read_csv(input_file)
df.columns = df.columns.str.strip()

# nuked all ranges of emojis from orbit
_EMOJI_RANGES = (
    "\U0001F1E6-\U0001F1FF"  # flags
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F700-\U0001F77F"  # alchemical
    "\U0001F780-\U0001F7FF"  # geometric extended
    "\U0001F800-\U0001F8FF"  # supplemental arrows-C
    "\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
    "\U0001FA00-\U0001FA6F"  # chess, symbols
    "\U0001FA70-\U0001FAFF"  # more symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "\U000025A0-\U000025FF"  # geometric shapes
    "\U00002B00-\U00002BFF"  # misc symbols & arrows
    "\U00002300-\U000023FF"  # technical
    "\U0001F3FB-\U0001F3FF"  # skin tones
)
emoji_pattern = re.compile(f"[{_EMOJI_RANGES}]", flags=re.UNICODE)
# extra extra emoji removal - compliled custom emojis
ZWJ_SELECTORS = re.compile(r"[\u200d\ufe0e\ufe0f\u20e3]")

def strip_emojis(text: object) -> object:
    if not isinstance(text, str):
        return text
    cleaned = emoji_pattern.sub("", text)
    cleaned = ZWJ_SELECTORS.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

#client anonymizer
SCRUB_PATTERNS = [
    re.compile(r"Tales\s+of\s+the\s+Cocktail", flags=re.IGNORECASE),
    re.compile(r"(?:#|@)?totcf\w*", flags=re.IGNORECASE),  # catches totcf, #totcf, totcf2023, etc.
    re.compile(r"(?:#|@)?totc\w*",  flags=re.IGNORECASE),  # catches totc, #totc, totc2023, etc.
    re.compile(r"talesofthecocktail", flags=re.IGNORECASE),
]

def scrub_client(text: object) -> object:
    if not isinstance(text, str):
        return text
    out = text
    for pat in SCRUB_PATTERNS:
        out = pat.sub("fooBar", out)
    # doubled space cleanup
    out = re.sub(r"\s+", " ", out).strip()
    return out

# url scrub
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
df["Source"] = "FB Organic"

# reorder columns for consistency
final_cols = ["Date", "Message", "Likes", "Impressions", "Comments", "Clicks", "Source"]
missing = [c for c in final_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing expected columns: {missing}")
df = df[final_cols]

# save
df.to_csv(output_file, index=False)
print(f"✅ Cleaned CSV saved as {output_file} (emojis removed, client scrubbed)")

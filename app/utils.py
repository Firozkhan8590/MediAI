import pandas as pd
import os
import logging
from django.conf import settings

def skincare_by_skin_type(skin_type, num_products=5):
    file_path = os.path.join(settings.BASE_DIR, 'app', 'export_skincare.csv')
    print("📄 Reading CSV file from:", file_path)

    try:
        df = pd.read_csv(file_path)
        print("✅ DataFrame loaded successfully")
        
        # Clean the image URLs in 'picture_src' column
        if 'picture_src' in df.columns:
            df['picture_src'] = df['picture_src'].str.replace(r'-(?=\.jpg$)', '', regex=True)
            # Rename for template compatibility
            df = df.rename(columns={'picture_src': 'image_url'})
        else:
            print("⚠️ 'picture_src' column not found. Available columns:", df.columns.tolist())

        # Map user input to column names
        skin_type_map = {
            "oily skin": "Oily",
            "dry skin": "Dry",
            "combination skin": "Combination",
            "sensitive skin": "Sensitive",
            "normal skin": "Normal",
        }

        column_name = skin_type_map.get(skin_type.lower())

        if not column_name or column_name not in df.columns:
            print(f"❌ Column '{column_name}' not found.")
            return []

        # Filter and return top products
        df_filtered = df[df[column_name] == 1].copy()
        print(f"🔍 Found {len(df_filtered)} matching products for: {skin_type}")
        print(df_filtered[['product_name', 'image_url']].head())

        return df_filtered.head(num_products).to_dict(orient="records")

    except Exception as e:
        logging.error("Error reading skincare CSV: %s", e)
        return []

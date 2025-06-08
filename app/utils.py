#Product Recommendation

import pandas as pd
import os

def skincare_by_skin_type(skin_type, num_products=5):
    file_path = os.path.join(os.path.dirname(__file__), "export_skincare.csv")

    try:
        df = pd.read_csv(file_path)
        df_filtered = df[df['skintype'].str.contains(skin_type, case=False, na=False)]
        recommended_products = df_filtered.head(num_products).to_dict(orient="records")
        return recommended_products
    except Exception as e:
        print("Error reading skincare CSV:", e)
        return []
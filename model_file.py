import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

product_category_map = {} 
item_similarity_df = None

def preprocess_df(df):
    # lower column names
    df.columns = df.columns.str.strip().str.lower()
    
    def find_col(possible_names):
        return next((col for col in df.columns if col in possible_names), None)

    # -------------------------
    # 1. Date Handling (Fast & Robust)
    # -------------------------
    date_cols = ['order date', 'date', 'ship date', 'order_date','ship_date']
    date_col = find_col(date_cols)

    if date_col:
        df['date'] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True, errors='coerce')
        df["month"] = df['date'].dt.month
    else:
        df["month"] = np.nan

    # -------------------------
    # 2. Core Numeric Features
    # -------------------------
    def clean_numeric(names):
        col = find_col(names)
        if col:
            # Removes currencies and commas safely
            return pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.-]", "", regex=True).replace('', np.nan), errors='coerce').fillna(0)
        return pd.Series([0.0]*len(df), index=df.index)

    df["sales"] = clean_numeric(['sales','sale','revenue','amount','total_sales','total sales','sales amount','net sales','gross sales'])
    df["profit"] = clean_numeric(['profit','net_profit','net profit'])
    df["product cost"] = clean_numeric(['product cost','cost','product_cost','cogs'])
    df["shipping cost"] = clean_numeric(['shipping cost','shipping_cost','delivery_cost','delivery cost'])
    df["discount"] = clean_numeric(['discount','discount amount','discount_rate','discount rate'])
      
    # Fill missing values logically
    if (df["sales"] == 0).all():
        df["sales"] = df["profit"] + df["product cost"]
    if (df["product cost"] == 0).all():
        df["product cost"] = df["sales"] - df["profit"]
    if (df["profit"] == 0).all():
        df["profit"] = df["sales"] - df["product cost"] - df["discount"] - df["shipping cost"]

    # -------------------------
    # 3. Quantity
    # -------------------------
    qty_col = find_col(['quantity','qty','units','quantity_sold','quantity sold','order_quantity'])
    df["quantity"] = pd.to_numeric(df[qty_col], errors='coerce').fillna(1).replace(0, 1) if qty_col else 1

    # -------------------------
    # 4. Product ID, Category, Region
    # -------------------------
    product_name_col = find_col(['product name','product_name','product','item name','item_name','item','name','product title','title'])
    product_id_col = find_col(['item_id','product id','product_id','item id'])
    
    df["product id"] = df[product_name_col] if product_name_col else (df[product_id_col] if product_id_col else "Unknown")
    df["product id"] = df["product id"].astype(str)

    category_col = find_col(['category','product category'])
    region_col = find_col(['region','area','location'])

    df["category"] = df[category_col].astype(str).fillna("Unknown") if category_col else "Unknown"
    df["region"] = df[region_col].astype(str).fillna("Unknown") if region_col else "Unknown"

    return df

# 2. FEATURE ENGINEERING
def feature_engineering(monthly_df):
    monthly_df = monthly_df.copy()
    monthly_df = monthly_df.sort_values(by=['product id', 'month'])
    
    monthly_df['price_after_discount'] = monthly_df['sales'] / monthly_df['quantity'].clip(lower=1)
    monthly_df['qty_lag_1'] = monthly_df.groupby('product id')['quantity'].shift(1).fillna(0)
    monthly_df['sales_lag_1'] = monthly_df.groupby('product id')['sales'].shift(1).fillna(0)
    monthly_df['qty_roll_mean_3'] = monthly_df.groupby('product id')['quantity'].transform(lambda x: x.rolling(3, min_periods=1).mean().fillna(0))
    
    return monthly_df

# 3. PIPELINE AND FORECASTING
def pipelining_modelfitting(features_raw):
    features = preprocess_df(features_raw)
    
    # Drop rows without month, else groupby fails
    features = features.dropna(subset=['month'])
    
    cat_cols = ['product id', 'month', 'category']
    sum_cols = ['quantity', 'profit', 'sales']
    mean_cols = ['shipping cost', 'discount', 'product cost']
    
    agg_dict = {col: 'sum' for col in sum_cols}
    agg_dict.update({col: 'mean' for col in mean_cols})
    
    monthly_df = features.groupby(cat_cols).agg(agg_dict).reset_index()
    monthly_df = feature_engineering(monthly_df)
    
    num_cols = mean_cols + sum_cols + ['qty_lag_1', 'sales_lag_1', 'qty_roll_mean_3', 'price_after_discount']
    num_cols = [c for c in num_cols if c not in ['quantity', 'profit']] 
    
    feature_cols = cat_cols + num_cols
    target_cols = ['quantity', 'profit']
    
    monthly_df = monthly_df.dropna(subset=target_cols)
    if monthly_df.empty:
        raise ValueError("Dataset is too small to train the model after preprocessing.")
    
    X = monthly_df[feature_cols]
    y = monthly_df[target_cols]
    
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    numerical_features = X.select_dtypes(include=['number']).columns
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", StandardScaler(), numerical_features)
        ])
    
    pipeline_prediction = Pipeline(steps=[
        ("preprocessing", preprocessor),
        ("model", XGBRegressor(
            n_estimators=300, # total tress
            learning_rate=0.05, # learning speed
            max_depth=7, # tree depth
            subsample=0.8, # row sampling 0.8 means 80% rows for each tree
            colsample_bytree=0.8, # feature sampling 0.8 means 80% features for each tree
            random_state=42, # random results reproducibility
            n_jobs=-1, # use all CPU cores
            tree_method="hist", # faster for large datasets (histogram-based)
            objective="reg:squarederror" # regression task
        ))
    ])
    
    pipeline_prediction.fit(X, y)
    
    # Predict Next Month based on data
    max_month = int(features['month'].max())
    # 6. Predict Next Month (System Date ke hisaab se)
    # Aaj May hai, toh agla mahina June 2026 hona chahiye
    now = datetime.now()
    next_month_dt = now + pd.DateOffset(months=1)
    next_month_name = next_month_dt.strftime("%B %Y") # e.g., "June 2026"
    
    # Prediction ke liye features uthana
    xtest = monthly_df.groupby('product id').tail(1).copy() 
    xtest_input = xtest[feature_cols]
    
    y_pred = pipeline_prediction.predict(xtest_input)
    y_pred_df = pd.DataFrame(y_pred, columns=target_cols)
    
    if 'quantity' in y_pred_df.columns:
        y_pred_df['quantity'] = y_pred_df['quantity'].clip(lower=0)
        
    # 7. Reconstruct Result
    result = pd.concat([
        xtest[['product id', 'category']].reset_index(drop=True),
        y_pred_df.reset_index(drop=True)
    ], axis=1)
    
    # Yahan mahine ka naam set kar rahe hain
    result['month'] = next_month_name
    
    return result

def preprocess_df1(df):
    df.columns = df.columns.str.strip().str.lower()
    def find_col(possible_names):
        return next((col for col in df.columns if col in possible_names), None)

    date_cols = ['order date', 'date', 'ship date', 'order_date', 'ship_date']
    date_col = find_col(date_cols)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', dayfirst=True, errors="coerce")

    id_col = find_col(['order id', 'bill id', 'invoice id', 'order_id', 'bill_id'])
    customer_col = find_col(['customer id', 'cust id', 'client id', 'customer_id'])

    df['order id'] = df[id_col] if id_col else np.nan
    df['customer id'] = df[customer_col] if customer_col else np.nan

    if df["order id"].isna().all():
        if not df["customer id"].isna().all() and date_col:
            df['basket id'] = df['customer id'].astype(str) + "_" + df[date_col].astype(str)
        else:
            df['basket id'] = np.arange(len(df))
    else:
        df['basket id'] = df['order id']

    return df

def build_similarity_matrix(df):
    global product_category_map
    
    cat_col = next((c for c in df.columns if 'category' in c.lower() or 'segment' in c.lower()), None)
    if cat_col and 'product id' in df.columns:
        product_category_map = df.drop_duplicates('product id').set_index('product id')[cat_col].to_dict()
    else:
        product_category_map = {}

    df_prepped = preprocess_df1(df)
    df_filtered = df_prepped[['basket id', 'product id']].dropna()

    basket_item_matrix = pd.crosstab(df_filtered['basket id'], df_filtered['product id'])
    sparse_matrix = csr_matrix(basket_item_matrix.values) 
    item_similarity = cosine_similarity(sparse_matrix.T) 

    similarity_df = pd.DataFrame(
        item_similarity,
        index=basket_item_matrix.columns,
        columns=basket_item_matrix.columns
    )
    return similarity_df

def get_top_similar_products(product_id, similarity_matrix, top_n=5):
    global product_category_map
    if product_id not in similarity_matrix.columns:
        return []

    scores = similarity_matrix[product_id].drop(product_id).copy()
    if product_category_map and product_id in product_category_map:
        target_category = product_category_map[product_id]
        for idx in scores.index:
            if idx in product_category_map:
                if product_category_map[idx] == target_category:
                    scores[idx] *= 3.0  
                else:
                    scores[idx] *= 0.1  

    top_products = scores.sort_values(ascending=False).head(top_n)
    return top_products.index.tolist()

def main_model1(df):
    df = preprocess_df(df) 
    global item_similarity_df
    item_similarity_df = build_similarity_matrix(df)

def main(df):
    global item_similarity_df
    df = preprocess_df(df)
    df_show = pipelining_modelfitting(df)
    df_show['quantity'] = np.ceil(df_show['quantity']).astype(int) 
    return df_show
    
def recommend_products(product_id, top_n=5):
    global item_similarity_df
    if item_similarity_df is None:
        return []
    return get_top_similar_products(product_id, item_similarity_df, top_n)
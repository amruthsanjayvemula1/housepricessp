import os
import pandas as pd
from sklearn.model_selection import train_test_split
from src.data_preprocessing import load_data, clean_data, get_important_features
from src.feature_engineering import add_engineered_features
from src.model import create_pipeline, train_and_evaluate, save_model

def main():
    print("Starting Training Pipeline...")
    
    # 1. Load Data
    print("Loading data...")
    # Read from root since that's where the user has downloaded it
    df = load_data('train.csv') 
    
    # 2. Select Features to simplify
    print("Selecting important features...")
    df = get_important_features(df)
    
    # 3. Clean Data
    print("Cleaning data...")
    df = clean_data(df)
    
    # 4. Feature Engineering
    print("Engineering advanced features...")
    df = add_engineered_features(df)
    
    # 5. Split Data
    X = df.drop('SalePrice', axis=1)
    y = df['SalePrice']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 6. Setup Preprocessing Pipeline
    cat_cols = X_train.select_dtypes(include=['object']).columns.tolist()
    num_cols = X_train.select_dtypes(exclude=['object']).columns.tolist()
    
    # 7. Train and Evaluate Models
    models_to_train = ['linear', 'random_forest', 'xgboost']
    best_model = None
    best_rmse = float('inf')
    
    for m in models_to_train:
        print(f"\\nTraining {m}...")
        pipeline = create_pipeline(model_type=m, cat_cols=cat_cols, num_cols=num_cols)
        pipeline, rmse, r2 = train_and_evaluate(pipeline, X_train, y_train, X_test, y_test)
        print(f"{m} - RMSE: {rmse:.2f}, R2: {r2:.4f}")
        
        if rmse < best_rmse:
            best_rmse = rmse
            best_model = pipeline
            
    # 8. Save the Best Model
    print("\\nSaving the optimal model (XGBoost usually wins)...")
    if not os.path.exists('models'):
        os.makedirs('models')
    save_model(best_model, 'models/trained_model.pkl')
    
    # Save the column names and categories for Streamlit
    print("Saving metadata for UI...")
    # Neighborhood unique values are needed for UI
    neighborhoods = sorted(df['Neighborhood'].unique().tolist())
    import json
    with open('models/metadata.json', 'w') as f:
        json.dump({'neighborhoods': neighborhoods}, f)
        
    print("Training Complete! Model saved successfully.")

if __name__ == "__main__":
    main()

"""
商品データに在庫状況を追加するスクリプト
OpenAI APIを使用して各商品の在庫状況を生成する
"""

import pandas as pd
import openai
import os
from dotenv import load_dotenv
import random
import time

# 環境変数の読み込み
load_dotenv()

# OpenAI APIの設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_stock_status_for_products(products_df):
    """
    商品データフレームに在庫状況を追加する関数
    """
    # 在庫状況の選択肢
    stock_options = ["あり", "残りわずか", "なし"]
    
    # 商品の特徴に基づいて在庫状況を生成
    stock_statuses = []
    
    for index, row in products_df.iterrows():
        product_name = row['name']
        category = row['category']
        price = row['price']
        score = row['score']
        review_number = row['review_number']
        
        # 商品の人気度を評価（レビュー数とスコアから）
        popularity_score = float(score) * int(review_number)
        
        # 価格帯による在庫影響（高価格商品は在庫が多い傾向）
        price_numeric = int(price.replace(',', '').replace('円', ''))
        
        # 在庫状況を決定するロジック
        if popularity_score > 1200:  # 人気商品
            if random.random() < 0.6:
                stock_status = "残りわずか"
            elif random.random() < 0.8:
                stock_status = "あり"
            else:
                stock_status = "なし"
        elif price_numeric > 8000:  # 高価格商品
            if random.random() < 0.7:
                stock_status = "あり"
            elif random.random() < 0.9:
                stock_status = "残りわずか"
            else:
                stock_status = "なし"
        else:  # 一般商品
            if random.random() < 0.5:
                stock_status = "あり"
            elif random.random() < 0.8:
                stock_status = "残りわずか"
            else:
                stock_status = "なし"
        
        stock_statuses.append(stock_status)
        print(f"商品ID {row['id']}: {product_name} -> {stock_status}")
    
    return stock_statuses

def main():
    """メイン処理"""
    # CSVファイルの読み込み
    csv_path = "data/products.csv"
    df = pd.read_csv(csv_path)
    
    print(f"読み込み完了: {len(df)}件の商品データ")
    print("在庫状況を生成中...")
    
    # 在庫状況の生成
    stock_statuses = generate_stock_status_for_products(df)
    
    # データフレームに在庫状況列を追加
    df['stock_status'] = stock_statuses
    
    # 結果の確認
    print("\n=== 在庫状況の分布 ===")
    print(df['stock_status'].value_counts())
    
    # CSVファイルに保存
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\n更新完了: {csv_path}")
    
    # 最初の5件を表示
    print("\n=== 更新後のデータ（最初の5件）===")
    print(df[['id', 'name', 'stock_status']].head())

if __name__ == "__main__":
    main()

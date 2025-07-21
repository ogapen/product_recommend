"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import streamlit as st
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: LLMからの回答
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # LLMレスポンスのテキストを辞書に変換
    product_lines = result[0].page_content.split("\n")
    product = {item.split(": ")[0]: item.split(": ")[1] for item in product_lines}

    st.markdown("以下の商品をご提案いたします。")

    # 「商品名」と「価格」
    st.success(f"""
            商品名：{product['name']}（商品ID: {product['id']}）\n
            価格：{product['price']}
    """)

    # 在庫状況の表示
    stock_status = product.get('stock_status', 'あり')
    if stock_status == "残りわずか":
        st.error("🟡 この商品につきまして、在庫が残りわずかとなっておりますので、早めのご注文をお待ちしております。")
    elif stock_status == "なし":
        st.error("🔴 申し訳ございません。本商品は品切れとなっております。入荷をされましてはいかがでしょうか。")

    # 「商品カテゴリ」と「メーカー」と「ユーザー評価」
    st.code(f"""
        商品カテゴリ：{product['category']}\n
        メーカー：{product['maker']}\n
        評価：{product['score']}({product['review_number']}件)
    """, language=None, wrap_lines=True)

    # 商品画像
    st.image(f"images/products/{product['file_name']}", width=400)

    # 商品説明
    st.code(product['description'], language=None, wrap_lines=True)

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product["recommended_people"])

    # 商品ページのリンク
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")

    # 在庫がない場合の代替商品提案
    if stock_status == "なし":
        st.markdown("### 【在庫状況が「なし」の商品】")
        
        # 代替商品の提案
        alternative_product = find_alternative_product(product)
        if alternative_product:
            st.markdown("😊 USB充電できる加湿器")
            st.error("🔴 以下の商品をご提案いたします。")
            
            # 代替商品の情報表示
            st.success(f"""
            商品名：{alternative_product['name']}（商品ID: {alternative_product['id']}）\n
            価格：{alternative_product['price']}
            """)
            
            # 代替商品の在庫状況
            alt_stock_status = alternative_product.get('stock_status', 'あり')
            if alt_stock_status == "残りわずか":
                st.error("🟡 申し訳ございませんが、本商品は在庫切れとなっております。入荷までもうしばらくお待ちください。")
            elif alt_stock_status == "なし":
                st.error("🔴 申し訳ございません。本商品は品切れとなっております。入荷をされましてはいかがでしょうか。")
            
            # 代替商品のカテゴリと評価
            st.code(f"""
            商品カテゴリ：{alternative_product['category']}\n
            メーカー：{alternative_product['maker']}\n
            評価：{alternative_product['score']}({alternative_product['review_number']}件)
            """, language=None, wrap_lines=True)


def find_alternative_product(out_of_stock_product):
    """
    在庫切れ商品の代替商品を検索する

    Args:
        out_of_stock_product: 在庫切れの商品辞書

    Returns:
        dict: 代替商品の辞書、見つからない場合はNone
    """
    import pandas as pd
    import os
    
    # 商品データを読み込み
    csv_path = "data/products.csv"
    if not os.path.exists(csv_path):
        return None
        
    df = pd.read_csv(csv_path)
    
    # 在庫切れ商品と同じカテゴリで在庫がある商品を検索
    same_category = df[
        (df['category'] == out_of_stock_product['category']) & 
        (df['stock_status'] != 'なし') &
        (df['id'] != int(out_of_stock_product['id']))
    ]
    
    if len(same_category) > 0:
        # 評価の高い順でソートして最初の商品を返す
        best_alternative = same_category.nlargest(1, 'score').iloc[0]
        return {
            'id': str(best_alternative['id']),
            'name': best_alternative['name'],
            'category': best_alternative['category'],
            'price': best_alternative['price'],
            'maker': best_alternative['maker'],
            'score': str(best_alternative['score']),
            'review_number': str(best_alternative['review_number']),
            'stock_status': best_alternative['stock_status']
        }
    
    # 同じカテゴリがない場合、すべての在庫ありから最高評価の商品を返す
    available_products = df[df['stock_status'] != 'なし']
    if len(available_products) > 0:
        best_alternative = available_products.nlargest(1, 'score').iloc[0]
        return {
            'id': str(best_alternative['id']),
            'name': best_alternative['name'],
            'category': best_alternative['category'],
            'price': best_alternative['price'],
            'maker': best_alternative['maker'],
            'score': str(best_alternative['score']),
            'review_number': str(best_alternative['review_number']),
            'stock_status': best_alternative['stock_status']
        }
    
    return None
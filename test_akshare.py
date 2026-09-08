import akshare as ak

try:
    df = ak.futures_main_sina(symbol="RB0", start_date="20240901", end_date="20250907")
    print("数据获取成功！")
    print(f"形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print("\n前3行:")
    print(df.head(3))
    print("\n后3行:")
    print(df.tail(3))
except Exception as e:
    print(f"错误: {e}")

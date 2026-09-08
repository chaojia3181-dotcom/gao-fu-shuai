#!/usr/bin/env python3
"""
策略1：高富帅 — 期货品种扫描器
每天扫描期货品种，找出同时满足三个条件的品种
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import akshare as ak
import pandas as pd

# 品种配置：代码 -> (名称, 交易所)
SYMBOLS = {
    # 上期所
    "RB0": ("螺纹钢", "上期所"),
    "HC0": ("热轧卷板", "上期所"),
    "SS0": ("不锈钢", "上期所"),
    "CU0": ("沪铜", "上期所"),
    "AL0": ("沪铝", "上期所"),
    "ZN0": ("沪锌", "上期所"),
    "PB0": ("沪铅", "上期所"),
    "NI0": ("沪镍", "上期所"),
    "SN0": ("沪锡", "上期所"),
    "AU0": ("黄金", "上期所"),
    "AG0": ("白银", "上期所"),
    "FU0": ("燃料油", "上期所"),
    "BU0": ("沥青", "上期所"),
    "SC0": ("原油", "上期所"),
    "LU0": ("低硫燃料油", "上期所"),
    "RU0": ("天然橡胶", "上期所"),
    "NR0": ("20号胶", "上期所"),
    "SP0": ("纸浆", "上期所"),
    # 大商所
    "I0": ("铁矿石", "大商所"),
    "J0": ("焦炭", "大商所"),
    "JM0": ("焦煤", "大商所"),
    "M0": ("豆粕", "大商所"),
    "Y0": ("豆油", "大商所"),
    "P0": ("棕榈油", "大商所"),
    "C0": ("玉米", "大商所"),
    "L0": ("塑料", "大商所"),
    "PP0": ("聚丙烯", "大商所"),
    "V0": ("PVC", "大商所"),
    "EG0": ("乙二醇", "大商所"),
    "EB0": ("苯乙烯", "大商所"),
    "PG0": ("液化石油气", "大商所"),
    # 郑商所
    "TA0": ("PTA", "郑商所"),
    "MA0": ("甲醇", "郑商所"),
    "FG0": ("玻璃", "郑商所"),
    "SA0": ("纯碱", "郑商所"),
    "UR0": ("尿素", "郑商所"),
    "SR0": ("白糖", "郑商所"),
    "CF0": ("棉花", "郑商所"),
    "OI0": ("菜油", "郑商所"),
    "RM0": ("菜粕", "郑商所"),
    "AP0": ("苹果", "郑商所"),
    "PK0": ("花生", "郑商所"),
    "PF0": ("短纤", "郑商所"),
    "SF0": ("硅铁", "郑商所"),
    "SM0": ("锰硅", "郑商所"),
    # 中金所
    "IF0": ("沪深300", "中金所"),
    "IH0": ("上证50", "中金所"),
    "IC0": ("中证500", "中金所"),
    "IM0": ("中证1000", "中金所"),
    # 广期所
    "SI0": ("工业硅", "广期所"),
    "LC0": ("碳酸锂", "广期所"),
    "PX0": ("对二甲苯", "广期所"),
    "SH0": ("烧碱", "广期所"),
    "EC0": ("集运指数", "广期所"),
}


def fetch_data(symbol: str, days: int = 60) -> pd.DataFrame | None:
    """获取期货主力连续合约最近 N 天日K线数据"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 15)  # 多取一些，避免节假日

    try:
        df = ak.futures_main_sina(
            symbol=symbol,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
        if df is None or df.empty:
            return None
        # 确保按日期升序排列
        df = df.sort_values("日期").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  [警告] {symbol} 数据获取失败: {e}", file=sys.stderr)
        return None


def analyze_symbol(symbol: str, name: str, exchange: str) -> dict | None:
    """分析单个品种，返回结果字典"""
    df = fetch_data(symbol, days=60)
    if df is None or len(df) < 21:  # 需要至少21天数据（20日平均 + 今日）
        return None

    # 取最近两天
    today_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    today_hold = int(today_row["持仓量"])
    prev_hold = int(prev_row["持仓量"])
    today_vol = int(today_row["成交量"])
    today_close = float(today_row["收盘价"])
    prev_close = float(prev_row["收盘价"])

    # 计算5日平均成交量（最近5天，含今日）
    vol_5ma = int(df["成交量"].iloc[-5:].mean())
    # 计算20日平均成交量（最近20天，含今日）
    vol_20ma = int(df["成交量"].iloc[-20:].mean())

    # 条件1：高（增仓）—— 持仓量日环比 ≥ 20%
    if prev_hold > 0:
        hold_change_pct = (today_hold - prev_hold) / prev_hold * 100
    else:
        hold_change_pct = 0.0
    is_high = hold_change_pct >= 20.0

    # 条件2：富（放量）—— 当日成交量 > 5日平均 且 > 20日平均
    is_rich = today_vol > vol_5ma and today_vol > vol_20ma

    # 条件3：帅（方向）—— 价格涨跌幅绝对值 > 0.1%
    if prev_close > 0:
        price_change_pct = (today_close - prev_close) / prev_close * 100
    else:
        price_change_pct = 0.0
    is_handsome = abs(price_change_pct) > 0.1

    # 是否同时满足三个条件
    is_gao_fu_shuai = is_high and is_rich and is_handsome

    return {
        "symbol": symbol,
        "name": name,
        "exchange": exchange,
        "date": str(today_row["日期"]),
        "today_hold": today_hold,
        "prev_hold": prev_hold,
        "hold_change_pct": round(hold_change_pct, 2),
        "hold_change_amount": today_hold - prev_hold,
        "today_vol": today_vol,
        "vol_5ma": vol_5ma,
        "vol_20ma": vol_20ma,
        "today_close": round(today_close, 2),
        "prev_close": round(prev_close, 2),
        "price_change_pct": round(price_change_pct, 2),
        "is_gao_fu_shuai": is_gao_fu_shuai,
        "is_high": is_high,
        "is_rich": is_rich,
        "is_handsome": is_handsome,
    }


def scan_all() -> dict:
    """扫描所有品种"""
    scan_date = datetime.now().strftime("%Y-%m-%d")
    all_results = []
    errors = []

    print(f"开始扫描 {len(SYMBOLS)} 个品种...")

    for symbol, (name, exchange) in SYMBOLS.items():
        print(f"扫描 {symbol} ({name})...", end=" ")
        result = analyze_symbol(symbol, name, exchange)
        if result:
            print(f"✓ 持仓变化 {result['hold_change_pct']:+.2f}%, 涨跌 {result['price_change_pct']:+.2f}%")
            all_results.append(result)
        else:
            print("✗ 数据不足或获取失败")
            errors.append(symbol)

    # 按增仓幅度降序排列
    all_results.sort(key=lambda x: x["hold_change_pct"], reverse=True)

    gao_fu_shuai = [r for r in all_results if r["is_gao_fu_shuai"]]
    high_count = sum(1 for r in all_results if r["is_high"])
    up_count = sum(1 for r in all_results if r["price_change_pct"] > 0)

    # 数据日期 = 最近一个有效交易日
    data_date = all_results[0]["date"] if all_results else scan_date

    output = {
        "scan_date": scan_date,
        "data_date": data_date,
        "strategy": "高富帅",
        "conditions": {
            "high": "持仓量日环比 ≥ 20%",
            "rich": "当日成交量 > 5日平均成交量 且 > 20日平均成交量",
            "handsome": "价格涨跌幅绝对值 > 0.1%",
        },
        "total_scanned": len(SYMBOLS),
        "valid_count": len(all_results),
        "error_count": len(errors),
        "errors": errors,
        "gao_fu_shuai_count": len(gao_fu_shuai),
        "high_count": high_count,
        "up_count": up_count,
        "all_results": all_results,
        "gao_fu_shuai": gao_fu_shuai,
    }

    return output


def save_json(data: dict, path: str = "data.json") -> None:
    """保存 JSON 数据文件"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到 {path}")


def main():
    data = scan_all()
    save_json(data, "data.json")

    print(f"\n{'='*50}")
    print(f"扫描日期: {data['scan_date']}")
    print(f"数据日期: {data['data_date']}")
    print(f"扫描品种: {data['total_scanned']} 个")
    print(f"有效数据: {data['valid_count']} 个")
    print(f"失败品种: {data['error_count']} 个")
    print(f"高富帅数量: {data['gao_fu_shuai_count']} 个")
    print(f"增仓≥20%: {data['high_count']} 个")
    print(f"上涨品种: {data['up_count']} 个")
    print(f"{'='*50}")

    if data["gao_fu_shuai"]:
        print("\n⭐ 高富帅品种:")
        for item in data["gao_fu_shuai"]:
            print(f"  {item['symbol']} {item['name']} — 增仓 {item['hold_change_pct']:+.2f}%, 涨跌 {item['price_change_pct']:+.2f}%")
    else:
        print("\n😔 今日没有高富帅品种")

    return data


if __name__ == "__main__":
    main()

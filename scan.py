#!/usr/bin/env python3
"""
期货品种八种形态扫描器
基于成交量、持仓量与价格的八种组合分类
"""

import json
import sys
from datetime import datetime, timedelta

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

# 八种形态配置
PATTERNS = {
    "高富帅": {
        "label": "强上涨信号",
        "desc": "新资金大量涌入，多头主动进攻，趋势大概率延续",
        "emoji": "🏆",
        "color": "gold",
        "dims": {"price": "up", "vol": "up", "hold": "up"},
    },
    "白富美": {
        "label": "强下跌信号",
        "desc": "新资金进入做空，空头主动打压，下跌趋势确认",
        "emoji": "💎",
        "color": "purple",
        "dims": {"price": "down", "vol": "up", "hold": "up"},
    },
    "上涨乏力": {
        "label": "上涨乏力",
        "desc": "老多头获利了结，新多头接盘意愿不强，警惕反转",
        "emoji": "⚠️",
        "color": "orange",
        "dims": {"price": "up", "vol": "up", "hold": "down"},
    },
    "下跌乏力": {
        "label": "下跌乏力",
        "desc": "老空头获利了结，新空头入场意愿不强，跌势或暂缓",
        "emoji": "🛑",
        "color": "cyan",
        "dims": {"price": "down", "vol": "up", "hold": "down"},
    },
    "虚涨分歧": {
        "label": "虚涨/分歧",
        "desc": "或为空方在高位开空，多空分歧显著加大，需观望",
        "emoji": "🔶",
        "color": "yellow",
        "dims": {"price": "up", "vol": "down", "hold": "up"},
    },
    "虚跌分歧": {
        "label": "虚跌/分歧",
        "desc": "或为多头在低位抄底，多空分歧加剧，趋势不明朗",
        "emoji": "🔷",
        "color": "blue",
        "dims": {"price": "down", "vol": "down", "hold": "up"},
    },
    "涨势将尽": {
        "label": "涨势将尽",
        "desc": "多头力量明显衰退，市场缺乏新方向，趋势大概率结束",
        "emoji": "📉",
        "color": "gray",
        "dims": {"price": "up", "vol": "down", "hold": "down"},
    },
    "跌势将尽": {
        "label": "跌势将尽",
        "desc": "空头力量衰退，抛压减小，市场或迎来反转契机",
        "emoji": "📈",
        "color": "green",
        "dims": {"price": "down", "vol": "down", "hold": "down"},
    },
}


def fetch_data(symbol: str, days: int = 60) -> pd.DataFrame | None:
    """获取期货主力连续合约最近 N 天日K线数据"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 15)

    try:
        df = ak.futures_main_sina(
            symbol=symbol,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
        if df is None or df.empty:
            return None
        df = df.sort_values("日期").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  [警告] {symbol} 数据获取失败: {e}", file=sys.stderr)
        return None


def classify_pattern(
    price_change_pct: float,
    today_vol: int,
    vol_5ma: int,
    vol_20ma: int,
    hold_change_pct: float,
) -> str:
    """根据三个维度判断品种属于哪种形态"""
    # 价格方向
    is_up = price_change_pct > 0
    is_down = price_change_pct < 0

    # 成交量方向
    is_vol_up = today_vol > vol_5ma and today_vol > vol_20ma  # 放量
    is_vol_down = not is_vol_up  # 缩量

    # 持仓量方向
    is_hold_up = hold_change_pct > 0  # 增仓
    is_hold_down = hold_change_pct < 0  # 减仓

    if is_up and is_vol_up and is_hold_up:
        return "高富帅"
    elif is_down and is_vol_up and is_hold_up:
        return "白富美"
    elif is_up and is_vol_up and is_hold_down:
        return "上涨乏力"
    elif is_down and is_vol_up and is_hold_down:
        return "下跌乏力"
    elif is_up and is_vol_down and is_hold_up:
        return "虚涨分歧"
    elif is_down and is_vol_down and is_hold_up:
        return "虚跌分歧"
    elif is_up and is_vol_down and is_hold_down:
        return "涨势将尽"
    elif is_down and is_vol_down and is_hold_down:
        return "跌势将尽"
    else:
        return "未分类"  # 涨跌幅=0 的平盘情况


def analyze_symbol(symbol: str, name: str, exchange: str) -> dict | None:
    """分析单个品种，返回结果字典"""
    df = fetch_data(symbol, days=60)
    if df is None or len(df) < 21:
        return None

    today_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    today_hold = int(today_row["持仓量"])
    prev_hold = int(prev_row["持仓量"])
    today_vol = int(today_row["成交量"])
    today_close = float(today_row["收盘价"])
    prev_close = float(prev_row["收盘价"])

    vol_5ma = int(df["成交量"].iloc[-5:].mean())
    vol_20ma = int(df["成交量"].iloc[-20:].mean())

    if prev_hold > 0:
        hold_change_pct = (today_hold - prev_hold) / prev_hold * 100
    else:
        hold_change_pct = 0.0

    if prev_close > 0:
        price_change_pct = (today_close - prev_close) / prev_close * 100
    else:
        price_change_pct = 0.0

    # 八种形态分类
    pattern = classify_pattern(
        price_change_pct=price_change_pct,
        today_vol=today_vol,
        vol_5ma=vol_5ma,
        vol_20ma=vol_20ma,
        hold_change_pct=hold_change_pct,
    )

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
        "pattern": pattern,
        "dims": {
            "price": "上涨" if price_change_pct > 0 else "下跌" if price_change_pct < 0 else "平盘",
            "vol": "放量" if today_vol > vol_5ma and today_vol > vol_20ma else "缩量",
            "hold": "增仓" if hold_change_pct > 0 else "减仓" if hold_change_pct < 0 else "持平",
        },
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
            print(f"✓ {result['pattern']} | 持仓变化 {result['hold_change_pct']:+.2f}%, 涨跌 {result['price_change_pct']:+.2f}%")
            all_results.append(result)
        else:
            print("✗ 数据不足或获取失败")
            errors.append(symbol)

    # 按持仓变化幅度降序排列
    all_results.sort(key=lambda x: x["hold_change_pct"], reverse=True)

    # 按形态分组
    pattern_groups = {name: [] for name in PATTERNS}
    for r in all_results:
        if r["pattern"] in pattern_groups:
            pattern_groups[r["pattern"]].append(r)

    # 数据日期
    data_date = all_results[0]["date"] if all_results else scan_date

    # 上涨/下跌统计
    up_count = sum(1 for r in all_results if r["price_change_pct"] > 0)
    down_count = sum(1 for r in all_results if r["price_change_pct"] < 0)

    output = {
        "scan_date": scan_date,
        "data_date": data_date,
        "strategy": "八种形态",
        "total_scanned": len(SYMBOLS),
        "valid_count": len(all_results),
        "error_count": len(errors),
        "errors": errors,
        "up_count": up_count,
        "down_count": down_count,
        "patterns": {
            name: {
                "label": info["label"],
                "desc": info["desc"],
                "emoji": info["emoji"],
                "color": info["color"],
                "dims": info["dims"],
                "count": len(pattern_groups[name]),
                "items": pattern_groups[name],
            }
            for name, info in PATTERNS.items()
        },
        "all_results": all_results,
    }

    return output


def save_json(data: dict, path: str = "data.json") -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到 {path}")


def main():
    data = scan_all()
    save_json(data, "data.json")

    print(f"\n{'='*60}")
    print(f"扫描日期: {data['scan_date']}")
    print(f"数据日期: {data['data_date']}")
    print(f"扫描品种: {data['total_scanned']} 个")
    print(f"有效数据: {data['valid_count']} 个")
    print(f"失败品种: {data['error_count']} 个")
    print(f"上涨: {data['up_count']} 个 | 下跌: {data['down_count']} 个")
    print(f"{'='*60}")

    print("\n📊 八种形态分布:")
    for name, info in PATTERNS.items():
        count = data["patterns"][name]["count"]
        bar = "█" * count + "░" * (5 - min(count, 5))
        print(f"  {info['emoji']} {name:8s} ({info['label']:10s}) : {count:2d} 个  {bar}")

    # 打印有品种的非空形态
    non_empty = [(n, data["patterns"][n]) for n in PATTERNS if data["patterns"][n]["count"] > 0]
    if non_empty:
        print(f"\n{'='*60}")
        for name, p in non_empty:
            print(f"\n{PATTERNS[name]['emoji']} {name} ({PATTERNS[name]['label']}) — {p['count']} 个:")
            for item in p["items"]:
                direction = "↑" if item["price_change_pct"] > 0 else "↓"
                print(f"    {item['symbol']:5s} {item['name']:6s} {direction} 持仓{item['hold_change_pct']:+6.2f}% 价格{item['price_change_pct']:+6.2f}%")

    return data


if __name__ == "__main__":
    main()

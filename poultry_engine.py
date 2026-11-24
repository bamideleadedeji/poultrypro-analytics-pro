"""
PoultryPro Analytics — Commercial Flock Profitability, FCR & EPEF Efficiency Engine
Computes Feed Conversion Ratio (FCR), Livability %, European Production Efficiency Factor (EPEF), and batch margins.
"""

import pandas as pd

DEFAULT_FLOCKS = [
    {"Flock_ID": "FLK-2026-A1", "House": "House 1 (Tunnel)", "Birds_Placed": 10000, "Birds_Harvested": 9680, "Harvest_Age_Days": 38, "Avg_Live_Weight_Kg": 2.42, "Total_Feed_Consumed_Kg": 37480.0, "Feed_Cost_Per_Kg_USD": 0.44, "DOC_And_Med_Cost_USD": 7650.0, "Energy_And_Labor_USD": 2150.0, "FarmGate_Price_Per_Kg_USD": 1.62},
    {"Flock_ID": "FLK-2026-A2", "House": "House 2 (Tunnel)", "Birds_Placed": 10000, "Birds_Harvested": 9540, "Harvest_Age_Days": 39, "Avg_Live_Weight_Kg": 2.38, "Total_Feed_Consumed_Kg": 38120.0, "Feed_Cost_Per_Kg_USD": 0.44, "DOC_And_Med_Cost_USD": 7650.0, "Energy_And_Labor_USD": 2200.0, "FarmGate_Price_Per_Kg_USD": 1.62},
    {"Flock_ID": "FLK-2026-B1", "House": "House 3 (Open-Sided)", "Birds_Placed": 8000, "Birds_Harvested": 7480, "Harvest_Age_Days": 41, "Avg_Live_Weight_Kg": 2.25, "Total_Feed_Consumed_Kg": 30950.0, "Feed_Cost_Per_Kg_USD": 0.45, "DOC_And_Med_Cost_USD": 6200.0, "Energy_And_Labor_USD": 1750.0, "FarmGate_Price_Per_Kg_USD": 1.60},
    {"Flock_ID": "FLK-2026-B2", "House": "House 4 (Open-Sided)", "Birds_Placed": 8000, "Birds_Harvested": 7610, "Harvest_Age_Days": 40, "Avg_Live_Weight_Kg": 2.31, "Total_Feed_Consumed_Kg": 30420.0, "Feed_Cost_Per_Kg_USD": 0.45, "DOC_And_Med_Cost_USD": 6200.0, "Energy_And_Labor_USD": 1720.0, "FarmGate_Price_Per_Kg_USD": 1.60},
]


def evaluate_poultry_flocks(df: pd.DataFrame) -> dict:
    work = df.copy()
    livability_list, total_wt_list, fcr_list, epef_list, grade_list = [], [], [], [], []
    total_cost_list, cost_per_kg_list, revenue_list, net_profit_list, margin_list = [], [], [], [], []

    for _, row in work.iterrows():
        placed = max(float(row.get("Birds_Placed", 1.0)), 1.0)
        harvested = float(row.get("Birds_Harvested", placed))
        age = max(float(row.get("Harvest_Age_Days", 35.0)), 1.0)
        avg_wt = float(row.get("Avg_Live_Weight_Kg", 2.0))
        feed_kg = float(row.get("Total_Feed_Consumed_Kg", 0.0))
        feed_px = float(row.get("Feed_Cost_Per_Kg_USD", 0.44))
        doc_med = float(row.get("DOC_And_Med_Cost_USD", 0.0))
        ops_cost = float(row.get("Energy_And_Labor_USD", 0.0))
        sale_px = float(row.get("FarmGate_Price_Per_Kg_USD", 1.60))

        livability = round((harvested / placed) * 100.0, 2)
        total_live_kg = round(harvested * avg_wt, 1)
        fcr = round(feed_kg / max(total_live_kg, 1.0), 3)
        epef = round((livability * avg_wt * 100.0) / max(age * fcr, 0.01), 1)

        if epef >= 360:
            grade = "ELITE BENCHMARK (>=360)"
        elif epef >= 310:
            grade = "COMMERCIAL TARGET (310-359)"
        else:
            grade = "EFFICIENCY DRAG (<310)"

        feed_cost = feed_kg * feed_px
        tot_cost = round(feed_cost + doc_med + ops_cost, 2)
        cost_kg = round(tot_cost / max(total_live_kg, 1.0), 3)
        rev = round(total_live_kg * sale_px, 2)
        profit = round(rev - tot_cost, 2)
        margin = round((profit / max(rev, 0.01)) * 100.0, 1)

        livability_list.append(livability)
        total_wt_list.append(total_live_kg)
        fcr_list.append(fcr)
        epef_list.append(epef)
        grade_list.append(grade)
        total_cost_list.append(tot_cost)
        cost_per_kg_list.append(cost_kg)
        revenue_list.append(rev)
        net_profit_list.append(profit)
        margin_list.append(margin)

    work["Livability_Pct"] = livability_list
    work["Total_Live_Weight_Kg"] = total_wt_list
    work["FCR"] = fcr_list
    work["EPEF_Score"] = epef_list
    work["Performance_Tier"] = grade_list
    work["Total_Batch_Cost_USD"] = total_cost_list
    work["Cost_Per_Kg_Live_USD"] = cost_per_kg_list
    work["Batch_Revenue_USD"] = revenue_list
    work["Net_Batch_Profit_USD"] = net_profit_list
    work["Net_Margin_Pct"] = margin_list

    return {
        "df": work,
        "avg_fcr": round(float(work["FCR"].mean()), 3),
        "avg_epef": round(float(work["EPEF_Score"].mean()), 1),
        "avg_livability": round(float(work["Livability_Pct"].mean()), 2),
        "total_profit": round(float(work["Net_Batch_Profit_USD"].sum()), 2),
        "avg_cost_per_kg": round(float(work["Cost_Per_Kg_Live_USD"].mean()), 3),
    }

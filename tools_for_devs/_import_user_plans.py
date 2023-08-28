import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from utils.utils.ReadWrite import ReadWrite

old_plans = ReadWrite().read_csv("tools_for_devs/old_augin/tabela_planos.csv")
filtered_plan = {}
for plan in old_plans:
    for key, val in plan.items():
        filtered_plan["plan_" + key] = val
        if val == "1" and (key not in ["id", "order", "plan_limit_days_offline"]):
            filtered_plan["plan_" + key] = True
        if val == "0" and (key not in ["id", "order", "plan_limit_days_offline"]):
            filtered_plan["plan_" + key] = False
        if val == "NULL" or val == "NONE":
            filtered_plan["plan_" + key] = ""

    print("END")
print("END")

"""
agents/customer_agent.py
Queries customer DB and returns insurance policy information.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "customers.csv"
df = None

def get_df():
    global df
    if df is None:
        df = pd.read_csv(DB_PATH)
    return df


def get_customer_info(customer_id: str) -> dict:
    """
    Query insurance policy information for logged-in customer.
    Returns: {customer_id, name, phone, policies: [...]}
    """
    rows = get_df()[get_df()["customer_id"] == customer_id]
    if rows.empty:
        return {}

    customer = {
        "customer_id": customer_id,
        "name":        rows.iloc[0]["customer_name"],
        "phone":       rows.iloc[0]["phone"],
        "policies":    []
    }

    for _, row in rows.iterrows():
        policy = {
            "product_name":   row["product_name"],
            "product_id":     row["product_id"],
            "policy_number":  row["policy_number"],
            "joined_year":    int(row["joined_year"]),
            "coverage_limit": row["coverage_limit"],
            "riders":         row["riders"],
            "vehicle_number": row.get("vehicle_number", ""),
        }
        customer["policies"].append(policy)

    return customer


def get_subscribed_domains(customer_info: dict) -> list:
    """
    Returns list of domains the customer is subscribed to.
    Example: ["auto", "teeth"]
    """
    from utils.llm_setup import PRODUCT_TO_DOMAIN

    domains = []
    for policy in customer_info.get("policies", []):
        domain = PRODUCT_TO_DOMAIN.get(policy["product_id"])
        if domain and domain not in domains:
            domains.append(domain)
    return domains


def format_customer_info(customer: dict) -> str:
    """Convert customer info to LLM prompt text"""
    if not customer:
        return "No customer information"

    current_year = datetime.now().year
    lines = [f"Customer: {customer['name']} (ID: {customer['customer_id']})"]

    for p in customer["policies"]:
        years = current_year - p["joined_year"]
        line = (
            f"- {p['product_name']} | "
            f"Enrolled: {p['joined_year']} ({years} years) | "
            f"Coverage Limit: {p['coverage_limit']} | "
            f"Riders: {p['riders']}"
        )
        if p.get("vehicle_number"):
            line += f" | Vehicle Number: {p['vehicle_number']}"
        lines.append(line)

    return "\n".join(lines)


def login(customer_id: str, password: str) -> dict | None:
    """
    Simple login verification.
    Returns: customer info dict (None if failed)
    """
    rows = get_df()[
        (get_df()["customer_id"] == customer_id) &
        (get_df()["password"].astype(str) == str(password))
    ]
    if rows.empty:
        return None
    return get_customer_info(customer_id)

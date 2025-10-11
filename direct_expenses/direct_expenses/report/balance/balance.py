# Copyright (c) 2025, Future-Support and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Link",
            "options": "Account",
        },
        {
            "fieldname": "balance",
            "label": _("Balance"),
            "fieldtype": "Currency",
            "precision": 4,
        },
    ]

    where = ["`tabGL Entry`.is_cancelled = 0", "`tabAccount`.account_type IN ('Cash','Bank')"]
    params = {}

    if filters.get("account"):
        where.append("`tabGL Entry`.`account` = %(account)s")
        params["account"] = filters["account"]

    if filters.get("company"):
        where.append("`tabGL Entry`.`company` = %(company)s")
        params["company"] = filters["company"]

    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    query = f"""
        SELECT
            `tabGL Entry`.`account` AS account,
            COALESCE(SUM(`tabGL Entry`.`debit_in_account_currency`), 0)
              - COALESCE(SUM(`tabGL Entry`.`credit_in_account_currency`), 0) AS balance
        FROM `tabGL Entry`
        INNER JOIN `tabAccount` ON `tabAccount`.`name` = `tabGL Entry`.`account`
        {where_sql}
        GROUP BY `tabGL Entry`.`account`
        ORDER BY `tabGL Entry`.`account`
    """

    data = frappe.db.sql(query, params, as_dict=True)

    return columns, data
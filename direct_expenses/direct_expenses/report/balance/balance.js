// Copyright (c) 2025, Future-Support and contributors
// For license information, please see license.txt

frappe.query_reports["balance"] = {
	"filters": [
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			get_query: () => {
				const company = frappe.query_report.get_filter_value("company");
				const filters = {
					account_type: ["in", ["Cash", "Bank"]],
				};
				if (company) {
					filters.company = company;
				}
				return { filters };
			}
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company"
		}
	]
};

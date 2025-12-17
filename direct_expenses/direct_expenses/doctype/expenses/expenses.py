# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Expenses(Document):
    def before_save(self):
        # إذا كان هناك قيد مرتبط، يتم تعديله، وإلا يتم إنشاء قيد جديد
        if self.journal_no:
            x = frappe.get_doc("Journal Entry", self.journal_no)
            x.posting_date = self.posting_date
            x.company = self.company
            x.user_remark = f"مصروف رقم : {self.name}\n{self.description}"
            # تحديث الحسابات
            x.accounts = []
            x.append("accounts", {
                "account": self.debit_account,
                "debit_in_account_currency": self.amount,
                "debit": self.amount
            })
            x.append("accounts", {
                "account": self.account,
                "credit_in_account_currency": self.amount,
                "credit": self.amount
            })
            x.save()
        else:
            x = frappe.new_doc("Journal Entry")
            x.posting_date = self.posting_date
            x.company = self.company
            x.user_remark = f"مصروف رقم : {self.name}\n{self.description}"
            x.append("accounts", {
                "account": self.debit_account,
                "debit_in_account_currency": self.amount,
                "debit": self.amount
            })
            x.append("accounts", {
                "account": self.account,
                "credit_in_account_currency": self.amount,
                "credit": self.amount
            })
            x.save()
            self.journal_no = x.name

    def before_submit(self):
        if self.journal_no:
            x = frappe.get_doc("Journal Entry", self.journal_no)
            if x.docstatus != 1:
                x.submit()
        else:
            # في حال لم يوجد قيد لأي سبب
            self.before_save()
            x = frappe.get_doc("Journal Entry", self.journal_no)
            x.submit()

    def on_cancel(self):
        if self.journal_no:
            x = frappe.get_doc("Journal Entry", self.journal_no)
            if x.docstatus == 1:
                x.cancel()
        # Clear journal_no field when canceling the document
        self.db_set("journal_no", None)

    def on_trash(self):
        if self.journal_no:
            x = frappe.get_doc("Journal Entry", self.journal_no)
            if x.docstatus == 1:
                x.cancel()
            frappe.delete_doc("Journal Entry", self.journal_no, force=1)

    def on_amend(self):
        # عند عمل amend للـ Expense، يتم عمل amend للقيد
        if self.journal_no:
            x = frappe.get_doc("Journal Entry", self.journal_no)
            new_x = frappe.copy_doc(x)
            new_x.amended_from = x.name
            new_x.docstatus = 0
            new_x.insert()
            self.journal_no = new_x.name

    def after_delete(self):
        if self.journal_no:
            frappe.delete_doc("Journal Entry", self.journal_no)

    def after_cancel(self):
        if self.journal_no:
            x = frappe.get_doc("Journal Entry", self.journal_no)
            x.cancel()

    def after_save(self):
        pass  # تم تعطيل منطق Expense Claim Type بناءً على طلبك

    def from_journal_entry(self, journal_entry):
        # تعيين القيم العامة
        self.voucher_type = getattr(journal_entry, "voucher_type", None)
        self.posting_date = getattr(journal_entry, "posting_date", None)
        self.company = getattr(journal_entry, "company", None)
        self.name = getattr(journal_entry, "cheque_no", None)
        self.posting_date = getattr(
            journal_entry, "cheque_date", self.posting_date)
        self.description = getattr(journal_entry, "user_remark", None)

        # تعيين القيم من child table accounts
        accounts = getattr(journal_entry, "accounts", [])
        if len(accounts) > 0:
            self.account = getattr(accounts[0], "account", None)
            self.amount = getattr(
                accounts[0], "credit_in_account_currency", None)
        if len(accounts) > 1:
            self.debit_account = getattr(accounts[1], "account", None)
            # إذا لم يتم تعيين المبلغ من الصف الأول، خذ من الصف الثاني
            if not self.amount:
                self.amount = getattr(
                    accounts[1], "debit_in_account_currency", None)

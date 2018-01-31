# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate

def execute(filters=None):
	if not filters: filters = {}
    
	validate_filters(filters)

	columns = get_columns()
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_map(filters)
	data = []
	summ_data = []
	item_prev = ""
	item_work = ""
	item_count = 1
	tot_bal_qty = 0
	loop_count = 1

    	for (company, item, warehouse) in sorted(iwb_map):
        	qty_dict = iwb_map[(company, item, warehouse)]
		data.append(
        	    [item,
        	    item_map[item]["item_group"],
        	    item_map[item]["item_name"],
        	    item_map[item]["detail"],
        	    item_map[item]["manufacturer"],
        	    item_map[item]["manufacturer_part_no"],
        	    item_map[item]["case"],
        	    warehouse,
        	    qty_dict.bal_qty
        	])

	for rows in data:
		if item_count == 1:
			item_prev = rows[0]
			summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]
				])
		else:
			item_work = rows[0]

			if item_prev == item_work:
				item_count = item_count + 1
				tot_bal_qty =float(tot_bal_qty + rows[8])
				summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]
				])
			else:
				summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]
				])
				item_prev = item_work
		item_count = item_count + 1

	return columns, summ_data

def get_columns():
    """return columns"""

    columns = [
        _("Item")+":Link/Item:110",
        _("Item Group")+"::120",
        _("Item Name")+"::180",
        _("Detail")+"::150",
        _("MFR")+":Link/Manufacturer:110",
        _("MFR PN")+"::130",
        _("Case")+"::90",
        _("Warehouse")+":Link/Warehouse:100",
        _("Qty")+":Float:80"
    ]
    return columns

def get_conditions(filters):
    conditions = ""
    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))

    if filters.get("to_date"):
        conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters["to_date"])
    else:
        frappe.throw(_("'To Date' is required"))

    if filters.get("item_code"):
        conditions += " and sle.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

    if filters.get("item_group"):
        conditions += " and it.item_group = '%s'" % frappe.db.escape(filters.get("item_group"), percent=False)

    if filters.get("warehouse"):
        conditions += " and sle.warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)

    if filters.get("item_name"):
        conditions += " and it.item_name = '%s'" % frappe.db.escape(filters.get("item_name"), percent=False)

    if filters.get("cases"):
        conditions += " and it.case = '%s'" % frappe.db.escape(filters.get("cases"), percent=False)

    if filters.get("detail"):
        conditions += " and it.detail = '%s'" % frappe.db.escape(filters.get("detail"), percent=False)

    if filters.get("mfr"):
        conditions += " and it.manufacturer = '%s'" % frappe.db.escape(filters.get("mfr"), percent=False)

    if filters.get("mfr_pn"):
        conditions += " and it.manufacturer_part_no = '%s'" % frappe.db.escape(filters.get("mfr_pn"), percent=False)




    return conditions

def get_conditions2(filters):
    conditions = ""

    if filters.get("item_code"):
        conditions += " and it.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

    if filters.get("item_group"):
        conditions += " and it.item_group = '%s'" % frappe.db.escape(filters.get("item_group"), percent=False)

    if filters.get("item_name"):
        conditions += " and it.item_name = '%s'" % frappe.db.escape(filters.get("item_name"), percent=False)

    if filters.get("cases"):
        conditions += " and it.case = '%s'" % frappe.db.escape(filters.get("cases"), percent=False)

    if filters.get("detail"):
        conditions += " and it.detail = '%s'" % frappe.db.escape(filters.get("detail"), percent=False)

    if filters.get("mfr"):
        conditions += " and it.manufacturer = '%s'" % frappe.db.escape(filters.get("mfr"), percent=False)

    if filters.get("mfr_pn"):
        conditions += " and it.manufacturer_part_no = '%s'" % frappe.db.escape(filters.get("mfr_pn"), percent=False)


    return conditions


def get_stock_ledger_entries(filters):
    conditions = get_conditions(filters)
    return frappe.db.sql("""select sle.item_code, sle.warehouse, sle.posting_date, actual_qty, sle.valuation_rate,
            sle.company, voucher_type, qty_after_transaction, stock_value_difference
        from `tabStock Ledger Entry` sle, tabItem it
        where sle.docstatus < 2 and it.item_code = sle.item_code %s order by posting_date, posting_time, sle.name""" %
        conditions, as_dict=1)

def get_stock_ledger_entries_wo_sl(filters):
    conditions = get_conditions2(filters)
    return frappe.db.sql("""select it.item_code, "" as warehouse, "" as posting_date, 0 as actual_qty, 0 as valuation_rate,
            "" as company, "" as voucher_type, 0 as qty_after_transaction, 0 as stock_value_difference from tabItem it
            where not exists (select 1 from `tabStock Ledger Entry` sle where sle.docstatus < 2 and sle.item_code = it.item_code) %s""" % conditions, as_dict=1)

def get_item_warehouse_map(filters):
	iwb_map = {}
	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])
	kle = {}
    	sle = get_stock_ledger_entries(filters)
	kle = get_stock_ledger_entries_wo_sl(filters)
#	frappe.msgprint(_(kle))

    	for d in sle:
        	key = (d.company, d.item_code, d.warehouse)
        	if key not in iwb_map:
        		iwb_map[key] = frappe._dict({
        	        "opening_qty": 0.0, "opening_val": 0.0,
	                "in_qty": 0.0, "in_val": 0.0,
        	        "out_qty": 0.0, "out_val": 0.0,
        	        "bal_qty": 0.0, "bal_val": 0.0,
        	        "val_rate": 0.0, "uom": None
        	    })

        	qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

        	if d.voucher_type == "Stock Reconciliation":
        		qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
	        else:
        		qty_diff = flt(d.actual_qty)

	        value_diff = flt(d.stock_value_difference)

	        if d.posting_date < from_date:
        		qty_dict.opening_qty += qty_diff
		        qty_dict.opening_val += value_diff

	        elif d.posting_date >= from_date and d.posting_date <= to_date:
        		if qty_diff > 0:
        	        	qty_dict.in_qty += qty_diff
        	        	qty_dict.in_val += value_diff
		        else:
        		        qty_dict.out_qty += abs(qty_diff)
        		        qty_dict.out_val += abs(value_diff)

        	qty_dict.val_rate = d.valuation_rate
        	qty_dict.bal_qty += qty_diff
        	qty_dict.bal_val += value_diff

	if kle:    	
		for d in kle:
        		key = (d.company, d.item_code, d.warehouse)
        		if key not in iwb_map:
        			iwb_map[key] = frappe._dict({
        		        "opening_qty": 0.0, "opening_val": 0.0,
		                "in_qty": 0.0, "in_val": 0.0,
        		        "out_qty": 0.0, "out_val": 0.0,
        		        "bal_qty": 0.0, "bal_val": 0.0,
        		        "val_rate": 0.0, "uom": None
        		    })

        		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

        		if d.voucher_type == "Stock Reconciliation":
        			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		        else:
        			qty_diff = flt(d.actual_qty)

		        value_diff = flt(d.stock_value_difference)
	
       			qty_dict.opening_qty = 0
			qty_dict.opening_val = 0

		        qty_dict.in_qty = 0
        		qty_dict.in_val = 0
    			qty_dict.out_qty = 0
        		qty_dict.out_val = 0

        		qty_dict.val_rate = 0
        		qty_dict.bal_qty = 0
        		qty_dict.bal_val = 0


	return iwb_map

def get_item_details(filters):
    condition = ''
    value = ()
    if filters.get("item_code"):
        condition = "where item_code=%s"
        value = (filters["item_code"],)

    items = frappe.db.sql("""select name, item_name, stock_uom, item_group, brand, description,
                             default_supplier, manufacturer, `case`, manufacturer_part_no, detail
        from tabItem {condition}""".format(condition=condition), value, as_dict=1)

    return dict((d.name, d) for d in items)

def validate_filters(filters):
    if not (filters.get("item_code") or filters.get("warehouse")):
        sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
        if sle_count > 500000:
            frappe.throw(_("Please set filter based on Item or Warehouse"))



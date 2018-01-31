// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Simple Stock Balance"] = {
	"filters": [

                
                {      "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                       "default": frappe.datetime.get_today()
                },
                {
                        "fieldname":"to_date",
                        "label": __("Committed Delivery To Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today()
                },
        	{
	            "fieldname": "item_code",
        	    "label": __("Item"),
        	    "fieldtype": "Link",
        	    "options": "Item"
        	},
 	{
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        },

                {
                        "fieldname":"item_name",
                        "label": __("Item Name"),
                        "fieldtype": "Data"
                },

		{
                        "fieldname":"cases",
                        "label": __("Case"),
			"fieldtype": "Data"

					

                },

		{
                        "fieldname":"warehouse",
                        "label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
				

                },
		
                {
                        "fieldname":"detail",
                        "label": __("Detail"),
                        "fieldtype": "Data"
                },
		
		{
                        "fieldname":"mfr",
                        "label": __("MFR"),
                        "fieldtype": "Link",
			"options": "Manufacturer"
                },

{
                        "fieldname":"mfr_pn",
                        "label": __("MFR PN"),
                        "fieldtype": "Data"
                },
		
		
                                  
                
        ]
}


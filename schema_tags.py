"""
Schema Tags - Semantic metadata for database columns.

Tags help the agent understand what each column represents,
improving query accuracy by providing business context.
"""

import sqlite3

DB_PATH = "shop.db"

# Tag definitions for each table.column
COLUMN_TAGS = {
    # =========================================================================
    # CATEGORIES TABLE
    # =========================================================================
    "categories": {
        "id": {
            "tag": "category_id",
            "description": "Unique identifier for each product category",
            "examples": "1, 2, 3",
            "use_for": "joining with products, identifying specific categories"
        },
        "name": {
            "tag": "category_name",
            "description": "Name of the product category",
            "examples": "Electronics, Furniture, Clothing",
            "use_for": "displaying category, filtering products by category"
        },
        "description": {
            "tag": "category_description",
            "description": "Detailed description of what products belong in this category",
            "examples": "Electronic devices and accessories",
            "use_for": "understanding category scope"
        },
        "parent_category_id": {
            "tag": "parent_category",
            "description": "Foreign key to parent category for hierarchical categorization",
            "examples": "1, 2, NULL",
            "use_for": "building category trees, subcategory relationships"
        },
        "created_at": {
            "tag": "category_created",
            "description": "When the category was created",
            "examples": "2024-01-15 10:30:00",
            "use_for": "tracking category additions"
        }
    },

    # =========================================================================
    # SUPPLIERS TABLE
    # =========================================================================
    "suppliers": {
        "id": {
            "tag": "supplier_id",
            "description": "Unique identifier for each supplier",
            "examples": "1, 2, 3",
            "use_for": "joining with products, identifying specific suppliers"
        },
        "name": {
            "tag": "supplier_name",
            "description": "Business name of the supplier",
            "examples": "TechCorp Industries, GameTech Solutions",
            "use_for": "displaying supplier identity, searching by name"
        },
        "email": {
            "tag": "supplier_email",
            "description": "Supplier's contact email address",
            "examples": "sales@techcorp.com",
            "use_for": "supplier contact, communication"
        },
        "phone": {
            "tag": "supplier_phone",
            "description": "Supplier's phone number",
            "examples": "555-0101",
            "use_for": "supplier contact"
        },
        "address": {
            "tag": "supplier_address",
            "description": "Street address of supplier",
            "examples": "100 Tech Park Dr",
            "use_for": "supplier location, shipping origin"
        },
        "city": {
            "tag": "supplier_city",
            "description": "City where supplier is located",
            "examples": "San Jose, Seattle",
            "use_for": "geographic filtering of suppliers"
        },
        "state": {
            "tag": "supplier_state",
            "description": "State/province where supplier is located",
            "examples": "CA, WA, TX",
            "use_for": "regional supplier analysis"
        },
        "country": {
            "tag": "supplier_country",
            "description": "Country where supplier is located",
            "examples": "USA, Canada",
            "use_for": "international supplier filtering"
        },
        "rating": {
            "tag": "supplier_rating",
            "description": "Supplier performance rating (1-5 scale)",
            "examples": "4.5, 3.8",
            "use_for": "supplier quality analysis, vendor selection"
        },
        "active": {
            "tag": "supplier_active",
            "description": "Whether supplier is currently active (1=active, 0=inactive)",
            "examples": "1, 0",
            "use_for": "filtering active suppliers"
        }
    },

    # =========================================================================
    # DEPARTMENTS TABLE
    # =========================================================================
    "departments": {
        "id": {
            "tag": "department_id",
            "description": "Unique identifier for each department",
            "examples": "1, 2, 3",
            "use_for": "joining with employees, identifying departments"
        },
        "name": {
            "tag": "department_name",
            "description": "Name of the department",
            "examples": "Sales, Customer Support, Warehouse",
            "use_for": "displaying department, filtering employees"
        },
        "description": {
            "tag": "department_description",
            "description": "Description of department responsibilities",
            "examples": "Handles customer sales and account management",
            "use_for": "understanding department function"
        },
        "budget": {
            "tag": "department_budget",
            "description": "Annual budget allocated to the department",
            "examples": "250000, 500000",
            "use_for": "budget analysis, financial planning"
        }
    },

    # =========================================================================
    # EMPLOYEES TABLE
    # =========================================================================
    "employees": {
        "id": {
            "tag": "employee_id",
            "description": "Unique identifier for each employee",
            "examples": "1, 2, 3",
            "use_for": "joining with orders, identifying employees"
        },
        "first_name": {
            "tag": "employee_first_name",
            "description": "Employee's first name",
            "examples": "John, Sarah",
            "use_for": "displaying employee name"
        },
        "last_name": {
            "tag": "employee_last_name",
            "description": "Employee's last name",
            "examples": "Smith, Johnson",
            "use_for": "displaying employee name, searching"
        },
        "email": {
            "tag": "employee_email",
            "description": "Employee's work email address",
            "examples": "john.smith@shop.com",
            "use_for": "employee contact, unique lookup"
        },
        "phone": {
            "tag": "employee_phone",
            "description": "Employee's phone number",
            "examples": "555-123-4567",
            "use_for": "employee contact"
        },
        "department_id": {
            "tag": "employee_department",
            "description": "Foreign key to departments - which department employee belongs to",
            "examples": "1, 2, 3",
            "use_for": "joining with departments, organizational analysis"
        },
        "manager_id": {
            "tag": "employee_manager",
            "description": "Foreign key to employees - who manages this employee",
            "examples": "1, 5, NULL",
            "use_for": "building org hierarchy, reporting structure"
        },
        "hire_date": {
            "tag": "employee_hire_date",
            "description": "Date when employee was hired",
            "examples": "2022-03-15",
            "use_for": "tenure calculation, hiring trends"
        },
        "salary": {
            "tag": "employee_salary",
            "description": "Employee's annual salary",
            "examples": "75000, 120000",
            "use_for": "compensation analysis, payroll calculations"
        },
        "commission_pct": {
            "tag": "employee_commission",
            "description": "Commission percentage for sales employees",
            "examples": "0.05, 0.10, 0",
            "use_for": "sales compensation, total earnings calculation"
        },
        "active": {
            "tag": "employee_active",
            "description": "Whether employee is currently active (1=active, 0=inactive)",
            "examples": "1, 0",
            "use_for": "filtering current employees"
        }
    },

    # =========================================================================
    # CUSTOMERS TABLE
    # =========================================================================
    "customers": {
        "id": {
            "tag": "customer_id",
            "description": "Unique identifier for each customer",
            "examples": "1, 2, 3",
            "use_for": "joining with orders, identifying specific customers"
        },
        "first_name": {
            "tag": "customer_first_name",
            "description": "Customer's first name",
            "examples": "Alice, Bob",
            "use_for": "displaying customer name"
        },
        "last_name": {
            "tag": "customer_last_name",
            "description": "Customer's last name",
            "examples": "Johnson, Smith",
            "use_for": "displaying customer name, searching"
        },
        "email": {
            "tag": "customer_email",
            "description": "Customer's email address (unique)",
            "examples": "alice@email.com",
            "use_for": "contact info, unique customer lookup"
        },
        "phone": {
            "tag": "customer_phone",
            "description": "Customer's phone number",
            "examples": "555-123-4567",
            "use_for": "customer contact"
        },
        "address": {
            "tag": "customer_address",
            "description": "Customer's street address",
            "examples": "123 Main St",
            "use_for": "shipping address, location data"
        },
        "city": {
            "tag": "customer_city",
            "description": "City where the customer is located",
            "examples": "New York, Los Angeles, Chicago",
            "use_for": "geographic filtering, location-based analysis"
        },
        "state": {
            "tag": "customer_state",
            "description": "State/province where customer is located",
            "examples": "NY, CA, TX",
            "use_for": "regional analysis, state-level filtering"
        },
        "postal_code": {
            "tag": "customer_postal_code",
            "description": "Customer's postal/ZIP code",
            "examples": "10001, 90210",
            "use_for": "delivery zone, geographic precision"
        },
        "country": {
            "tag": "customer_country",
            "description": "Country where customer is located",
            "examples": "USA, Canada, UK",
            "use_for": "international filtering, market analysis"
        },
        "date_of_birth": {
            "tag": "customer_dob",
            "description": "Customer's date of birth",
            "examples": "1985-03-15",
            "use_for": "age calculation, demographic analysis"
        },
        "gender": {
            "tag": "customer_gender",
            "description": "Customer's gender",
            "examples": "Male, Female, Other",
            "use_for": "demographic analysis"
        },
        "membership_tier": {
            "tag": "customer_tier",
            "description": "Customer loyalty program tier",
            "examples": "Bronze, Silver, Gold, Platinum",
            "use_for": "VIP filtering, loyalty analysis, tier-based pricing"
        },
        "loyalty_points": {
            "tag": "customer_points",
            "description": "Accumulated loyalty/reward points",
            "examples": "1500, 5000",
            "use_for": "rewards analysis, customer value"
        },
        "total_spent": {
            "tag": "customer_lifetime_value",
            "description": "Total amount customer has spent (calculated)",
            "examples": "2500.50, 15000.00",
            "use_for": "customer value analysis, high-value customer identification"
        },
        "order_count": {
            "tag": "customer_order_count",
            "description": "Total number of orders placed (calculated)",
            "examples": "5, 25",
            "use_for": "purchase frequency analysis, engagement metrics"
        },
        "preferred_payment": {
            "tag": "customer_payment_preference",
            "description": "Customer's preferred payment method",
            "examples": "Credit Card, PayPal",
            "use_for": "payment analysis, checkout optimization"
        },
        "newsletter_subscribed": {
            "tag": "customer_newsletter",
            "description": "Whether customer is subscribed to newsletter (1=yes, 0=no)",
            "examples": "1, 0",
            "use_for": "marketing targeting, email lists"
        },
        "account_status": {
            "tag": "customer_status",
            "description": "Current status of customer account",
            "examples": "active, suspended, closed",
            "use_for": "filtering active customers"
        },
        "last_login": {
            "tag": "customer_last_login",
            "description": "When the customer last logged in",
            "examples": "2026-01-20 14:30:00",
            "use_for": "engagement analysis, inactive customer identification"
        },
        "created_at": {
            "tag": "customer_registration_date",
            "description": "When the customer account was created",
            "examples": "2024-01-15 10:30:00",
            "use_for": "customer tenure, cohort analysis, time-based filtering"
        }
    },

    # =========================================================================
    # PRODUCTS TABLE
    # =========================================================================
    "products": {
        "id": {
            "tag": "product_id",
            "description": "Unique identifier for each product",
            "examples": "1, 2, 3",
            "use_for": "joining with order_items, identifying specific products"
        },
        "sku": {
            "tag": "product_sku",
            "description": "Stock Keeping Unit - unique product code",
            "examples": "SKU-01-0001",
            "use_for": "inventory management, unique product lookup"
        },
        "name": {
            "tag": "product_name",
            "description": "Name/title of the product",
            "examples": "Laptop Pro 15, Wireless Mouse",
            "use_for": "displaying product identity, searching by name"
        },
        "description": {
            "tag": "product_description",
            "description": "Detailed product description",
            "examples": "High-performance laptop with 15-inch display",
            "use_for": "product details, search matching"
        },
        "category_id": {
            "tag": "product_category",
            "description": "Foreign key to categories table",
            "examples": "1, 2, 3",
            "use_for": "joining with categories, filtering by type"
        },
        "brand": {
            "tag": "product_brand",
            "description": "Brand/manufacturer of the product",
            "examples": "TechCorp, GameTech, AudioMax",
            "use_for": "brand filtering, manufacturer analysis"
        },
        "price": {
            "tag": "product_price",
            "description": "Current selling price in dollars",
            "examples": "999.99, 29.99",
            "use_for": "price filtering, revenue projections"
        },
        "cost": {
            "tag": "product_cost",
            "description": "Cost to acquire/manufacture the product",
            "examples": "450.00, 15.00",
            "use_for": "profit margin calculations, cost analysis"
        },
        "weight": {
            "tag": "product_weight",
            "description": "Product weight in pounds",
            "examples": "2.1, 0.5",
            "use_for": "shipping calculations, logistics"
        },
        "stock": {
            "tag": "product_stock",
            "description": "Current quantity in stock",
            "examples": "50, 200, 0",
            "use_for": "inventory checks, stock alerts, availability filtering"
        },
        "reorder_level": {
            "tag": "product_reorder_level",
            "description": "Stock level at which to reorder",
            "examples": "10, 25",
            "use_for": "inventory management, reorder alerts"
        },
        "supplier_id": {
            "tag": "product_supplier",
            "description": "Foreign key to suppliers table",
            "examples": "1, 2, 3",
            "use_for": "joining with suppliers, supplier analysis"
        },
        "rating": {
            "tag": "product_rating",
            "description": "Average customer rating (1-5 scale)",
            "examples": "4.5, 3.8",
            "use_for": "quality filtering, top-rated products"
        },
        "review_count": {
            "tag": "product_review_count",
            "description": "Number of customer reviews",
            "examples": "150, 25",
            "use_for": "popularity analysis, social proof metrics"
        },
        "is_active": {
            "tag": "product_active",
            "description": "Whether product is currently for sale (1=yes, 0=no)",
            "examples": "1, 0",
            "use_for": "filtering available products"
        },
        "is_featured": {
            "tag": "product_featured",
            "description": "Whether product is featured/promoted (1=yes, 0=no)",
            "examples": "1, 0",
            "use_for": "featured product listings"
        },
        "created_at": {
            "tag": "product_created",
            "description": "When product was added to catalog",
            "examples": "2024-01-15 10:30:00",
            "use_for": "new product identification"
        },
        "updated_at": {
            "tag": "product_updated",
            "description": "When product was last updated",
            "examples": "2026-01-15 10:30:00",
            "use_for": "tracking product changes"
        }
    },

    # =========================================================================
    # SHIPPING METHODS TABLE
    # =========================================================================
    "shipping_methods": {
        "id": {
            "tag": "shipping_method_id",
            "description": "Unique identifier for shipping method",
            "examples": "1, 2, 3",
            "use_for": "joining with orders"
        },
        "name": {
            "tag": "shipping_method_name",
            "description": "Name of shipping method",
            "examples": "Standard, Express, Overnight",
            "use_for": "displaying shipping option"
        },
        "price": {
            "tag": "shipping_price",
            "description": "Cost of shipping method",
            "examples": "5.99, 12.99, 24.99",
            "use_for": "shipping cost calculations"
        },
        "min_days": {
            "tag": "shipping_min_days",
            "description": "Minimum delivery days",
            "examples": "1, 3, 5",
            "use_for": "delivery time estimates"
        },
        "max_days": {
            "tag": "shipping_max_days",
            "description": "Maximum delivery days",
            "examples": "3, 7, 14",
            "use_for": "delivery time estimates"
        },
        "is_active": {
            "tag": "shipping_active",
            "description": "Whether shipping method is available",
            "examples": "1, 0",
            "use_for": "filtering available shipping options"
        }
    },

    # =========================================================================
    # DISCOUNT CODES TABLE
    # =========================================================================
    "discount_codes": {
        "id": {
            "tag": "discount_id",
            "description": "Unique identifier for discount code",
            "examples": "1, 2, 3",
            "use_for": "joining with orders"
        },
        "code": {
            "tag": "discount_code",
            "description": "The actual discount code string",
            "examples": "SAVE10, WELCOME5",
            "use_for": "discount lookup, validation"
        },
        "discount_value": {
            "tag": "discount_amount",
            "description": "Value of the discount",
            "examples": "10, 15, 25",
            "use_for": "calculating discounts"
        },
        "discount_type": {
            "tag": "discount_type",
            "description": "Type of discount (percentage or fixed)",
            "examples": "percentage, fixed",
            "use_for": "discount calculation method"
        },
        "valid_from": {
            "tag": "discount_start",
            "description": "Start date for discount validity",
            "examples": "2024-01-01",
            "use_for": "validating discount applicability"
        },
        "valid_until": {
            "tag": "discount_end",
            "description": "End date for discount validity",
            "examples": "2025-12-31",
            "use_for": "validating discount applicability"
        },
        "minimum_order": {
            "tag": "discount_minimum",
            "description": "Minimum order amount to apply discount",
            "examples": "50, 100",
            "use_for": "discount eligibility check"
        },
        "usage_count": {
            "tag": "discount_usage",
            "description": "How many times code has been used",
            "examples": "50, 150",
            "use_for": "tracking discount popularity"
        },
        "is_active": {
            "tag": "discount_active",
            "description": "Whether discount is currently active",
            "examples": "1, 0",
            "use_for": "filtering valid discounts"
        }
    },

    # =========================================================================
    # ORDERS TABLE
    # =========================================================================
    "orders": {
        "id": {
            "tag": "order_id",
            "description": "Unique identifier for each order",
            "examples": "1, 2, 3",
            "use_for": "joining with order_items, identifying specific orders"
        },
        "order_number": {
            "tag": "order_number",
            "description": "Human-readable order reference number",
            "examples": "ORD-100001, ORD-100002",
            "use_for": "customer-facing order reference"
        },
        "customer_id": {
            "tag": "ordering_customer",
            "description": "Foreign key to customers table - who placed the order",
            "examples": "1, 2, 3",
            "use_for": "joining with customers, customer order history"
        },
        "employee_id": {
            "tag": "order_handler",
            "description": "Foreign key to employees - who processed the order",
            "examples": "1, 5, NULL",
            "use_for": "joining with employees, sales attribution"
        },
        "order_date": {
            "tag": "purchase_date",
            "description": "When the order was placed",
            "examples": "2026-01-20 14:30:00",
            "use_for": "time-based filtering, sales trends, date range queries"
        },
        "required_date": {
            "tag": "delivery_deadline",
            "description": "Requested delivery date",
            "examples": "2026-01-25",
            "use_for": "delivery scheduling, SLA tracking"
        },
        "shipped_date": {
            "tag": "ship_date",
            "description": "When the order was shipped",
            "examples": "2026-01-21, NULL",
            "use_for": "fulfillment tracking, shipping metrics"
        },
        "status": {
            "tag": "order_status",
            "description": "Current state of the order",
            "examples": "pending, processing, shipped, delivered, cancelled",
            "use_for": "filtering by fulfillment state, order tracking"
        },
        "shipping_method_id": {
            "tag": "order_shipping_method",
            "description": "Foreign key to shipping_methods table",
            "examples": "1, 2, 3",
            "use_for": "joining with shipping_methods"
        },
        "shipping_address": {
            "tag": "ship_to_address",
            "description": "Delivery street address",
            "examples": "456 Oak Ave",
            "use_for": "delivery information"
        },
        "shipping_city": {
            "tag": "ship_to_city",
            "description": "Delivery city",
            "examples": "New York, Los Angeles",
            "use_for": "delivery location, shipping analysis"
        },
        "shipping_state": {
            "tag": "ship_to_state",
            "description": "Delivery state/province",
            "examples": "NY, CA",
            "use_for": "regional shipping analysis"
        },
        "shipping_postal_code": {
            "tag": "ship_to_postal",
            "description": "Delivery postal/ZIP code",
            "examples": "10001, 90210",
            "use_for": "delivery zone analysis"
        },
        "shipping_country": {
            "tag": "ship_to_country",
            "description": "Delivery country",
            "examples": "USA, Canada",
            "use_for": "international shipping analysis"
        },
        "subtotal": {
            "tag": "order_subtotal",
            "description": "Sum of all line items before tax/shipping",
            "examples": "150.00, 500.00",
            "use_for": "order value analysis"
        },
        "shipping_cost": {
            "tag": "order_shipping_cost",
            "description": "Shipping charges for the order",
            "examples": "5.99, 12.99",
            "use_for": "shipping revenue analysis"
        },
        "tax_amount": {
            "tag": "order_tax",
            "description": "Tax amount charged",
            "examples": "12.00, 40.00",
            "use_for": "tax reporting"
        },
        "discount_amount": {
            "tag": "order_discount",
            "description": "Total discount applied",
            "examples": "0, 15.00",
            "use_for": "discount impact analysis"
        },
        "total_amount": {
            "tag": "order_total",
            "description": "Final order total (subtotal + shipping + tax - discount)",
            "examples": "167.99, 545.00",
            "use_for": "revenue calculations, order value analysis"
        },
        "payment_method": {
            "tag": "order_payment_method",
            "description": "How the customer paid",
            "examples": "Credit Card, PayPal, Apple Pay",
            "use_for": "payment analysis"
        },
        "payment_status": {
            "tag": "order_payment_status",
            "description": "Status of payment",
            "examples": "pending, completed, failed, refunded",
            "use_for": "payment tracking, revenue recognition"
        },
        "discount_code_id": {
            "tag": "order_discount_code",
            "description": "Foreign key to discount_codes table",
            "examples": "1, 2, NULL",
            "use_for": "discount code usage analysis"
        },
        "notes": {
            "tag": "order_notes",
            "description": "Special instructions or notes",
            "examples": "Leave at door",
            "use_for": "order handling"
        },
        "created_at": {
            "tag": "order_created",
            "description": "When the order record was created",
            "examples": "2026-01-20 14:30:00",
            "use_for": "order tracking"
        }
    },

    # =========================================================================
    # ORDER ITEMS TABLE
    # =========================================================================
    "order_items": {
        "id": {
            "tag": "line_item_id",
            "description": "Unique identifier for each order line item",
            "examples": "1, 2, 3",
            "use_for": "identifying specific line items"
        },
        "order_id": {
            "tag": "parent_order",
            "description": "Foreign key to orders - which order this item belongs to",
            "examples": "1, 2, 3",
            "use_for": "joining with orders, grouping items by order"
        },
        "product_id": {
            "tag": "ordered_product",
            "description": "Foreign key to products - which product was ordered",
            "examples": "1, 2, 3",
            "use_for": "joining with products, product sales analysis"
        },
        "quantity": {
            "tag": "quantity_ordered",
            "description": "Number of units ordered",
            "examples": "1, 2, 3",
            "use_for": "calculating totals, volume analysis"
        },
        "unit_price": {
            "tag": "price_at_purchase",
            "description": "Price per unit at time of order (may differ from current product price)",
            "examples": "999.99, 29.99",
            "use_for": "revenue calculations, historical pricing"
        },
        "discount_pct": {
            "tag": "line_discount",
            "description": "Discount percentage applied to this line item",
            "examples": "0, 0.05, 0.10",
            "use_for": "discount analysis"
        },
        "line_total": {
            "tag": "line_total",
            "description": "Total for this line item (quantity * unit_price * (1 - discount_pct))",
            "examples": "999.99, 59.98",
            "use_for": "revenue calculations, order value breakdown"
        }
    },

    # =========================================================================
    # REVIEWS TABLE
    # =========================================================================
    "reviews": {
        "id": {
            "tag": "review_id",
            "description": "Unique identifier for each review",
            "examples": "1, 2, 3",
            "use_for": "identifying specific reviews"
        },
        "product_id": {
            "tag": "reviewed_product",
            "description": "Foreign key to products - which product is being reviewed",
            "examples": "1, 2, 3",
            "use_for": "joining with products, product feedback analysis"
        },
        "customer_id": {
            "tag": "reviewer",
            "description": "Foreign key to customers - who wrote the review",
            "examples": "1, 2, 3",
            "use_for": "joining with customers, reviewer analysis"
        },
        "order_id": {
            "tag": "review_order",
            "description": "Foreign key to orders - which order prompted the review",
            "examples": "1, 2, NULL",
            "use_for": "verified purchase tracking"
        },
        "rating": {
            "tag": "review_rating",
            "description": "Star rating (1-5)",
            "examples": "5, 4, 3, 2, 1",
            "use_for": "product quality analysis, satisfaction metrics"
        },
        "title": {
            "tag": "review_title",
            "description": "Review headline/title",
            "examples": "Great product!, Disappointed",
            "use_for": "sentiment analysis, review display"
        },
        "comment": {
            "tag": "review_comment",
            "description": "Full review text",
            "examples": "This product exceeded my expectations...",
            "use_for": "detailed feedback, text analysis"
        },
        "helpful_votes": {
            "tag": "review_helpful",
            "description": "Number of helpful votes from other customers",
            "examples": "15, 0",
            "use_for": "review quality ranking"
        },
        "verified_purchase": {
            "tag": "review_verified",
            "description": "Whether reviewer actually purchased the product (1=yes, 0=no)",
            "examples": "1, 0",
            "use_for": "filtering trustworthy reviews"
        },
        "created_at": {
            "tag": "review_date",
            "description": "When the review was written",
            "examples": "2026-01-15 10:30:00",
            "use_for": "review freshness, time-based analysis"
        }
    },

    # =========================================================================
    # INVENTORY LOG TABLE
    # =========================================================================
    "inventory_log": {
        "id": {
            "tag": "inventory_log_id",
            "description": "Unique identifier for inventory log entry",
            "examples": "1, 2, 3",
            "use_for": "identifying specific log entries"
        },
        "product_id": {
            "tag": "inventory_product",
            "description": "Foreign key to products - which product's inventory changed",
            "examples": "1, 2, 3",
            "use_for": "joining with products, inventory tracking"
        },
        "change_type": {
            "tag": "inventory_change_type",
            "description": "Type of inventory change",
            "examples": "sale, restock, adjustment, return",
            "use_for": "inventory movement analysis"
        },
        "quantity_change": {
            "tag": "inventory_quantity_change",
            "description": "Amount of change (negative for decreases)",
            "examples": "-5, 100, -1",
            "use_for": "inventory flow analysis"
        },
        "quantity_after": {
            "tag": "inventory_quantity_after",
            "description": "Stock level after this change",
            "examples": "45, 150",
            "use_for": "historical stock levels"
        },
        "reference_type": {
            "tag": "inventory_reference_type",
            "description": "What triggered this change (order, purchase_order, etc.)",
            "examples": "order, purchase_order, adjustment",
            "use_for": "tracking change sources"
        },
        "reference_id": {
            "tag": "inventory_reference_id",
            "description": "ID of the related record",
            "examples": "1234, 5678",
            "use_for": "linking to source records"
        },
        "notes": {
            "tag": "inventory_notes",
            "description": "Additional notes about the change",
            "examples": "Damaged goods returned",
            "use_for": "audit trail"
        },
        "created_at": {
            "tag": "inventory_change_date",
            "description": "When the inventory change occurred",
            "examples": "2026-01-15 10:30:00",
            "use_for": "inventory timeline, auditing"
        }
    }
}


def create_tags_table(db_path: str = DB_PATH):
    """Create and populate the column_tags metadata table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create metadata table
    cursor.execute("DROP TABLE IF EXISTS column_tags")
    cursor.execute("""
        CREATE TABLE column_tags (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            tag TEXT NOT NULL,
            description TEXT,
            examples TEXT,
            use_for TEXT,
            PRIMARY KEY (table_name, column_name)
        )
    """)

    # Insert tag data
    for table, columns in COLUMN_TAGS.items():
        for column, meta in columns.items():
            cursor.execute("""
                INSERT INTO column_tags (table_name, column_name, tag, description, examples, use_for)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                table,
                column,
                meta["tag"],
                meta["description"],
                meta["examples"],
                meta["use_for"]
            ))

    conn.commit()
    conn.close()
    print(f"Created column_tags table with {sum(len(cols) for cols in COLUMN_TAGS.values())} entries")


def get_all_tags(db_path: str = DB_PATH) -> dict:
    """Load all tags from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name, column_name, tag, description, examples, use_for
        FROM column_tags
        ORDER BY table_name, column_name
    """)

    tags = {}
    for row in cursor.fetchall():
        table, column, tag, desc, examples, use_for = row
        if table not in tags:
            tags[table] = {}
        tags[table][column] = {
            "tag": tag,
            "description": desc,
            "examples": examples,
            "use_for": use_for
        }

    conn.close()
    return tags


def format_tags_for_prompt(tags: dict) -> str:
    """Format tags as a clear reference for the LLM."""
    lines = ["COLUMN TAGS & SEMANTIC METADATA:", "=" * 50]

    for table, columns in tags.items():
        lines.append(f"\n[{table}]")
        for column, meta in columns.items():
            lines.append(f"  {column}:")
            lines.append(f"    tag: {meta['tag']}")
            lines.append(f"    meaning: {meta['description']}")
            lines.append(f"    use for: {meta['use_for']}")

    return "\n".join(lines)


if __name__ == "__main__":
    create_tags_table()

    # Display the tags
    tags = get_all_tags()
    print("\n" + format_tags_for_prompt(tags))

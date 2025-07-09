# transform.py

import pandas as pd
import numpy as np
from loader import load_orders, load_products

def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = orders.copy()

    # Fill missing countries
    orders['billing_address_country'] = orders['billing_address_country'].fillna('Unknown')

    # Fix corrupted encoding for Côte d'Ivoire
    # Fix corrupted encoding for Côte d'Ivoire (multiple variants)
    orders['billing_address_country'] = orders['billing_address_country'].replace({
    "C√¥te d'Ivoire": "Côte d'Ivoire",
    "C√¥te d&#39;Ivoire": "Côte d'Ivoire"
})

    # Drop ZIP code column
    if 'billing_address_zip' in orders.columns:
        orders.drop(columns=['billing_address_zip'], inplace=True)

    # Convert date columns
    date_cols = ['created_at', 'processed_at', 'cancelled_at', 'first_date_order']
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # Add cancellation flag
    orders['is_cancelled'] = orders['cancelled_at'].notnull()

    # Add month column
    orders['order_month'] = orders['created_at'].dt.tz_localize(None).dt.to_period('M')

    return orders


def deduplicate_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = orders.copy()

    # Identify conflicting order_numbers
    order_to_customer_counts = orders.groupby('order_number')['customer_id'].nunique()
    conflicting_orders = order_to_customer_counts[order_to_customer_counts > 1].index

    # Remove orders with reused order_number across customers
    orders = orders[~orders['order_number'].isin(conflicting_orders)].copy()

    # Drop exact duplicates
    orders = orders.drop_duplicates(subset=['customer_id', 'order_number'])
    orders.reset_index(drop=True, inplace=True)

    return orders


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    products = products.copy()
    return products.drop_duplicates(subset=['product_title'])


def enrich_orders_with_products(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    orders = orders.copy()
    products = products.copy()

    # Explode product list
    orders['product_list'] = orders['product_items'].str.split(r',\s*')
    orders_exploded = orders.explode('product_list')
    orders_exploded.rename(columns={'product_list': 'product_title'}, inplace=True)
    # Merge
    enriched = orders_exploded.merge(products, on='product_title', how='left')

    return enriched


def create_product_level_df(enriched: pd.DataFrame) -> pd.DataFrame:
    df = enriched.copy()

    df['gross_order_total'] = df.groupby('order_number')['product_price'].transform('sum')
    df['discount_allocated'] = (df['product_price'] / df['gross_order_total']) * df['total_discounts']
    df['net_price'] = df['product_price'] - df['discount_allocated']

    product_level_df = df[[
        'order_number', 'customer_id', 'processed_at', 'billing_address_country',
        'cancelled_at', 'cancel_reason', 'product_title', 'product_category',
        'product_type', 'product_price', 'discount_allocated', 'net_price'
    ]]

    return product_level_df


def create_order_level_df(product_level_df: pd.DataFrame) -> pd.DataFrame:
    df = product_level_df.copy()

    order_level_df = df.groupby('order_number').agg({
        'customer_id': 'first',
        'processed_at': 'first',
        'billing_address_country': 'first',
        'cancelled_at': 'first',
        'cancel_reason': 'first',
        'discount_allocated': 'sum',
        'product_price': 'sum',
        'net_price': 'sum'
    }).rename(columns={
        'product_price': 'gross_revenue',
        'discount_allocated': 'total_discounts',
        'net_price': 'net_revenue'
    }).reset_index()

    # Derive human-readable order status
    order_level_df['order_status'] = order_level_df['cancelled_at'].notnull().map({
    True: "Cancelled", 
    False: "Delivered"
})
    return order_level_df


def run_sanity_checks(product_level_df: pd.DataFrame, order_level_df: pd.DataFrame) -> None:
    # Net Revenue Check
    net_price_sum_check = product_level_df.groupby('order_number')['net_price'].sum().reset_index(name='product_level_net')
    revenue_check = order_level_df.merge(net_price_sum_check, on='order_number')
    revenue_check['difference'] = (revenue_check['net_revenue'] - revenue_check['product_level_net']).round(2)
    mismatches = revenue_check[revenue_check['difference'] != 0].shape[0]
    print(f"Net Revenue Mismatches: {mismatches}")

    # Discount Allocation Check
    discount_sum_check = product_level_df.groupby('order_number')['discount_allocated'].sum().reset_index(name='allocated_discount_total')
    discount_check = order_level_df.merge(discount_sum_check, on='order_number')
    discount_check['diff'] = (discount_check['total_discounts'] - discount_check['allocated_discount_total']).round(2)
    discount_mismatches = discount_check[discount_check['diff'] != 0].shape[0]
    print(f"Discount Mismatch Rows: {discount_mismatches}")


def prepare_cleaned_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = load_orders()
    products = load_products()

    orders = clean_orders(orders)
    orders = deduplicate_orders(orders)
    products = clean_products(products)

    enriched = enrich_orders_with_products(orders, products)

    product_level_df = create_product_level_df(enriched)
    order_level_df = create_order_level_df(product_level_df)

    # Add cohort_month for cohort-level analyses
    order_level_df['cohort_month'] = order_level_df.groupby('customer_id')['processed_at'].transform('min').dt.to_period('M')
    # Calculate discount rate
    if 'total_discounts' in order_level_df.columns and 'subtotal_price' in order_level_df.columns:
           order_level_df['discount_rate'] = order_level_df['total_discounts'] / order_level_df['subtotal_price']
    else:
           order_level_df['discount_rate'] = 0  


    return product_level_df, order_level_df
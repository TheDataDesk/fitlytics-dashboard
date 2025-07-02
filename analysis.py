# analysis.py
import pandas as pd
import numpy as np
from datetime import timedelta

def calculate_retention_matrix(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['cohort_month'] = df.groupby('customer_id')['processed_at'].transform('min').dt.to_period('M')
    df['order_month'] = df['processed_at'].dt.to_period('M')

    cohort_pivot = (
        df.groupby(['cohort_month', 'order_month'])['customer_id']
        .nunique()
        .unstack(fill_value=0)
    )

    cohort_sizes = pd.Series({
        cohort: cohort_pivot.loc[cohort, cohort]
        for cohort in cohort_pivot.index
    })

    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0).round(3)
    retention_matrix.replace([np.inf, -np.inf], np.nan, inplace=True)
    retention_matrix.dropna(how="all", inplace=True)

    return retention_matrix

def calculate_retention_matrix(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['cohort_month'] = df.groupby('customer_id')['processed_at'].transform('min').dt.to_period('M')
    df['order_month'] = df['processed_at'].dt.to_period('M')

    cohort_pivot = (
        df.groupby(['cohort_month', 'order_month'])['customer_id']
        .nunique()
        .unstack(fill_value=0)
    )

    cohort_sizes = pd.Series({
        cohort: cohort_pivot.loc[cohort, cohort]
        for cohort in cohort_pivot.index
    })

    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0).round(3)
    retention_matrix.replace([np.inf, -np.inf], np.nan, inplace=True)
    retention_matrix.dropna(how="all", inplace=True)

    return retention_matrix


def calculate_month1_retention(retention_matrix: pd.DataFrame) -> pd.DataFrame:
    month_1_retention_clean = []

    for cohort in retention_matrix.index:
        cohort_period = pd.Period(cohort, freq='M')
        month_1 = str(cohort_period + 1)

        if month_1 in retention_matrix.columns:
            rate = retention_matrix.loc[cohort, month_1]
        else:
            rate = None

        month_1_retention_clean.append({
            'cohort_month': str(cohort),
            'month_1_retention': None if pd.isna(rate) else round(rate * 100, 1)
        })

    month_1_retention_df = pd.DataFrame(month_1_retention_clean)
    return month_1_retention_df.sort_values('cohort_month')

def prepare_retention_curves(retention_matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, str]:
    retention_long = retention_matrix.reset_index().melt(
        id_vars='cohort_month',
        var_name='order_month',
        value_name='retention'
    )

    retention_long['cohort_month_ts'] = pd.PeriodIndex(retention_long['cohort_month'], freq='M').to_timestamp()
    retention_long['order_month_ts'] = pd.PeriodIndex(retention_long['order_month'], freq='M').to_timestamp()


    retention_long['month_offset'] = (
        (retention_long['order_month_ts'].dt.year - retention_long['cohort_month_ts'].dt.year) * 12 +
        (retention_long['order_month_ts'].dt.month - retention_long['cohort_month_ts'].dt.month)
    )

    retention_long = retention_long[retention_long['month_offset'] >= 0].copy()

    avg_retention = (
        retention_long.groupby('month_offset')['retention']
        .mean()
        .reset_index()
    )
    avg_retention['retention'] = (avg_retention['retention'] * 100).round(2)

    month1_ret = retention_long[retention_long['month_offset'] == 1].copy()
    best_row = month1_ret.loc[month1_ret['retention'].idxmax()]
    worst_row = month1_ret.loc[month1_ret['retention'].idxmin()]
    best_cohort = best_row['cohort_month']
    worst_cohort = worst_row['cohort_month']

    best_curve = retention_long[retention_long['cohort_month'] == best_cohort].copy()
    worst_curve = retention_long[retention_long['cohort_month'] == worst_cohort].copy()

    best_curve['retention'] = (best_curve['retention'] * 100).round(2)
    worst_curve['retention'] = (worst_curve['retention'] * 100).round(2)

    return avg_retention, best_curve, worst_curve, best_cohort, worst_cohort, retention_long

def calculate_cohort_sizes(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['cohort_month'] = df['cohort_month'].astype(str)
    cohort_sizes = df.groupby('cohort_month')['customer_id'].nunique().reset_index()
    cohort_sizes.columns = ['cohort_month', 'n_customers']
    return cohort_sizes


def calculate_avg_revenue_by_cohort(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['cohort_month'] = df['cohort_month'].astype(str)
    revenue_by_cohort = df.groupby('cohort_month')['net_revenue'].mean().reset_index()
    revenue_by_cohort.columns = ['cohort_month', 'avg_revenue']
    return revenue_by_cohort

def calculate_days_to_second_order(order_level_df: pd.DataFrame) -> pd.DataFrame:
    repeat_orders = order_level_df.sort_values(by=['customer_id', 'processed_at']).copy()
    repeat_orders['rank'] = repeat_orders.groupby('customer_id')['processed_at'].rank(method='first')

    second_orders = repeat_orders[repeat_orders['rank'] == 2].copy()
    first_orders = repeat_orders[repeat_orders['rank'] == 1][['customer_id', 'processed_at']]
    first_orders.columns = ['customer_id', 'first_order_date']

    second_orders = second_orders.merge(first_orders, on='customer_id')
    second_orders['days_to_second_order'] = (
        second_orders['processed_at'] - second_orders['first_order_date']
    ).dt.days

    return second_orders[['customer_id', 'days_to_second_order']]

def get_top_products_by_revenue(product_level_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    top_products = (
        product_level_df.groupby("product_title")["net_price"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    return top_products

def get_category_revenue_trend(product_level_df):
    product_level_df = product_level_df.copy()
    product_level_df['processed_at'] = pd.to_datetime(product_level_df['processed_at'], errors='coerce')
    product_level_df['order_month'] = product_level_df['processed_at'].dt.to_period('M').astype(str)

    category_trend = (
        product_level_df.groupby(["order_month", "product_category"])["net_price"]
        .sum()
        .reset_index()
    )
    return category_trend

def get_avg_price_per_category(product_level_df):
    avg_price_per_category = (
        product_level_df.groupby("product_category")["product_price"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    return avg_price_per_category

def get_top_categories_by_units_sold(product_level_df, top_n=10):
    units_per_category = (
        product_level_df.groupby("product_category")
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index(name="units_sold")
    )
    return units_per_category


def get_geo_revenue(product_level_df: pd.DataFrame) -> pd.DataFrame:
    return (
        product_level_df.groupby("billing_address_country")["net_price"]
        .sum()
        .reset_index()
        .rename(columns={"billing_address_country": "country", "net_price": "revenue"})
    )

def get_new_vs_returning_user_counts(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)
    df['first_order_date'] = df.groupby('customer_id')['processed_at'].transform('min')
    df['is_returning'] = df['processed_at'] > df['first_order_date']
    df['user_type'] = df['is_returning'].map({False: 'New', True: 'Returning'})

    return (
        df.groupby(['order_month', 'user_type'])['customer_id']
        .nunique()
        .reset_index(name='user_count')
    )

def get_monthly_net_revenue(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)
    return df.groupby('order_month')['net_revenue'].sum().reset_index()


def get_discount_rate_trend(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)

    if 'gross_revenue' not in df.columns:
        df['gross_revenue'] = df['net_revenue'] + df['total_discounts']

    df['discount_rate'] = df['total_discounts'] / df['gross_revenue']

    return (
        df.groupby('order_month')['discount_rate']
        .mean()
        .reset_index()
    )
def get_monthly_aov(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)

    monthly_aov = (
        df.groupby('order_month')
        .agg(
            total_revenue=('net_revenue', 'sum'),
            total_orders=('order_number', 'nunique')
        )
        .reset_index()
    )
    monthly_aov['aov'] = monthly_aov['total_revenue'] / monthly_aov['total_orders']
    return monthly_aov


def get_revenue_by_order_type(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()

    # Make sure datetime
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')

    # Compute first order date
    df['first_order_date'] = df.groupby('customer_id')['processed_at'].transform('min')

    # Tag order type
    df['order_type'] = (
        (df['processed_at'] == df['first_order_date'])
        .map({True: 'First Order', False: 'Repeat Order'})
    )

    # Group by order type and sum revenue
    revenue_by_type = (
        df.groupby('order_type')['net_revenue']
        .sum()
        .reset_index()
    )

    # Add percentage of total revenue
    total_rev = revenue_by_type['net_revenue'].sum()
    revenue_by_type['% of Revenue'] = (revenue_by_type['net_revenue'] / total_rev * 100).round(1)

    return revenue_by_type


def calculate_monthly_summary_table(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)

    summary = (
        df.groupby('order_month')
        .agg(
            total_orders=('order_number', 'nunique'),
            total_revenue=('net_revenue', 'sum'),
            total_discounts=('total_discounts', 'sum')
        )
        .reset_index()
    )

    summary['aov'] = (summary['total_revenue'] / summary['total_orders']).round(2)
    summary['total_revenue'] = summary['total_revenue'].round(2)
    summary['total_discounts'] = summary['total_discounts'].round(2)

    return summary

def calculate_month1_churn(retention_long: pd.DataFrame) -> pd.DataFrame:
    month1_ret = retention_long[retention_long['month_offset'] == 1].copy()
    month1_ret['churn_rate'] = (1 - month1_ret['retention']) * 100
    month1_ret['churn_category'] = pd.cut(
        month1_ret['churn_rate'],
        bins=[-1, 50, 75, 100],
        labels=['Low Churn', 'Moderate Churn', 'High Churn']
    )
    month1_ret['cohort_month'] = month1_ret['cohort_month'].astype(str)
    return month1_ret

def calculate_monthly_category_trends(product_level_df: pd.DataFrame) -> pd.DataFrame:
    df = product_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)

    monthly_category_trends = (
        df.groupby(['order_month', 'product_category'])['net_price']
        .sum()
        .reset_index()
    )

    return monthly_category_trends


def perform_rfm_segmentation(order_level_df: pd.DataFrame) -> pd.DataFrame:
    df = order_level_df.copy()
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
    snapshot_date = df['processed_at'].max() + timedelta(days=1)

    rfm = (
        df.groupby('customer_id')
        .agg({
            'processed_at': lambda x: (snapshot_date - x.max()).days,
            'customer_id': 'count',
            'net_revenue': 'sum'
        })
        .rename(columns={
            'processed_at': 'Recency',
            'customer_id': 'Frequency',
            'net_revenue': 'Monetary'
        })
        .reset_index()
    )

    rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    def segment_customer(score):
        if score >= 9:
            return 'Champions'
        elif score >= 6:
            return 'Potential Loyalists'
        elif score >= 3:
            return 'At Risk'
        else:
            return 'Hibernating'

    rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)
    return rfm


def get_rfm_segment_counts(rfm_df: pd.DataFrame) -> pd.DataFrame:
    segment_counts = rfm_df['Segment'].value_counts().reset_index(name="Customer Count")
    segment_counts.columns = ["Segment", "Customer Count"]
    return segment_counts

def get_retention_by_discount_level(order_df: pd.DataFrame) -> pd.DataFrame:
    import numpy as np
    df = order_df.copy()

    # Parse dates and remove timezone
    df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce').dt.tz_localize(None)
    
    # Add cohort and order month
    df['first_order_month'] = df.groupby('customer_id')['processed_at'].transform('min').dt.tz_localize(None)
    df['cohort_month'] = df['first_order_month'].dt.to_period('M').astype(str)
    df['order_month'] = df['processed_at'].dt.to_period('M').astype(str)

    # Period number (0 = first month)
    df['period_number'] = ((df['processed_at'] - df['first_order_month']).dt.days // 30)
    df = df[df['period_number'] >= 0]  # remove any bad data

    # Tag discount level
    df['discount_level'] = df['discount_rate'].apply(lambda x: 'High Discount' if x > 0.05 else 'Low Discount')

    # Initial cohort size
    cohort_sizes = df[df['period_number'] == 0].groupby(
        ['cohort_month', 'discount_level']
    )['customer_id'].nunique().reset_index(name='n_users')

    # Active users
    retention_counts = df.groupby(
        ['cohort_month', 'discount_level', 'period_number']
    )['customer_id'].nunique().reset_index(name='active_users')

    # Merge + calculate %
    retention = retention_counts.merge(cohort_sizes, on=['cohort_month', 'discount_level'])
    retention['retention_rate'] = retention['active_users'] / retention['n_users']

    # Average across cohorts
    avg_retention = retention.groupby(['discount_level', 'period_number'])['retention_rate'].mean().reset_index()

    return avg_retention

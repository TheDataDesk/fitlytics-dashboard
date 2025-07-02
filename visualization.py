# visualization.py
import plotly.express as px
import pandas as pd
import streamlit as st  
import plotly.graph_objects as go

def plot_retention_matrix(retention_matrix: pd.DataFrame) -> None:
    """
    Visualize a retention matrix as a heatmap.
    """
    matrix = retention_matrix.copy()
    matrix.index = matrix.index.astype(str)
    matrix.columns = matrix.columns.astype(str)
    matrix = matrix.loc[:, (matrix != 0).any(axis=0)]  

    fig = px.imshow(
        matrix,
        labels=dict(x="Order Month", y="Cohort Month", color="Retention Rate"),
        text_auto=".0%",
        color_continuous_scale="Blues"
    )
    fig.update_layout(title="Customer Retention by Cohort", height=600)

    st.plotly_chart(fig, use_container_width=True)  

def plot_retention_matrix(retention_matrix: pd.DataFrame) -> None:
    matrix = retention_matrix.copy()
    matrix.index = matrix.index.astype(str)
    matrix.columns = matrix.columns.astype(str)
    matrix = matrix.loc[:, (matrix != 0).any(axis=0)]

    fig = px.imshow(
        matrix,
        labels=dict(x="Order Month", y="Cohort Month", color="Retention Rate"),
        text_auto=".0%",
        color_continuous_scale="Blues"
    )
    fig.update_layout(title="Customer Retention by Cohort", height=600)
    st.plotly_chart(fig, use_container_width=True)


def plot_month1_retention(month_1_df: pd.DataFrame) -> None:
    fig = px.bar(
        month_1_df,
        x='cohort_month',
        y='month_1_retention',
        title='Month 1 Repurchase Rate by Cohort',
        labels={'cohort_month': 'Cohort Month', 'month_1_retention': 'Repurchase Rate (%)'},
        text='month_1_retention'
    )

    fig.update_layout(
        yaxis_title="Repurchase Rate (%)",
        xaxis_title="Cohort Month",
        xaxis_tickangle=-45,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_retention_curves(avg_ret, best, worst, best_label, worst_label) -> None:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=avg_ret['month_offset'],
        y=avg_ret['retention'],
        mode='lines+markers',
        name='Average Retention',
        line=dict(color='gray', dash='dash'),
        marker=dict(symbol='circle')
    ))

    fig.add_trace(go.Scatter(
        x=best['month_offset'],
        y=best['retention'],
        mode='lines+markers+text',
        name=f'Best Cohort: {best_label}',
        line=dict(color='green'),
        text=["Best"] + [""] * (len(best) - 1),
        textposition="top center",
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=worst['month_offset'],
        y=worst['retention'],
        mode='lines+markers+text',
        name=f'Worst Cohort: {worst_label}',
        line=dict(color='red'),
        text=["Worst"] + [""] * (len(worst) - 1),
        textposition="top center",
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="Retention Over Time: Avg vs Best & Worst Cohorts",
        xaxis_title="Months Since First Order",
        yaxis_title="Retention Rate (%)",
        height=600,
        legend=dict(x=0.01, y=0.99)
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_cohort_sizes(cohort_sizes_df: pd.DataFrame) -> None:
        fig = px.bar(cohort_sizes_df, x='cohort_month', y='n_customers',
                 title='Number of Customers per Cohort',
                 labels={'n_customers': 'Customer Count', 'cohort_month': 'Cohort Month'},
                 text='n_customers')
        fig.update_traces(marker_color='steelblue', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def plot_avg_revenue_by_cohort(revenue_df: pd.DataFrame) -> None:
    fig = px.bar(revenue_df, x='cohort_month', y='avg_revenue',
                 title='Average Revenue per User by Cohort',
                 labels={'avg_revenue': 'Avg Revenue per Customer', 'cohort_month': 'Cohort Month'},
                 text='avg_revenue')
    fig.update_traces(marker_color='mediumseagreen', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def plot_days_to_second_order_histogram(df: pd.DataFrame):
    fig = px.histogram(
        df,
        x='days_to_second_order',
        nbins=30,
        title='Distribution of Days to Second Purchase',
        labels={'days_to_second_order': 'Days to Second Order'}
    )
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig)
    return fig

def plot_top_products_by_revenue(top_products_df: pd.DataFrame):
    fig = px.bar(
        top_products_df,
        x="product_title",
        y="net_price",
        title="Top 10 Products by Revenue",
        text_auto=".2s",
        labels={"net_price": "Total Revenue (€)", "product_title": "Product"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_category_revenue_trend(category_trend_df: pd.DataFrame):
    fig = px.line(
        category_trend_df,
        x="order_month",
        y="net_price",
        color="product_category",
        title="Revenue Trend by Product Category Over Time",
        labels={"order_month": "Order Month", "net_price": "Revenue (€)", "product_category": "Category"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_avg_price_per_category(avg_price_df: pd.DataFrame):
    fig = px.bar(
        avg_price_df,
        x="product_category",
        y="product_price",
        title="Average Product Price per Category",
        labels={"product_price": "Average Price (€)", "product_category": "Category"},
        text_auto=".2f"
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_top_categories_by_units(units_df: pd.DataFrame):
    fig = px.bar(
        units_df,
        x="product_category",
        y="units_sold",
        title="Top 10 Product Categories by Units Sold",
        labels={"product_category": "Category", "units_sold": "Units Sold"},
        text_auto=True
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_geo_revenue_map(df: pd.DataFrame):
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="revenue",
        hover_name="country",
        color_continuous_scale="Greens",
        title="Revenue by Country (Choropleth Map)",
        labels={"revenue": "Total Revenue (€)"}
    )
    fig.update_geos(showframe=False, showcoastlines=False)
    return fig


def plot_new_vs_returning_area(user_counts_df: pd.DataFrame):
    fig = px.area(
        user_counts_df,
        x='order_month',
        y='user_count',
        color='user_type',
        title='New vs Returning Customers Over Time',
        labels={'user_count': 'Customer Count', 'order_month': 'Month', 'user_type': 'User Type'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_monthly_revenue_trend(monthly_revenue_df: pd.DataFrame):
    fig = px.line(
        monthly_revenue_df,
        x='order_month',
        y='net_revenue',
        title="Monthly Net Revenue Trend",
        markers=True,
        labels={'order_month': 'Month', 'net_revenue': 'Net Revenue (€)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_discount_rate_trend(discount_rate_df: pd.DataFrame):
    fig = px.line(
        discount_rate_df,
        x='order_month',
        y='discount_rate',
        title="Discount Rate Trends Over Time",
        markers=True,
        labels={'order_month': 'Month', 'discount_rate': 'Avg. Discount Rate'}
    )
    fig.update_layout(yaxis_tickformat=".1%")
    return fig

def plot_monthly_aov(monthly_aov_df: pd.DataFrame):
    fig = px.line(
        monthly_aov_df,
        x='order_month',
        y='aov',
        title="Average Order Value (AOV) Over Time",
        markers=True,
        labels={'order_month': 'Month', 'aov': 'Average Order Value (€)'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_revenue_by_order_type(revenue_by_type_df: pd.DataFrame):
    fig = px.bar(
        revenue_by_type_df,
        x='order_type',
        y='net_revenue',
        text='net_revenue',
        color='order_type',
        title='Revenue Breakdown: First vs Repeat Orders',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        showlegend=False,
        yaxis_title='Revenue (€)',
        xaxis_title='Order Type'
    )
    return fig

def plot_monthly_summary_table(monthly_summary_df: pd.DataFrame):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(monthly_summary_df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[monthly_summary_df[col] for col in monthly_summary_df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(title='Monthly Business Summary')
    return fig

def plot_monthly_category_trends(monthly_category_trends_df: pd.DataFrame):
    fig = px.line(
        monthly_category_trends_df,
        x='order_month',
        y='net_price',
        color='product_category',
        title=' Monthly Revenue Trends by Product Category',
        labels={'net_price': 'Revenue (€)', 'order_month': 'Order Month'},
        markers=True
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_month1_churn_rate(month1_ret_df: pd.DataFrame):
    fig = px.bar(
        month1_ret_df,
        x='cohort_month',
        y='churn_rate',
        color='churn_category',
        text=month1_ret_df['churn_rate'].round(1).astype(str) + '%',
        color_discrete_map={
            'Low Churn': 'green',
            'Moderate Churn': 'orange',
            'High Churn': 'crimson'
        },
        title='Month 1 Churn Rate by Cohort'
    )
    fig.update_layout(
        xaxis_title='Cohort Month',
        yaxis_title='Churn Rate (%)',
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )
    return fig

def plot_rfm_segmentation_bar(segment_counts_df: pd.DataFrame):
    fig = px.bar(
        segment_counts_df,
        x='Segment',
        y='Customer Count',
        color='Segment',
        title='RFM Segment Distribution',
        color_discrete_map={
            'Champions': 'seagreen',
            'Potential Loyalists': 'steelblue',
            'At Risk': 'orange',
            'Hibernating': 'crimson'
        }
    )
    return fig

def plot_retention_by_discount_level(df):
    fig = px.line(
        df,
        x='period_number',
        y='retention_rate',
        color='discount_level',
        markers=True,
        title='Retention Curves: High vs Low Discount Cohorts',
        labels={
            'period_number': 'Months Since First Purchase',
            'retention_rate': 'Retention Rate'
        }
    )
    fig.update_layout(yaxis_tickformat=".1%", legend_title="Discount Level")
    return fig

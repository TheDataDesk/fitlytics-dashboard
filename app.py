# app.py

import streamlit as st
from transform import prepare_cleaned_datasets
import pandas as pd
import plotly.express as px
from analysis import (
    calculate_retention_matrix, 
    calculate_month1_retention,
    prepare_retention_curves,
    calculate_cohort_sizes, 
    calculate_avg_revenue_by_cohort,
    calculate_days_to_second_order,
    get_top_products_by_revenue,
    get_category_revenue_trend,
    get_avg_price_per_category,
    get_top_categories_by_units_sold,
    get_geo_revenue,
    get_new_vs_returning_user_counts,
    get_monthly_net_revenue,
    get_discount_rate_trend,
    get_monthly_aov,
    get_revenue_by_order_type,
    calculate_monthly_summary_table,
    calculate_month1_churn,
    perform_rfm_segmentation,
    get_rfm_segment_counts,
    get_retention_by_discount_level
    
)
from visualization import(
    plot_retention_matrix, 
    plot_month1_retention,
    plot_retention_curves, 
    plot_cohort_sizes, 
    plot_avg_revenue_by_cohort,
    plot_days_to_second_order_histogram,
    plot_top_products_by_revenue,
    plot_category_revenue_trend,
    plot_avg_price_per_category,
    plot_top_categories_by_units,
    plot_geo_revenue_map,
    plot_new_vs_returning_area,
    plot_monthly_revenue_trend,
    plot_discount_rate_trend,
    plot_monthly_aov,
    plot_revenue_by_order_type,
    plot_monthly_summary_table,
    plot_month1_churn_rate,
    plot_rfm_segmentation_bar,
    plot_retention_by_discount_level,
    plot_revenue_by_category_area_chart
)


# Page setup
st.set_page_config(page_title="Fitlytics Dashboard", layout="wide")
st.title("🚀 Fitlytics Dashboard: Customer & Revenue Deep Dive")

st.markdown("""
Welcome to the **Fitlytics Dashboard**! 

This dashboard is designed to **analyze customer behavior and revenue dynamics** for a growing athletic gear e-commerce brand, based on a randomized sample dataset.

### Why are we doing this?

We're aiming to answer two core business questions:

1. **Customer Cohorts & Retention:** How are customers behaving post-purchase? Are they coming back? When do they churn? Which cohorts are thriving, and which need attention?
2. **Business Growth Signals:** What does our revenue trend look like? Which products or categories are driving it? How are discounts, AOV, and returning users evolving?

By diving deep into cohorts, revenue drivers, product trends, and segmentation, we can uncover valuable insights to:

- Improve **customer retention**
- Spot **high-performing product segments**
- Evaluate **growth levers** and **potential revenue leaks**

### What you’ll explore in this dashboard:

This dashboard is organized into **5 insightful sections**:

1. **Customer Behavior & Retention** – Understand repurchase behavior, cohort performance, churn rate, and more.
2. **Revenue & Monetization Patterns** – See how customer groups differ in revenue contribution and order types.
3. **Product-Level Insights** – Dive into top-performing products, pricing strategies, and units sold.
4. **Category & Geographic Trends** – Explore revenue by category trends and international distribution.
5. **Growth, Discounts, and Profitability** – Track AOV, discount patterns, returning users, and monthly business summaries.

---

Let’s get into it and uncover some actionable insights! 
""")




# Load and transform data
with st.spinner("Loading and transforming data..."):
    product_level_df, order_level_df = prepare_cleaned_datasets()

with st.sidebar:
    st.header("🔍 Filters")
    selected_products = st.multiselect("Product", options=product_level_df['product_title'].unique())
    selected_categories = st.multiselect("Category", options=product_level_df['product_category'].unique())
    selected_types = st.multiselect("Product Type", options=product_level_df['product_type'].unique())
    selected_country = st.multiselect("Country", options=order_level_df['billing_address_country'].unique())
    selected_status = st.multiselect("Order Status", options=order_level_df['order_status'].unique())
    selected_orders = st.multiselect("Order Number", options=order_level_df['order_number'].unique())
    selected_customers = st.multiselect("Customer ID", options=order_level_df['customer_id'].unique())
    selected_date = st.date_input("Date Range", value=(order_level_df['processed_at'].min(), order_level_df['processed_at'].max()))
    st.caption("Data available from **2019-12-03** to **2021-03-08**")



# Apply filters
filtered_product_df = product_level_df.copy()
filtered_order_df = order_level_df.copy()

if selected_products:
    filtered_product_df = filtered_product_df[filtered_product_df['product_title'].isin(selected_products)]
if selected_categories:
    filtered_product_df = filtered_product_df[filtered_product_df['product_category'].isin(selected_categories)]
if selected_types:
    filtered_product_df = filtered_product_df[filtered_product_df['product_type'].isin(selected_types)]
if selected_country:
    filtered_order_df = filtered_order_df[filtered_order_df['billing_address_country'].isin(selected_country)]
if selected_status:
    filtered_order_df = filtered_order_df[filtered_order_df['order_status'].isin(selected_status)]
if selected_orders:
    filtered_order_df = filtered_order_df[filtered_order_df['order_number'].isin(selected_orders)]
if selected_customers:
    filtered_order_df = filtered_order_df[filtered_order_df['customer_id'].isin(selected_customers)]
if selected_date:
    start_date, end_date = selected_date
    start_date = pd.to_datetime(start_date).tz_localize("UTC")
    end_date = pd.to_datetime(end_date).tz_localize("UTC")
    filtered_order_df = filtered_order_df[
        (filtered_order_df['processed_at'] >= start_date) &
        (filtered_order_df['processed_at'] <= end_date)
]
    filtered_product_df = filtered_product_df[
         (filtered_product_df['processed_at'] >= start_date) &
         (filtered_product_df['processed_at'] <= end_date)
]

  

# Generate retention matrix
retention_matrix = calculate_retention_matrix(filtered_order_df)

# SECTION 1: Customer Behavior & Retention
st.header(" 👥 SECTION 1: Customer Behavior & Retention")

# Graph 1: heatmap for customer Retention by Cohort
st.subheader("Customer Retention Trends by Acquisition Cohort")
plot_retention_matrix(retention_matrix)
st.markdown("""

- **Y-axis:** Cohort Month (month of user acquisition)  
- **X-axis:** Order Month (month of follow-up orders)  
- **Each cell:** Shows % of users from a cohort who reordered in that month

### Observations

- Retention starts at **100%** for each cohort in their acquisition month  
- **Sep–Nov 2020 cohorts** show the strongest long-term retention — up to **11%** by Month 6–7  
- Other cohorts drop to **0–3%** within a couple of months  
- Later cohorts (2021) show **shorter timelines** due to limited data window

### Takeaways

- Strong early drop-off suggests users often churn after their first order  
- High-performing cohorts likely benefited from better product-market fit, or seasonality  
- There's a need to strengthen **Month 1 engagement** and **repeat purchase nudges**  
- Investigate standout cohorts to uncover repeat behavior drivers"""
)
st.markdown("---")

# Graph 2: Month 1 bar chart
st.subheader("Month 1 Repurchase Rate")
month1_df = calculate_month1_retention(retention_matrix)
plot_month1_retention(month1_df)
st.markdown("""

### Observations
- **Early 2020 cohorts** (Jan–May) show low repurchase rates between **1.1% and 1.9%**.
- **Mid-2020** starts improving, **July** cohort hits **4.1%**.
- **Highest rates** observed in **Oct 2020 (5.9%)** and **Jan 2021 (5.8%)**, suggesting strong campaign or seasonal effects.
- **Recent dip** in **Feb 2021 (2.1%)** highlights possible early churn for new users.

### Takeaways
            
Month 1 repurchase has improved over time, but post-Jan 2021 cohorts may require engagement attention.
""")
st.markdown("---")

# Graph 3: avg vs best/worst retention curves
st.subheader("Best vs Worst Cohorts Compared to Average")
avg_ret, best_curve, worst_curve, best_cohort, worst_cohort,retention_long  = prepare_retention_curves(retention_matrix)
plot_retention_curves(avg_ret, best_curve, worst_curve, best_cohort, worst_cohort)
st.markdown(""" 
### Observations
            
- The **best cohort** retains ~10–12% of users up to Month 4–5, well above the average.
- The **worst cohort (Jan 2020)** drops close to **0%** retention after Month 1 and stays flat.
- The **average retention** line highlights a general drop to ~5% by Month 2 and lower thereafter.

### Takeaways
            
- Some cohorts (like Oct 2020) show clear signs of stronger product-market fit or effective onboarding.
- Early 2020 cohorts underperform significantly, likely due to weaker acquisition sources or experience gaps.
- Benchmarking top vs bottom cohorts helps isolate factors behind **successful long-term engagement**.

""") 
st.markdown("---")

# Graph 4: Customer Acquisition Over Time
st.subheader("Cohort Size: Customer Acquisition Over Time")
cohort_sizes = calculate_cohort_sizes(filtered_order_df)
plot_cohort_sizes(cohort_sizes)

st.markdown("""

### Observations
- Customer acquisition picked up sharply from **early 2020**, with **13k+ new customers** in some months.
- Peak acquisition occurred in **Jan 2021 (15.7k)** the highest among all cohorts.
- The earliest cohort (pre-Jan 2020) had negligible volume (only **60 users**), likely test or early-stage data.
- A noticeable drop is seen in **Mar 2021 (4.1k)**, possibly due to data cutoff.

### Takeaways
- Acquisition efforts scaled significantly post-2020, aligning with higher activity in retention and revenue charts.
- The **larger cohort sizes in late 2020 to early 2021** are important for driving overall business outcomes.
- Sharp drop in latest cohort may indicate **partial data or reduced acquisition**, which should be validated.

""")
st.markdown("---")

# Graph 5: Days to second purchase
st.subheader("Time to Second Purchase")
days_to_second = calculate_days_to_second_order(filtered_order_df)
plot_days_to_second_order_histogram(days_to_second)
st.markdown("""

### Observations
- Most users who reorder do so **within the first 30–60 days**.
- there is still a steady stream of reorders happening over the next 2 to 4 months.
- Long-tail behavior is visible, some customers return even after **300+ days**.

### Takeaways
- Early repurchase behavior is **critical to long-term retention**.
- Campaigns aimed at encouraging reorders within the **first 60–90 days** could significantly boost repeat rates.
- The long-tail highlights potential for **reactivation strategies** targeting dormant users.
""")
st.markdown("---")


# Graph 6: Month 1 Churn Rate
st.subheader("Month 1 Churn Rate by Cohort")
month1_churn_df = calculate_month1_churn(retention_long)
st.plotly_chart(plot_month1_churn_rate(month1_churn_df), use_container_width=True, key="month1_churn")
st.markdown("""

### Observations
- Month 1 churn is consistently **very high** across all cohorts, ranging from **94% to 98.9%**
- Only a **small fraction of customers** are retained after their first purchase
- Slight improvements are seen in **Oct 2020 (94.1%)** and **Jan 2021 (94.2%)**, but still indicate critical drop-off

### Takeaways
- There's an **urgent need to improve first-month retention**
- Customers often **do not return after their first order**, signaling weak onboarding or lack of product stickiness
- **Early lifecycle interventions** (e.g. win-back emails, loyalty programs, product education) could help reduce this churn
""")
st.markdown("---")

# Graph 7: RFM Segmentation
st.subheader("RFM Segment Distribution")
rfm_df = perform_rfm_segmentation(filtered_order_df)
rfm_segment_counts = get_rfm_segment_counts(rfm_df)
st.plotly_chart(plot_rfm_segmentation_bar(rfm_segment_counts), use_container_width=True, key="rfm_segments")
st.markdown("""

### Observations
- **Potential Loyalists** make up the **largest segment (~70k)** these are customers who buy somewhat frequently and recently, showing strong potential for conversion to loyalty
- **Champions (~45k)** are the most valuable customers they purchase often, spend more, and bought recently
- **At Risk (~35k)** customers have lapsed previously engaged but haven’t bought in a while

### Takeaways
- Focus on **converting Potential Loyalists into Champions** through loyalty rewards, exclusive offers, or reactivation nudges
- **Re-engage At Risk customers** with personalized win-back campaigns before they churn completely
- Maintain high satisfaction among **Champions** to protect CLV and encourage advocacy
""")
st.markdown("---")


# SECTION 2: Monetization by Cohort
st.header("💰 SECTION 2: Revenue & Monetization Patterns")


# Graph 8: Average Revenue per Customer by Cohort
st.subheader("Average Revenue per Customer by Cohort")
cohort_revenue = calculate_avg_revenue_by_cohort(filtered_order_df)
plot_avg_revenue_by_cohort(cohort_revenue)
st.markdown("""

### Observations
- Most cohorts maintain an average revenue per user (ARPU) between **€260–€290**
- **Cohorts from Dec 2021 and Jan 2021** show the **highest ARPU**, peaking at **€310–€308**
- Early 2020 cohorts (Jan–May) show slightly **lower ARPU**, around **€260–€270**

### Takeaways
- **Recent cohorts (Dec 2020 - Jan 2021)** are not just engaging more but also **spending more per customer**
- Suggests potential **increased order value or more frequent purchases** in later periods
- Worth analyzing what changed in early 2021 — e.g., **product mix, campaign strategy, pricing, or customer segment targeting**
""")
st.markdown("---")

# Graph 9: Revenue by Order Type
st.subheader("First vs Repeat Order Revenue")
revenue_by_type = get_revenue_by_order_type(filtered_order_df)
st.plotly_chart(plot_revenue_by_order_type(revenue_by_type), use_container_width=True, key="revenue_by_order_type_chart")
st.markdown("""

### Observations
- **First orders contribute €44.86M**, while **repeat orders contribute only €8.77M**
- That’s a **5x gap**, with over **83% of total revenue** coming from first-time purchases

### Takeaways
- Heavy reliance on **new customer acquisition** for revenue generation  
- Indicates a **leaky retention funnel**, low repeat behavior despite large user base  
- Strengthening **post-purchase engagement** could unlock major growth in **CLTV and profitability**
""")
st.markdown("---")

# Graph 10: AOV over Time
st.subheader("Average Order Value (AOV) Over Time")
monthly_aov = get_monthly_aov(filtered_order_df)
st.plotly_chart(plot_monthly_aov(monthly_aov), use_container_width=True, key="aov_over_time")
st.markdown("""

### Observations
- AOV **dipped to €259 in Feb 2020**, its lowest point during the period
- From **May to July 2020**, there's a sharp **AOV spike (~€295+)**, followed by a steady plateau
- **October 2020** marks the **highest AOV (~€303)**, likely tied to peak campaign season
- Post Oct 2020, **AOV declined**, bottoming out again in **Feb 2021 (~€269)**

### Takeaways
- Mid-to-late 2020 shows **strong purchasing power per order**
- Potential drivers: **bundling offers, seasonal campaigns, or premium SKUs**
- Recent drop signals a need to evaluate **product pricing strategy** or shifting user behavior
""")
st.markdown("---")


# SECTION 3: Product-Level Insights
st.header("🛍️ SECTION 3: Product-Level Insights")


# Graph 11: Top products by revenue
st.subheader("Top Products by Revenue")
top_products = get_top_products_by_revenue(filtered_product_df)
fig = plot_top_products_by_revenue(top_products)
st.plotly_chart(fig, use_container_width=True, key="top_products_chart")
st.sidebar.markdown(f"🎯 Filtered products: **{len(filtered_product_df)}** rows")

st.markdown("""

### Observations
- **Golf sets dominate** the leaderboard, with the top 3 products all being variations of **golf sets** bundled with caddy, shoes, and balls
- The **#1 product** ("Golf_set_with_caddy_shoes_and_100_balls") alone contributed **€11M**, significantly ahead of others
- Multisport bundles and tennis sets appear in the mid and lower tiers of the top 10
- Lowest revenue products (~€1.4M) include **branded/signed memorabilia** and **tennis kits**

### Takeaways
- Golf-related SKUs are **clear revenue leaders**, indicating **strong customer demand and pricing power**
- High-performing bundles suggest an opportunity to **expand upsell packages** for other sports
- Strategic promotion of tennis or football bundles might help **diversify revenue sources**
""")
st.markdown("---")


# Graph 12: Average Price per Category
st.subheader("Average Product Price per Category")
avg_price_df = get_avg_price_per_category(filtered_product_df)
st.plotly_chart(plot_avg_price_per_category(avg_price_df), use_container_width=True, key="avg_price_per_category")
st.markdown("""

### Observations
- **Multi-sport bundles** command the highest average price at **€445.83**, nearly double that of golf products
- **Golf (€223.97)** and **Tennis (€199.08)** are the next highest-priced categories
- **Accessories** have the **lowest average price** at just **€49.32**

### Takeaways
- Pricing is highly **tiered by category**, with bundles and premium sports leading in value
- High-price categories likely contribute disproportionately to revenue and margin
- Lower-price categories (like accessories) could be **leveraged for cross-sells or entry offers**
""")
st.markdown("---")


# Graph 13: Top Categories by Units Sold
st.subheader("Top 10 Product Categories by Units Sold")
units_df = get_top_categories_by_units_sold(filtered_product_df)
st.plotly_chart(plot_top_categories_by_units(units_df), use_container_width=True, key="top_units_by_category")
st.markdown("""

### Observations
- **Golf** dominates with over **141k units sold**, nearly **4x** more than the next category  
- **Tennis (38k)** and **Accessories (35k)** follow at a distant second and third  
- **Multi-sport bundles**, despite highest price, sold only **~22k units**  
- **Football** and **Swimming** had the **lowest unit sales**, both under **14k**

### Takeaways
- **Golf** is the primary sales driver in volume — likely a **core category**  
- **High-priced bundles** have lower sales but may still drive revenue (high AOV)  
- **Accessories** sold well despite low pricing — ideal for **upsells or frequent repurchases**
""")
st.markdown("---")

#Graph 14: Monthly Revenue by Product Category

st.subheader("Monthly Revenue by Product Category")
plot_revenue_by_category_area_chart(filtered_product_df)


# SECTION 4: Category & Country Revenue Trends
st.header("🌍 SECTION 4: Category & Geographic Trends") 

# Graph 14: Revenue Trend by Product Category
st.subheader("Revenue Trend by Product Category")
category_trend = get_category_revenue_trend(filtered_product_df)
st.plotly_chart(plot_category_revenue_trend(category_trend), use_container_width=True, key="cat_revenue_trend")
st.markdown("""

### Observations
- **Golf** was the top revenue driver early on, peaking around **Feb 2020** with over **€3.5M**
- **Multi-sport bundles** surged later, surpassing all other categories around **Jan 2021**
- **Tennis** showed steady growth from **May 2020 to Feb 2021**
- **Accessories**, **Football**, and **Swimming** remained consistently low across all months

### Takeaways
- **Shift in demand** from Golf to **high-value multi-sport bundles** in later months  
- **Tennis products** gained steady traction, indicating potential for consistent future growth  
- Lower-tier categories (e.g., Swimming, Football) may need **product/marketing revamp**  
- Seasonality or campaigns likely influenced peak months — worth deeper analysis
""")
st.markdown("---")


# Graph 15: Revenue by Country
st.subheader("Revenue by Country")
geo_revenue = get_geo_revenue(filtered_product_df)
st.plotly_chart(plot_geo_revenue_map(geo_revenue), use_container_width=True, key="revenue_by_country")
st.markdown("""

### Observations
- **Germany** is the dominant revenue generator with a total revenue of **€48.82M**, indicated by the darkest green shade.
- **Afghanistan** ranks second with **€15.7K**, followed by the **United Kingdom** with **€10.2K**.
- Other countries appear on the map with **lighter shades**, representing **progressively lower revenue values**.
- The choropleth shading effectively visualizes **geographic revenue concentration**, with a steep drop-off beyond Germany.

### Takeaways
- **Germany is the core market**, vastly outperforming all other countries in revenue generation.
- There is **limited international traction**, as seen by the significant gap between Germany and the next-highest countries.
- The presence of other countries, even with minimal revenue, indicates **potential global interest**.
- Strategic implications:
  - Consider **investing in localized marketing or distribution** in countries like the UK or Afghanistan to test growth potential.
  - Perform a **geographic performance audit** to understand why some regions underperform.
  - Evaluate whether operational limitations (e.g. shipping, payment, language) are **barriers to scaling internationally**.
""")
st.markdown("---")

# SECTION 5 : Growth, Discounts, and Profitability
st.header(" 📈 SECTION 5:  Growth, Discounts, and Profitability")


# Graph 16: New vs Returning Customers
st.subheader("New vs Returning Customers Over Time")
user_counts = get_new_vs_returning_user_counts(filtered_order_df)
st.plotly_chart(plot_new_vs_returning_area(user_counts), use_container_width=True, key="user_retention_type")

st.markdown("""
### Observations
- Both **new** and **returning customers** increased significantly starting around **September 2020**, peaking around **January 2021**.
- **New customers** consistently outnumbered returning ones, highlighting strong acquisition campaigns.
- A sharp decline in both segments is observed in **March 2021**, likely due to data cutoff.
### Takeaways
- The growth in returning users mirrors acquisition success, indicating that **some conversion to loyalty is occurring**, but not at optimal levels.
- The retention rate needs improvement despite a high volume of new customers, returning customers form a **smaller share**.
- A strategic opportunity lies in:
  - Enhancing **early engagement and retention** initiatives (e.g., onboarding flows, targeted promotions).
  - Building **post-purchase journeys** to re-engage new users.
  - Monitoring March’s drop-off—this could be a lack of data beyond March 8, 2021. 
""")
st.markdown("---")

# Graph 17: Monthly Net Revenue Trend
st.subheader("Monthly Net Revenue Trend")
monthly_revenue = get_monthly_net_revenue(filtered_order_df)
st.plotly_chart(plot_monthly_revenue_trend(monthly_revenue), use_container_width=True, key="monthly_revenue")
st.markdown("""

### Observations
- Net revenue steadily increased from **January 2020**, peaking in **January 2021** at over **€6M**, reflecting a strong growth phase.
- A period of revenue stability occurred between **April and August 2020**, averaging around **€2.5–2.7M**.
- Revenue accelerated again from **September 2020**, with two major growth spurts:
  - **October to November 2020**
  - **December 2020 to January 2021**

### Recent Decline
- A sharp drop is observed in **March 2021**, is due to data cutoff. 

### Strategic Insights
- **Q4 2020–Q1 2021** was the revenue high point likely driven by successful campaigns or holiday momentum.
- **March 2021’s dip** requires immediate review, investigate changes in acquisition, product availability, or external market conditions.
- Plan to **reignite momentum post-Q1** with targeted growth and re-engagement strategies.
""")
st.markdown("---")

# Graph 18: Discount Rate Trend
st.subheader("Discount Rate Trend")
monthly_discount = get_discount_rate_trend(filtered_order_df)
st.plotly_chart(plot_discount_rate_trend(monthly_discount), use_container_width=True, key="discount_rate")
st.markdown("""

### Observations
- A **significant spike in discount rate** was recorded in **April 2020**, peaking around **0.35%**.
- This was followed by a **steady decline** through **May and June**, returning close to 0% by July 2020.
- A minor uptick occurred again in **August 2020**, after which the discount rate **stabilized at a very low level (~0.01–0.03%)** through early 2021.
- The overall discounting activity was minimal except during a brief promotional period in **Spring 2020**.

### Takeaways
- The peak discounting in **April–May 2020** likely corresponds to a **campaign or sales event**, potentially in response to COVID-19's market disruption.
- Since mid-2020, the brand maintained a **premium pricing strategy** with very limited discounting.
- Low sustained discount levels suggest:
  - Strong perceived product value
  - Focus on high-margin sales
  - Confidence in customer willingness to pay full price

**Next Step**: Correlate this with the **April–May revenue and customer trends** to assess campaign effectiveness.
""")
st.markdown("---")


# Graph 19: Monthly Summary Table
st.subheader(" Monthly Business Summary Table")
summary_table = calculate_monthly_summary_table(filtered_order_df)
st.plotly_chart(plot_monthly_summary_table(summary_table), use_container_width=True, key="summary_table")

st.markdown("""

### Observations
- **Rapid growth** in total orders from **60 (Dec 2019)** to **17,983 (Nov 2020)**.
- **Revenue grew proportionally**, peaking at **€5.13M in Nov 2020**.
- **Average Order Value (AOV)** ranged between **€259–€303**, with the **highest in Oct 2020** (€303.74).
- **Discount spikes**:
  - **April 2020**: 6925 (biggest spike)
  - **May 2020**: 4448 (second biggest spike)
  - **August 2020**: 2158
- Discount activity **correlates with dips** in AOV (e.g., Apr–May 2020).

### Takeaways
- Growth trajectory in both **volume (orders)** and **value (revenue)** shows a healthy expanding business.
- **May 2020 discounts** likely reflect a **large promotional campaign**.
- Despite discounts, **AOV remained stable**, indicating bundling or high-ticket promotions.
- Post-June, **discounts dropped sharply**, yet **orders and revenue kept rising**, signals **strong organic demand**.
- Peak **efficiency in Oct 2020**, combining high orders, low discounts, and highest AOV.
""")
st.markdown("---")


# Discount vs Retention Analysis
st.header("Discount Impact on Retention")

st.subheader("Retention Curves by Discount Level")
discount_retention_df = get_retention_by_discount_level(filtered_order_df)
st.plotly_chart(plot_retention_by_discount_level(discount_retention_df), use_container_width=True, key="retention_by_discount")

st.markdown("""
            
### Observations 
            
I attempted to analyze retention patterns across different discount levels to see if heavier discounts led to better long-term customer engagement.

However, almost **all customers (over 95%)** fell under the **low or no discount** category. This means the business **rarely relied on promotions or discounts** during the analyzed period.

### Takeaways

- The brand maintains a **premium pricing strategy**, focusing on full-price orders.
- There’s **limited data to evaluate the impact of discounts on retention**, because high-discount cohorts are almost non-existent.
- This reinforces earlier findings: strong AOV, low discount activity, and healthy revenue,  all achieved **without needing to discount heavily**.
""")

st.markdown("---")

st.markdown(
    """
## Final Thoughts: What the Data Tells Us

After digging into all the charts and numbers, one thing is clear:

This brand is doing a **great job at getting people to buy** for the first time. There’s strong growth in new customers, revenue peaks in late 2020 and early 2021, and top products (like golf sets and multi-sport bundles) are selling well.

But here’s the catch, **most customers don’t come back**.

In fact, over **95% of them churn after their first order**. That’s a huge missed opportunity. Repeat orders make up only a small piece of the revenue pie, even though the first-order engine is working really well.

At the same time, we saw:

- Strong revenue trends without heavy reliance on discounts
- High-value products driving both sales and margins
- A large group of customers who could become loyal, but aren’t there yet

---

## So What Should We Do?

Here’s where the biggest wins lie:

1. **Focus on retention** not just acquisition. Getting users to come back is the next big unlock.
2. **Improve Month 1 experience** most churn happens here. Onboarding emails, small perks, or reminders could help.
3. **Personalize for the right groups**  like Potential Loyalists. They’re already showing interest.
4. **Use bundles or perks instead of heavy discounts** to nudge repeat orders without hurting brand value.

---

## Bottom Line

The brand has built strong momentum, now it’s time to turn one-time buyers into long-term customers.

Retention is where the real growth and profitability will come from.
""")

st.markdown("---") 

st.markdown(
    """
    <style>
    .watermark {
        position: fixed;
        bottom: 10px;
        right: 15px;
        opacity: 0.5;
        font-size: 13px;
        color: #6c757d;
        z-index: 100;
    }
    </style>
    <div class="watermark">Sirisha | Hey Holy Challenge | July 2025</div>
    """,
    unsafe_allow_html=True
)


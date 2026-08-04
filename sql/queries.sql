-- ======================================
-- Top 5 Schemes by AUM:
-- ======================================
try:
    cursor.execute("""
        SELECT
            f.scheme_name,
            MAX(a.aum_crore) AS total_aum
        FROM fact_aum a
        JOIN dim_fund f
        ON a.fund_key = f.fund_key
        GROUP BY f.scheme_name
        ORDER BY total_aum DESC
        LIMIT 5;
    """)
    results = cursor.fetchall()
    print("Top 5 Schemes by AUM:")
    for row in results:
        print(row)
except sqlite3.Error as e:
    print(f"Error executing query: {e}")

-- ======================================
-- Average NAV per Month:
-- ======================================

try:
    cursor.execute("""
        SELECT
            d.year,
            d.month,
            ROUND(AVG(n.nav), 2) AS average_nav
        FROM fact_nav n
        JOIN dim_date d
        ON n.date_key = d.date_key
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month;
    """)
    results = cursor.fetchall()
    print("Average NAV per Month:")
    for row in results:
        print(row)
except sqlite3.Error as e:
    print(f"Error executing query: {e}")


-- ======================================
-- SIP Investment YOY Growth:
-- ======================================

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                d.year,
                SUM(t.amount_inr) AS sip_investment,
                LAG(SUM(t.amount_inr)) OVER(ORDER BY d.year) AS previous_year_sip,
                ROUND(
                    (
                        SUM(t.amount_inr) - LAG(SUM(t.amount_inr)) OVER(ORDER BY d.year)
                    )
                    * 100.0 /
                    LAG(SUM(t.amount_inr)) OVER(ORDER BY d.year),
                2) AS yoy_growth_pct
            FROM fact_transactions t
            JOIN dim_date d
            ON t.date_key = d.date_key
            WHERE t.transaction_type = 'SIP'
            GROUP BY d.year;
            """
        )
        result = conn.execute(query).fetchall()
        print("SIP Investment YOY Growth:")
        for row in result:
            print(row)
except Exception as e:
    print(f"Error executing query: {e}")

-- ======================================
-- Transactions by State:
-- ======================================

from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                state,
                COUNT(transaction_key) AS total_transactions,
                SUM(amount_inr) AS total_amount
            FROM fact_transactions
            GROUP BY state
            ORDER BY total_transactions DESC;
            """
        )
        result = conn.execute(query).fetchall()
        print("Transactions by State:")
        for row in result:
            print(f"State: {row[0]}, Total Transactions: {row[1]}, Total Amount: {row[2]:,.2f}")
except Exception as e:
    print(f"Error executing query: {e}")


-- ======================================
-- Funds with Expense Ratio < 1%:
-- ======================================


from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                fund_key,
                fund_house,
                scheme_name,
                expense_ratio_pct
            FROM dim_fund
            WHERE expense_ratio_pct < 1
            ORDER BY expense_ratio_pct;
            """
        )
        result = conn.execute(query).fetchall()
        print("Funds with Expense Ratio < 1%:")
        for row in result:
            print(f"Fund Key: {row[0]}, Fund House: {row[1]}, Scheme Name: {row[2]}, Expense Ratio: {row[3]}%")
except Exception as e:
    print(f"Error executing query: {e}")

-- ======================================
-- Top 5 Schemes by 5-Year Return:
-- ======================================

from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                f.scheme_name,
                f.fund_house,
                p.return_5yr_pct
            FROM fact_performance p
            JOIN dim_fund f
            ON p.fund_key = f.fund_key
            ORDER BY p.return_5yr_pct DESC
            LIMIT 5;
            """
        )
        result = conn.execute(query).fetchall()
        print("Top 5 Schemes by 5-Year Return:")
        for row in result:
            print(f"Scheme: {row[0]}, Fund House: {row[1]}, 5-Year Return: {row[2]}%")
except Exception as e:
    print(f"Error executing query: {e}")

-- ======================================
-- Total Investment by Fund Category:
-- ======================================


from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                f.category,
                SUM(t.amount_inr) AS total_investment
            FROM fact_transactions t
            JOIN dim_fund f
            ON t.fund_key = f.fund_key
            GROUP BY f.category
            ORDER BY total_investment DESC;
            """
        )
        result = conn.execute(query).fetchall()
        print("Total Investment by Fund Category:")
        for row in result:
            print(f"Category: {row[0]}, Total Investment: {row[1]:,.2f}")
except Exception as e:
    print(f"Error executing query: {e}")


-- ======================================
-- Transactions by Year and Month:
-- ======================================
from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                d.year,
                d.month,
                COUNT(t.transaction_key) AS total_transactions,
                SUM(t.amount_inr) AS total_amount
            FROM fact_transactions t
            JOIN dim_date d
            ON t.date_key = d.date_key
            GROUP BY d.year,d.month
            ORDER BY d.year,d.month;
            """
        )
        result = conn.execute(query).fetchall()
        print("Transactions by Year and Month:")
        for row in result:
            print(f"Year: {row[0]}, Month: {row[1]}, Total Transactions: {row[2]}, Total Amount: {row[3]:,.2f}")
except Exception as e:
    print(f"Error executing query: {e}")

-- ======================================
-- Top 10 Schemes by Highest NAV:
-- ======================================

from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                f.scheme_name,
                MAX(n.nav) AS highest_nav
            FROM fact_nav n
            JOIN dim_fund f
            ON n.fund_key = f.fund_key
            GROUP BY f.scheme_name
            ORDER BY highest_nav DESC
            LIMIT 10;
            """
        )
        result = conn.execute(query).fetchall()
        print("Top 10 Schemes by Highest NAV:")
        for row in result:
            print(f"Scheme Name: {row[0]}, Highest NAV: {row[1]:,.2f}")
except Exception as e:
    print(f"Error executing query: {e}")

-- ======================================
-- Number of Funds by Risk Category:
-- ======================================

from sqlalchemy import text

try:
    with engine.connect() as conn:
        query = text(
            """
            SELECT
                risk_category,
                COUNT(fund_key) AS number_of_funds
            FROM dim_fund
            GROUP BY risk_category
            ORDER BY number_of_funds DESC;
            """
        )
        result = conn.execute(query).fetchall()
        print("Number of Funds by Risk Category:")
        for row in result:
            print(f"Risk Category: {row[0]}, Number of Funds: {row[1]}")
except Exception as e:
    print(f"Error executing query: {e}")



import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Live Portfolio Health Lab", layout="centered")

st.title("📈 Live Portfolio Health Lab")
st.write("Track any NSE/BSE stock with real-time market data.")

if 'holdings' not in st.session_state:
    st.session_state.holdings = []

# Input Form for Any Stock Symbol
with st.form("holding_form", clear_on_submit=True):
    st.subheader("Add Any Stock Holding")
    
    # Text input allowing any ticker symbol across exchanges
    ticker_symbol = st.text_input("Enter NSE/BSE Ticker Symbol (e.g., HFCL, SUZLON, ZOMATO, RELIANCE)").upper().strip()
    qty = st.number_input("Quantity", min_value=0.0, step=1.0, value=10.0)
    cost = st.number_input("Average Cost Price (₹)", min_value=0.0, step=1.0, value=100.0)
    
    submitted = st.form_submit_button("Add to Portfolio")
    
    if submitted:
        if not ticker_symbol:
            st.error("Please enter a valid stock symbol.")
        else:
            # Auto-format ticker for Yahoo Finance (defaults to National Stock Exchange .NS)
            formatted_ticker = ticker_symbol
            if not formatted_ticker.endswith(('.NS', '.BO')):
                formatted_ticker += '.NS'
                
            st.session_state.holdings.append({
                'display_name': ticker_symbol,
                'ticker': formatted_ticker,
                'qty': qty,
                'cost': cost
            })
            st.success(f"Added {ticker_symbol} successfully!")

# Display Portfolio & Fetch Live Prices
if st.session_state.holdings:
    st.subheader("Your Live Holdings")
    
    portfolio_data = []
    total_market_value = 0
    total_cost_value = 0
    
    for h in st.session_state.holdings:
        current_price = h['cost']
        try:
            stock = yf.Ticker(h['ticker'])
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
        except Exception:
            pass
            
        market_val = h['qty'] * current_price
        invested_val = h['qty'] * h['cost']
        pnl = market_val - invested_val
        pnl_pct = (pnl / invested_val) * 100 if invested_val > 0 else 0
        
        total_market_value += market_val
        total_cost_value += invested_val
        
        portfolio_data.append({
            'Stock': h['display_name'],
            'Qty': h['qty'],
            'Cost (₹)': h['cost'],
            'Live Price (₹)': round(current_price, 2),
            'Market Value (₹)': round(market_val, 2),
            'P&L (₹)': round(pnl, 2),
            'Return (%)': round(pnl_pct, 2)
        })
        
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)
    
    total_pnl = total_market_value - total_cost_value
    total_pnl_pct = (total_pnl / total_cost_value) * 100 if total_cost_value > 0 else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Total Portfolio Value", f"₹{total_market_value:,.2f}")
    col2.metric("Total P&L", f"₹{total_pnl:,.2f}", delta=f"{total_pnl_pct:.2f}%")
    
    if st.button("🗑️ Clear All Holdings", type="primary"):
        st.session_state.holdings = []
        st.rerun()
else:
    st.info("No holdings added yet. Type any stock ticker above (e.g., HFCL) to track it.")

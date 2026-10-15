import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Live Portfolio Health Lab", layout="centered")

st.title("📈 Live Portfolio Health Lab")
st.write("Real-time Indian equity portfolio tracker powered by live market data.")

# Initialize session state for holdings
if 'holdings' not in st.session_state:
    st.session_state.holdings = []

# Input Form
with st.form("holding_form", clear_on_submit=True):
    st.subheader("Add Holding")
    # User inputs NSE/BSE symbol
    ticker_input = st.text_input("Stock Ticker (e.g., RELIANCE, TCS, HDFCBANK, INFY)")
    qty = st.number_input("Quantity", min_value=0.0, step=1.0, value=10.0)
    cost = st.number_input("Average Cost Price (₹)", min_value=0.0, step=1.0, value=1000.0)
    
    submitted = st.form_submit_button("Add to Portfolio")
    
    if submitted and ticker_input:
        clean_ticker = ticker_input.upper().strip()
        # Automatically append .NS for National Stock Exchange if not provided
        if not clean_ticker.endswith(('.NS', '.BO')):
            clean_ticker += '.NS'
            
        st.session_state.holdings.append({
            'ticker': clean_ticker,
            'qty': qty,
            'cost': cost
        })
        st.success(f"Added {clean_ticker} successfully!")

# Display Portfolio & Fetch Live Prices
if st.session_state.holdings:
    st.subheader("Your Live Holdings")
    
    portfolio_data = []
    total_market_value = 0
    total_cost_value = 0
    
    for h in st.session_state.holdings:
        try:
            stock = yf.Ticker(h['ticker'])
            # Fetch live current price
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else h['cost']
        except Exception:
            current_price = h['cost'] # Fallback if network fails
            
        market_val = h['qty'] * current_price
        invested_val = h['qty'] * h['cost']
        pnl = market_val - invested_val
        pnl_pct = (pnl / invested_val) * 100 if invested_val > 0 else 0
        
        total_market_value += market_val
        total_cost_value += invested_val
        
        portfolio_data.append({
            'Stock': h['ticker'].replace('.NS', ''),
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
    
    # Metrics Summary
    col1, col2 = st.columns(2)
    col1.metric("Total Portfolio Value", f"₹{total_market_value:,.2f}")
    col2.metric("Total P&L", f"₹{total_pnl:,.2f}", delta=f"{total_pnl_pct:.2f}%")
    
    if st.button("🗑️ Clear All Holdings", type="primary"):
        st.session_state.holdings = []
        st.rerun()
else:
    st.info("No holdings added yet. Enter a stock ticker above to begin tracking with live prices.")
  

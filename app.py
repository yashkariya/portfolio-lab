import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Live Portfolio Health Lab", layout="centered")

st.title("📈 Live Portfolio Health Lab")
st.write("Real-time Indian equity portfolio tracker powered by live market data.")

# Comprehensive Indian Stock Directory
stock_directory = {
    "Reliance Industries (RELIANCE)": "RELIANCE.NS",
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "HDFC Bank (HDFCBANK)": "HDFCBANK.NS",
    "ICICI Bank (ICICIBANK)": "ICICIBANK.NS",
    "Infosys (INFY)": "INFY.NS",
    "State Bank of India (SBIN)": "SBIN.NS",
    "Bharti Airtel (BHARTIARTL)": "BHARTIARTL.NS",
    "ITC Limited (ITC)": "ITC.NS",
    "Larsen & Toubro (LT)": "LT.NS",
    "Hindustan Unilever (HINDUNILVR)": "HINDUNILVR.NS",
    "Kotak Mahindra Bank (KOTAKBANK)": "KOTAKBANK.NS",
    "Axis Bank (AXISBANK)": "AXISBANK.NS",
    "Bajaj Finance (BAJFINANCE)": "BAJFINANCE.NS",
    "Maruti Suzuki (MARUTI)": "MARUTI.NS",
    "Sun Pharmaceutical (SUNPHARMA)": "SUNPHARMA.NS",
    "Tata Motors (TATAMOTORS)": "TATAMOTORS.NS",
    "Tata Steel (TATASTEEL)": "TATASTEEL.NS",
    "NTPC (NTPC)": "NTPC.NS",
    "Power Grid Corp (POWERGRID)": "POWERGRID.NS",
    "ONGC (ONGC)": "ONGC.NS",
    "Wipro (WIPRO)": "WIPRO.NS",
    "HCL Technologies (HCLTECH)": "HCLTECH.NS",
    "Zomato (ZOMATO)": "ZOMATO.NS",
    "Tata Consumer (TATACONSUM)": "TATACONSUM.NS",
    "Titan Company (TITAN)": "TITAN.NS",
    "Asian Paints (ASIANPAINT)": "ASIANPAINT.NS",
    "Nifty BeES ETF (NIFTYBEES)": "NIFTYBEES.NS",
    "Bank BeES ETF (BANKBEES)": "BANKBEES.NS"
}

if 'holdings' not in st.session_state:
    st.session_state.holdings = []

# Input Form
with st.form("holding_form", clear_on_submit=True):
    st.subheader("Add Holding")
    
    # Searchable selectbox for stocks
    selected_stock_name = st.selectbox(
        "Select or Search Stock", 
        options=list(stock_directory.keys())
    )
    
    qty = st.number_input("Quantity", min_value=0.0, step=1.0, value=10.0)
    cost = st.number_input("Average Cost Price (₹)", min_value=0.0, step=1.0, value=1000.0)
    
    submitted = st.form_submit_button("Add to Portfolio")
    
    if submitted:
        ticker = stock_directory[selected_stock_name]
        st.session_state.holdings.append({
            'name': selected_stock_name,
            'ticker': ticker,
            'qty': qty,
            'cost': cost
        })
        st.success(f"Added {selected_stock_name} successfully!")

# Display Portfolio & Fetch Live Prices
if st.session_state.holdings:
    st.subheader("Your Live Holdings")
    
    portfolio_data = []
    total_market_value = 0
    total_cost_value = 0
    
    for h in st.session_state.holdings:
        try:
            stock = yf.Ticker(h['ticker'])
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else h['cost']
        except Exception:
            current_price = h['cost']
            
        market_val = h['qty'] * current_price
        invested_val = h['qty'] * h['cost']
        pnl = market_val - invested_val
        pnl_pct = (pnl / invested_val) * 100 if invested_val > 0 else 0
        
        total_market_value += market_val
        total_cost_value += invested_val
        
        portfolio_data.append({
            'Stock': h['name'],
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
    st.info("No holdings added yet. Select a stock above to begin tracking with live prices.")

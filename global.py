import requests
from datetime import datetime, date
import pandas as pd
import streamlit as st 
import plotly.graph_objects as go

def currency_finder(amount, fc="INR", base="USD"):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url)
        data = response.json()
        
        if fc in data["rates"]:
            rate = data["rates"][fc]
            converted = rate * amount
            st.success(f"{amount} {base} = {converted:.2f} {fc}")
            return True
        else:
            st.error("Currency not found!")
            return False
    except Exception as e:
        st.error(f"Error fetching exchange rate: {str(e)}")
        return False

def currency_graph_data(fc="INR", base="USD"):
    start_date = datetime(2025, 1, 1)
    end_date = date.today()
    dates = pd.date_range(start_date, end_date, freq='D')
    
    date_list = []
    price_list = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, current_date in enumerate(dates):
        date_str = current_date.strftime("%Y-%m-%d")
        status_text.text(f'Fetching data for {date_str}...')
        progress_bar.progress((i + 1) / len(dates))
        
        try:
            url = f"https://api.frankfurter.app/{date_str}?from={base}&to={fc}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if "rates" in data and fc in data["rates"]:
                    rate = data["rates"][fc]
                    date_list.append(data["date"])
                    price_list.append(rate)
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if date_list and price_list:
        df = pd.DataFrame({
            'date': pd.to_datetime(date_list),
            'price': price_list
        })
        return df
    else:
        st.error("No data available for the selected currency pair.")
        return None

def currency_graph_drawing(df, fc, base):
    if df is None or df.empty:
        st.error("No data to display")
        return
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['price'],
        mode='lines+markers',
        name='Exchange Rate',
        line=dict(color='#00ff88', width=2),
        marker=dict(size=4),
        hovertemplate=f'<b>%{{y:.4f}} {fc}</b><br>%{{x}}<extra></extra>'
    ))

    fig.update_layout(
        title=f"{base} to {fc} Exchange Rate Over Time",
        xaxis_title="Date",
        yaxis_title=f"Exchange Rate ({fc})",
        template="plotly_dark",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary statistics
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Rate", f"{df['price'].iloc[-1]:.4f}")
        with col2:
            st.metric("Highest", f"{df['price'].max():.4f}")
        with col3:
            st.metric("Lowest", f"{df['price'].min():.4f}")
        with col4:
            st.metric("Average", f"{df['price'].mean():.4f}")

def main():
    st.set_page_config(page_icon="📈", page_title="GlobeXchange", layout="wide")
    st.title("GlobeXchange")
    st.subheader("🌍 Your Global Currency Guide")
    st.markdown("Convert any currency and view its exchange rate history over time.")

    currencies = [
        "USD", "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT",
        "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", 
        "CHF", "CLP", "CNY", "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", 
        "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL", "GGP", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", 
        "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", 
        "JOD", "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", 
        "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", 
        "MXN", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", 
        "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", 
        "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", 
        "TRY", "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "UYU", "UZS", "VES", "VND", "VUV", "WST", "XAF", 
        "XCD", "XDR", "XOF", "XPF", "YER", "ZAR", "ZMW", "ZWL"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        amount = st.number_input("Enter the amount:", min_value=0.0, value=1.0, step=0.01)

    with col2:
        base_currency = st.selectbox("From Currency:", currencies, index=currencies.index("USD"))

    with col3:
        target_currency = st.selectbox("To Currency:", currencies, index=currencies.index("INR"))

    if st.button("Convert & Show Graph", type="primary"):
        with st.spinner("Converting currency..."):
            success = currency_finder(amount, target_currency, base_currency)
        
        if success:
            with st.spinner("Fetching historical data..."):
                df = currency_graph_data(target_currency, base_currency)
                if df is not None:
                    currency_graph_drawing(df, target_currency, base_currency)

    st.markdown("---")
    st.markdown("**Note:** Historical data is fetched from Frankfurter API and current rates from ExchangeRate-API.")

if __name__ == "__main__":
    main()
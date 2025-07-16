import requests
from datetime import datetime ,date
import pandas as pd
import streamlit as st 
import plotly.graph_objects as go

start_date = datetime(2025, 1, 1)
end_date = date.today()

dates = pd.date_range(start_date, end_date, freq='D')

date_list = []
price_list = []


def currenc_finder(amount, fc ="INR", base="USD"):
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    response = requests.get(url)
    data = response.json()
    
    if fc in data["rates"]:
        rate = data["rates"][fc]
        converted = rate * amount
        st.success(f"{amount} {base} = {converted:.2f} {fc}")
    else:
        st.error("Currency not found!")

def currency_graph_data( fc ="INR", base="USD"):
    global df  # make it accessible in graph_drawing
    for i in dates:
        date_str = i.strftime("%Y-%m-%d")
        url = f"https://api.frankfurter.app/{date_str}?from={base}&to={fc}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "rates" in data and "INR" in data["rates"]:
                rate = data["rates"]["INR"]
                date_list.append(data["date"])
                price_list.append(rate)

    df = pd.DataFrame({
        'date': date_list,
        'price': price_list
    })

def currency_graph_drawing():
    # Create the plotly chart
    fig = go.Figure()

    # Add the main line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['price'],
        mode='lines',
        name='Price',
        line=dict(color='#00ff88', width=2),
        hovertemplate='<b>%{y:.2f}</b><br>%{x}<extra></extra>'
    ))

    fig.update_layout(
        title="USD to INR Exchange Rate Over Time",
        xaxis_title="Date",
        yaxis_title="Exchange Rate (INR)",
        template="plotly_dark",
        hovermode="x unified"
    )

    # Show chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    
    
    
    


def main():
    st.set_page_config(page_icon="📈", page_title="GlobeXchange", layout="wide")
    st.title("GlobeXchange")
    st.subheader("🌍 Your Global Currency Guide")
    st.markdown("Convert any currency and view its exchange rate history over the past 30 days.")
    
    

    col1, col2, col3 = st.columns(3)

    currencies = ([ "USD","AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT",
        "BGN","BHD","BIF","BMD","BND","BOB","BRL","BSD","BTN","BWP","BYN","BZD","CAD","CDF","CHF","CLP",
        "CNY","COP","CRC","CUP","CVE","CZK","DJF","DKK","DOP","DZD","EGP","ERN","ETB","EUR","FJD","FKP",
        "FOK","GBP","GEL","GGP","GHS","GIP","GMD","GNF","GTQ","GYD","HKD","HNL","HRK","HTG","HUF","IDR",
        "ILS","IMP","INR","IQD","IRR","ISK","JEP","JMD","JOD","JPY","KES","KGS","KHR","KID","KMF","KRW",
        "KWD","KYD","KZT","LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT","MOP",
        "MRU","MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR","NZD","OMR","PAB","PEN",
        "PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR","SBD","SCR","SDG","SEK","SGD",
        "SHP","SLE","SLL","SOS","SRD","SSP","STN","SYP","SZL","THB","TJS","TMT","TND","TOP","TRY","TTD",
        "TVD","TWD","TZS","UAH","UGX","UYU","UZS","VES","VND","VUV","WST","XAF","XCD","XCG","XDR","XOF",
        "XPF","YER","ZAR","ZMW","ZWL"])

    with col1:
        amount = st.number_input("Enter the amount:", min_value=0.0, value=1.0)

    with col2:
        base_currency = st.selectbox("From Currency (FROM):", currencies, index=currencies.index("USD"))

    with col3:
        target_currency = st.selectbox("To Currency (TO):", currencies, index=currencies.index("INR"))

    if st.button("Convert"):
        currenc_finder(amount, target_currency, base_currency)
        currency_graph_data(target_currency, base_currency)
        currency_graph_drawing()

if __name__ == "__main__":
    main()

# Display result
for d, r in zip(date_list, price_list):
    print(f"{d} : {r}")


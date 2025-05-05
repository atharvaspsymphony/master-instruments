import streamlit as st
import pandas as pd
import requests
# Title
st.title("Instrument Master Downloader")

# Input for API URL
api_url = st.text_input(
    "API URL", 
    value="https://developers.symphonyfintech.in/apibinarymarketdata/instruments/master"
)

# Exchange segment options
segment_options = [
    "NSECM", "NSEFO", "NSECD", "NSECO",
    "BSECM", "BSEFO", "BSECD",
    "NCDEX", "MSECM", "MSEFO", "MSECD", "MCXFO"
]

selected_segments = st.multiselect(
    "Select Exchange Segments",
    options=segment_options,
    default=["NSECM", "NSEFO"]
)

# Headers
CM_HEADERS = [
    "ExchangeSegment", "ExchangeInstrumentID", "InstrumentType", "Name", "Description", "Series",
    "NameWithSeries", "InstrumentID", "PriceBand.High", "PriceBand.Low", "FreezeQty", "TickSize",
    "LotSize", "Multiplier", "DisplayName", "ISIN", "PriceNumerator", "PriceDenominator",
    "DetailedDescription", "ExtendedSurvIndicator", "CautionIndicator", "GSMIndicator"
]

FO_HEADERS = [
    "ExchangeSegment", "ExchangeInstrumentID", "InstrumentType", "Name", "Description", "Series",
    "NameWithSeries", "InstrumentID", "PriceBand.High", "PriceBand.Low", "FreezeQty", "TickSize",
    "LotSize", "Multiplier", "UnderlyingInstrumentId", "UnderlyingIndexName", "ContractExpiration",
    "StrikePrice", "OptionType", "DisplayName", "PriceNumerator", "PriceDenominator",
    "DetailedDescription"
]

# Mapping
HEADERS = {
    "NSECM": CM_HEADERS,
    "BSECM": CM_HEADERS,
    "MSECM": CM_HEADERS
}
FO_SEGMENTS = {"NSEFO", "BSEFO", "NSECD", "BSECD", "NSECO", "BSECO", "NCDEX", "MSEFO", "MSECD", "MCXFO"}
for seg in FO_SEGMENTS:
    HEADERS[seg] = FO_HEADERS

def parse_line(line):
    fields = line.split("|")
    segment = fields[0]
    if segment not in HEADERS:
        return None

    header = HEADERS[segment]
    if segment in FO_SEGMENTS:
        if len(fields) == 21:
            fields.insert(17, None)  # StrikePrice
            fields.insert(18, None)  # OptionType
        if len(fields) != len(header):
            return None
    else:
        if len(fields) != len(header):
            return None
    return dict(zip(header, fields))

if st.button("Fetch and Download CSV"):
    if not selected_segments:
        st.error("Please select at least one exchange segment.")
    else:
        with st.spinner("Fetching data..."):
            try:
                payload = {"exchangeSegmentList": selected_segments}
                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                lines = data.get("result", "").strip().split("\n")
                parsed_data = [parsed for line in lines if (parsed := parse_line(line))]

                if not parsed_data:
                    st.warning("No valid data returned.")
                else:
                    df = pd.DataFrame(parsed_data)
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.success("Data fetched successfully!")

                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="instruments_master.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error fetching data: {e}")

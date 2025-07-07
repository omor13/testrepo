import streamlit as st
import requests
import time

# -----------------------
# Azure Computer Vision Config
# -----------------------

endpoint = "https://<YOUR-ENDPOINT>.cognitiveservices.azure.com/"
subscription_key = "<YOUR-SUBSCRIPTION-KEY>"

ocr_url = endpoint + "vision/v3.2/read/analyze"

# -----------------------
# Streamlit App
# -----------------------

st.title("📄 OCR App with Azure Computer Vision")

uploaded_file = st.file_uploader("Upload an image with text", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    image_data = uploaded_file.read()

    # Set headers
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream'
    }

    # Call Read API
    response = requests.post(
        ocr_url,
        headers=headers,
        data=image_data
    )

    if response.status_code != 202:
        st.error("Error: " + str(response.json()))
    else:
        # Extract Operation-Location to poll result
        operation_url = response.headers["Operation-Location"]

        st.write("Processing... please wait ⏳")

        # Poll for result
        analysis = {}
        while True:
            response_final = requests.get(
                operation_url,
                headers={'Ocp-Apim-Subscription-Key': subscription_key}
            )
            analysis = response_final.json()

            status = analysis["status"]

            if status == "succeeded":
                break
            elif status == "failed":
                st.error("OCR failed.")
                break
            time.sleep(1)

        # Show detected text
        st.subheader("📝 Extracted Text")
        text = ""
        for read_result in analysis["analyzeResult"]["readResults"]:
            for line in read_result["lines"]:
                text += line["text"] + "\n"
        st.text_area("Detected Text", text, height=300)
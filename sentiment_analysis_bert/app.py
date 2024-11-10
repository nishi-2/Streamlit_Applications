import streamlit as st
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import tensorflow as tf
import pandas as pd

# Load the saved model and tokenizer
model_path = "doitlazy/bert_binary_sentiment_analysis" 
model = TFAutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)


label_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}

# Function to make predictions
def predict_sentiment(sentences):
    inputs = tokenizer(sentences, return_tensors="tf", padding=True, truncation=True)
    outputs = model(inputs)
    prediction_label = tf.argmax(outputs.logits, axis=1).numpy()
    return prediction_label


# Streamlit App
st.title("Sentiment Analysis App")


# Text area for user input
st.write("Enter sentences below (one per line):")
text_data = st.text_area("Input Text", height=200)


# Predict button
if st.button("Analyze Sentiments"):
    if text_data:
        # Process input into list of sentences
        sentences = text_data.splitlines()
        
        # Make predictions
        predictions = predict_sentiment(sentences)

        # Define sentiment labels as a dictionary
        labels = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}

        # Map predictions to labels
        result = [{"Sentence": s, "Predicted Sentiment": labels[p]} for s, p in zip(sentences, predictions)]

        result_df = pd.DataFrame(result)

        
        # Display the results
        st.write("Sentiment Predictions:")
        st.dataframe(result_df)
        

        # Provide download button for CSV
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Predictions as CSV",
            data=csv,
            file_name="sentiment_predictions.csv",
            mime="text/csv",
        )
    else:
        st.write("Please enter some text to analyze.")

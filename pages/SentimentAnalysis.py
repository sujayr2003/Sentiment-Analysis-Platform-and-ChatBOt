import streamlit as st
import pandas as pd
import pandasql as psql
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import defaultdict
import plotly.graph_objects as go
from plotly import tools
from plotly.subplots import make_subplots
import plotly.express as px
from plotly import __version__
import cufflinks as cf
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected = True)
cf.go_offline()
from wordcloud import WordCloud
import plotly.graph_objs as go
from plotly.offline import iplot
from collections import defaultdict
from wordcloud import STOPWORDS
from plotly import tools
from streamlit_option_menu import option_menu
import io
from hmac import new
import pandas as pd
from sklearn.svm import SVC
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, LSTM, Dense, Dropout,GlobalMaxPooling1D
from keras.layers import GRU,Bidirectional
from tensorflow.keras.optimizers import Adam
from sklearn import metrics
from sklearn.metrics import accuracy_score,f1_score,recall_score,precision_score,confusion_matrix, roc_curve, auc
from streamlit_option_menu import option_menu
from transformers import pipeline
hide_st_style="""
<style> #MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>"""
st.markdown(hide_st_style,unsafe_allow_html=True)
st.title("Classifying reviews as positive or negative based on the ratings given by the users")
option = st.selectbox(
"Select an Option:",
["Perform Sentiment Analysis on the preprocessed dataset you just downloaded from earlier","Classify new review dataset into postive or negative sentiment and then perform sentiment analysis based on the model you select"]
)
if option == "Perform Sentiment Analysis on the preprocessed dataset you just downloaded from earlier":
    uploaded_file = st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings,and Review_Text", type="csv")
    st.write("Note:It is advisible to use a dataset with less no of rows as time to classify may increase with more no of rows")
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        dataframe['Brand'] = dataframe['Product_Title'].apply(lambda x: x.split()[0])
        def label_sentiment(rating):
            if str(rating).startswith("1") or str(rating).startswith("2") or str(rating).startswith("3"):
                return "Negative"
            else:
                return "Positive"
        st.write("Below is a preview of the newly created table with the sentiment of each review mentioned which is classified as positive or negative and as well as renamed columns")
        st.write("Note:Ratings 1,2,3 are classified as negative and ratings 4,5 are classified as positive")
        sentimentdata = dataframe[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
        sentimentdata['Sentiment'] = sentimentdata['Ratings'].apply(label_sentiment)
        st.write(sentimentdata)
        st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
        for sentiment in ['Positive', 'Negative']:
            reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
            wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
            st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
        Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
        st.subheader("Pie Chart representing the number of positive and negative reviews")
        fig, ax = plt.subplots()
        Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
        ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
        ax.set_title('Count of Sentiment')
        st.pyplot(fig)
        query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
        result_pos = psql.sqldf(query_pos, locals())
        st.subheader("Positive Sentiment Word Clouds by Brand:")
        brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
        for index, row in brands_reviews_pos.iterrows():
            brand = row['Brand']
            reviews_text = row['Reviews']
            wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
            st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud_pos, interpolation='bilinear')
            ax.set_title(f"Word Cloud for {brand}")
            ax.axis('off')
            st.pyplot(fig)
        query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
        result_neg = psql.sqldf(query_neg, locals())
        st.subheader("Negative Sentiment Word Clouds by Brand:")
        brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
        for index, row in brands_reviews_neg.iterrows():
            brand = row['Brand']
            reviews_text = row['Reviews']
            wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
            st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud_neg, interpolation='bilinear')
            ax.set_title(f"Word Cloud for {brand}")
            ax.axis('off')
            st.pyplot(fig)
        review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
        review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
        st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
        st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
        #Function for uni-gram generation
        def generate_ngrams(text, n_gram=1):
            token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
            ngrams = zip(*[token[i:] for i in range(n_gram)])
            return [" ".join(ngram) for ngram in ngrams]

        #Function used to generate frequency chart based on uni-grams
        def horizontal_bar_chart(df, color):
            trace = go.Bar(
            y=df["word"].values[::-1],
            x=df["wordcount"].values[::-1],
            showlegend=False,
            orientation='h',
            marker=dict(color=color),
            )
            return trace
        #Generate the bar chart for positive reviews
        freq_dict_pos = defaultdict(int)
        for sent in review_positive["Reviews"]:
            for word in generate_ngrams(sent):
                freq_dict_pos[word] += 1
        fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
        fd_sorted_pos.columns = ["word", "wordcount"]
        trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

        #Generate the bar chart for negative reviews
        freq_dict_neg = defaultdict(int)
        for sent in review_negative["Reviews"]:
            for word in generate_ngrams(sent):
                freq_dict_neg[word] += 1
        fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
        fd_sorted_neg.columns = ["word", "wordcount"]
        trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

        #Creating subplots in Streamlit
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
        fig.add_trace(trace0, row=1, col=1)
        fig.add_trace(trace1, row=2, col=1)
        fig.update_layout(height=1000, width=1000)

        #Displaying the plots in Streamlit
        st.plotly_chart(fig)
        st.write()
        st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
        #Function for bi-gram generation
        def generate_ngrams(text, n_gram=2):
            token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
            ngrams = zip(*[token[i:] for i in range(n_gram)])
            return [" ".join(ngram) for ngram in ngrams]

        #Function used to generate frequency chart based on bi-grams
        def horizontal_bar_chart(df, color):
            trace = go.Bar(
            y=df["word"].values[::-1],
            x=df["wordcount"].values[::-1],
            showlegend=False,
            orientation='h',
            marker=dict(color=color),
            )
            return trace
        #Generate the bar chart for positive reviews
        freq_dict_pos = defaultdict(int)
        for sent in review_positive["Reviews"]:
            for word in generate_ngrams(sent):
                freq_dict_pos[word] += 1
        fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
        fd_sorted_pos.columns = ["word", "wordcount"]
        trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

        #Generate the bar chart for negative reviews
        freq_dict_neg = defaultdict(int)
        for sent in review_negative["Reviews"]:
            for word in generate_ngrams(sent):
                freq_dict_neg[word] += 1
        fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
        fd_sorted_neg.columns = ["word", "wordcount"]
        trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

        #Creating subplots in Streamlit
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
        fig.add_trace(trace0, row=1, col=1)
        fig.add_trace(trace1, row=2, col=1)
        fig.update_layout(height=1000, width=1000)

        #Displaying the plots in Streamlit
        st.plotly_chart(fig)
        st.write()
        st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
        #Function for Tri-gram generation
        def generate_ngrams(text, n_gram=3):
            token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
            ngrams = zip(*[token[i:] for i in range(n_gram)])
            return [" ".join(ngram) for ngram in ngrams]

        #Function used to generate frequency chart based on Tri-grams
        def horizontal_bar_chart(df, color):
            trace = go.Bar(
            y=df["word"].values[::-1],
            x=df["wordcount"].values[::-1],
            showlegend=False,
            orientation='h',
            marker=dict(color=color),
            )
            return trace
        #Generate the bar chart for positive reviews
        freq_dict_pos = defaultdict(int)
        for sent in review_positive["Reviews"]:
            for word in generate_ngrams(sent):
                freq_dict_pos[word] += 1
        fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
        fd_sorted_pos.columns = ["word", "wordcount"]
        trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

        #Generate the bar chart for negative reviews
        freq_dict_neg = defaultdict(int)
        for sent in review_negative["Reviews"]:
            for word in generate_ngrams(sent):
                freq_dict_neg[word] += 1
        fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
        fd_sorted_neg.columns = ["word", "wordcount"]
        trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

        #Creating subplots in Streamlit
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
        fig.add_trace(trace0, row=1, col=1)
        fig.add_trace(trace1, row=2, col=1)
        fig.update_layout(height=1000, width=1000)
        st.plotly_chart(fig)
        st.title("The frequency of each brand present under postive and negative reviews")
        st.write("The frequency of each brand present under postive reviews")
        query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
        output= psql.sqldf(query, locals())
        st.write(output)
        st.write("The frequency of each brand present under negative reviews")
        query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
        output= psql.sqldf(query, locals())
        st.write(output)
        st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
        text = review_positive["Reviews"]
        wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
        st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
        text = review_negative["Reviews"]
        wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
        st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
        st.write()
        # Count of Sentiments by Brand
        st.subheader("The Number of Postive and Negative Reviews for each Brand")
        query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
        result_positive = psql.sqldf(query, locals())
        st.write("The Number of Positive Reviews for each Brand:", result_positive)
        query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
        result_negative = psql.sqldf(query, locals())
        st.write("The Number of Negative Reviews for each Brand:", result_negative)   
        # Display sentiment analysis by product title
        st.subheader("The Number of Postive and Negative Reviews for each Product Title")
        query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
        result_positive_product = psql.sqldf(query, locals())
        st.write("The Number of Positive Reviews for each Product:", result_positive_product)
        query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
        result_negative_product = psql.sqldf(query, locals())
        st.write("The Number of Negative Reviews for each Product:", result_negative_product)
        st.write("Download the final preprocessed and classifed data:")
        csv_buffer = io.BytesIO()
        sentimentdata.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Go back to the start of the buffer
        st.download_button(label="Download the final preprocessed and classified CSV File",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
        st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
        # task_1 Completion Checkbox
        SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
        if SentimentAnalysis_complete:
            st.session_state["SentimentAnalysis_complete"] = True
            st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
            if st.session_state.get("SentimentAnalysis_complete"):
                if st.button("Next Page"):
                   st.session_state.current_page = "ChatBot"
        else:
            st.button("Next Page", disabled=True)
if option == "Classify new review dataset into postive or negative sentiment and then perform sentiment analysis based on the model you select":
   uploaded_file = st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings,and Review_Text based on ratings and then train models", type="csv")
   st.write("Note:It is advisible to use a dataset with less no of rows as time to classify may increase with more no of rows")
   if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    dataframe['Brand'] = dataframe['Product_Title'].apply(lambda x: x.split()[0])
    def label_sentiment(rating):
     if str(rating).startswith("1") or str(rating).startswith("2") or str(rating).startswith("3"):
        return "Negative"
     else:
        return "Positive"
    st.write("Below is a preview of the newly created table with the sentiment of each review mentioned which is classified as positive or negative and as well as renamed columns")
    st.write("Note:Ratings 1,2,3 are classified as negative and ratings 4,5 are classified as positive")
    sentimentdata = dataframe[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
    sentimentdata['Sentiment'] = sentimentdata['Ratings'].apply(label_sentiment)
    st.write(sentimentdata)
    csv_buffer = io.BytesIO()
    sentimentdata.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Go back to the start of the buffer
    st.download_button(label="Click on this button if you want to download this data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
    selected=option_menu(menu_title="Select the type of model you want to train/view results from",options=["Machine Learning","Deep Learning",'Hugging Face Transformer'],orientation="horizontal",)
    if selected == "Machine Learning":
        newdf = sentimentdata
        st.write("### Raw Data Preview")
        st.write(newdf)
    # Dropdown menu
        option = st.selectbox(
        "Select a Model:",
        ["MultinomialNBClassifier", "LogisticRegressionClassifier", "DecisionTreeClassifier", "RandomForestClassifier", "KNeighborsClassifier","SupportVectorMachineClassifier"]
        )
    # Perform action based on the selected option
        if option == "MultinomialNBClassifier":
            data = newdf[['Reviews', 'Sentiment']]
            data['Sentiment'] = data['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)

            splits = {
            "60-40": 0.4,
            "75-25": 0.25,
            "80-20": 0.2,
            "99-1": 0.01
            }

            results = []

            for split_name, test_size in splits.items():
                x_train, x_test, y_train, y_test = train_test_split(data['Reviews'], data['Sentiment'], test_size=test_size, random_state=42)

                # Vectorize the data
                cv = CountVectorizer()
                x_train_count = cv.fit_transform(x_train.values)
                x_test_count = cv.transform(x_test)

                # Train the model
                model = MultinomialNB()
                model.fit(x_train_count, y_train)

                # Predictions
                y_pred = model.predict(x_test_count)
                y_pred_prob = model.predict_proba(x_test_count)[:, 1]

                # Evaluate the model
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                accuracy = accuracy_score(y_test, y_pred)

                # Store results
                results.append([split_name, precision, recall, f1, accuracy])

                # For 80-20 split, plot confusion matrix and ROC curve
                if split_name == "80-20":
                    # Confusion matrix
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)

                    # ROC curve
                    fpr, tpr, _ = roc_curve(y_test, y_pred)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            # Display evaluation results
            results_df = pd.DataFrame(results, columns=['Split', 'Precision', 'Recall', 'F1 Score', 'Accuracy'])
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            # Streamlit input for real-time prediction
            user_input = st.text_input("Enter a review:")
            if user_input:
               x_user_count = cv.transform([user_input])
               user_pred = model.predict(x_user_count)
               sentiment = "positive" if user_pred[0] == 1 else "negative"
               st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = model.predict(cv.transform(sentimentdata['Reviews']))
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(lambda y: "Positive" if y == 1 else "Negative")
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "LogisticRegressionClassifier":
            data = newdf[['Reviews', 'Sentiment']]
            data['Sentiment'] = data['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)
            splits = {
            "60-40": 0.4,
            "75-25": 0.25,
            "80-20": 0.2,
            "99-1": 0.01
            }

            results = []

            for split_name, test_size in splits.items():
                x_train, x_test, y_train, y_test = train_test_split(data['Reviews'], data['Sentiment'], test_size=test_size, random_state=42)
                cv=CountVectorizer()
                x_train_count = cv.fit_transform(x_train.values)
                x_test_count = cv.transform(x_test)
                model=LogisticRegression()
                model.fit(x_train_count,y_train)
                y_pred = model.predict(x_test_count)
                y_pred_prob = model.predict_proba(x_test_count)[:, 1]
                # Evaluate the model
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                accuracy = accuracy_score(y_test, y_pred)

                # Store results
                results.append([split_name, precision, recall, f1, accuracy])

                # For 80-20 split, plot confusion matrix and ROC curve
                if split_name == "80-20":
                    # Confusion matrix
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)

                    # ROC curve
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            # Display evaluation results
            results_df = pd.DataFrame(results, columns=['Split', 'Precision', 'Recall', 'F1 Score', 'Accuracy'])
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            # Streamlit input for real-time prediction
            user_input = st.text_input("Enter a review:")
            if user_input:
               x_user_count = cv.transform([user_input])
               user_pred = model.predict(x_user_count)
               sentiment = "positive" if user_pred[0] == 1 else "negative"
               st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = model.predict(cv.transform(sentimentdata['Reviews']))
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(lambda y: "Positive" if y == 1 else "Negative")
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "DecisionTreeClassifier":
            data = newdf[['Reviews', 'Sentiment']]
            data['Sentiment'] = data['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)
            splits = {
            "60-40": 0.4,
            "75-25": 0.25,
            "80-20": 0.2,
            "99-1": 0.01
            }
            results = []
            for split_name, test_size in splits.items():
                x_train, x_test, y_train, y_test = train_test_split(data['Reviews'], data['Sentiment'], test_size=test_size, random_state=42)
                cv=CountVectorizer()
                x_train_count = cv.fit_transform(x_train.values)
                x_test_count = cv.transform(x_test)
                model=DecisionTreeClassifier()
                model.fit(x_train_count,y_train)
                y_pred = model.predict(x_test_count)
                y_pred_prob = model.predict_proba(x_test_count)[:, 1]
                # Evaluate the model
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                accuracy = accuracy_score(y_test, y_pred)
                # Store results
                results.append([split_name, precision, recall, f1, accuracy])

                # For 80-20 split, plot confusion matrix and ROC curve
                if split_name == "80-20":
                    # Confusion matrix
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)

                    # ROC curve
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            # Display evaluation results
            results_df = pd.DataFrame(results, columns=['Split', 'Precision', 'Recall', 'F1 Score', 'Accuracy'])
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            # Streamlit input for real-time prediction
            user_input = st.text_input("Enter a review:")
            if user_input:
               x_user_count = cv.transform([user_input])
               user_pred = model.predict(x_user_count)
               sentiment = "positive" if user_pred[0] == 1 else "negative"
               st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = model.predict(cv.transform(sentimentdata['Reviews']))
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(lambda y: "Positive" if y == 1 else "Negative")
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "RandomForestClassifier":
            data = newdf[['Reviews', 'Sentiment']]
            data['Sentiment'] = data['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)
            splits = {
            "60-40": 0.4,
            "75-25": 0.25,
            "80-20": 0.2,
            "99-1": 0.01
            }
            results = []

            for split_name, test_size in splits.items():
                x_train, x_test, y_train, y_test = train_test_split(data['Reviews'], data['Sentiment'], test_size=test_size, random_state=42)
                cv=CountVectorizer()
                x_train_count = cv.fit_transform(x_train.values)
                x_test_count = cv.transform(x_test)
                model=RandomForestClassifier()
                model.fit(x_train_count,y_train)
                y_pred = model.predict(x_test_count)
                y_pred_prob = model.predict_proba(x_test_count)[:, 1]
                # Evaluate the model
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                accuracy = accuracy_score(y_test, y_pred)
                # Store results
                results.append([split_name, precision, recall, f1, accuracy])
                if split_name == "80-20":
                    # Confusion matrix
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)

                    # ROC curve
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            # Display evaluation results
            results_df = pd.DataFrame(results, columns=['Split', 'Precision', 'Recall', 'F1 Score', 'Accuracy'])
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            # Streamlit input for real-time prediction
            user_input = st.text_input("Enter a review:")
            if user_input:
               x_user_count = cv.transform([user_input])
               user_pred = model.predict(x_user_count)
               sentiment = "positive" if user_pred[0] == 1 else "negative"
               st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = model.predict(cv.transform(sentimentdata['Reviews']))
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(lambda y: "Positive" if y == 1 else "Negative")
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "KNeighborsClassifier":
            data = newdf[['Reviews', 'Sentiment']]
            data['Sentiment'] = data['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)
            splits = {
            "60-40": 0.4,
            "75-25": 0.25,
            "80-20": 0.2,
            "99-1": 0.01
            }
            results = []

            for split_name, test_size in splits.items():
                x_train, x_test, y_train, y_test = train_test_split(data['Reviews'], data['Sentiment'], test_size=test_size, random_state=42)
                cv=CountVectorizer()
                x_train_count = cv.fit_transform(x_train.values)
                x_test_count = cv.transform(x_test)
                model=KNeighborsClassifier()
                model.fit(x_train_count,y_train)
                y_pred = model.predict(x_test_count)
                y_pred_prob = model.predict_proba(x_test_count)[:, 1]
                # Evaluate the model
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                accuracy = accuracy_score(y_test, y_pred)
                # Store results
                results.append([split_name, precision, recall, f1, accuracy])
                if split_name == "80-20":
                    # Confusion matrix
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)

                    # ROC curve
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            # Display evaluation results
            results_df = pd.DataFrame(results, columns=['Split', 'Precision', 'Recall', 'F1 Score', 'Accuracy'])
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            # Streamlit input for real-time prediction
            user_input = st.text_input("Enter a review:")
            if user_input:
               x_user_count = cv.transform([user_input])
               user_pred = model.predict(x_user_count)
               sentiment = "positive" if user_pred[0] == 1 else "negative"
               st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = model.predict(cv.transform(sentimentdata['Reviews']))
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(lambda y: "Positive" if y == 1 else "Negative")
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "SupportVectorMachineClassifier":
            data = newdf[['Reviews', 'Sentiment']]
            data['Sentiment'] = data['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)
            splits = {
            "60-40": 0.4,
            "75-25": 0.25,
            "80-20": 0.2,
            "99-1": 0.01
            }
            results = []

            for split_name, test_size in splits.items():

                x_train, x_test, y_train, y_test = train_test_split(data['Reviews'], data['Sentiment'], test_size=test_size, random_state=42)
                cv=CountVectorizer()
                x_train_count = cv.fit_transform(x_train.values)
                x_test_count = cv.transform(x_test)
                model = SVC()
                model.fit(x_train_count, y_train)
                y_pred = model.predict(x_test_count)
                #y_pred_prob = model.predict_proba(x_test_count)[:, 1]
                # Evaluate the model
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                accuracy = accuracy_score(y_test, y_pred)
                # Store results
                results.append([split_name, precision, recall, f1, accuracy])
                if split_name == "80-20":
                    # Confusion matrix
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)

                    # ROC curve
                    fpr, tpr, _ = roc_curve(y_test, y_pred)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(y_test, y_pred)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(y_test, y_pred)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            # Display evaluation results
            results_df = pd.DataFrame(results, columns=['Split', 'Precision', 'Recall', 'F1 Score', 'Accuracy'])
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            # Streamlit input for real-time prediction
            user_input = st.text_input("Enter a review:")
            if user_input:
               x_user_count = cv.transform([user_input])
               user_pred = model.predict(x_user_count)
               sentiment = "positive" if user_pred[0] == 1 else "negative"
               st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = model.predict(cv.transform(sentimentdata['Reviews']))
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(lambda y: "Positive" if y == 1 else "Negative")
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
    if selected == "Deep Learning":
        newdf = sentimentdata
        st.write("### Raw Data Preview")
        st.write(newdf)
        option = st.selectbox(
        "Select a Model:",
        ["LSTM", "RecurrentandConvolutionalNeuralNetwork", "ConvolutionalNeuralNetwork", "GateRecurrentUnit", "BidirectionalLSTM"]
        )
        if option == "LSTM":
            data = newdf[['Reviews', 'Sentiment']]
            data.replace({"Sentiment": {"Positive": 1, "Negative": 0}}, inplace=True)

            # Define different train-test split ratios
            split_ratios = {
                "80-20": 0.2,
                "99-1": 0.01,
                "75-25": 0.25,
                "60-40": 0.4
            }

            # Initialize table to store results
            results = []

            for split_name, test_size in split_ratios.items():
                train_data, test_data = train_test_split(data, test_size=test_size, random_state=42)
                tokenizer = Tokenizer(num_words=10000)
                tokenizer.fit_on_texts(train_data["Reviews"])
                X_train = pad_sequences(tokenizer.texts_to_sequences(train_data["Reviews"]), maxlen=200)
                X_test = pad_sequences(tokenizer.texts_to_sequences(test_data["Reviews"]), maxlen=200)
                Y_train = train_data["Sentiment"].values
                Y_test = test_data["Sentiment"].values
                model = Sequential([
                    Embedding(input_dim=10000, output_dim=128, input_length=200),
                    LSTM(128, dropout=0.2, recurrent_dropout=0.2),
                    Dense(1, activation="sigmoid")
                ])
                model.compile(optimizer=Adam(), loss="binary_crossentropy", metrics=["accuracy"])
                model.fit(X_train, Y_train, epochs=5, batch_size=32, validation_split=0.2, verbose=1)
                y_pred_prob = model.predict(X_test).flatten()
                y_pred_classes = (y_pred_prob > 0.5).astype(int)
                precision = precision_score(Y_test, y_pred_classes)
                recall = recall_score(Y_test, y_pred_classes)
                f1 = f1_score(Y_test, y_pred_classes)
                accuracy = accuracy_score(Y_test, y_pred_classes)
                results.append({
                    "Split": split_name,
                    "Precision": precision,
                    "Recall": recall,
                    "F1 Score": f1,
                    "Accuracy": accuracy
                })
                if split_name == "80-20":
                    # Confusion Matrix
                    st.write("Confusion Matrix and ROC Curve for 80-20 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            results_df = pd.DataFrame(results)
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            if 'lstm_model' not in st.session_state:
                st.session_state['lstm_model'] = model
                st.session_state['tokenizer'] = tokenizer
            def predict_sentiment(review):
                sequence = st.session_state['tokenizer'].texts_to_sequences([review])
                padded_sequence = pad_sequences(sequence, maxlen=200)
                prediction = st.session_state['lstm_model'].predict(padded_sequence)
                sentiment = "positive" if prediction[0][0] > 0.5 else "negative"
                return sentiment
            user_input = st.text_input("Enter a review:")
            if user_input:
                sentiment = predict_sentiment(user_input)
                st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(label_sentiment)
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "RecurrentandConvolutionalNeuralNetwork":
            data = newdf[['Reviews', 'Sentiment']]
            data.replace({"Sentiment": {"Positive": 1, "Negative": 0}}, inplace=True)

            # Define different train-test split ratios
            split_ratios = {
                "80-20": 0.2,
                "99-1": 0.01,
                "75-25": 0.25,
                "60-40": 0.4
            }

            results = []

            for split_name, test_size in split_ratios.items():
                train_data, test_data = train_test_split(data, test_size=test_size, random_state=42)
                tokenizer = Tokenizer(num_words=10000)
                tokenizer.fit_on_texts(train_data["Reviews"])
                X_train = pad_sequences(tokenizer.texts_to_sequences(train_data["Reviews"]), maxlen=200)
                X_test = pad_sequences(tokenizer.texts_to_sequences(test_data["Reviews"]), maxlen=200)
                Y_train = train_data["Sentiment"]
                Y_test = test_data["Sentiment"]
                # Define Hybrid CNN-LSTM Model
                model = Sequential([
                Embedding(input_dim=10000, output_dim=128, input_length=200),
                Conv1D(filters=64, kernel_size=3, activation='relu'),
                MaxPooling1D(pool_size=2),
                LSTM(128, dropout=0.2, recurrent_dropout=0.2),
                Dense(1, activation='sigmoid')
                ])
                model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                model.fit(X_train, Y_train, epochs=5, batch_size=32, validation_split=0.2)
                y_pred_prob = model.predict(X_test).flatten()
                y_pred_classes = (y_pred_prob > 0.5).astype(int)
                precision = precision_score(Y_test, y_pred_classes)
                recall = recall_score(Y_test, y_pred_classes)
                f1 = f1_score(Y_test, y_pred_classes)
                accuracy = accuracy_score(Y_test, y_pred_classes)
                results.append({
                    "Split": split_name,
                    "Precision": precision,
                    "Recall": recall,
                    "F1 Score": f1,
                    "Accuracy": accuracy
                })
                if split_name == "80-20":
                    # Confusion Matrix
                    st.write("Confusion Matrix and ROC Curve for 80-20 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            results_df = pd.DataFrame(results)
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            if 'rnnandcnn_model' not in st.session_state:
                st.session_state['rnnandcnn_model'] = model
                st.session_state['tokenizer'] = tokenizer
            def predict_sentiment(review):
                sequence = st.session_state['tokenizer'].texts_to_sequences([review])
                padded_sequence = pad_sequences(sequence, maxlen=200)
                prediction = st.session_state['rnnandcnn_model'].predict(padded_sequence)
                sentiment = "positive" if prediction[0][0] > 0.5 else "negative"
                return sentiment
            user_input = st.text_input("Enter a review:")
            if user_input:
                sentiment = predict_sentiment(user_input)
                st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(label_sentiment)
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "ConvolutionalNeuralNetwork":
            data = newdf[['Reviews', 'Sentiment']]
            data.replace({"Sentiment": {"Positive": 1, "Negative": 0}}, inplace=True)

            # Define different train-test split ratios
            split_ratios = {
                "80-20": 0.2,
                "99-1": 0.01,
                "75-25": 0.25,
                "60-40": 0.4
            }

            results = []

            for split_name, test_size in split_ratios.items():
                train_data, test_data = train_test_split(data, test_size=test_size, random_state=42)
                tokenizer = Tokenizer(num_words=10000)
                tokenizer.fit_on_texts(train_data["Reviews"])
                X_train = pad_sequences(tokenizer.texts_to_sequences(train_data["Reviews"]), maxlen=200)
                X_test = pad_sequences(tokenizer.texts_to_sequences(test_data["Reviews"]), maxlen=200)
                Y_train = train_data["Sentiment"]
                Y_test = test_data["Sentiment"]
                max_words = 10000
                max_len = 200
                model = Sequential()
                model.add(Embedding(max_words, 128, input_length=max_len))
                model.add(Conv1D(128, 5, activation='relu'))
                model.add(GlobalMaxPooling1D())
                model.add(Dense(10, activation='relu'))
                model.add(Dense(1, activation='sigmoid'))
                model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                model.fit(X_train, Y_train, epochs=5, batch_size=32, validation_split=0.2)
                y_pred_prob = model.predict(X_test).flatten()
                y_pred_classes = (y_pred_prob > 0.5).astype(int)
                precision = precision_score(Y_test, y_pred_classes)
                recall = recall_score(Y_test, y_pred_classes)
                f1 = f1_score(Y_test, y_pred_classes)
                accuracy = accuracy_score(Y_test, y_pred_classes)
                results.append({
                    "Split": split_name,
                    "Precision": precision,
                    "Recall": recall,
                    "F1 Score": f1,
                    "Accuracy": accuracy
                })
                if split_name == "80-20":
                    # Confusion Matrix
                    st.write("Confusion Matrix and ROC Curve for 80-20 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            results_df = pd.DataFrame(results)
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            if 'cnn_model' not in st.session_state:
                st.session_state['cnn_model'] = model
                st.session_state['tokenizer'] = tokenizer
            def predict_sentiment(review):
                sequence = st.session_state['tokenizer'].texts_to_sequences([review])
                padded_sequence = pad_sequences(sequence, maxlen=200)
                prediction = st.session_state['cnn_model'].predict(padded_sequence)
                sentiment = "positive" if prediction[0][0] > 0.5 else "negative"
                return sentiment
            user_input = st.text_input("Enter a review:")
            if user_input:
                sentiment = predict_sentiment(user_input)
                st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(label_sentiment)
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "GateRecurrentUnit":
            data = newdf[['Reviews', 'Sentiment']]
            data.replace({"Sentiment": {"Positive": 1, "Negative": 0}}, inplace=True)
            split_ratios = {
                "80-20": 0.2,
                "99-1": 0.01,
                "75-25": 0.25,
                "60-40": 0.4
            }

            results = []
            for split_name, test_size in split_ratios.items():
                train_data, test_data = train_test_split(data, test_size=test_size, random_state=42)
                tokenizer = Tokenizer(num_words=10000)
                tokenizer.fit_on_texts(train_data["Reviews"])
                X_train = pad_sequences(tokenizer.texts_to_sequences(train_data["Reviews"]), maxlen=200)
                X_test = pad_sequences(tokenizer.texts_to_sequences(test_data["Reviews"]), maxlen=200)
                Y_train = train_data["Sentiment"]
                Y_test = test_data["Sentiment"]
                max_words = 10000
                max_len = 200
                model = Sequential()
                model.add(Embedding(max_words, 128, input_length=max_len))
                model.add(GRU(128, return_sequences=False))
                model.add(Dense(1, activation='sigmoid'))
                model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy']) 
                model.fit(X_train, Y_train, epochs=5, batch_size=32, validation_split=0.2)
                y_pred_prob = model.predict(X_test).flatten()
                y_pred_classes = (y_pred_prob > 0.5).astype(int)
                precision = precision_score(Y_test, y_pred_classes)
                recall = recall_score(Y_test, y_pred_classes)
                f1 = f1_score(Y_test, y_pred_classes)
                accuracy = accuracy_score(Y_test, y_pred_classes)
                results.append({
                    "Split": split_name,
                    "Precision": precision,
                    "Recall": recall,
                    "F1 Score": f1,
                    "Accuracy": accuracy
                })
                if split_name == "80-20":
                    # Confusion Matrix
                    st.write("Confusion Matrix and ROC Curve for 80-20 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            results_df = pd.DataFrame(results)
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            if 'gru_model' not in st.session_state:
                st.session_state['gru_model'] = model
                st.session_state['tokenizer'] = tokenizer
            def predict_sentiment(review):
                sequence = st.session_state['tokenizer'].texts_to_sequences([review])
                padded_sequence = pad_sequences(sequence, maxlen=200)
                prediction = st.session_state['gru_model'].predict(padded_sequence)
                sentiment = "positive" if prediction[0][0] > 0.5 else "negative"
                return sentiment
            user_input = st.text_input("Enter a review:")
            if user_input:
                sentiment = predict_sentiment(user_input)
                st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(label_sentiment)
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
        if option == "BidirectionalLSTM":
            data = newdf[['Reviews', 'Sentiment']]
            data.replace({"Sentiment": {"Positive": 1, "Negative": 0}}, inplace=True)
            split_ratios = {
                "80-20": 0.2,
                "99-1": 0.01,
                "75-25": 0.25,
                "60-40": 0.4
            }

            results = []
            for split_name, test_size in split_ratios.items():
                train_data, test_data = train_test_split(data, test_size=test_size, random_state=42)
                tokenizer = Tokenizer(num_words=10000)
                tokenizer.fit_on_texts(train_data["Reviews"])
                X_train = pad_sequences(tokenizer.texts_to_sequences(train_data["Reviews"]), maxlen=200)
                X_test = pad_sequences(tokenizer.texts_to_sequences(test_data["Reviews"]), maxlen=200)
                Y_train = train_data["Sentiment"]
                Y_test = test_data["Sentiment"]
                max_words = 10000
                max_len = 200
                model = Sequential()
                model.add(Embedding(max_words, 128, input_length=max_len))
                model.add(Bidirectional(LSTM(128)))
                model.add(Dense(1, activation='sigmoid'))
                model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                model.fit(X_train, Y_train, epochs=5, batch_size=32, validation_split=0.2)
                y_pred_prob = model.predict(X_test).flatten()
                y_pred_classes = (y_pred_prob > 0.5).astype(int)
                precision = precision_score(Y_test, y_pred_classes)
                recall = recall_score(Y_test, y_pred_classes)
                f1 = f1_score(Y_test, y_pred_classes)
                accuracy = accuracy_score(Y_test, y_pred_classes)
                results.append({
                    "Split": split_name,
                    "Precision": precision,
                    "Recall": recall,
                    "F1 Score": f1,
                    "Accuracy": accuracy
                })
                if split_name == "80-20":
                    # Confusion Matrix
                    st.write("Confusion Matrix and ROC Curve for 80-20 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (80-20 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (80-20 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "99-1":
                    st.write("Confusion Matrix and ROC Curve for 99-1 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (99-1 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (99-1 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "75-25":
                    st.write("Confusion Matrix and ROC Curve for 75-25 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (75-25 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (75-25 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
                if split_name == "60-40":
                    st.write("Confusion Matrix and ROC Curve for 60-40 Split:")
                    cm = confusion_matrix(Y_test, y_pred_classes)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
                    plt.xlabel('Predicted')
                    plt.ylabel('Actual')
                    plt.title('Confusion Matrix (60-40 Split)')
                    st.pyplot(plt)
                    fpr, tpr, _ = roc_curve(Y_test, y_pred_prob)
                    roc_auc = auc(fpr, tpr)
                    plt.figure(figsize=(8, 6))
                    plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve (60-40 Split)')
                    plt.legend(loc="lower right")
                    st.pyplot(plt)
            results_df = pd.DataFrame(results)
            st.write("Evaluation Metrics for Different Splits:")
            st.table(results_df)
            if 'cnn_model' not in st.session_state:
                st.session_state['cnn_model'] = model
                st.session_state['tokenizer'] = tokenizer
            def predict_sentiment(review):
                sequence = st.session_state['tokenizer'].texts_to_sequences([review])
                padded_sequence = pad_sequences(sequence, maxlen=200)
                prediction = st.session_state['cnn_model'].predict(padded_sequence)
                sentiment = "positive" if prediction[0][0] > 0.5 else "negative"
                return sentiment
            user_input = st.text_input("Enter a review:")
            if user_input:
                sentiment = predict_sentiment(user_input)
                st.write(f"The predicted sentiment is: {sentiment}")
            uploaded_file_2=st.file_uploader("Upload the dataset you want to classify with columns Product_Title,Ratings and Reviews to perform sentiment analysis as as determine the sentiment of the reviews based on the model you trained", type="csv")
            newdf=pd.read_csv(uploaded_file_2)
            if uploaded_file_2 is not None:
                newdf['Brand'] = newdf['Product_Title'].apply(lambda x: x.split()[0])
                st.write("Below is a preview of the newly created table with renamed columns")
                sentimentdata = newdf[['Product_Title', 'Brand', 'Review_Text', 'Ratings']].rename(columns={'Product_Title': 'Product_Title', 'Review_Text': 'Reviews'})
                st.write(sentimentdata)
                sentimentdata['Sentiment'] = sentimentdata['Sentiment'].apply(label_sentiment)
                st.write("Your newly created data:")
                st.write(sentimentdata)
                st.subheader("Word Clouds for each of the reviews present in each product of each brand based on whether they are positive or negative")
                for sentiment in ['Positive', 'Negative']:
                    reviews = " ".join(sentimentdata[sentimentdata['Sentiment'] == sentiment]['Reviews'])
                    wordcloud = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(reviews)
                    st.image(wordcloud.to_array(), caption=f"Word Cloud for {sentiment} Reviews")
                Sentiment_Count = sentimentdata['Sentiment'][sentimentdata['Sentiment'] != '-------'].value_counts()
                st.subheader("Pie Chart representing the number of positive and negative reviews")
                fig, ax = plt.subplots()
                Sentiment_Count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99','#cc9999'], ax=ax)
                ax.set_ylabel("")  # Hide y-axis label for cleaner pie chart
                ax.set_title('Count of Sentiment')
                st.pyplot(fig)
                query_pos = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Positive'"
                result_pos = psql.sqldf(query_pos, locals())
                st.subheader("Positive Sentiment Word Clouds by Brand:")
                brands_reviews_pos = result_pos.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_pos.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Positive Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_pos, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                query_neg = "SELECT Brand, Reviews FROM sentimentdata WHERE Sentiment='Negative'"
                result_neg = psql.sqldf(query_neg, locals())
                st.subheader("Negative Sentiment Word Clouds by Brand:")
                brands_reviews_neg = result_neg.groupby('Brand')['Reviews'].apply(lambda x: ' '.join(x)).reset_index()
                for index, row in brands_reviews_neg.iterrows():
                    brand = row['Brand']
                    reviews_text = row['Reviews']
                    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(reviews_text)
                    st.subheader(f"Word Cloud for {brand} (Negative Sentiment)")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_neg, interpolation='bilinear')
                    ax.set_title(f"Word Cloud for {brand}")
                    ax.axis('off')
                    st.pyplot(fig)
                review_positive = sentimentdata[sentimentdata["Sentiment"]=='Positive'].dropna()
                review_negative =sentimentdata[sentimentdata["Sentiment"]=='Negative'].dropna()
                st.title("N- Gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                st.write("Uni-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for uni-gram generation
                def generate_ngrams(text, n_gram=1):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on uni-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Uni-grams)", "Frequent words in negative reviews (Uni-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Bi-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for bi-gram generation
                def generate_ngrams(text, n_gram=2):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on bi-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Bi-grams)", "Frequent words in negative reviews (Bi-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)

                #Displaying the plots in Streamlit
                st.plotly_chart(fig)
                st.write()
                st.write("Tri-gram Analysis based on the most-frequently occuring terms from positive and negative reviews")
                #Function for Tri-gram generation
                def generate_ngrams(text, n_gram=3):
                    token = [token for token in text.lower().split(" ") if token != "" if token not in STOPWORDS]
                    ngrams = zip(*[token[i:] for i in range(n_gram)])
                    return [" ".join(ngram) for ngram in ngrams]

                #Function used to generate frequency chart based on Tri-grams
                def horizontal_bar_chart(df, color):
                    trace = go.Bar(
                    y=df["word"].values[::-1],
                    x=df["wordcount"].values[::-1],
                    showlegend=False,
                    orientation='h',
                    marker=dict(color=color),
                    )
                    return trace
                #Generate the bar chart for positive reviews
                freq_dict_pos = defaultdict(int)
                for sent in review_positive["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_pos[word] += 1
                fd_sorted_pos = pd.DataFrame(sorted(freq_dict_pos.items(), key=lambda x: x[1])[::-1])
                fd_sorted_pos.columns = ["word", "wordcount"]
                trace0 = horizontal_bar_chart(fd_sorted_pos.head(25), 'green')

                #Generate the bar chart for negative reviews
                freq_dict_neg = defaultdict(int)
                for sent in review_negative["Reviews"]:
                    for word in generate_ngrams(sent):
                        freq_dict_neg[word] += 1
                fd_sorted_neg = pd.DataFrame(sorted(freq_dict_neg.items(), key=lambda x: x[1])[::-1])
                fd_sorted_neg.columns = ["word", "wordcount"]
                trace1 = horizontal_bar_chart(fd_sorted_neg.head(25), 'red')

                #Creating subplots in Streamlit
                fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1,
                        subplot_titles=["Frequent words in positive reviews (Tri-grams)", "Frequent words in negative reviews (Tri-grams)"])
                fig.add_trace(trace0, row=1, col=1)
                fig.add_trace(trace1, row=2, col=1)
                fig.update_layout(height=1000, width=1000)
                st.plotly_chart(fig)
                st.title("The frequency of each brand present under postive and negative reviews")
                st.write("The frequency of each brand present under postive reviews")
                query = "SELECT Brand,Count(Brand) FROM review_positive group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.write("The frequency of each brand present under negative reviews")
                query = "SELECT Brand,Count(Brand) FROM review_negative group by Brand order by 2"
                output= psql.sqldf(query, locals())
                st.write(output)
                st.title("Word Clouds representing the most frequently occuring terms present in positive and negative reviews")
                text = review_positive["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in postive reviews:")
                text = review_negative["Reviews"]
                wordcloud = WordCloud(width = 3000,height = 2000,background_color = 'black',stopwords = STOPWORDS).generate(str(text))
                st.image(wordcloud.to_array(),caption=f"Word Cloud representing the most frequently occuring terms present in negative reviews:")
                st.write()
                # Count of Sentiments by Brand
                st.subheader("The Number of Postive and Negative Reviews for each Brand")
                query = "SELECT Brand, COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Brand"
                result_positive = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Brand:", result_positive)
                query = "SELECT Brand, COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Brand"
                result_negative = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Brand:", result_negative)   
                # Display sentiment analysis by product title
                st.subheader("The Number of Postive and Negative Reviews for each Product Title")
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Positive_Count FROM sentimentdata WHERE Sentiment='Positive' GROUP BY Product_Title"
                result_positive_product = psql.sqldf(query, locals())
                st.write("The Number of Positive Reviews for each Product:", result_positive_product)
                query = "SELECT Product_Title,Brand,COUNT(Brand) AS Negative_Count FROM sentimentdata WHERE Sentiment='Negative' GROUP BY Product_Title"
                result_negative_product = psql.sqldf(query, locals())
                st.write("The Number of Negative Reviews for each Product:", result_negative_product)
                csv_buffer = io.BytesIO()
                newdf.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)  # Go back to the start of the buffer
                st.download_button(label="Download your newly created data",data=csv_buffer,file_name="sentimentdata.csv",mime="text/csv")
                st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
                # task_1 Completion Checkbox
                SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
                if SentimentAnalysis_complete:
                    st.session_state["SentimentAnalysis_complete"] = True
                    st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
                if st.session_state.get("SentimentAnalysis_complete"):
                    if st.button("Next Page"):
                        st.session_state.current_page = "ChatBot"
                else:
                    st.button("Next Page", disabled=True)
    if selected == "Hugging Face Transformer":
        st.write("Note: These group of models will not undergo training as it is a pre-trained model only output will be generated and no dataset can be uploaded")
        st.write("Only a table containing classfied sentiment will be generated no sentiment analysis will be done")
        option = st.selectbox(
        "Select a Model:",
        ["mrm8488/t5-base-finetuned-emotion", "j-hartmann/emotion-english-distilroberta-base", "michellejieli/emotion_text_classifier", "LiYuan/amazon-review-sentiment-analysis", "cardiffnlp/twitter-roberta-base-sentiment-latest"]
        )
        if option == "mrm8488/t5-base-finetuned-emotion":
           user_input = st.text_input("Enter the review")
           pipe = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-emotion")
           sentiment=pipe(user_input)
           st.write("Model Output")
           st.write(sentiment[0]['generated_text'])
           st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
            # task_1 Completion Checkbox
           SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
           if SentimentAnalysis_complete:
              st.session_state["SentimentAnalysis_complete"] = True
              st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
           if st.session_state.get("SentimentAnalysis_complete"):
               if st.button("Next Page"):
                    st.session_state.current_page = "ChatBot"
           else:
                st.button("Next Page", disabled=True)
        
        if option == "j-hartmann/emotion-english-distilroberta-base":
            user_input = st.text_input("Enter the review")
            classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
            sentiment1=classifier(user_input)
            st.write("Model Output")
            st.write(sentiment1[0]['label'])   
            st.write(sentiment1[0]['score'])
            st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
            # task_1 Completion Checkbox
            SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
            if SentimentAnalysis_complete:
                st.session_state["SentimentAnalysis_complete"] = True
                st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
            if st.session_state.get("SentimentAnalysis_complete"):
                if st.button("Next Page"):
                    st.session_state.current_page = "ChatBot"
            else:
                st.button("Next Page", disabled=True)
        
        if option == "michellejieli/emotion_text_classifier":
            user_input = st.text_input("Enter the review")
            classifier = pipeline("sentiment-analysis", model="michellejieli/emotion_text_classifier")
            sentiment2=classifier(user_input)
            st.write("Model Output")
            st.write(sentiment2[0]['label'])   
            st.write(sentiment2[0]['score'])
            st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
            # task_1 Completion Checkbox
            SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
            if SentimentAnalysis_complete:
                st.session_state["SentimentAnalysis_complete"] = True
                st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
            if st.session_state.get("SentimentAnalysis_complete"):
                if st.button("Next Page"):
                    st.session_state.current_page = "ChatBot"
            else:
                st.button("Next Page", disabled=True)
        
        if option == "LiYuan/amazon-review-sentiment-analysis":
            user_input = st.text_input("Enter the review")
            classifier = pipeline("text-classification", model="LiYuan/amazon-review-sentiment-analysis")
            sentiment3=classifier(user_input)
            st.write("Model Output")
            st.write(sentiment3[0]['label'])   
            st.write(sentiment3[0]['score'])
            st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
            # task_1 Completion Checkbox
            SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
            if SentimentAnalysis_complete:
                st.session_state["SentimentAnalysis_complete"] = True
                st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
            if st.session_state.get("SentimentAnalysis_complete"):
                if st.button("Next Page"):
                    st.session_state.current_page = "ChatBot"
            else:
                st.button("Next Page", disabled=True)
        
            

        if option == "cardiffnlp/twitter-roberta-base-sentiment-latest":
            user_input = st.text_input("Enter the review")
            classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            sentiment4=classifier(user_input)
            st.write("Model Output")
            st.write(sentiment4[0]['label'])   
            st.write(sentiment4[0]['score'])
            st.write("Complete SentimentAnalysis by checking the box below, then proceed to ChatBot.")
            # task_1 Completion Checkbox
            SentimentAnalysis_complete = st.checkbox("Mark SentimentAnalysis as complete")
            if SentimentAnalysis_complete:
                st.session_state["SentimentAnalysis_complete"] = True
                st.success("SentimentAnalysis complete! You can proceed to the chatbot.")
            if st.session_state.get("SentimentAnalysis_complete"):
                if st.button("Next Page"):
                    st.session_state.current_page = "ChatBot"
            else:
                st.button("Next Page", disabled=True)
        
import twint
import nest_asyncio
nest_asyncio.apply()

import re
import numpy as np
import pandas as pd
from wordcloud import WordCloud

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.font_manager.fontManager.addfont('thsarabunnew-webfont.ttf')
mpl.rc('font', family='TH Sarabun New')

import seaborn as sns

import warnings
warnings.filterwarnings("ignore")

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from sklearn.feature_extraction.text import CountVectorizer

###############################################################################
def get_tweetsDF(hashtag,until,since = '2020-07-14 01:00:00'):
    c = twint.Config()
    c.Pandas =True
    c.Search = hashtag #searching for a phrase or hashtag
    c.Show_hashtags = True  
    c.Limit = 1000000  
    c.Until = until
    c.Since = since
    c.Count = True #show the number of tweets fetched
    c.Retweets = True
    c.Hide_output = True #makes the command line less noisy
    c.Lang = 'th' #ภาษาไทย  อยากดึงข้อมูลภาษาอังกฤษแก้เป็น en 
    #c.Store_csv = True

    twint.run.Search(c)
    
    return twint.storage.panda.Tweets_df

###############################################################################
def cleanText(text):
  text = str(text)
  text = re.sub('[^ก-๙]','',text)
  stop_word = list(thai_stopwords())
  sentence = word_tokenize(text)
  result = [word for word in sentence if word not in stop_word and " " not in word]
  return " /".join(result)

def slash_tokenize(d):
  result = d.split("/")
  result = list(filter(None, result))
  return result

def WordCount(df,column_count):
  new_text = []
  for txt in df[column_count]:
      new_text.append(cleanText(txt))

  vectorizer = CountVectorizer(tokenizer=slash_tokenize)
  transformed_data = vectorizer.fit_transform(new_text)
  count_data = zip(vectorizer.get_feature_names(), np.ravel(transformed_data.sum(axis=0)))
  keyword_df = pd.DataFrame(columns = ['word', 'count'])
  keyword_df['word'] = vectorizer.get_feature_names()
  keyword_df['count'] = np.ravel(transformed_data.sum(axis=0))   
  keyword_df.sort_values(by=['count'], ascending=False).head(10)

  return keyword_df

def plotWordCloud(df):
  word_dict = {}
  for i in range(0,len(df)):
    word_dict[df.word[i]]= df['count'][i]
  wordcloud = WordCloud(font_path='/content/thsarabunnew-webfont.ttf',background_color ='white',max_words=100).fit_words(word_dict)
  fig, ax = plt.subplots(1, 1, figsize=(16, 12))
  ax.imshow(wordcloud, interpolation='bilinear')
  ax.axis("off")
  fig.show()

def plotHashtags(df):

  data_list = df.loc[:,"hashtags"].to_list()

  # putting the twitter in flat list
  flat_data_list = [item for sublist in data_list for item in sublist]
  data_count= pd.DataFrame(flat_data_list)
  data_count= data_count[0].value_counts()
  from nltk.probability import FreqDist
  freq_count= FreqDist()
  for words in data_count:
    freq_count[words] +=1

  data_count = data_count[:20,]
  plt.figure(figsize=(10,5))
  sns.barplot(data_count.values, data_count.index, alpha=0.8)
  plt.title('Top Hashtags Overall')
  plt.ylabel('Hashtags from Tweet', fontsize=12)
  plt.xlabel('Count of Hashtags', fontsize=12)
  plt.show()

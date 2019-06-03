import json
from hazm import *
from nltk import Tree
from sys import getsizeof
from time import sleep
import resource
import re



def clean_text(text):
    result = " "
    for c in text :
        # if c in "qwertyuiopasdfghjklzxcvbnm,.?ض‌صثقفغعهخحجچشسیبلاتنمکگظطزرذدپو #@":
        #     result += c
        if c in "qwertyuiopasdfghjklzxcvbnm,.?ض‌صثقفغعهخحجچشسیبلاتنمکگظطزرذدپو #@":
                result += c
        else:
            result += " "
    return result
# soft, hard = resource.getrlimit(resource.RLIMIT_AS)
# resource.setrlimit(resource.RLIMIT_AS, ( 102400000, hard))
# sleep(10)
# https://www.nltk.org/_modules/nltk/tree.html
normalizer = Normalizer()
stemmer = Stemmer()
# chunker = Chunker(model='resources/chunker.model')
# tagger = POSTagger(model='resources/postagger.model')
emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                u"\U0001f926-\U0001f937"
                u'\U00010000-\U0010ffff'
                u"\u200d"
                u"\u2640-\u2642"
                u"\u2600-\u2B55"
                u"\u23cf"
                u"\u23e9"
                u"\u231a"
                u"\u3030"
                u"\ufe0f"
    "]+", flags=re.UNICODE) 

post_index = 0
c = .0001 #
frequentcy_threshold = 3
one_mines_c = 1 - c

bigram = dict()
layer1_frequency = dict()
layer1_add = 1
layer1_total_add = 1
layer1_threshold = 10 #it was .5
layer1_c = .000001
frequencies = dict() #word to c

farsi_stop_words = []
with open("stopwords_farsi.txt") as f:
    for line in f.readlines():
        farsi_stop_words.append(line.replace("\n", ""))

print(farsi_stop_words)
test_file = open("testfile.txt", 'a')
with open("farsiPosts.txt", 'r') as f:
    for line in f:
        # break
        # if post_index > 200000:
        #     break
        if post_index % 10000 == 9999:
            counters_count = sum(len(v) for v in bigram.values())

            mean_counter_per_word = counters_count / len(bigram)
            print("post index", post_index,"total words:",len(bigram),  "len words:", getsizeof(bigram),"total counters:", counters_count, "mean counter:",
            mean_counter_per_word, "salam len :", len(bigram["سلام"]), bigram["سلام"]["دوستان"], sorted(bigram["سلام"].items(), key=lambda kv: kv[1])[-10:], "c is", frequencies["سلام"] )
            print("layer1add:", layer1_add , layer1_total_add)
        if post_index % 1000 == 999:
            for word in list(bigram):
                
                layer1_frequency[word] /= layer1_add
                if layer1_frequency[word] < layer1_threshold:
                    del bigram[word]
                    del layer1_frequency[word]
                    continue
                for second_word in list(bigram[word]): #change to list for force copy
                    bigram[word][second_word] = bigram[word][second_word] / frequencies[word]
                    if bigram[word][second_word] < frequentcy_threshold:
                        del bigram[word][second_word]
                        # bigram[word].pop(second_word)
                
                frequencies[word] = 1
            layer1_add = 1
        
        post = json.loads(line)["node"]
        try : 
            caption = post["caption"]["text"]
        except:
            continue
        # caption = "حالا هزار بارهم سجده‌ی شکر به جا بیارم، بازهم قطعا کمه😊 من هر روز به حضرت فاطمه توسل کردم"
        # words = word_tokenize(normalizer.normalize(caption))

        # print("old words:", len(words), words)
        # words = [word for word in words if word not in farsi_stop_words]
        # print("medium words:", len(words), words)
        caption = clean_text(caption)
        caption = emoji_pattern.sub(r'', caption) #remove emojies
        words =  [[word for word in word_tokenize(sentence) if word not in farsi_stop_words ]for sentence in sent_tokenize(normalizer.normalize(caption)) ]
        # print("new words:", len(words[0]), words)
        # print(caption)
        if len(words) == 0:
            continue
        else:
            words = words[0]
        # sleep(10)
        for i in range(len(words)):
            # print(words[i])
            if words[i] not in bigram:
                bigram[words[i]] = dict()
                frequencies[words[i]] = 1
            layer1_frequency[words[i]] = layer1_frequency.get(words[i], 0) + layer1_add
            for j in range(max(0, i - 10), min(len(words),i +10)):
                if i != j :
                    # if words[j] not in bigram[words[i]]:
                        # print(words[i], words[j], file = test_file)
                    bigram[words[i]][words[j]] = bigram[words[i]].get(words[j], 0) + frequencies[words[i]]
            frequencies[words[i]] = frequencies[words[i]] / (1 - c)
        layer1_add /= (1 - layer1_c)
        layer1_total_add /= (1 - layer1_c)
        # layer1_add /= (1 - layer1_c)
        

        post_index += 1
        # normalizer.normalize(caption)
        # tagged = tagger.tag(words)
        # chunkedTrees = chunker.parse_all(tagged)
    
        # print("big tree:", chunkedTrees)
        # print("treeeee:", chunker.parse_all(tagged))
        # for tree in chunkedTrees:
            # if(type(tree) == Tree):
            #     print(tree.label())
            #     if(tree.label() == "NP"):
            #         print(tree.leaves())
            # else:
            #     print("bug:",tree)
            
            # print("oO", chunker.parse_one(tagged))
            # for tree.subtrees():

            #     print("tree0:", tree.label())
            # if tree is Tree:

            #     print(tree.subtrees())
            # # for x in tree:
            #     print(x)
            
            # print(tree, "\n\n\n\n\n\n")
        # tree2brackets(chunker.parse(tagged))
        # print("\n\n\n\ncaption:" , caption, "\nnormalized:", normalizer.normalize(caption),
        #      "\ntokenized:", words, "\nstemmed:", stemmer.stem(caption),
        #           "\ntagged:", tagged, "\nt2b:", chunker.parse_all(tagged))
        #             #   chunker.tag

# with open("resulthigh.txt", 'w') as f:
#     for w in sorted(bigram.keys(), key=lambda kv: layer1_frequency[kv])[-10:]:
#         print("word:", w, "\n", "\n\n\n", bigram[w], file=f)

# with open("resultlow.txt", 'w') as f:
#     for w in sorted(bigram.keys(), key=lambda kv: layer1_frequency[kv])[:10]:
#         print("word:", w, "\n", "\n\n\n", bigram[w], file=f)

d= {"چطوری":5, "خوبی ": 67}
# from wordcloud import WordCloud
import matplotlib.pyplot as plt
from persian_wordcloud.wordcloud import PersianWordCloud

# text = text.decode("utf-8")
# text = arabic_reshaper.reshape(text)
# text = get_display(arabic_reshaper.reshape(text))
# import re
# text = "ت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت قیمت دست دست دست دست دست دست ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ ۳۰ دامن دامن دامن دامن دامن دامن دامن دامن دامن مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل مدل قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد قد کار کار کار کار کار کار کار کار کار کار کار کار کار کار کار کار کار عکس عکس عکس عکس عکس عکس عکس عکس عکس عکس عکس عکس عکس عکس سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت سانت غواصی غواصی غواصی غواصی غواصی غواصی غواصی غواصی ۸۰ ۸۰ ۸۰ ۸۰ ۸۰ ۸۰ سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش سفارش رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ رنگ ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست ست پلی پلی پلی پلی پلی پلی پلی استر استر استر استر دلخواه دلخواه دلخواه دلخواه دلخواه دلخواه دلخواه دلخواه دلخواه کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن کالکشن ۹۸ ۹۸ ۹۸ ۹۸ ۹۸ ۹۸ ۹۸ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ کرپ آستین آستین آستین آستین آستین ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ ۳۸ رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی رنگبندی دارای دارای دارای دارای دارای دارای دارای دارای دارای دارای دارای ترک ترک ترک ترک ترک ترک موجود موجود موجود موجود موجود موجود موجود موجود موجود موجود موجود شلوار شلوار شلوار شلوار شلوار شلوار شلوار شلوار شلوار"
 # # emoji_pattern = re.compile(
# #     u"(\ud83d[\ude00-\ude4f])|"  # emoticons
# #     u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
# #     u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
# #     u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
# #     u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
# #     "+", flags=re.UNICODE)
# text = clean_text(text)
# text = emoji_pattern.sub(r'', text)
# wordcloud = PersianWordCloud(width=2000, height=1000,only_persian=True).generate(text)
# image = wordcloud.to_image()
# image.show()
with open("result/result.txt" , 'w') as f:

    for w1 in sorted(bigram.keys(), key=lambda kv: layer1_frequency[kv])[-20:]:
        print("\n\nL1 word:\n", w1,"\nfrequency:", layer1_frequency[w1], "\nwindow size", len(bigram[w1]), "\n20samples:", file = f)
        text = "‌"
        # print(w1)
        i = 0
        for w2 in bigram[w1]:
            if i < 20:
                print(w2,"frequency:", bigram[w1][w2], file = f)
            i += 1
            # print(w1, w2)
            # w2 = w2.split("#")[0]
            
            for _ in range(int(bigram[w1][w2])):
                text = text + w2 + " "

        # print("text is", text)
        wordcloud = PersianWordCloud(width=2000, height=1000, collocations=False).generate(text)
        image = wordcloud.to_image()
        # image.show()
        # image.title
        image.save("result/" + w1+ str(int(layer1_frequency[w1])) +"_"+ str(i) + ".png")
# wordcloud.generate_from_frequencies(frequencies=d)

# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")
# plt.margins(x=0, y=0)
# plt.show()

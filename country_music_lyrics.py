# Dictionary to hold the title,lyrics of the songs
# All lyrics and songs are the property of their copyright holders
# The lyrics are only being used for search purposes in a project to help search songs
import nltk
import collections
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk.corpus import stopwords
import string
nltk.download('punkt')
nltk.download('stopwords')

songs = [
    {
        "title": "Amos Moses",
        "artist": "Jerry Reed",
        "copyright": "BMG Rights Management, Concord Music Publishing LLC",
        "lyrics": """Yeah, here comes Amos
Now Amos Moses was a Cajun
He lived by himself in the swamp
He hunted alligator for a living
He'd just knock them in the head with a stump
The Louisiana law gonna get you, Amos
It ain't legal hunting alligator down in the swamp, boy
Now everyone blamed his old man
For making him mean as a snake
When Amos Moses was a boy
His daddy would use him for alligator bait
Tie a rope around his base and throw him in the swamp (hahaha)
Alligator bait in the Louisiana bayou
About forty-five minutes southeast of Thibodaux, Louisiana
Lived a man called Doc Millsap and his pretty wife Hannah
Well, they raised up a son that could eat up his weight in groceries
Named him after a man of the cloth
Called him Amos Moses, yeah (haha)
Now the folks from down south Louisiana
Said Amos was a hell of a man
He could trap the biggest, the meanest alligator
And he'd just use one hand
That's all he got left 'cause an alligator bit it (hahaha)
Left arm gone clear up to the elbow
Well the sheriff caught wind that Amos
Was in the swamp trapping alligator skin
So he snuck in the swamp to gon' and get the boy
But he never come out again
Well, I wonder where the Louisiana sheriff went to
Well, you can sure get lost in the Louisiana bayou
About forty-five minutes southeast of Thibodaux, Louisiana
Lived a cat called Doc Millsap and his pretty wife Hannah
Well, they raised up a son that could eat up his weight in groceries
Named him after a man of the cloth
Called him Amos Moses
Sit down on 'em Amos!
Make it count son
About forty-five minutes southeast of Thibodaux, Louisiana
Lived a man called Doc Millsap and his pretty wife Hannah

"""
    },
    {
        "title": "Diggin' Up Bones",
        "artist": "Randy Travis",
        "copyright": "Sony/ATV Music Publishing LLC",
        "lyrics": """Last night, I dug your picture out from my old dresser drawer
I set it on the table and I talked to it 'til four
I read some old love letters right up 'til the break of dawn
Yeah, I've been sittin' alone, diggin' up bones
Then I went through the jewelry and I found our wedding rings
I put mine on my finger and I gave yours a fling
Across this lonely bedroom of our recent broken home
Yeah, tonight, I'm sittin' alone, diggin' up bones
I'm diggin' up bones (diggin' up bones)
I'm diggin' up bones (diggin' up bones)
Exhumin' things that's better left alone
I'm resurrectin' memories of a love that's dead and gone
Yeah, tonight, I'm sittin' alone, diggin' up bones
And I went through the closet and I found some things in there
Like that pretty negligee that I bought you to wear
And I recall how good you looked each time you had it on
Yeah, tonight, I'm sittin' alone, diggin' up bones
I'm diggin' up bones (diggin' up bones)
I'm diggin' up bones (diggin' up bones)
Exhumin' things that's better left alone
I'm resurrectin' memories of a love that's dead and gone
Yeah, tonight, I'm sittin' alone, diggin' up bones
I'm resurrectin' memories of a love that's dead and gone
Yeah, tonight, I'm sittin' alone, diggin' up bones (diggin' up bones)
I'm diggin' up bones (diggin' up bones)
Exhumin' things that's better left alone
I'm resurrectin' memories of a love that's dead and gone
Yeah, tonight, I'm sittin' alone, diggin' up bones (diggin' up bones)
I'm diggin' up bones (diggin' up bones)
Exhumin' things that's better left alone
I'm resurrectin' memories of a love that's dead and gone
Yeah, tonight, I'm sittin' alone, diggin' up bones"""

    },
    {
        "title": "Mamas don't let your babies grow up to be cowboys",
        "artist": "Ed Bruce",
        "copyright": "",
        "lyrics": """Mamas, don't let your babies grow up to be cowboys
Don't let 'em pick guitars and drive them old trucks
Make 'em be doctors and lawyers and such
Mamas don't let your babies grow up to be cowboys
'Cause they'll never stay home and they're always alone
Even with someone they love
A Cowboy ain't easy to love and he's harder to hold
He'd rather give you a song than silver or gold
Budweiser buckles and soft faded levis
And each night begins a new day
If you can't understand him, and he don't die young
He'll probably just ride away
Mamas, don't let your babies grow up to be cowboys
Don't let 'em pick guitars and drive them old trucks
Make 'em be doctors and lawyers and such
Mamas don't let your babies grow up to be cowboys
'Cause they'll never stay home and they're always alone
Even with someone they love
A Cowboy like smoky old pool rooms and clear mountain mornings
Little warm puppies and children and girls of the night
Them that don't know him won't like him and them that do
Sometimes won't know how to take him
He ain't wrong, he's just different but his pride won't let him
Do things to make you think he's right
Mamas, don't let your babies grow up to be cowboys
Don't let 'em pick guitars and drive them old trucks
Make 'em be doctors and lawyers and such
Mamas don't let your babies grow up to be cowboys
'Cause they'll never stay home and they're always alone
Even with someone they love
"""

    }
]

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

# set lyrics to lowercase in the dict file
for i in range(len(songs)):
    songs[i]['lyrics'] = songs[i]['lyrics'].lower()

print(songs[0]['lyrics'])

test_lyrics = songs[1]['lyrics']

# tagged_words = nltk.pos_tag(tokens)

# print(tokens)
# print(tagged_words)


class ModifyLyrics:

    def __init__(self, title, lyrics):
        self.title = title
        self.lyrics = lyrics

    def title(self):
        return self.title


def tokenize_lyrics(top_words=1):

    cleaned_lyics = []
    # create the vocabulary
    vocab = set()
    # create the bag-of-words model
    bow_model = []

    for song in range(len(songs)):
        lyrics = songs[song]['lyrics']
        print(lyrics)

        tokens = word_tokenize(lyrics)

        # create a dictionary to store the word counts
        word_counts = {}

        # update the vocabulary
        vocab.update(tokens)

        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        # Add custom words
        custom_words = ["the", "a", ",", "in", "his", "him", "and", "to", "of", "on", "for", "it", "an", "that", "with",
                        "is", "was", "he", "for", "as", "I", "his", "with", "they", "at", "be", "this", "from", "or", "by",
                        "are", "we", "you", "her", "will", "there", "their", "what", "so", "if", "into", "all", "your",
                        "has", "can", "were", "my", "she", "do", "its", "about", "who", "them", "would", "me", "more",
                        "himself", "one", "our", "but", "so", "not", "than", "these", "he's", "who's", "i'm", "she's",
                        "it's", "that's", "there's", "where's", "how's", "what's", "here's", "you're", "i've", "we've",
                        "they've", "isn't", "wasn't", "aren't", "weren't", "can't", "couldn't", "don't", "didn't", "won't",
                        "wouldn't", "shouldn't", "mustn't", "hasn't", "haven't", "hadn't", "doesn't", "aren't", "n't",
                        "get", "let", "'ll", "'m", "'em", "things", "make", "well", "'s","'re", "yeah", "could", "'til"
                        ,"last", "better", "'cause", "'d"
                        
                        
                        ]
        for word in custom_words:
            stop_words.add(word)
        punctuation = set(string.punctuation)

        # remove the stopwords and punctuation
        filtered_tokens = [
            word for word in tokens if word not in stop_words and word not in punctuation]

        # count the occurrences of each word
        for word in filtered_tokens:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        # print each word with its count in
        sorted_word_counts = collections.Counter(word_counts)
        cleaned_lyics.append(sorted_word_counts.most_common(top_words))

    return cleaned_lyics

# bow_model.append(sorted_word_counts)


# print the 10 most common items
# for model in bow_model:
#   print(model.most_common(10))

# puts the lyrics for each song into a list for now
run_function = tokenize_lyrics(top_words=20)

for i in run_function:
    print(i)
    print("")



#No need to convert dictionary to json objects but for reference -
#import json

#json_object = json.dumps(songs[0]['lyrics'])

#print(json_object)
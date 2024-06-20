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
nltk.download('averaged_perceptron_tagger')


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

# set lyrics to lowercase in the dict file
for i in range(len(songs)):
    songs[i]['lyrics'] = songs[i]['lyrics'].lower()
print(songs[0]['lyrics'])
test_lyrics = songs[1]['lyrics']


class song_object:

    """
    The song object tokenizes the lyrics of a list of country songs
    param: songs: a list of dictionaries containing the title, artist, and lyrics of a song
    param: list_of_songs: a list of tokenized lyrics of each song generated in the constructor

    """

    def __init__(self, songs):
        self.songs = songs
        self.attribute = "run"
        self.list_of_songs = self.tokenize_lyrics()

    def choice(self):
        return self.topic

    def get_list_of_songs(self):
        return self.list_of_songs

    def more_than_three(self):
        """
        Here the goal is to return all words that repeat 3 or more times in the lyrics
        """
        def filter_tuples(tuples_list):
            return list((t for t in tuples_list if t[1] >= 3))
        filtered_lists = []
        for i in self.list_of_songs:
            filtered_lists.append(filter_tuples(i))
            return filtered_lists

    def tokenize_lyrics(self):
        """
        Tokenizes the lyrics of each song in the list of songs
        """
        cleaned_lyrics = []
        vocab = set()
        bow_model = []
        for song in range(len(self.songs)):
            lyrics = self.songs[song]['lyrics']
            tokens = word_tokenize(lyrics)
            word_counts = {}
            vocab.update(tokens)
            # Remove stopwords and punctuation
            stop_words = set(stopwords.words('english'))
            # Add custom words to remove e.g. slang stuff a lot of country songs have
            custom_words = ["the", "a", ",", "in", "his", "him", "and", "to", "of", "on", "for", "it", "an", "that", "with",
                            "is", "was", "he", "for", "as", "I", "his", "with", "they", "at", "be", "this", "from", "or", "by",
                            "are", "we", "you", "her", "will", "there", "their", "what", "so", "if", "into", "all", "your",
                            "has", "can", "were", "my", "she", "do", "its", "about", "who", "them", "would", "me", "more",
                            "himself", "one", "our", "but", "so", "not", "than", "these", "he's", "who's", "i'm", "she's",
                            "it's", "that's", "there's", "where's", "how's", "what's", "here's", "you're", "i've", "we've",
                            "they've", "isn't", "wasn't", "aren't", "weren't", "can't", "couldn't", "don't", "didn't", "won't",
                            "wouldn't", "shouldn't", "mustn't", "hasn't", "haven't", "hadn't", "doesn't", "aren't", "n't",
                            "get", "let", "'ll", "'m", "'em", "things", "make", "well", "'s", "'re", "yeah", "could", "'til", "last", "better", "'cause", "'d"]
            for word in custom_words:
                stop_words.add(word)

            punctuation = set(string.punctuation)
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
            cleaned_lyrics.append(sorted_word_counts.most_common())

        return cleaned_lyrics

# sort of the goal here might be to run a sentiment analysis on the lyrics and decide how positive or negative the song is


class evaluation:
    def __init__(self):
        self.song = "Test"

    def tokenize(self):
        return tokenize_lyrics


the_song = song_object(songs)


print(the_song.more_than_three())

import os
import dill
from collections import defaultdict
from tqdm import tqdm
# import string
import chardet

from nltk import sent_tokenize, word_tokenize, ngrams
import random
from collections import Counter
# from nltk.corpus import words
# nltk.download('words')

class NGramLM:
    def __init__(self, corpus_dir, model_dir, ngram_count=2):
        self.corpus_dir = corpus_dir
        self.model_dir = model_dir
        self.ngram_count = ngram_count
        self.model = defaultdict(lambda: defaultdict(int))
        self.context_count = defaultdict(int)
        self.sentences = list()

    def sentence_tokenizer(self):
        for filename in tqdm(os.listdir(self.corpus_dir), desc='Reading files', unit=' file'):
            with open(os.path.join(self.corpus_dir, filename), 'rb') as file:
                data = file.read()
                encoding = chardet.detect(data)['encoding']
                text = data.decode(encoding)
                sentences = sent_tokenize(text)

                # for sentence in sentences:
                #     yield word_tokenize(sentence.lower())
            self.sentences.extend(sentences)

    def build_model(self):
        print('\rBuilding model...', end='')
        self.sentence_tokenizer()
        ngram_count = self.ngram_count
        for sentence in tqdm(self.sentences, desc='Sentences', unit=' sentence'):
            if len(sentence) > 5:
                sentence_ngrams = list(ngrams(word_tokenize(sentence.lower()), 
                                            n=ngram_count, 
                                            pad_left=True, 
                                            pad_right=True, 
                                            left_pad_symbol='<start>', 
                                            right_pad_symbol='<end>'))
    
                for ngram in sentence_ngrams:
                    context = ngram[:-1]
                    next_word = ngram[-1]
                    self.model[context][next_word] += 1
                    self.context_count[context] += 1

    def probability_distribution(self, ngram):
        probabilities = {}
        ngram_tuple = tuple(ngram)
        total_count = self.context_count[ngram_tuple[:-1]]
        
        for word, count in self.model[ngram_tuple[:-1]].items():
            probabilities[word] = count / total_count
        return probabilities

    def save_model(self):
        model_name = 'LM' + str(self.ngram_count) + '.bin'
        model_path = os.path.join(self.model_dir, model_name)
        with open(model_path, 'wb') as file:
            dill.dump((self.model, self.context_count), file)

    def load_model(self):
        model_name = 'LM' + str(self.ngram_count) + '.bin'
        model_path = os.path.join(self.model_dir, model_name)
        with open(model_path, 'rb') as file:
            self.model, self.context_count = dill.load(file)

    def next_word(self, prompt, word_count=1):
        ngram = prompt + ('',)  # Extend prefix with an empty string to match ngram length
        probabilities = self.probability_distribution(ngram)
        prob_counter = Counter(probabilities)
        most_common_kv = prob_counter.most_common(word_count)
        sorted_kv = sorted(most_common_kv, key=lambda x: x[1], reverse=True)
        kv = [(key, value) for key, value in sorted_kv]
        return kv

    def perplexity(sentence):
        #Complete the code
        pass

    def generate_sentences(self, sent_count=2):
        for i in range(sent_count):
            sent_probability = 0.0
            sentence = ''
            start_tokens = ('<start> ' * (self.ngram_count)).lower().split()
            # prompt = tuple(start_tokens)
            probabilities = self.probability_distribution(start_tokens)
            prob_counter = Counter(probabilities)
            print(prob_counter.most_common(10))
            keys = [key for key, _ in prob_counter.most_common(200) 
                            if key.isalpha()]
            #pick a random start word from the collection of 200
            random_key = random.choice(keys)
            sent_probability *= prob_counter[random_key]
            start_tokens.append(random_key)
            n = 0
            sentence = []
            sentence.append(start_tokens[-1])
            new_word = ' '
            while new_word != '<end>':
                # sentence = tuple(start_tokens)
                print(tuple(start_tokens)[-(len(tuple(start_tokens)) - 2):])
                kv = self.next_word(tuple(start_tokens)[-(len(tuple(start_tokens)) - 2):],word_count=1)

                kv2 = self.next_word(tuple(start_tokens)[-(len(tuple(start_tokens)) - 2):],word_count=3)

                for k,v in kv2:
                    print(f'{k}:{v:.4f}')
                print()
                if kv == []:
                    break
                else:
                    new_word = kv[0][0]
                    prob = kv[0][1]
                    start_tokens.pop(0)
                    start_tokens.append(new_word)
                    n += 1
                    if new_word == '<end>':
                        break
                    else:
                        sentence.append(new_word)
                        sent_probability *= prob

            print(f'Sentence[{i}]', ':', (' '.join(sentence).capitalize()).rstrip(),\
                  '\n', f'Probability of the sentence {i} = {sent_probability}')

if __name__ == '__main__':
    corpus_directory = '/home/ramaseshan/corpus/budget_speech'
    model_directory = './models'
    ngram_count = 5

    #Instantiate the object
    lm = NGramLM(corpus_directory, model_directory, ngram_count)

    # lm.build_model()
    # lm.save_model()

    # Load the model and generate sentences ...
    lm.load_model()
    lm.generate_sentences(sent_count=5)
    del lm

    # Exercise - find the perplexity of the sentence

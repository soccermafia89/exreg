import re
import random
import string
import os
from numpy.random import choice

p = re.compile('[a-z]+')

special = ['.','^','$','*','+','?','{','}','\\','[',']','|','(',')']
choices = special + list(string.ascii_letters)
special_weight = [100]*len(special)
letters_weight = [20]*len(list(string.ascii_letters))

weights = special_weight + letters_weight
normal_weights = [float(i)/sum(weights) for i in weights]

class DataGenerator:

  def __init__(self):
    pass;

  def gen_regex(self):
    length = random.randint(3,15)
    raw = ''.join(choice(choices, length, True, normal_weights))

    try:
       re.compile(raw)
       return raw
    except:
      return self.gen_regex() 

  def find_matches(self, raw_regex):

    unique_matches = set()

    regex = re.compile(raw_regex)

    files = os.listdir("./data");
    for filename in files:
      with open("./data/" + filename, "r") as myfile:
        for line in myfile:
          matches = regex.findall(line)
          unique_matches.update(matches)
          if(len(unique_matches) > 10):
              break

    if(len(unique_matches) > 10):
        unique_matches = list(unique_matches)[:10]
    return unique_matches

  def run(self):
    for i in range(0,10000):
      raw_regex = self.gen_regex()
      unique_matches = self.find_matches(raw_regex)

      if(len(unique_matches) > 3):
          print(raw_regex + " -> " + "[" + ", ".join(unique_matches) + "]")

dataGenerator = DataGenerator()
dataGenerator.run()

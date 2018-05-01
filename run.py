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

class LineSampler:
  def __init__(self, file_path):
    self.file_path = file_path

    with open(file_path, "r") as myfile:
      line_offsets = []
      offset = 0
      for line in myfile:
        line_offsets.append(offset)
        offset += len(line)

    random.shuffle(line_offsets)
    self.line_offsets = line_offsets
    self.count = 0
  
  def has_next(self):
    if(self.count > 200 or len(self.line_offsets) == 0):
      return False
    else:
      return True
    pass

  def get_next(self):
    line_offset = self.line_offsets.pop()
    self.count += 1
    with open(self.file_path, "r") as myfile:
      myfile.seek(line_offset)
      return myfile.readline()

class FileSampler:

  def __init__(self, base_path="./data"):
    
    file_samples = []

    for root, sub_dir, files in os.walk(base_path):
      for filename in files:
        path = os.path.join(root, filename)
        if(os.path.isfile(path) and not os.path.isdir(path)):
          line_sampler = LineSampler(path)
          file_samples.append(line_sampler)

    self.file_samples = file_samples

  def has_next(self):
    if(len(file_samples) > 0):
      return True
    else:
      return False

  def get_next(self):
    
    random_index = random.randint(0,len(self.file_samples) - 1)
    line_sampler = self.file_samples[random_index]

    if(not line_sampler.has_next()):
      del self.file_samples[random_index]
      return self.get_next()

    return line_sampler.get_next()

class DataGenerator:

  def __init__(self):
    pass

  def gen_regex(self):
    length = random.randint(3,15)
    raw = ''.join(choice(choices, length, True, normal_weights))

    try:
      re.compile(raw)
      return raw
    except:
      return self.gen_regex() 

  # Randomly selects a list of files
  def select_files(base_path="./data"):
    file_paths = []
    for root, sub_folder, files in os.walk(base_path):
      for item in files:
        path = str(os.path.join(root,sub_folder,item))
        if(os.path.isfile(path) and not os.path.isdir(path)):
          file_paths.append(path)
    random.shuffle(file_paths)
    return file_paths

  def find_matches(self, raw_regex, samples=1000):

    unique_matches = set()

    regex = re.compile(raw_regex)

    sampler = FileSampler()
    for count in range(0, samples):
      line = sampler.get_next()
      matches = regex.findall(line)
      unique_matches.update(matches)
      if(len(unique_matches) > 20):
        break
    
    return unique_matches

  def get_quality(self, unique_matches):
    if(len(unique_matches) == 0):
      return 200

    total_match_length = 0
    for unique_match in unique_matches:
      total_match_length += len(unique_match)
    average_match_length = total_match_length / len(unique_matches)

    match_length_score = 0
    if(average_match_length > 27):
      match_length_score = 25
    elif(average_match_length > 20):
      match_length_score = 15
    elif(average_match_length < 4):
      match_length_score = 11
    elif(average_match_length < 5):
      match_length_score = 7
    elif(average_match_length < 7):
      match_length_score = 3

    num_matches_score = 0
    if len(unique_matches) < 20:
      num_matches_score = (20 - len(unique_matches))/2
      
    return match_length_score + num_matches_score

  # Todo: This can be a lot better (randomly insert and randomly remove)
  def generate_children(self, base_regex, attempts=50):

    children = []

    for count in range(0,attempts):
      length = random.randint(1,3)
      raw = ''.join(choice(choices, length, True, normal_weights))
      child_regex = base_regex + raw

      try:
        re.compile(child_regex)
        children.append(child_regex)
      except:
        pass

    return children
 
  def generate_data(self, base_regex, child_limit=50, child_count=0):
    if(child_count > child_limit):
      return []

    data = {}

    unique_matches = self.find_matches(base_regex, 1500)
    match_quality = self.get_quality(unique_matches)

    if(match_quality < 20):
      print(str(match_quality) + ": " + base_regex + " -> " + str(unique_matches))
      #print(str(match_quality) + ": " + base_regex + " -> " + " ".join(unique_matches))

    if(match_quality < 10):
      data[base_regex] = unique_matches

      if(match_quality < 5):

        print("Quality Regex: " + base_regex + " Score: " + str(match_quality))

        child_regex_list = self.generate_children(base_regex)
        child_count += len(child_regex_list)
        for child_regex in child_regex_list:
          child_data = self.generate_data(child_regex, child_count, child_limit)
          data.update(child_data)

    return data
 
  def run(self):

    total_data = {}

    for i in range(0,5000):
      raw_regex = self.gen_regex()
      data = self.generate_data(raw_regex)
      total_data.update(data)

    for raw_regex in total_data:
      matches = total_data[raw_regex]
      print(raw_regex + " -> " + "".join(matches))

dataGenerator = DataGenerator()
dataGenerator.run()

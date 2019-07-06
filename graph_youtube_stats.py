import numpy as np
from matplotlib import pyplot as plt

view_count_list = []
episode_list = []

with open(input("Insert data file to graph: ")) as f:
    for line in f:
        line = line.split()
        print(line[0],line[1],sep = "\t")
        view_count_list.append(int(line[0]))
        episode_list.append(int(line[1]))

plt.xlabel('Podcast episode')
plt.ylabel('Episode Views')
plt.plot(view_count_list,episode_list)
plt.show()

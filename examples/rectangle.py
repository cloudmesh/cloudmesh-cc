import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G = nx.DiGraph()

nodes = np.arange(0, 8).tolist()

G.add_nodes_from(nodes)
G.add_edges_from([(0,1), (0,2),
 (1,3), (1, 4),
 (2, 5), (2, 6), (2,7)])

pos = {0:(10, 10),
 1:(7.5, 7.5), 2:(12.5, 7.5),
 3:(6, 6), 4:(9, 6),
 5:(11, 6), 6:(14, 6), 7:(17, 6)}

labels = {0:"CEO",
 1:"Team A\nLead", 2: "Team B\nLead",
 3: "Staff A", 4: "Staff B",
 5: "Staff C", 6: "Staff D", 7: "Staff E"}

nx.draw_networkx(G, pos = pos, labels = labels, arrows = True,
 node_shape = "s", node_color = "white")

plt.title("Organogram of a company.")
plt.savefig("plain organogram using networkx.jpeg",
 dpi = 300)
plt.show()


colors = ["white", "skyblue","mistyrose", "skyblue",
          "skyblue","mistyrose", "mistyrose", "mistyrose"]
edge_colors = ["blue", "red", "blue","blue", "red","red","red"]
sizes = [1000, 2000, 2000, 1200, 1200, 1200, 1200, 1200]
nx.draw_networkx(G, pos = pos, labels = labels, arrows = True,
                 node_shape = "s", node_size = sizes,
                 node_color = colors,
                 edge_color = edge_colors,  #color of the edges
                 edgecolors = "gray") #edges of the box of node

nx.draw_networkx_edge_labels(G, pos = pos,
edge_labels={(0, 1): 'A', (0, 2): 'B'},
font_color='black')
plt.title("Organogram of Company X")
plt.show()


nx.draw_networkx(G, pos = pos, labels = labels, 
                 bbox = dict(facecolor = "skyblue",
                 boxstyle = "round", ec = "silver", pad = 0.3),
                 edge_color = "gray"
                )
plt.title("Organogram of Company X")
plt.show()

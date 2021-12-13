import matplotlib.pyplot as plt

x = [1, 2, 3]

y = [1, 2, 3]

plt.scatter(x, y, marker='o')

ax = plt.gca()                            # get the axis
ax.invert_yaxis()
plt.show()

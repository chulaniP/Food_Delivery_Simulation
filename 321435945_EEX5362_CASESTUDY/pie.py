import matplotlib.pyplot as plt

x = [10, 15, 20, 25]
y = [363, 466, 439, 442]

plt.bar(x, y, color='green', edgecolor='black', linewidth=2)

plt.title("Competed Orders")
plt.xlabel("No of Riders")
plt.ylabel("No of order")
plt.show()
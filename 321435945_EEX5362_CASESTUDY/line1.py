import matplotlib.pyplot as plt

x = [10, 15, 20, 25]
y = [2043.91,331.32,170.48,159.70]


plt.plot(x,y)
plt.title("Line chart")
plt.ylabel("dispatch delay(seconds)")
plt.xlabel("No of orders completed")
plt.show()
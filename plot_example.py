import matplotlib.pyplot as plt

# Sample data for the XY plot
x = [1, 2, 3, 4, 5]
y = [2, 3, 5, 7, 11]

# Create the plot
plt.plot(x, y, marker='o')

# Add title and labels
plt.title('Sample XY Plot')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# Show the plot
plt.show()
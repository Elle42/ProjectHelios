import numpy as np
import heapq
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
from scipy.ndimage import binary_dilation

# Define the directions for movement (4-connected grid: up, down, left, right)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1,1), (-1,1), (1,-1), (-1,-1)]

def ManhattanDistanceHeuristic(a, b):          # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def EuclidianDistanceHeuristic(a, b):          # Euclidian distance
    return np.sqrt(np.square(a[0] - b[0])) + np.square(abs(a[1] - b[1]))

def ChebyshevDistanceHeuristic(a, b):          # Chebyshev distance
    return max({abs(a[0] - b[0]), abs(a[1] - b[1])})

def DiagonalDistanceHeuristic(a, b):           # Diagonal distance 
    return 14 * max({abs(a[0] - b[0]), abs(a[1] - b[1])}) + 10 * min({abs(a[0] - b[0]), abs(a[1] - b[1])})

def DijkstraNoHeuristic(a, b):
    return 0

def a_star(bitmap, start, end):
    rows, cols = bitmap.shape
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start:EuclidianDistanceHeuristic(start, end)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for direction in DIRECTIONS:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and bitmap[neighbor] == 1:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + EuclidianDistanceHeuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # Kein Pfad Vorhanden

def visualize_path(bitmap, path, start, end):
    display_map = np.copy(bitmap)
    for x, y in path:
        display_map[x, y] = 0.25  # Path marked as 0.5 for visualization
    display_map[start] = 0.25  # Start point marked as 0.25
    display_map[end] = 0.75  # End point marked as 0.75

    plt.imshow(display_map, cmap="grey")
    plt.title("Path Visualization")
    plt.show()

def load_bitmap_from_png(file_path):
    image = Image.open(file_path).convert("L")  # Convert to grayscale
    bitmap = np.array(image)
    # Treat white pixels (value 255) as walkable and others as obstacles
    bitmap = (bitmap > 232).astype(int)
    return bitmap

def interactive_selection(bitmap):
    fig, ax = plt.subplots()
    ax.imshow(bitmap, cmap="gray")
    plt.title("Start und Enpunkte auswählen")

    points = []

    def on_click(event):
        if len(points) < 2:
            x, y = int(event.ydata), int(event.xdata)
            points.append((x, y))
            ax.plot(y, x, "ro" if len(points) == 1 else "go")  # Red for start, green for end
            plt.draw()

    cid = fig.canvas.mpl_connect("button_press_event", on_click)

    def on_done(event):
        if len(points) == 2:
            plt.close(fig)

    button_ax = plt.axes([0.8, 0.01, 0.1, 0.05])
    button = Button(button_ax, "Done")
    button.on_clicked(on_done)

    plt.show()
    fig.canvas.mpl_disconnect(cid)
    return points if len(points) == 2 else None

# Using the Pathfindr
def main():
    file_path = "C:\\Tst_Data\\Tst_Map.png"
    bitmap = load_bitmap_from_png(file_path)

    print("Bitmap loaded from file.")

    points = interactive_selection(bitmap)
    if points is None:
        print("Selection was not completed.")
        return

    start, end = points
    print(f"Start point: {start}, End point: {end}")

    # Define a 7x7 kernel for a 3-pixel radius
    radius = 7
    kernel_size = 2 * radius + 1
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)



    path = a_star(1 - (binary_dilation(1 - bitmap, structure=kernel).astype(np.uint8)), start, end)

    if path:
        print("Path found:", path)
        visualize_path(bitmap, path, start, end)
    else:
        print("No path found!")

if __name__ == "__main__":
    main()

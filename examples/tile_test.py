import numpy as np
import matplotlib.pyplot as plt

# Example: Simulated 2D DOE pattern (e.g., wrapped phase map)
# Replace this with your actual DOE pattern
unit_doe = np.random.rand(100, 100) * 2 * np.pi  # Random phase from 0 to 2π

# Number of replications in each dimension (e.g., 4x4 tiling)
tile_rows = 4
tile_cols = 4

# Create the larger tiled DOE
tiled_doe = np.tile(unit_doe, (tile_rows, tile_cols))

plt.figure()
plt.imshow(unit_doe,cmap='twilight')

# Optional: Show the result
plt.figure(figsize=(6, 6))
plt.imshow(tiled_doe, cmap='twilight', extent=[0, tiled_doe.shape[1], 0, tiled_doe.shape[0]])
plt.colorbar(label='Phase (radians)')
plt.title('4x4 Replicated DOE Pattern')
plt.show()
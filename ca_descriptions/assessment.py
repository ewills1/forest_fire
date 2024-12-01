# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np

generation = 0

def fire_probability(density, terrain, theta):
    fire_constant = 0.58
    initial_prob = fire_constant * (1+density) * (1+terrain)

    theta_rad = np.radians(theta)

    #Values from literature
    V = 2
    C1 = 0.03
    C2 = 0.05

    ft = np.exp(V * C2 * (np.cos(theta_rad) - 1))
    Pw = ft * np.exp(C1 * V)

    fire_prob = initial_prob * Pw
    return fire_prob


def transition_func(grid, neighbourstates, neighbourcounts, fuel_grid, theta=0):
    new_grid = np.copy(grid)

    NW, N, NE, W, E, SW, S, SE = neighbourstates

    chaparral_terrain = 0
    forest_terrain = -0.4
    canyon_terrain = 0.4

    chaparral_density = 0
    forest_density = 0.3
    canyon_density = -0.2

    chaparral_prob = fire_probability(chaparral_density, chaparral_terrain, theta)
    forest_prob = fire_probability(forest_density, forest_terrain, theta)
    canyon_prob = fire_probability(canyon_density, canyon_terrain, theta)

    # Define wind influence based on theta (wind direction)
    theta_rad = np.radians(theta)
    wind_weights = {
        'N': max(0, np.cos(theta_rad)),
        'NE': max(0, np.cos(theta_rad - np.pi / 4)),
        'E': max(0, np.cos(theta_rad - np.pi / 2)),
        'SE': max(0, np.cos(theta_rad - 3 * np.pi / 4)),
        'S': max(0, np.cos(theta_rad - np.pi)),
        'SW': max(0, np.cos(theta_rad - 5 * np.pi / 4)),
        'W': max(0, np.cos(theta_rad - 3 * np.pi / 2)),
        'NW': max(0, np.cos(theta_rad - 7 * np.pi / 4))
    }

    # Normalize weights to sum to 1 for probability scaling
    total_weight = sum(wind_weights.values())
    for direction in wind_weights:
        wind_weights[direction] /= total_weight

    # Find burnt out cells
    burnt_out_cells = fuel_grid[:,:] < 0.19

    # Set burnt out cells to state 0
    grid[burnt_out_cells] = 0

    # Find cells on fire
    burning_cells = (grid == 6)
    # Reduce fuel
    fuel_grid[burning_cells] -= 0.2

    delay_cells = (grid == 7)
    grid[delay_cells] = 6

    # Find chaparral cells
    chaparral_unburnt = (grid == 2)

    # Find forest cells 
    forest_unburnt = (grid == 3)

    # Find canyon cells
    canyon_unburnt = (grid == 5)

    # Calculate fire spread probabilities for all neighbors based on wind influence
    fire_probabilities = {
        'N': wind_weights['N'],
        'NE': wind_weights['NE'],
        'E': wind_weights['E'],
        'SE': wind_weights['SE'],
        'S': wind_weights['S'],
        'SW': wind_weights['SW'],
        'W': wind_weights['W'],
        'NW': wind_weights['NW']
    }

    # Spread fire to chaparral
    for direction, neighbor in zip(fire_probabilities.keys(), [N, NE, E, SE, S, SW, W, NW]):
        chaparral_fire = chaparral_unburnt & (neighbor == 6)
        chaparral_fire = chaparral_fire & (np.random.random(chaparral_fire.shape) < chaparral_prob * fire_probabilities[direction])
        grid[chaparral_fire] = 6

    # Spread fire to forest
    for direction, neighbor in zip(fire_probabilities.keys(), [N, NE, E, SE, S, SW, W, NW]):
        forest_fire = forest_unburnt & (neighbor == 6)
        forest_fire = forest_fire & (np.random.random(forest_fire.shape) < forest_prob * fire_probabilities[direction])
        grid[forest_fire] = 6

    # Spread fire to canyon
    for direction, neighbor in zip(fire_probabilities.keys(), [N, NE, E, SE, S, SW, W, NW]):
        canyon_fire = canyon_unburnt & (neighbor == 6)
        canyon_fire = canyon_fire & (np.random.random(canyon_fire.shape) < canyon_prob * fire_probabilities[direction])
        grid[canyon_fire] = 6

    global generation
    generation += 1

    # Debugging: Check if any cell has changed in this generation
    if not np.array_equal(grid, new_grid):  # Check if the grid has changed
        print("Grid updated in this generation")
    else:
        print("No change in this generation")

    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Forest Fire Simulation"
    config.dimensions = 2
    # 0 - Burnt Out, 1 - Building, 2 - Chaparral, 3 - Forest, 4 - Lake, 5 - Canyon, 6 - Building on Fire,
    # 7 - Chaparral On Fire,8 - Forest on Fire, 9 - Canyon on Fire
    config.states = (0, 1, 2, 3, 4, 5, 6, 7)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----
    config.state_colors = [(0, 0, 0), # 0 - burnt out
                            (0.25, 0.25, 0.25), #  1 - Building
                            (0.60, 0.80, 0.20), # 2 - chaparral
                            (0.13, 0.54, 0.13), # 3 - forest
                            (0, 0.46, 0.74), # 4 - lake
                            (1, 1, 0), # 5 - canyon
                            (1, 0, 0), # 6 - burning
                            (1, 0, 0) #7 - burning, not spreading yet
                            ]
                               
    config.num_generations = 168
    config.grid_dims = (100,100)

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Initialise decay grid - different values to be given for each terrain, 10 is standard for chaparral
    fuel_grid = np.zeros(config.grid_dims)
    fuel_grid.fill(np.random.uniform(5, 18))

    theta = 0

    # Create grid object
    grid = Grid2D(config, (transition_func, fuel_grid, theta))

    numrows, numcols = grid.grid.shape  # Assuming grid shape is (100, 100)

    # Initialise grid 
    grid.grid.fill(2)

    #Right lake
    grid.grid[52:80, 84:90] = 4

    #Bottom lake
    grid.grid[80:86, 30:60] = 4

    # forest 
    grid.grid[12:20, 0:20] = 3
    grid.grid[12:80, 18:40] = 3

    fuel_grid[12:20, 0:20] = np.random.uniform(36, 72) # last for months
    fuel_grid[12:80, 18:40] = np.random.uniform(36, 72) 

    # right forest
    grid.grid[28:40, 60:86] = 3

    fuel_grid[28:40, 60:86] = np.random.uniform(36, 72) # last for months

    #canyon 
    grid.grid[46:50, 50:86] = 5

    fuel_grid[46:50, 50:86] = np.random.uniform(0.8, 2) # lasts 4 - 10 hours

    #town
    TOWN = 1
    for x in np.arange(67.5, 72.5, 1):  # finer resolution
        for y in np.arange(49.5, 54.5, 1):
            grid.grid[int(x), int(y)] = TOWN

    #powerplant
    POWERPLANT = 1
    grid.grid[30:32, 10:12] = POWERPLANT

    #incinerator
    INCINERATOR = 6
    grid.grid[0:2, numcols-2:numcols] = INCINERATOR


    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)

def drop_water(grid, top_left_x, top_left_y):
    grid[top_left_y:top_left_y + 7, top_left_x:top_left_x + 7] = 4


if __name__ == "__main__":
    main()

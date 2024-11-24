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


def transition_func(grid, neighbourstates, neighbourcounts, decay_grid):
    new_grid = np.copy(grid)

    NW, N, NE, W, E, SW, S, SE = neighbourstates

    #chaparral
    chaparral_unburnt = (grid == 2)

    # forest 
    forest_unburnt = (grid == 3)

    #canyon 
    canyon_unburnt = (grid == 5)

    north_on_fire = (N == 6)
    fire_neighbour = (NW == 6) | (N == 6) | (NE == 6) | (W == 6) | (E == 6) | (SW == 6) | (S == 6) | (SE == 6)

    set_chaparral_fire = chaparral_unburnt & fire_neighbour
    grid[set_chaparral_fire] = 6

    set_forest_on_fire = forest_unburnt & fire_neighbour
    grid[set_forest_on_fire] = 6

    set_canyon_fire = canyon_unburnt & fire_neighbour
    grid[set_canyon_fire] = 6


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
    config.states = (0, 1, 2, 3, 4, 5, 6)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----
    config.state_colors = [(0, 0, 0), # 0 - burnt out
                            (0.25, 0.25, 0.25), #  1 - Building
                            (0.60, 0.80, 0.20), # 2 - chaparral
                            (0.13, 0.54, 0.13), # 3 - forest
                            (0, 0.46, 0.74), # 4 - lake
                            (1, 1, 0), # 5 - canyon
                            (1, 0, 0), # 6 - burning
                            ]
                               
    config.num_generations = 168
    config.grid_dims = (50,50)

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Initialise decay grid
    decay_grid = np.zeros(config.grid_dims)
    decay_grid.fill(10)

    # Create grid object
    grid = Grid2D(config, (transition_func, decay_grid))

    numrows, numcols = grid.grid.shape  # Assuming grid shape is (50, 50)

    # Initialise grid 
    grid.grid.fill(2)

    #Right lake
    grid.grid[26:40, 42:45] = 4

    #Bottom lake
    grid.grid[40:43, 15:30] = 4

    # forest 
    grid.grid[6:10, 0:10] = 3
    grid.grid[6:40, 9:20] = 3

    # right forest
    grid.grid[14:20, 30:43] = 3

    #canyon 
    grid.grid[23:25, 25:43] = 5

    #town
    TOWN = 1
    for x in np.arange(33.75, 36.25, 0.5):  # finer resolution
        for y in np.arange(24.75, 27.25, 0.5):
            grid.grid[int(x), int(y)] = TOWN

    #powerplant
    POWERPLANT = 6
    grid.grid[15:16, 5:6] = POWERPLANT

    #incinerator
    INCINERATOR = 6
    grid.grid[0:1, numcols-1:numcols] = INCINERATOR

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()

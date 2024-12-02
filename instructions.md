# How to run

- Run CAPyLE with `python main.py`.

- Navigate to `file > open` and select the `assessment.py` file.

- Ensure that the selected neighbourhood is `Moore`.

- Press `Apply configuration & run CA`. 

- Note: All other relevant config settings will be applied automatically; only neighbour needs to be set manually.

# Changing fire start position

- By default, incinerator will begin burning.

- To make the power plant the start position, uncomment the following in `main()`:

```py
INCINERATOR = 1
POWERPLANT = 6
```

# Dropping water

- Water can be dropped at any point by uncommenting the following in `transition_func()`:

```py
if generation > 15:
drop_water(grid, 33, 57)
```

- The generation number and (x,y) parameters in drop_water should be changed to drop the water when/where it is needed.

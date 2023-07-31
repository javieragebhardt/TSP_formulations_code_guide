# TSP FORMULATIONS CODE GUIDE
In each file you'll find an explanation of each function and parameters to change.

- ```formulations.py```: file that contains de class ```Solver``` (parent class of all formulations). If you want to add a formulation, you have to edit this file.
- ```generate_instance.py``` file containing a function that generates random instances for a certain number of nodes.
- ```process_data.py```: file that processes data obtained by the Solver class. It contains different functions, each one explained in the file itself.
- ```main.py```: example code of how to use the functions. It exemplifies how to generate instances, solve problems, and process results.
- ```logs```: folder that saves logs of executions.
- ```ìnstances```: folder that stores random generated instances.
- ```graphs```: folder that stores the graphs made.
- ```results_no_relaxed.txt```: example of output thrown when solving a problem
- ```results_no_relaxed.txt```: example of output thrown when solving a problem (relaxation)

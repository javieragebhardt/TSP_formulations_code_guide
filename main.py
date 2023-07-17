# file that exemplifies the use of the code
# IMPORTANT: You must install tsplib95 amd gurobi to use this code

from formulations import DFJ, MTZ, Single_Commodity, Multi_Commodity, Log_Lex  # add formulations here if necessary
from tsplib95 import load
from generate_instance import generate_tsp_file
from process_data import data_by_formulation, average_execution_time, generate_graphic

def create_problem_from_file(filename):
    # creates a problem from a file in TSPLIB format
    problem = load(filename)
    return problem

# Example: creating random instances
# We create 5 instances of 5 nodes, 5 instances of 10 nodes, and 5 instances of 15 nodes
for i in [5, 10, 15]:
    for j in range(1, 6):
        name = f'instances/{i}_{j}.tsp' # modify to change the directory where the instances are saved
        generate_tsp_file(name, i)

# Example: solving random instances with different formulations
for i in [5, 10, 15]:
    for j in range(1, 6):
        name = f'instances/{i}_{j}.tsp'
        problem = create_problem_from_file(name)
        model1 = DFJ(problem, 60 * 10, 'javieragebhardt')
        model1.solve()
        model2 = MTZ(problem, 60 * 10, 'javieragebhardt')
        model2.solve()
        model3 = Single_Commodity(problem, 60 * 10, 'javieragebhardt')
        model3.solve()
        model4 = Multi_Commodity(problem, 60 * 10, 'javieragebhardt')
        model4.solve()
        model5 = Log_Lex(problem, 60 * 10, 'javieragebhardt')
        model5.solve()


# Example: calculating average execution time of a formulation (in this case MTZ) for a given number of nodes
for i in [5, 10, 15]:
    average_no_relaxed = average_execution_time(data_by_formulation('results_no_relaxed.txt')['MTZ'], i)
    average_relaxed = average_execution_time(data_by_formulation('results_relaxed.txt')['MTZ'], i)
    print(f'Average execution time of MTZ for {i} nodes (no relaxed): {average_no_relaxed}')
    print(f'Average execution time of MTZ for {i} nodes (relaxed): {average_relaxed}')

# Example: generating a graphic comparing two formulations Relaxed Objective Value
# In this case Log_Lex and MTZ for 5, 10 and 15 nodes, remember to adjust x and y limits
generate_graphic('results_relaxed.txt', 'Log_Lex', 'MTZ', 3, [5, 10, 15])

# Example: generating a graphic comparing two formulations Execution Time
# In this case Log_Lex and MTZ for 5, 10 and 15 nodes, remember to adjust x and y limits
generate_graphic('results_no_relaxed.txt', 'Log_Lex', 'MTZ', 7, [5, 10, 15])
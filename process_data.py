# file that process data

import matplotlib.pyplot as plt
import os

def data_by_formulation(file_path):
    # reads the data from the file and returns a dictionary with the data separated by formulation
    # receives the path to the file. Example: 'results.txt'
    # could be use in relaxed or not relaxed data
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data_by_formulation = {}
    for line in lines:
        line = line.strip()  
        datos = line.split(',') 
        formulation = datos[0]  
        if formulation not in data_by_formulation:
            data_by_formulation[formulation] = []  
        data_by_formulation[formulation].append(datos)  
    return data_by_formulation

def average_execution_time(data, nodes): 
    # calculates the average execution time of a formulation for a given number of nodes
    # receives:
    # (1) data: data separated by formulation -> data_by_formulation(file_path)[formulation]
    #                                            formulation has to be equal as in the file
    # (3) nodes: number of nodes 
    # could be use in relaxed or not relaxed data
    average_time = 0
    for dato in data:
        if dato[2] == str(nodes):
            average_time += float(dato[-1].strip(';'))
    return average_time/nodes
        

def generate_graphic(file, formulation1, formulation2, comparison, nodes_comparing):
    # generates a graph comparing data of a formulation with data of another formulation 
    # receives:
    # (1) file: file with the data to be compared 
    # (2) formulation1: formulation to be compared (name has to be equal as in the file)
    #                   goes on the x axis
    # (3) formulation2: formulation to be compared (name has to be equal as in the file)
    #                   goes on the y axis
    # (4) comparison: position (int) of the comparison in the file 
    #  Be careful with de type of data:
    #                 Not Relaxed data: (3: status, 4: Objective Value, 5: Best Bound, 6: GAP, 7: Execution Time)
    #                 Relaxed data: (2: Objective Value Relaxed, 3: Execution Time)
    # (5) nodes_comparing: list of nodes to be compared
    data = data_by_formulation(file)
    data_formulation1 = data[formulation1]
    data_formulation2 = data[formulation2]
    # If you want logaritmic scale, just do this:
    # data_formulation1 = np.log10(data_formulation1)
    # data_formulation2 = np.log10(data_formulation2)
    for node in nodes_comparing:
        exec(f"data_formulation_1_{node} = []")
        exec(f"data_formulation_2_{node} = []")
    for instance in data_formulation1:
        for node in nodes_comparing:
            if instance[2] == str(node):
                eval(f"data_formulation_1_{node}").append(float(instance[comparison]))
    for instance in data_formulation2:
        for node in nodes_comparing:
            if instance[2] == str(node):
                eval(f"data_formulation_2_{node}").append(float(instance[comparison]))
    for node in nodes_comparing:
        plt.scatter(eval(f'data_formulation_1_{node}'), eval(f'data_formulation_2_{node}'), 
                    marker='*', label=f'{node} nodes')
    plt.plot([-1000000000, 1000000000], [-1000000000, 1000000000], color='red', linewidth=1) # y = x line
    plt.xlabel(f'{formulation1}')
    plt.ylabel(f'{formulation2}')
    plt.legend()
    plt.title(f'{formulation1} vs {formulation2}')
    plt.axis('equal')
    plt.xlim(0, 30000)  # Adjust x axis limits
    plt.ylim(0, 30000)  # Adjust y axis limits 
    path = os.path.join(os.getcwd(), 'graphs') # Change path where you want to save the graph
    file_name = f'{formulation1}_{formulation2}_{comparison}.pdf' # Change name of the file if necessary
    # Be carefull with the name of the file, if you don't change it, it will overwrite the previous file
    # plt.show() # Show the image, comment if you don't want to show it
    plt.savefig(os.path.join(path, file_name), 
                format='pdf') # Save the image in pdf format, change if necessary
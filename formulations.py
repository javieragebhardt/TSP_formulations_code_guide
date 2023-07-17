# this file includes all the formulations of the TSP

import gurobipy as gp
from gurobipy import GRB
import itertools
import numpy as np

class Solver:
    # Father class that solves different formulations, receives:
    #  (1) name of the file of the instance: 'file_name.tsp'
    #  (2) maximum time of execution in seconds.
    #  (3) username of Gurobi
    def __init__(self, problem, time_limit, username):
        # Initialize the problem
        self.problem = problem
        self.time_limit = time_limit
        self.username = username
        self.env = gp.Env()
        self.env.setParam('username', username)
        self.model = gp.Model('tsp', env = self.env)
        self.formulation_name = type(self).__name__

        # Modify Parameters
        self.model.setParam('TimeLimit', self.time_limit)
        self.model.setParam("Threads", 1)
        self.model.setParam('Heuristics', 0)
        self.model.setParam('Cuts', 0)

        # Generate log file 
        instance = self.problem.name.split('/')[1]
        log_file = f'logs/test/{self.formulation_name}/{instance}.log' 
        # In this case, the log file is saved in logs -> test -> self.formulation.name (DFJ, MTZ, etc)
        # The files must be created before executing the code (not instance.log)
        # with the name 'instance.log' 
        self.model.setParam('LogFile', log_file)

        # TSP for all formulations
        self.x = self.model.addVars(self.problem.get_edges(), vtype = GRB.BINARY, name = "x")
        self.model.addConstrs((gp.quicksum(self.x[i,j] for j in self.problem.get_nodes() if i != j) == 1 for i in self.problem.get_nodes()), name = f"RA")
        self.model.addConstrs((gp.quicksum(self.x[i,j] for i in self.problem.get_nodes() if i != j) == 1 for j in self.problem.get_nodes()), name = f"RB")

        # Update
        self.model.update()
    
    def solve(self):
        # Solves the original and relaxed problem

        # Sets objective, creates relaxed problem and and includes the formulation
        self.model.setObjective(gp.quicksum(self.problem.get_weight(i, j) * self.x[i, j] for j in self.problem.get_nodes() for i in self.problem.get_nodes() if i != j), GRB.MINIMIZE)
        self.formulation()
        self.model.update()
        self.model_relax = self.model.relax()

        # Solves the problem 
        obj_val, exec_time, gap, bestbound = self.solve_no_relaxed(self.model)
        # Solves the relaxed problem
        obj_val_relaxed, time_exec_relaxed = self.solve_relaxed(self.model_relax)

        #No relaxed: 
        # (0) formulation name 
        # (1) problem name 
        # (2) # nodes
        # (3) status
        # (4) Objective Value
        # (5) Best Bound
        # (6) GAP
        # (7) Execution Time
        results = f'{self.formulation_name},{self.problem.name},{len(list(self.problem.get_nodes()))},{self.model.status},{obj_val},{bestbound},{gap},{exec_time}'

        # Relaxed
        # (0) formulation name 
        # (1) problem name 
        # (2) # nodes
        # (3) Objective Value Relaxed
        # (4) Execution Time
        results_relaxed = f'{self.formulation_name},{self.problem.name},{len(list(self.problem.get_nodes()))},{obj_val_relaxed}, {time_exec_relaxed}'


        # Saves the results in 2 different files
        file_no_relaxed = 'results_no_relaxed.txt' # Change name if necessary
        file_relaxed = 'results_relaxed.txt'    # Change name if necessary
        with open(file_no_relaxed, "a") as file:
            file.write(results + "\n")
        with open(file_relaxed, "a") as file:
            file.write(results_relaxed + "\n")
            
        self.model.resetParams()

    def solve_no_relaxed(self, model):
        # Solves the original problem
        model.optimize()
        objective_value = model.ObjVal
        time_execution = model.runtime
        gap = model.MIPGap
        bestbound = model.getAttr("ObjBound")

        return objective_value, time_execution, gap, bestbound
    
    def solve_relaxed(self, model_relaxed):
        # Solves the relaxed problem
        model_relaxed.optimize()
        objective_value_relaxed = model_relaxed.ObjVal
        time_execution = model_relaxed.runtime

        return objective_value_relaxed, time_execution
    
    def formulation(self):
        # Abstract function
        pass

# Formulations:

class DFJ(Solver):
    # DFJ formulation
    def __init__(self, problem, time_limit, username):
        # Inherit from Solver
        super().__init__(problem, time_limit, username)
    
    def formulation(self):
        # Sub-tour restrictions
        for subset_size in range(2, len(list(self.problem.get_nodes()))):
            for subset in itertools.combinations(range(1, len(list(self.problem.get_nodes())) + 1), subset_size):
                self.model.addConstr(gp.quicksum(self.x[i, j] for i in subset for j in subset if i != j) <= subset_size - 1)

class MTZ(Solver):

    def __init__(self, problem, time_limit, username):
        # Inherit from Solver
        super().__init__(problem, time_limit, username)

    def formulation(self):
        # Sub-tour restrictions
        self.u = self.model.addVars(self.problem.get_nodes(), vtype = GRB.CONTINUOUS, name = "u") 
        self.model.addConstrs(gp.quicksum(self.x[i,j] for j in self.problem.get_nodes() if i != j) == 1 for i in self.problem.get_nodes())
        self.model.addConstrs(gp.quicksum(self.x[i,j] for i in self.problem.get_nodes() if i != j) == 1 for j in self.problem.get_nodes())
        self.model.addConstrs(self.u[i] - self.u[j] + (len(list(self.problem.get_nodes())) - 1) * self.x[i, j] <= len(list(self.problem.get_nodes())) - 2 for i in range(1, len(list(self.problem.get_nodes()))) for j in range(1, len(list(self.problem.get_nodes()))) if i != j)
        self.model.addConstrs(self.u[i] >= 1 for i in range(1, len(list(self.problem.get_nodes()))))
        self.model.addConstrs(self.u[i] <= len(list(self.problem.get_nodes())) - 1 for i in range(1, len(list(self.problem.get_nodes()))))
        self.model.addConstrs(self.x[i,j] <= 1 for i in self.problem.get_nodes() for j in self.problem.get_nodes() if i != j)
        self.model.addConstrs(self.x[i,j] >= 0 for i in self.problem.get_nodes() for j in self.problem.get_nodes() if i != j)

class Single_Commodity(Solver):

    def __init__(self, problem, time_limit, username):
        # Inherit from Solver
        super().__init__(problem, time_limit, username)

    def formulation(self):
        # Sub-tour restrictions
        self.g = self.model.addVars(self.problem.get_edges(), vtype = GRB.CONTINUOUS, name = "g_ij")
        self.model.addConstrs(gp.quicksum(self.g[j, i] for j in range(1, len(list(self.problem.get_nodes())) + 1)) -  gp.quicksum(self.g[i, j] for j in range(2, len(list(self.problem.get_nodes())) + 1)) == 1 for i in range(2, len(list(self.problem.get_nodes())) + 1))
        self.model.addConstrs(self.g[i, j] >= 0 for i in range(1, len(list(self.problem.get_nodes())) + 1) for j in range(2, len(list(self.problem.get_nodes())) + 1))
        self.model.addConstrs(self.g[i, j] <= (len(list(self.problem.get_nodes())) - 1) * self.x[i, j] for i in range(1, len(list(self.problem.get_nodes())) + 1) for j in range(2, len(list(self.problem.get_nodes())) + 1) if i != j)

class Multi_Commodity(Solver):

    def __init__(self, problem, time_limit, username):
        # Inherit from Solver
        super().__init__(problem, time_limit, username)

    def formulation(self):
        # Sub-tour restrictions
        w = self.model.addVars(self.problem.get_edges(), self.problem.get_nodes(), self.problem.get_nodes(), name = "wl")

        self.model.addConstrs(gp.quicksum(self.x[i, j] for j in self.problem.get_nodes() if i != j) == 1 for i in self.problem.get_nodes())
        self.model.addConstrs(gp.quicksum(self.x[i, j] for i in self.problem.get_nodes() if i != j) == 1 for j in self.problem.get_nodes())

        self.model.addConstrs(gp.quicksum(w[i, j, 1, l] for j in self.problem.get_nodes()) - gp.quicksum(w[j, i, 1, l] for j in self.problem.get_nodes()) == 0 for i in range(2, len(list(self.problem.get_nodes())) + 1) for l in range(2, len(list(self.problem.get_nodes())) + 1) if i != l)
        self.model.addConstrs(gp.quicksum(w[1, j, 1, l] for j in range(2, len(list(self.problem.get_nodes())) + 1)) - gp.quicksum(w[j, 1, 1, l] for j in range(2, len(list(self.problem.get_nodes())) + 1)) == 1 for l in range(2, len(list(self.problem.get_nodes())) + 1))
        self.model.addConstrs(gp.quicksum(w[i, j, 1, i] for j in self.problem.get_nodes()) - gp.quicksum(w[j, i, 1, i] for j in self.problem.get_nodes()) ==  - 1 for i in range(2, len(list(self.problem.get_nodes())) + 1))
        self.model.addConstrs(gp.quicksum(w[i, j, k, 1] for j in self.problem.get_nodes()) - gp.quicksum(w[j, i, k, 1] for j in self.problem.get_nodes()) == 0 for i in range(2, len(list(self.problem.get_nodes())) + 1) for k in range(2, len(list(self.problem.get_nodes())) + 1) if i != k)
        self.model.addConstrs(gp.quicksum(w[1, j, k, 1] for j in range(2, len(list(self.problem.get_nodes())) + 1)) - gp.quicksum(w[j, 1, k, 1] for j in range(2, len(list(self.problem.get_nodes())) + 1)) == - 1 for k in range(2, len(list(self.problem.get_nodes())) + 1))
        self.model.addConstrs(gp.quicksum(w[i, j, i, 1] for j in self.problem.get_nodes()) - gp.quicksum(w[j, i, i, 1] for j in self.problem.get_nodes()) ==  1 for i in range(2, len(list(self.problem.get_nodes())) + 1))

        self.model.addConstrs(w[i, j, 1, l] <= self.x[i,j] for i in self.problem.get_nodes() for j in self.problem.get_nodes() for l in range(2, len(list(self.problem.get_nodes())) + 1) if i != j)
        self.model.addConstrs(w[i, j, 1, l] >= 0 for i in self.problem.get_nodes() for j in self.problem.get_nodes() for l in range(2, len(list(self.problem.get_nodes())) + 1) if i != j)
        self.model.addConstrs(w[i, j, k, 1] <= self.x[i,j] for i in self.problem.get_nodes() for j in self.problem.get_nodes() for k in range(2, len(list(self.problem.get_nodes())) + 1) if i != j)
        self.model.addConstrs(w[i, j, k, 1] >= 0 for i in self.problem.get_nodes() for j in self.problem.get_nodes() for k in range(2, len(list(self.problem.get_nodes())) + 1) if i != j)


class Log_Lex(Solver):

    def __init__(self, problem, time_limit, username):
        # Inherit from Solver
        super().__init__(problem, time_limit, username)

    def formulation(self):
        # Sub-tour restrictions
        l = int(np.ceil(np.log(len(list(self.problem.get_nodes()))))) + 1
        self.z = {}
        self.p0 = {}
        self.p00 = {}
        self.p11 = {}
        self.q10 = {}
        self.q01 = {}
        self.r0 = {}
        self.r00 = {}
        self.r11 = {}
        self.r10 = {}
        self.r01 = {}
        for i in self.problem.get_nodes():
            if i != 1:
                for t in range(1, l + 1):
                    self.z[i, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"z[{i},{t}]")
        for i in self.problem.get_nodes():
            for j in self.problem.get_nodes():
                if i < j and i != 1 and j != 1:
                    self.p0[i, j] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"p0[{i},{j}]")
                    self.r0[i, j] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"r0[{i},{j}]")
                    for t in range(1, l + 1):
                        self.q10[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"q10[{i},{j},{t}]")
                        self.q01[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"q01[{i},{j},{t}]")
                        self.r00[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"r00[{i},{j},{t}]")
                        self.r11[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"r11[{i},{j},{t}]")
                        self.r10[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"r10[{i},{j},{t}]")
                        self.r01[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"r01[{i},{j},{t}]")
                    for t in range(1, l):
                        self.p00[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"p00[{i},{j},{t}]")
                        self.p11[i, j, t] = self.model.addVar(vtype = GRB.CONTINUOUS, name = f"p11[{i},{j},{t}]")
                    self.model.addConstrs(self.z[i, t] == self.p11[i, j, t] + self.q10[i, j, t] + self.r10[i, j, t] + self.r11[i, j, t] for t in range(1, l))
                    self.model.addConstrs(self.z[j, t] == self.p11[i, j, t] + self.q01[i, j, t] + self.r01[i, j, t] + self.r11[i, j, t] for t in range(1, l))
                    self.model.addConstr(self.z[i, l] == self.q10[i, j, l] + self.r10[i, j, l] + self.r11[i, j, l])
                    self.model.addConstr(self.z[j, l] == self.q01[i, j, l] + self.r01[i, j, l] + self.r11[i, j, l])
                    self.model.addConstr(self.p0[i, j] + self.r0[i, j] == 1)
                    self.model.addConstr(self.p0[i, j] == self.p00[i, j, 1] + self.p11[i, j, 1] + self.q01[i, j, 1] + self.q10[i, j, 1])
                    self.model.addConstrs(self.p00[i, j, t] + self.p11[i, j, t] == self.p00[i, j, t + 1] + self.p11[i, j, t + 1] + self.q01[i, j, t + 1] + self.q10[i, j, t + 1] for t in range(1, l - 1))
                    self.model.addConstr(self.p00[i, j, l - 1] + self.p11[i, j, l - 1] == self.q01[i, j, l] + self.q10[i, j, l])
                    self.model.addConstr(self.r0[i, j] == self.r00[i, j, 1] + self.r10[i, j, 1] + self.r01[i, j, 1] + self.r11[i, j, 1])
                    self.model.addConstrs(self.r00[i, j, t] + self.r10[i, j, t] + self.r01[i, j, t] + self.r11[i, j, t] + self.q01[i, j, t] + self.q10[i, j, t] == self.r00[i, j, t + 1] + self.r10[i, j, t + 1] + self.r01[i, j, t + 1] + self.r11[i, j, t + 1] for t in range(1, l))
                    self.model.addConstr(self.r00[i, j, l] + self.r10[i, j, l] + self.r01[i, j, l] + self.r11[i, j, l] + self.q01[i, j, l] + self.q10[i, j, l] == 1)
                    self.model.addConstr(self.x[i, j] == gp.quicksum(self.q01[i, j, t] for t in range(1, l + 1)))
                    self.model.addConstr(self.x[j, i] == gp.quicksum(self.q10[i, j, t] for t in range(1, l + 1)))






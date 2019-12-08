from __future__ import print_function
from ortools.linear_solver import pywraplp

from edgeDevice import edgeDevice
from virtualChain import virtualChain
from virtualFunction import virtualFunction

import random
import numpy as np

if __name__ == "__main__":

    #Create edge network
    D01 = edgeDevice("D01", 1.2*10**6);
    D02 = edgeDevice("D02", 1.2*10**4);
    D03 = edgeDevice("D03", 1.2*10**5);
    D04 = edgeDevice("D04", 9.2*10**2);
    D05 = edgeDevice("D05", 2.2*10**3);
    D06 = edgeDevice("D06", 6.2*10**2);
    D07 = edgeDevice("D07", 2.2*10**4);
    D08 = edgeDevice("D08", 1.2*10**6);

    edgeDevicelist = [];
    edgeDevicelist.append(D01);
    edgeDevicelist.append(D02);
    edgeDevicelist.append(D03);
    edgeDevicelist.append(D04);
    edgeDevicelist.append(D05);
    edgeDevicelist.append(D06);
    edgeDevicelist.append(D07);
    edgeDevicelist.append(D08);

    #Create Virtal Functions
    VF01 = virtualFunction("VF01", 3*10**4);
    VF02 = virtualFunction("VF02", 2*10**5);
    VF03 = virtualFunction("VF03", 6*10**4);
    VF04 = virtualFunction("VF04", 2*10**3);

    #create virtualChain
    service01 = virtualChain("service01", 10);
    service01.addVF(VF01);
    service01.addVF(VF02);
    service01.addVF(VF03);
    service01.addVF(VF04);

    service01.print();

    print(D01.getProcessingTime(VF01.getLoad()));

    num_workers = len(edgeDevicelist);
    num_tasks = len(service01.getGVF());

    solver = pywraplp.Solver('SolveAssignmentProblemMIP',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    #create cost matrix
    cost = np.zeros([num_workers, num_tasks]);
    for i in range(num_workers):
        for j in range(num_tasks):
            cost[i][j] = edgeDevicelist[i].getCost(service01.getVF(j).getLoad());
    #print(cost);


    #create time processing matrix
    timeProc = np.zeros([num_workers, num_tasks]);
    for i in range(num_workers):
        for j in range(num_tasks):
            timeProc[i][j] = edgeDevicelist[i].getProcessingTime(service01.getVF(j).getLoad());
    print(timeProc);


    team1 = [0, 1, 2, 3, 5, 6, 7];
    #print(team1);
    #team2 = [1, 3, 5]
    #team_max = 2

    #num_workers = len(cost)
    #num_tasks = len(cost[1])
    x = {}

    for i in range(num_workers):
        for j in range(num_tasks):
            x[i, j] = solver.BoolVar('x[%i,%i]' % (i, j))

    # Objective
    solver.Minimize(solver.Sum([cost[i][j] * x[i,j] for i in range(num_workers)
                                                  for j in range(num_tasks)]))

    # Constraints

    # Each worker is assigned to at most 1 task.

    for i in range(num_workers):
        solver.Add(solver.Sum([x[i, j] for j in range(num_tasks)]) <= 1)

    # Each task is assigned to exactly one worker.

    for j in range(num_tasks):
        solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) == 1)


    #support QoS
    solver.Add( solver.Sum( [ timeProc[i][j] * x[i, j] for i in team1 for j in range(num_tasks) ] ) <= service01.getQoS() )########################
    #solver.Add(solver.Sum([x[i, j] for i in team2 for j in range(num_tasks)]) <= team_max)
    sol = solver.Solve()

    print('Total cost = ', solver.Objective().Value());
    print()
    for i in range(num_workers):
        for j in range(num_tasks):
            if x[i, j].solution_value() > 0:
                print('Edge Device %d assigned to VF %d:  Cost = %f' % (
                i,
                j,
                cost[i][j]))


    tpsum = 0;
    for i in range(num_workers):
        for j in range(num_tasks):
            if x[i, j].solution_value() > 0:
                tpsum = tpsum + timeProc[i][j];
                print(i, ' ', j, ' ', tpsum)
    print('Total processing time = ', tpsum);
    print('QoS                   = ', service01.getQoS());

    print()
    print("Time = ", solver.WallTime(), " milliseconds")

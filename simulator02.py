from __future__ import print_function
from ortools.linear_solver import pywraplp

from edgeDevice import edgeDevice
from virtualChain import virtualChain
from virtualFunction import virtualFunction

import random
import numpy as np
from gekko import GEKKO


if __name__ == "__main__":

    #Create edge network
    D00 = edgeDevice("D00", 1.2*10**7);
    D01 = edgeDevice("D01", 1.2*10**7);
    D02 = edgeDevice("D02", 1.2*10**5);
    D03 = edgeDevice("D03", 9.2*10**2);
    D04 = edgeDevice("D04", 2.2*10**3);
    D05 = edgeDevice("D05", 6.2*10**2);
    D06 = edgeDevice("D06", 2.2*10**4);
    D07 = edgeDevice("D07", 1.2*10**6);

    edgeDevicelist = [];
    edgeDevicelist.append(D00);
    edgeDevicelist.append(D01);
    edgeDevicelist.append(D02);
    edgeDevicelist.append(D03);
    edgeDevicelist.append(D04);
    edgeDevicelist.append(D05);
    edgeDevicelist.append(D06);
    edgeDevicelist.append(D07);

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

    num_workers = len(edgeDevicelist);
    num_tasks = len(service01.getGVF());

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

    m = GEKKO() # Initialize gekko
    m.options.SOLVER=1  # APOPT is an MINLP solver

    # optional solver settings with APOPT
    m.solver_options = ['minlp_maximum_iterations 500', \
                        # minlp iterations with integer solution
                        'minlp_max_iter_with_int_sol 10', \
                        # treat minlp as nlp
                        'minlp_as_nlp 0', \
                        # nlp sub-problem max iterations
                        'nlp_maximum_iterations 50', \
                        # 1 = depth first, 2 = breadth first
                        'minlp_branch_method 1', \
                        # maximum deviation from whole number
                        'minlp_integer_tol 0.05', \
                        # covergence tolerance
                        'minlp_gap_tol 0.01']

    # Initialize variables
    x = {}
    for i in range(num_workers):
        for j in range(num_tasks):
            x[i, j] = m.Var(value=0,lb=0,ub=1,integer=True)


    # Equations
    for i in range(num_workers):
        m.Equation(
            sum([x[i, j] for j in range(num_tasks)]) <= 1
            );

    for j in range(num_tasks):
        m.Equation(
            sum([x[i, j] for i in range(num_workers)]) == 1
            );


    #m.Equation(x1*x2*x3*x4>=25)
    m.Equation(
                sum( [ timeProc[i][j] * x[i, j] for i in range(num_workers) for j in range(num_tasks) ] ) <= service01.getQoS()
                );
    m.Obj(sum([cost[i][j] * x[i,j] for i in range(num_workers)
                                for j in range(num_tasks)])) # Objective
    m.solve(disp = True) # Solve
    print('Results')
    for i in range(num_workers):
        for j in range(num_tasks):
            #print(str(x[i, j].value))
            if int(str(x[i, j].value)[1]) == 1:
                print('VF %d assigned to Edge Device %s:  Cost = %f' % (
                j,
                edgeDevicelist[i].getName(),
                cost[i][j]))
    print('Objective: ' + str(m.options.objfcnval))


    tpsum = 0;
    for i in range(num_workers):
        for j in range(num_tasks):
            if int(str(x[i, j].value)[1]) == 1:
                tpsum = tpsum + timeProc[i][j];
                print(i, ' ', j, ' ', tpsum)
    print('Total processing time = ', tpsum);
    print('QoS                   = ', service01.getQoS());

from __future__ import print_function
from ortools.linear_solver import pywraplp
from operator import itemgetter

from edgeDevice import edgeDevice
from virtualChain import virtualChain
from virtualFunction import virtualFunction

import random
import numpy as np
from gekko import GEKKO

def getEDminkth(k):
    cpus = [];
    for i in range(len(edgeDevicelist)):
        cpus.append([i,edgeDevicelist[i].getCPU()]);

    cpus = sorted(cpus, key=itemgetter(1));

    return edgeDevicelist[cpus[k][0]];

if __name__ == "__main__":

    #Create edge network
    D00 = edgeDevice("D00", 1.2*10**7);
    D01 = edgeDevice("D01", 1.2*10**6);
    D02 = edgeDevice("D02", 9.7*10**5);
    D03 = edgeDevice("D03", 9.5*10**5);
    D04 = edgeDevice("D04", 9.9*10**6);
    D05 = edgeDevice("D05", 9.7*10**5);
    D06 = edgeDevice("D06", 9.7*10**5);
    D07 = edgeDevice("D07", 9.7*10**6);
    D08 = edgeDevice("D08", 6.7*10**6);
    D09 = edgeDevice("D09", 9.7*10**7);
    D10 = edgeDevice("D10", 2.7*10**6);
    D11 = edgeDevice("D11", 3.7*10**6);
    D12 = edgeDevice("D12", 3.7*10**7);
    D13 = edgeDevice("D13", 9.7*10**5);
    D14 = edgeDevice("D14", 9.7*10**5);
    D15 = edgeDevice("D15", 9.7*10**6);
    D16 = edgeDevice("D16", 3.7*10**7);
    D17 = edgeDevice("D17", 9.7*10**7);
    D18 = edgeDevice("D18", 7.7*10**7);
    D19 = edgeDevice("D19", 9.7*10**8);

    edgeDevicelist = [];
    edgeDevicelist.append(D00);
    edgeDevicelist.append(D01);
    edgeDevicelist.append(D02);
    edgeDevicelist.append(D03);
    edgeDevicelist.append(D04);
    edgeDevicelist.append(D05);
    edgeDevicelist.append(D06);
    edgeDevicelist.append(D07);
    edgeDevicelist.append(D08);
    edgeDevicelist.append(D09);
    edgeDevicelist.append(D10);
    edgeDevicelist.append(D11);
    edgeDevicelist.append(D12);
    edgeDevicelist.append(D13);
    edgeDevicelist.append(D14);
    edgeDevicelist.append(D15);
    edgeDevicelist.append(D16);
    edgeDevicelist.append(D17);
    edgeDevicelist.append(D18);
    edgeDevicelist.append(D19);

    #Create Virtal Functions
    VF01 = virtualFunction("VF01", 5*10**4, False);
    VF02 = virtualFunction("VF02", 4*10**5, False);
    VF03 = virtualFunction("VF03", 5*10**6, False);
    VF04 = virtualFunction("VF04", 5*10**6, False);

    #create virtualChain
    service01 = virtualChain("service01", 25);
    service01.addVF(VF01);
    service01.addVF(VF02);
    service01.addVF(VF03);
    service01.addVF(VF04);

    #service01.print();

    while (True):#repeat until chain has been successfully deployed

        num_workers = len(edgeDevicelist);
        num_tasks = len(service01.getVFCHAIN());
        print('num tasks = ', num_tasks);

        service01.print();

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
                if (not service01.getVF(j).getReplica()):
                    timeProc[i][j] = edgeDevicelist[i].getProcessingTime(service01.getVF(j).getLoad());
                else:
                    timeProc[i][j] = 0;
        print(timeProc);

        m = 0;

        m = GEKKO() # Initialize gekko
        m.options.SOLVER = 1  # APOPT is an MINLP solver

        # optional solver settings with APOPT
        m.solver_options = ['minlp_maximum_iterations 5000', \
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

        m.Equation(
                    sum( [ timeProc[i][j] * x[i, j] for i in range(num_workers) for j in range(num_tasks) ] ) <= service01.getQoS()
                    );
        m.Obj(sum([cost[i][j] * x[i,j] for i in range(num_workers)
                                       for j in range(num_tasks)])) # Objective


        try:
            m.solve(disp = False) # Solve
            print('Results')
            for i in range(num_workers):
                for j in range(num_tasks):
                    #print(str(x[i, j].value))
                    if int(str(x[i, j].value)[1]) == 1:
                        print(' %d assigned to Edge Device %s:  Cost = %f' % (
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

            break;

        except:
            print('No feasible solution.... retrying')
            #Approach #1 - worstCase

            index = 0;

            while (True):

                VFtest = getEDminkth(index);
                print('[INFO]', VFtest.getName())

                try:
                    s = GEKKO() # Initialize gekko
                    s.options.SOLVER = 1  # APOPT is an MINLP solver

                    # optional solver settings with APOPT
                    s.solver_options = ['minlp_maximum_iterations 500', \
                                        # minlp iterations with integer solution
                                        'minlp_max_iter_with_int_sol 100', \
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

                    #retrive the least powerfull edge device

                    minCPU = edgeDevicelist[0].getCPU();
                    minDevice = edgeDevicelist[0];
                    for i in range(len(edgeDevicelist)):
                        if (edgeDevicelist[i].getCPU() < minCPU):
                            minCPU = edgeDevicelist[i].getCPU();
                            minDevice = edgeDevicelist[i];

                    timeProcDevice = np.zeros([num_tasks]);

                    for j in range(num_tasks):
                        #timeProcDevice[j] = minDevice.getProcessingTime(service01.getVF(j).getLoad());
                        timeProcDevice[j] = VFtest.getProcessingTime(service01.getVF(j).getLoad());

                    # Initialize variables
                    y = {}
                    for j in range(num_tasks):
                        y[j] = s.Var(value=1, lb=1, integer=True);

                    s.Equation(
                                sum( [ timeProcDevice[j] / y[j] for j in range(num_tasks) ] ) <= service01.getQoS()
                                );

                    s.Equation(
                                sum( [ y[j] for j in range(num_tasks) ] ) <= len(edgeDevicelist)
                                );
                    s.Obj( sum([y[j] for j in range(num_tasks)])) # Objective
                    s.solve(disp = False) # Solve
                    instances = np.zeros(num_tasks);
                    for j in range(num_tasks):
                        instances[j] = int(str(y[j].value)[1:-1].split('.')[0]);

                    print(instances);

                    removeVFs = [];
                    for j in range(len(instances)):
                        if (instances[j] > 1):
                            #create replicas of VF
                            VFrepl = service01.getVF(j);
                            removeVFs.append(VFrepl);

                            for r in range(int(instances[j])):
                                name = VFrepl.getName() + '_replica_' + str(r);
                                if (r == 0):
                                    VFtmp = virtualFunction(name, VFrepl.getLoad()/instances[j], False);
                                else:
                                    VFtmp = virtualFunction(name, VFrepl.getLoad()/instances[j], True);
                                service01.addVF(VFtmp);

                    for vf in removeVFs:
                        service01.deleteVF(vf);

                    break;
                except:
                    print('You need to change the testing processing device...')
                    index = index + 1;

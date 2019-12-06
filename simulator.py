from __future__ import print_function
from ortools.linear_solver import pywraplp

from edgeDevice import edgeDevice
from virtualChain import virtualChain
from virtualFunction import virtualFunction

import random

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

    #Create Virtal Functions
    VF01 = virtualFunction("VF01", 3*10**4);
    VF02 = virtualFunction("VF02", 2*10**5);
    VF03 = virtualFunction("VF03", 6*10**4);
    VF04 = virtualFunction("VF04", 2*10**3);

    #create virtualChain
    service01 = virtualChain("service01", 1/10);
    service01.addVF(VF01);
    service01.addVF(VF02);
    service01.addVF(VF03);
    service01.addVF(VF04);

    service01.print();

    print(D01.processingTime(VF01.getLoad()));

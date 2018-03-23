#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: mipex1.py
# Version 12.7.0
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
# Copyright IBM Corporation 2009, 2016. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ---------------------------------------------------------------------------
#
# mipex1.py - Entering and optimizing a mixed integer programming problem
#             Demonstrates different methods for creating a problem.
#
# The user has to choose the method on the command line:
#
#    python mipex1.py -r     generates the problem by adding rows
#    python mipex1.py -c     generates the problem by adding columns
#    python mipex1.py -n     generates the problem by adding a
#                            list of coefficients
#
# The MIP problem solved in this example is:
#
#   Maximize  x1 + 2 x2 + 3 x3 + x4
#   Subject to
#      - x1 +   x2 + x3 + 10 x4 <= 20
#        x1 - 3 x2 + x3         <= 30
#               x2      - 3.5x4  = 0
#   Bounds
#        0 <= x1 <= 40
#        0 <= x2
#        0 <= x3
#        2 <= x4 <= 3
#   Integers
#       x4

from __future__ import print_function

import sys

import cplex
from cplex.exceptions import CplexError

# data common to all populateby functions
my_obj = [1.0, 2.0, 3.0, 1.0]
my_ub = [40.0, cplex.infinity, cplex.infinity, 3.0]
my_lb = [0.0, 0.0, 0.0, 2.0]
my_ctype = "CCCI"

my_colnames = ["x1", "x2", "x3", "x4"]
my_rhs = [20.0, 30.0, 0.0]
my_rownames = ["r1", "r2", "r3"]
my_sense = "LLE"


def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)

    rows = [[["x1", "x2", "x3", "x4"], [-1.0, 1.0, 1.0, 10.0]],
            [["x1", "x2", "x3"], [1.0, -3.0, 1.0]],
            [["x2", "x4"], [1.0, -3.5]]]

    prob.linear_constraints.add(lin_expr=rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)


def mipex1():

    try:
        my_prob = cplex.Cplex()
        handle = populatebyrow(my_prob)
        my_prob.solve()
    except CplexError as exc:
        print(exc)
        return

    print()
    # solution.get_status() returns an integer code
    print("Solution status = ", my_prob.solution.get_status(), ":", end=' ')
    # the following line prints the corresponding string
    print(my_prob.solution.status[my_prob.solution.get_status()])
    print("Solution value  = ", my_prob.solution.get_objective_value())

    numcols = my_prob.variables.get_num()
    numrows = my_prob.linear_constraints.get_num()

    slack = my_prob.solution.get_linear_slacks()
    x = my_prob.solution.get_values()

    for j in range(numrows):
        print("Row %d:  Slack = %10f" % (j, slack[j]))
    for j in range(numcols):
        print("Column %d:  Value = %10f" % (j, x[j]))

if __name__ == "__main__":
    mipex1()

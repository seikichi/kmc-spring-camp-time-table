#!/usr/bin/python
# -*- coding: utf-8 -*-

from milp import Variable, BinaryVariable, IntegerVariable, VariableSet, VariableDict
from milp import LinearExpression, CPLEX, SCIP
from unittest import TestCase, main
import unittest
import os

class TestBinaryVariable(TestCase):
    def setUp(self):
        self.x = BinaryVariable('x')
        self.y = BinaryVariable('y')
        self.b1 = BinaryVariable()
        self.b2 = BinaryVariable()

    def test_name(self):
        self.assertEqual(str(self.x), 'x')
        self.assertEqual(str(self.y), 'y')

    def test_set(self):
        s = VariableSet()
        s.add(self.x)
        s.add(self.y)
        self.assertEqual(len(s), 2)
        self.assertIn(self.x, s)
        self.assertIn(self.y, s)
        self.assertNotIn(self.b1, s)
        self.assertNotIn(self.b2, s)

    def test_dict(self):
        d = VariableDict()
        d[self.x] = 10
        d[self.y] = 100
        self.assertEqual(len(d), 2)
        self.assertIn(self.x, d)
        self.assertIn(self.y, d)
        self.assertNotIn(self.b1, d)
        self.assertNotIn(self.b2, d)
        self.assertEqual(d[self.x], 10)
        self.assertEqual(d[self.y], 100)


class TestLinearExpression(TestCase):
    def assertLinearConstraintEqual(self, constraint, lhs_terms, sense, rhs_constant):
        if isinstance(lhs_terms, list):
            lhs_terms = VariableDict(lhs_terms)
        self.assertAlmostEqual(constraint.rhs, rhs_constant)
        self.assertEqual(constraint.sense, sense)
        self.assertEqual(len(constraint.lhs.variable_terms), len(lhs_terms))
        for v, c in constraint.lhs.variable_terms.items():
            self.assertAlmostEqual(c, lhs_terms[v])


class TestVariableOperators(TestLinearExpression):
    def setUp(self):
        self.x = BinaryVariable('x')
        self.y = BinaryVariable('y')
        self.z = BinaryVariable('z')

    def assertLinearExpressionEqual(self, exp, variable_terms, constant=0.0):
        if isinstance(exp, Variable):
            exp = LinearExpression(VariableDict([(exp, 1.0)]))
        if isinstance(variable_terms, list):
            variable_terms = VariableDict(variable_terms)
        self.assertAlmostEqual(exp.constant, constant)
        self.assertEqual(len(exp.variable_terms), len(variable_terms))
        for v, c in exp.variable_terms.items():
            self.assertAlmostEqual(c, variable_terms[v])

    def test_posneg(self):
        self.assertLinearExpressionEqual(+self.x, VariableDict([(self.x, +1.0)]))
        self.assertLinearExpressionEqual(-self.x, VariableDict([(self.x, -1.0)]))

    def test_add(self):
        self.assertLinearExpressionEqual(self.x + self.x, [(self.x, 2.0)])
        self.assertLinearExpressionEqual(self.x + 10, [(self.x, 1.0)], 10)
        self.assertLinearExpressionEqual(10 + self.x, [(self.x, 1.0)], 10)
        self.assertLinearExpressionEqual(self.x + self.y, [(self.x, 1), (self.y, 1)])
        self.assertLinearExpressionEqual(self.x + self.y + self.z,
                                         [(self.x, 1), (self.y, 1), (self.z, 1)])

    def test_sub(self):
        self.assertLinearExpressionEqual(self.x - self.x, [(self.x, 0.0)])
        self.assertLinearExpressionEqual(self.x - self.y, [(self.x, 1), (self.y, -1)])
        self.assertLinearExpressionEqual(self.x - 10, [(self.x, +1)], -10)
        self.assertLinearExpressionEqual(10 - self.x, [(self.x, -1)], +10)

    def test_mul(self):
        self.assertLinearExpressionEqual(2 * self.x, [(self.x, +2)])
        self.assertLinearExpressionEqual(self.x * -3.0, [(self.x, -3)])

    def test_cmp(self):
        self.assertLinearConstraintEqual(self.x < 10,  [(self.x, 1)], '<',  10)
        self.assertLinearConstraintEqual(self.x > 10,  [(self.x, 1)], '>',  10)
        self.assertLinearConstraintEqual(self.x <= 10, [(self.x, 1)], '<=', 10)
        self.assertLinearConstraintEqual(self.x >= 10, [(self.x, 1)], '>=', 10)
        self.assertLinearConstraintEqual(self.x == 10, [(self.x, 1)], '=',  10)


class TestLinearExpression(TestLinearExpression):
    def setUp(self):
        self.x = BinaryVariable('x')
        self.y = BinaryVariable('y')
        self.z = BinaryVariable('z')

        self.x_p_y = self.x + self.y
        self.x_m_y = self.x - self.y
        self.x_p_x = self.x + self.x

    def test_str(self):
        self.assertEqual(str(self.x_p_y), 'x + y')
        self.assertEqual(str(self.x_m_y), 'x - y')
        self.assertEqual(str(self.x_p_x), '2.0 x')

        self.assertEqual(str(-self.x_p_x), '- 2.0 x')
        self.assertEqual(str(2.0 * self.x_p_y - self.z), '2.0 x + 2.0 y - z')
        self.assertEqual(str(self.z * 2.0 - self.x_m_y * 1.0), '- x + y + 2.0 z')

        self.assertEqual(str(-(-(+(2.0 * self.x_p_y * 0.5)))), 'x + y')
        self.assertEqual(str(5 + sum([self.x, self.y, self.z, 10.0])), 'x + y + z + 15.0')
        self.assertEqual(str(self.x - self.x + self.y), 'y')

    def test_constraint(self):
        self.assertEqual(str(self.x_p_y < 10.0), 'x + y < 10.0')
        self.assertEqual(str(self.x_m_y <= -self.x + 10.0), '2.0 x - y <= 10.0')
        self.assertEqual(str(self.x_p_y > 10.0), 'x + y > 10.0')
        self.assertEqual(str(self.x_m_y >= -self.x + 10.0), '2.0 x - y >= 10.0')
        self.assertEqual(str(self.x_p_x == self.x + 1.0), 'x = 1.0')


class CPLEXTest(TestCase):
    @unittest.skipIf(os.system('which cplex >/dev/null'), 'cplex not found')
    def test_milp_problem(self):
        x1 = IntegerVariable('x1')
        x2 = IntegerVariable('x2')
        solver = CPLEX(quiet=True)
        solution = solver.maximize(x2, [
            3 * x1 + 2 * x2 <= 6,
            -3 * x1 + 2 * x2 <= 0,
        ])
        self.assertIsNotNone(solution)
        self.assertAlmostEqual(solution.objective_value, 1.0)
        self.assertAlmostEqual(solution[x1], 1.0)
        self.assertAlmostEqual(solution[x2], 1.0)


class SCIPTest(TestCase):
    @unittest.skipIf(os.system('which scip >/dev/null'), 'cplex not found')
    def test_milp_problem(self):
        x1 = IntegerVariable('x1')
        x2 = IntegerVariable('x2')
        solver = SCIP(quiet=True)
        solution = solver.maximize(x2, [
            3 * x1 + 2 * x2 <= 6,
            -3 * x1 + 2 * x2 <= 0,
        ])
        self.assertIsNotNone(solution)
        self.assertAlmostEqual(solution.objective_value, 1.0)
        self.assertAlmostEqual(solution[x1], 1.0)
        self.assertAlmostEqual(solution[x2], 1.0)


if __name__ == '__main__':
    main(verbosity=2)

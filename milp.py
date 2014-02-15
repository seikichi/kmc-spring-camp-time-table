#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import numbers
from collections import MutableSet, MutableMapping


class Variable(object):
    def _to_linear_expression(self):
        terms = VariableDict()
        terms[self] = 1.0
        return LinearExpression(terms)

    def __add__(self, rhs):
        terms = VariableDict()
        terms[self] = 1.0
        if isinstance(rhs, numbers.Number):
            return LinearExpression(terms, rhs)
        elif isinstance(rhs, Variable):
            if rhs in terms:
                terms[rhs] += 1.0
            else:
                terms[rhs] = 1.0
            return LinearExpression(terms)
        elif isinstance(rhs, LinearExpression):
            return rhs + self

    def __radd__(self, lhs):
        return self + lhs

    def __rmul__(self, lhs):
        assert(isinstance(lhs, numbers.Number))
        terms = VariableDict()
        terms[self] = lhs
        return LinearExpression(terms)

    def __mul__(self, rhs):
        return rhs * self

    def __sub__(self, rhs):
        return self + (-rhs)

    def __rsub__(self, lhs):
        return -self + lhs

    def __neg__(self):
        return -1.0 * self

    def __pos__(self):
        return self

    def __lt__(self, rhs):
        return LinearConstraint(self._to_linear_expression(), '<', rhs)

    def __le__(self, rhs):
        return LinearConstraint(self._to_linear_expression(), '<=', rhs)

    def __gt__(self, rhs):
        return LinearConstraint(self._to_linear_expression(), '>', rhs)

    def __ge__(self, rhs):
        return LinearConstraint(self._to_linear_expression(), '>=', rhs)

    def __eq__(self, rhs):
        return LinearConstraint(self._to_linear_expression(), '=', rhs)


class RealVariable(Variable):
    _real_variable_number = 0

    def __init__(self, name=None):
        RealVariable._real_variable_number += 1
        if name is None:
            name = 'ur{0}'.format(RealVariable._real_variable_number)
        self.name = name.replace(' ', '')

    def __repr__(self):
        return 'RealVariable({0})'.format(repr(self.name))

    def __str__(self):
        return self.name


class IntegerVariable(Variable):
    _integer_variable_number = 0

    def __init__(self, name=None):
        IntegerVariable._integer_variable_number += 1
        if name is None:
            name = 'ui{0}'.format(IntegerVariable._integer_variable_number)
        self.name = name.replace(' ', '')

    def __repr__(self):
        return 'IntegerVariable({0})'.format(repr(self.name))

    def __str__(self):
        return self.name


class BinaryVariable(Variable):
    _binary_variable_number = 0

    def __init__(self, name=None):
        BinaryVariable._binary_variable_number += 1
        if name is None:
            name = 'ub{0}'.format(BinaryVariable._binary_variable_number)
        self.name = name.replace(' ', '')

    def __repr__(self):
        return 'BinaryVariable({0})'.format(repr(self.name))

    def __str__(self):
        return self.name


class VariableWrapperForCollections(object):
    def __init__(self, variable):
        self.variable = variable
        self.name = str(variable)
        self.hash = hash(self.name)

    def __eq__(self, lhs):
        return self.name == lhs.name

    def __ne__(self, rhs):
        return not self == rhs

    def __hash__(self):
        return self.hash


class VariableSet(MutableSet):
    def __init__(self):
        self._set = set()

    def add(self, variable):
        self._set.add(VariableWrapperForCollections(variable))

    def discard(self, variable):
        self._set.discard(VariableWrapperForCollections(variable))

    def __contains__(self, variable):
        return VariableWrapperForCollections(variable) in self._set

    def __iter__(self):
        return iter([wrapper.variable for wrapper in self._set])

    def __len__(self):
        return len(self._set)

    def __str__(self):
        return '{{{0}}}'.format(', '.join((str(wrapper.variable) for wrapper in self._set)))


class VariableDict(MutableMapping):
    def __init__(self, args=[]):
        self._dict = dict()
        for k, v in args:
            self[k] = v

    def __delitem__(self, variable):
        del self._dict[VariableWrapperForCollections(variable)]

    def __getitem__(self, variable):
        return self._dict[VariableWrapperForCollections(variable)]

    def __iter__(self):
        return iter([wrapper.variable for wrapper in self._dict])

    def __len__(self):
        return len(self._dict)

    def __setitem__(self, variable, value):
        self._dict[VariableWrapperForCollections(variable)] = value

    def copy(self):
        copied_dictionary = VariableDict()
        for k in self:
            copied_dictionary[k] = self[k]
        return copied_dictionary


class Solution(VariableDict):
    def __init__(self):
        self.objective_value = None
        VariableDict.__init__(self)


class LinearExpression(object):
    def __init__(self, variable_terms=VariableDict(), constant=0.0):
        self.variable_terms = variable_terms
        self.constant = constant

    def __repr__(self):
        return 'LinearExpression({0}, {1})'.format(repr(self.variable_terms), repr(self.constant))

    def __str__(self):
        EPS = 1e-7
        term_strs = []

        for var, coeff in sorted(self.variable_terms.items(), key=lambda vc: vc[0].name):
            if abs(coeff) <= EPS:
                continue
            s = ''
            if term_strs or coeff < 0:
                s += '+ ' if coeff > 0 else '- '
            if abs(abs(coeff) - 1) > EPS:
                s += '{0} '.format(abs(coeff))
            s += '{0}'.format(var)
            term_strs.append(s)

        if abs(self.constant) > EPS:
            s = ''
            if term_strs or self.constant < 0:
                s += '+ ' if self.constant > 0 else '- '
            s += '{0}'.format(abs(self.constant))
            term_strs.append(s)

        return ' '.join(term_strs)

    def __add__(self, rhs):
        if isinstance(rhs, numbers.Number):
            return LinearExpression(self.variable_terms, self.constant + rhs)
        new_variable_terms = self.variable_terms.copy()
        if isinstance(rhs, Variable):
            if rhs in new_variable_terms:
                new_variable_terms[rhs] += 1.0
            else:
                new_variable_terms[rhs] = 1.0
            return LinearExpression(new_variable_terms, self.constant)
        elif isinstance(rhs, LinearExpression):
            for v, c in rhs.variable_terms.items():
                if v in new_variable_terms:
                    new_variable_terms[v] += c
                else:
                    new_variable_terms[v] = c
            return LinearExpression(new_variable_terms, self.constant + rhs.constant)

    def __radd__(self, lhs):
        return self + lhs

    def __sub__(self, rhs):
        return self + (-rhs)

    def __rsub__(self, lhs):
        return -self + lhs

    def __neg__(self):
        return -1.0 * self

    def __pos__(self):
        return self

    def __rmul__(self, lhs):
        assert(isinstance(lhs, numbers.Number))
        new_variable_terms = VariableDict()
        for v, c in self.variable_terms.items():
            new_variable_terms[v] = c * lhs
        return LinearExpression(new_variable_terms, self.constant * lhs)

    def __mul__(self, rhs):
        return rhs * self

    def __lt__(self, rhs):
        return LinearConstraint(self, '<', rhs)

    def __le__(self, rhs):
        return LinearConstraint(self, '<=', rhs)

    def __gt__(self, rhs):
        return LinearConstraint(self, '>', rhs)

    def __ge__(self, rhs):
        return LinearConstraint(self, '>=', rhs)

    def __eq__(self, rhs):
        return LinearConstraint(self, '=', rhs)


class LinearConstraint(object):
    def __init__(self, lhs, sense, rhs):
        self.lhs = lhs - rhs
        self.rhs = - self.lhs.constant
        self.lhs.constant = 0
        self.sense = sense

    def __repr__(self):
        return 'LinearConstraint({0}, {1}, {2})'.format(repr(self.lhs),
                                                        repr(self.sense),
                                                        repr(self.rhs))

    def __str__(self):
        return '{0} {1} {2}'.format(str(self.lhs), self.sense, self.rhs)

    def variables(self):
        variable_set = VariableSet()
        for v in self.lhs.variable_terms:
            variable_set.add(v)
        return variable_set


class Solver(object):
    def _export_to_mps(self, is_minimize, objective, constraints):
        self.variables = VariableSet()
        for c in constraints:
            for v in c.variables():
                self.variables.add(v)
        subprocess.call('rm -f {0}'.format(self.filename), shell=True)
        # if not self.quiet:
        print('variables:{0}, constraints: {1}'.format(len(self.variables), len(constraints)),
               file=sys.stderr)
        with open(self.filename, 'w') as f:
            print('min' if is_minimize else 'max', file=f)
            print('  {0}'.format(str(objective)), file=f)
            print('subject to', file=f)
            for i, c in enumerate(constraints):
                print('  c{0}: {1}'.format(i, c), file=f)
            if any(isinstance(v, IntegerVariable) for v in self.variables):
                print('general', file=f)
                for v in self.variables:
                    if isinstance(v, IntegerVariable):
                        print('  {0}'.format(str(v)), file=f)
            if any(isinstance(v, BinaryVariable) for v in self.variables):
                print('binary', file=f)
                for v in self.variables:
                    if isinstance(v, BinaryVariable):
                        print('  {0}'.format(str(v)), file=f)
            print('end', file=f)

    def minimize(self, objective, constraints):
        self._export_to_mps(True, objective, constraints)
        self._optimize()
        return self._read_solution()

    def maximize(self, objective, constraints):
        self._export_to_mps(False, objective, constraints)
        self._optimize()
        return self._read_solution()


class CPLEX(Solver):
    def __init__(self, filename='cplex-input.lp', quiet=False):
        self.filename = filename
        self.quiet = quiet

    def _optimize(self):
        subprocess.call('rm -f {0}.sol'.format(self.filename), shell=True)
        commands = 'cplex -c' \
                   ' "read {0}"' \
                   ' "optimize"' \
                   ' "write {0}.sol"' \
                   ' "q"'.format(self.filename)
        if self.quiet:
            commands += ' >&/dev/null'
        os.system(commands)

    def _read_solution(self):
        solution = Solution()

        variable_dict = {}
        for v in self.variables:
            variable_dict[str(v)] = v
            solution[v] = 0.0

        try:
            import xml.etree.ElementTree as ET
            root = ET.parse('{0}.sol'.format(self.filename)).getroot()
            solution.objective_value = float(root.find('header').get('objectiveValue'))
            for v in root.findall('variables/variable'):
                if v.get('name') in variable_dict:
                    value = float(v.get('value'))
                    if abs(value) < 1e-7:
                        value = 0
                    solution[variable_dict[v.get('name')]] = value
        except:
            return None
        return solution


class SCIP(Solver):
    def __init__(self, filename='scip-input.lp', quiet=False, path='scip'):
        self.filename = filename
        self.quiet = quiet
        self.path = path

    def _optimize(self):
        subprocess.call('rm -f {0}.sol'.format(self.filename), shell=True)
        commands = '{2} {1}' \
                   ' -c "read {0}"' \
                   ' -c "optimize"' \
                   ' -c "write solution {0}.sol"' \
                   ' -c "q"'.format(self.filename, '-q' if self.quiet else '', self.path)
        # subprocess.call(commands, shell=True)
        os.system(commands)

    def _read_solution(self):
        solution = Solution()

        variable_dict = {}
        for v in self.variables:
            variable_dict[str(v)] = v
            solution[v] = 0.0

        if not os.path.exists(self.filename):
            return None
        with open('{0}.sol'.format(self.filename)) as f:
            line = f.readline().strip()
            if line != 'solution status: optimal solution found':
                return None
            solution.objective_value = float(f.readline().strip().split()[-1])
            for line in f:
                line = line.strip().split()
                s, v = line[0], float(line[1])
                solution[variable_dict[s]] = v
        return solution

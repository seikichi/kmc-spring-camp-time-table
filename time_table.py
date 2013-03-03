#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
from milp import CPLEX, BinaryVariable


def read_input_file(filename):
    with open(filename) as f:
        input = json.loads(f.read())
        # 講座数は正しい？
        all_time_slots_num = sum(input['time_slots'].values())
        if len(input['courses']) != all_time_slots_num:
            print('Error: 講座数({0})と枠数({1})が一致しません'.format(len(input['courses']),
                                                                       all_time_slots_num),
                  file=sys.stderr)
            exit(-1)
        # 時間は足りているか？
        total_times = 0
        for session in input['sessions']:
            total_times += session['time'] * session['rooms']
        necessary_time = sum(int(slot) * num for slot, num in input['time_slots'].items())
        if necessary_time > total_times:
            print('Error: 講座が多すぎます ({0} > {1})'.format(necessary_time, total_times),
                  file=sys.stderr)
            exit(-1)
        # 講座担当者は出欠を書いているか
        for course in input['courses']:
            if course['name'] not in input['participants']:
                print('Error: 講座担当者 {0} さんが出欠を書いていません'.format(course['name']),
                      file=sys.stderr)
                exit(-1)
        # 見たい人に名前を書いている人は出欠を書いているか
        for applicant in set.union(*[set(course['applicants']) for course in input['courses']]):
            if applicant not in input['participants']:
                print('Warning: 講座見たい人 {0} さんが出欠を書いていません'.format(applicant), file=sys.stderr)
        # セッションの時間は講座枠の倍数にしておいて下さい
        for session in input['sessions']:
            for time in input['time_slots'].keys():
                if session['time'] % int(time):
                    print('セッション({0})の時間は講座時間({1})の倍数にして下さい'.format(session['time'], time),
                          file=sys.stderr)
                    exit(-1)
        return input


def find_best_time_table(input):
    # timeslots 列挙
    timeslots = []
    for time in map(int, input['time_slots'].keys()):
        for i, session in enumerate(input['sessions']):
            for j in range(session['time'] // time):
                timeslots.append((time, i, j))
    # 変数作成 (全てバイナリ変数)
    ## Xがidの講座を時間Tに見れるかどうか
    w = {}
    for applicant in set.union(*[set(course['applicants']) for course in input['courses']]):
        w[applicant] = {}
        for cid, course in enumerate(input['courses']):
            if applicant not in course['applicants']:
                continue
            w[applicant][cid] = {}
            for slot in timeslots:
                v = BinaryVariable('w_{{{0},{1},{2}}}'.format(applicant, cid, slot))
                w[applicant][cid][slot] = v
    ## 誰がどの時間に講座をするか
    c = {}
    for cid, course in enumerate(input['courses']):
        c[cid] = {}
        for slot in timeslots:
            v = BinaryVariable('c_{{{0},{1}}}'.format(cid, slot))
            c[cid][slot] = v
    ## セッション内の講座時間
    s = {}
    for sid, session in enumerate(input['sessions']):
        s[sid] = {}
        for time in input['time_slots'].keys():
            time = int(time)
            s[sid][int(time)] = BinaryVariable('s_{{{0},{1}}}'.format(sid, time))
    # 目的関数
    objective = 0
    for applicant in w:
        for cid in w[applicant]:
            objective += (1.0 / len(w[applicant].keys())) * sum(w[applicant][cid].values())
    # 制約
    constraints = []
    ## 講座の時間は各セッション内では全て同じ
    for sid in s:
        constraints.append(sum(s[sid].values()) <= 1)
    ## n分講座があればそのセッション内の講座は全てn分
    for cid in c:
        for cslot in c[cid]:
            for sid in s:
                if sid != cslot[1]:
                    continue
                constraints.append(c[cid][cslot] <= s[sid][cslot[0]])
    ## 部屋数より多い講座は無理
    for slot in timeslots:
        session_id = slot[1]
        rooms = input['sessions'][session_id]['rooms']
        constraints.append(sum(c[n][slot] for n in c) <= rooms)
    ## 1人の講座は1回だけ
    for cid in c:
        constraints.append(sum(c[cid].values()) == 1)
    ## 同じ時間帯に複数の講座を見ることはできない
    for applicant in w:
        for slot in timeslots:
            constraints.append(sum(w[applicant][cid][slot] for cid in w[applicant]) <= 1)
    ## input['time_slots'] に従ってコマ数設定
    for t, n in input['time_slots'].items():
        t = int(t)
        lhs = 0.0
        for cid in c:
            for cslot in c[cid]:
                if cslot[0] == t:
                    lhs += c[cid][cslot]
        constraints.append(lhs == n)
    # ソルバで求解
    solver = CPLEX()
    solution = solver.maximize(objective, constraints)
    if solution:
        for sid, session in enumerate(input['sessions']):
            sname = session['name']
            rooms = session['rooms']
            stime = session['time']
            for t in s[sid]:
                if solution[s[sid][t]]:
                    print('{0} => {1}'.format(sname, t))
                    for i in range(stime // t):
                        names = []
                        slot = (t, sid, i)
                        for cid in c:
                            if solution[c[cid][slot]]:
                                names.append(input['courses'][cid]['name'])
                        print(', '.join(names))
            # for cid in c:
            #     for cslot in c[cid]:
            #         if solution[c] and cslot[]


def output_time_table(time_table):
    pass


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: time_table.py input.json', file=sys.stderr)
        exit(-1)
    input = read_input_file(sys.argv[1])
    time_table = find_best_time_table(input)
    output_time_table(time_table)

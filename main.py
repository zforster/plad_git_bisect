# import json
# import websocket
#
# if __name__ == '__main__':
#     websocket.enableTrace(True)
#     ws = websocket.create_connection("ws://129.12.44.229:1234")
#     print("connected")
#     ws.send('{"User":"zf31"}')
#     result = ws.recv()
#     print(result + " hello")
#     ws.close()
# if __name__ == '__main__':
#     import websocket, json
#     try:
#         import thread
#     except ImportError:
#         import _thread as thread
#     import time
#
#     def on_message(ws, message):
#         print('test')
#         print(message)
#
#     def on_error(ws, error):
#         print(error)
#
#     def on_close(ws):
#         print("### closed ###")
#
#     def on_open(ws):
#         def run(*args):
#             x = '{"User": "zf31"}'
#             y = json.loads(json.dumps(x).encode('utf-8'))
#             ws.send(y)
#             time.sleep(1)
#             ws.close()
#             print("thread terminating...")
#         thread.start_new_thread(run, ())
#
#     # HTTP/1.1 101 Switching Protocols
#     # HTTP/1.1 101 Web Socket Protocol Handshake
#     if __name__ == "__main__":
#         websocket.enableTrace(True)
#         ws = websocket.WebSocketApp("ws://129.12.44.229:1234",
#                                     on_message=on_message,
#                                     on_error=on_error,
#                                     on_close=on_close)
#         ws.on_open = on_open
#         ws.run_forever()

import json
import os
import pandas


class Server:
    def __init__(self):
        self.name = None
        self.good = None
        self.bad = None
        self.dag = None
        self.bug = None
        self.all_bad = None
        self.question_count = 0

    def set_problem_instance(self, data: dict):
        self.name = data[0]['name']
        self.good = data[0]['good']
        self.bad = data[0]['bad']
        self.dag = data[0]['dag']
        self.bug = data[1]['bug']
        self.all_bad = data[1]['all_bad']
        self.question_count = 0

    def get_problem_instance(self):
        return {"Problem": {"name": "{}".format(self.name),
                            "good": "{}".format(self.good),
                            "bad": "{}".format(self.bad),
                            "dag": self.dag}}

    def response_to_question(self, question: dict):
        self.question_count = self.question_count + 1
        commit = question['Question']
        if commit in self.all_bad:
            return {"Answer": "bad"}
        return {"Answer": "good"}

    def handle_solution(self, solution: dict):
        answer = solution['Solution']
        if answer == self.bug:
            return {"Score": {self.name: self.question_count}}
        return {"Score": {self.name: "null"}}

class Client:
    def __init__(self):
        self.problem = None

    def set_problem(self, problem: dict):
        self.problem = problem['Problem']

    def remove_good_ancestors(self, good_commit: str):
        potential_bad_list = []
        parents = []
        for index in range(0, len(self.problem['dag'])):
            if good_commit == self.problem['dag'][index][0]:
                for i in self.problem['dag'][index][1]:
                    parents.append(i)
            else:
                potential_bad_list.append(self.problem['dag'][index])
        self.problem['dag'] = potential_bad_list
        return parents
        #
        # for i in range(0, 100000):
        #     for commit in self.problem['dag']:
        #         if parents == []:
        #             if good == commit[0]:
        #                 to_remove.append(commit)
        #                 for par in commit[1]:
        #                     parents.append(par)
        #         else:
        #             for par in parents:
        #                 if par == commit[0]:
        #
        #
        # print(to_remove)

        # print(self.problem['dag'])
        # for i in range(0, 10000000):
        #     for commit in self.problem['dag']:
        #         if parents is []:
        #             if self.problem['good'] == commit[0]:
        #                 good = commit[0]
        #                 for par in commit[1]:
        #                     parents.append(par)
        #         else:
        #             try:
        #                 for parent in parents:
        #                     if parent == commit[0]:
        #
        #         else:
        #             try:
        #                 if parent == commit[0]:
        #                     good = commit[0]
        #                     for par in commit[1]:
        #                         print(par)
        #                     parent = commit[1][0]
        #                     # print(parent)
        #             except IndexError:
        #                 print(good)
        #                 exit(0)
        # for i in self.problem['dag']:
        #     print(i)

# 899ae83acbaca830fadc633e75f4f97da582648f
  # 3c1e0f0a8cf693c0e510ff8749b201d14f7ab9b8
    # 10f3d93df728274685b3ce16468862199b6876ff
      #  1c77e1a492f701f921fba9aea31560eec7d83c88

if __name__ == '__main__':
    s = Server()
    c = Client()
    content = None
    for file in os.listdir("{}/tests/".format(os.getcwd())):
        with open("{}/tests/{}".format(os.getcwd(), file), "r") as json_file:
            content = json.load(json_file)
            s.set_problem_instance(data=content)
            c.set_problem(s.get_problem_instance())
            par = c.remove_good_ancestors(c.problem['good'])
            print('new parents to remove')
            print(par)
            for i in range(0, 1000):
                new_parents = []
                for p in par:
                    new_parents = c.remove_good_ancestors(p)
                    print('new parents to remove')
                    print(new_parents)
                par = new_parents
            #     print(par)
            # print(len(c.problem['dag']))

            # print(s.response_to_question(question={"Question": problem['Problem']['good']}))
            # print(s.response_to_question(question={"Question": problem['Problem']['bad']}))
            # print(s.handle_solution(solution={"Solution": problem['Problem']['bad']}))
            print(" ")
        break


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
        self.tree = {}
        self.bad_ancestors = {}
        self.good_ancestors = {}

    def set_problem(self, problem: dict):
        self.problem = problem['Problem']
        self.bad_ancestors = {}
        self.good_ancestors = {}

    def generate_json_tree(self):
        for commit in self.problem['dag']:
            self.tree[commit[0]] = commit[1]

    def extract_parents(self, bad_commit):
        return self.tree[bad_commit]

    def extract_bad_ancestors(self, bad_commits):
        parents = []
        for commit in bad_commits:
            data = self.extract_parents(commit)
            self.bad_ancestors[commit] = data
            for parent in set(data):
                parents.append(parent)
        return set(parents)

    def extract_good_ancestors(self, good_commits):
        parents = []
        for commit in good_commits:
            data = self.extract_parents(commit)
            self.good_ancestors[commit] = data
            for parent in set(data):
                parents.append(parent)
        return set(parents)


if __name__ == '__main__':
    import time
    s = Server()
    c = Client()
    content = None
    for file in os.listdir("{}/tests/".format(os.getcwd())):
        with open("{}/tests/{}".format(os.getcwd(), file), "r") as json_file:
            print("OPERATING ON FILE {}".format(file))
            keep_bad_ancestors = {}
            problem_content = json.load(json_file)
            s.set_problem_instance(data=problem_content)
            c.set_problem(s.get_problem_instance())
            c.generate_json_tree()
            print("WE WANT TO FIND THE BUG {}:".format(s.bug))
            print("STARTING SIZE: {}".format(len(c.tree.keys())))
            bad = [c.problem['bad']]
            # print("bad: {}".format(c.problem['bad']))
            while len(bad) != 0:
                bad = c.extract_bad_ancestors(bad)

            good = [c.problem['good']]
            # print("good: {}".format(c.problem['good']))
            while len(good) != 0:
                good = c.extract_good_ancestors(good)

            print("LENGTH OF BAD ANCESTORS WITHOUT REMOVING GOOD KEYS: {}".format(len(c.bad_ancestors.keys())))
            print("LENGTH OF GOOD ANCESTORS: {}".format(len(c.good_ancestors.keys())))
            for key in c.good_ancestors.keys():
                del c.bad_ancestors[key]
            print("LENGTH OF BAD ANCESTORS AFTER REMOVING GOOD ONES: {}".format(len(c.bad_ancestors.keys())))
            for key in c.bad_ancestors.keys():
                if s.handle_solution({'Solution': key})['Score'][c.problem['name']] != "null":
                    print("FOUND: {} {}".format(key, s.bug))
            print(" ")
            # break
                # print(len(bad))
                # print(len(good))
            # print(c.bad_ancestors)

            # for b in bad:
            #     bad = c.extract_parents(b)
            # print(bad)
            # new_bad = []
            # for b in bad:
            #     data = c.extract_parents(b)
            #     for i in data:
            #         new_bad.append(i)
            # print(new_bad)

            # print(c.extract_parents('5640d641d6066a85439d7027b960ebc2cebd37de'))
            # for i in c.tree.keys():
            #     for a in c.tree[i]:
            #         if a == '5640d641d6066a85439d7027b960ebc2cebd37de':
            #             print(i)
            # print(" ")
            # for i in c.problem['dag']:
            #     print(i)
            # break
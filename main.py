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
        self.test = {}
        self.ancestors = {}

    def set_problem(self, problem: dict):
        self.problem = problem['Problem']
        self.bad_ancestors = {}
        self.good_ancestors = {}
        self.test = {}

    def generate_json_tree(self):
        self.tree = {}
        for commit in self.problem['dag']:
            self.tree[commit[0]] = commit[1]

    def select_mid_point_ask(self):
        half_number = round(len(c.bad_ancestors.keys()) / 2)
        self.problem['bad'] = list(c.bad_ancestors.keys())[half_number]
        answer = s.response_to_question({'Question': c.problem['bad']})['Answer']
        return answer

    def bfs(self, source_node: str, dag: dict):
        visited = {source_node: True}
        queue = [source_node]
        parent_count = [] #
        while len(queue) != 0:

            vertex = queue[len(queue) - 1]
            print(vertex)
            queue.pop(len(queue) - 1)
            parent = dag[vertex]
            for w in parent:
                if w not in visited:
                    queue.append(w)
                    visited[w] = True


                    for i in parent:#
                        parent_count.append(i)#
            print(len(set(parent_count)))


        # print(len(set))
        return len(visited.keys())

    def keep_ancestors(self, source_node, dag: dict, removed_keys: dict):
        visited = {source_node: True}
        queue = [source_node]
        while len(queue) != 0:
            vertex = queue[len(queue) - 1]
            queue.pop(len(queue) - 1)
            if vertex not in removed_keys.keys():  # dont try to index a key that has been removed
                parent = dag[vertex]
                for w in parent:
                    if w not in visited:
                        queue.append(w)
                        visited[w] = True
        new_dag = dag.copy()
        for key in dag.keys():  # go through the keys containing decendents of the bad key
            if key not in visited.keys():  # if the key is not an ancestor of our bad commit
                del new_dag[key]  # remove that key from the dag, leaving only decendents of the bad commit
        return new_dag

    def remove_ancestors(self, source_node: str, dag: dict):
        starting_dag = dag
        visited = {source_node: True}
        queue = [source_node]
        while len(queue) != 0:
            vertex = queue[len(queue) - 1]
            queue.pop(len(queue) - 1)
            parent = starting_dag[vertex]
            for w in parent:
                if w not in visited:
                    queue.append(w)
                    visited[w] = True

        for key in visited.keys():
            del starting_dag[key]

        return starting_dag, visited

if __name__ == '__main__':
    s = Server()
    c = Client()
    content = None
    for file in os.listdir("{}/tests/".format(os.getcwd())):
        with open("{}/tests/{}".format(os.getcwd(), file), "r") as json_file:
            # if "test_tensorflow12" in file:
            print("OPERATING ON FILE {}".format(file))
            problem_content = json.load(json_file)

            s.set_problem_instance(data=problem_content)

            c.set_problem(s.get_problem_instance())

            c.generate_json_tree()

            print("WE WANT TO FIND THE BUG {}:".format(s.bug))
            print("DEFINED GOOD COMMIT {}:".format(c.problem['good']))
            print("DEFINED BAD COMMIT {}:".format(c.problem['bad']))
            print("STARTING SIZE: {}".format(len(c.tree.keys())))

            old_dag = c.tree.copy()
            new_dag, removed_keys = c.remove_ancestors(c.problem['good'], old_dag)
            print("NEW SIZE: {}".format(len(new_dag.keys())))
            # print(new_dag)
            new_dag = c.keep_ancestors(c.problem['bad'], new_dag, removed_keys)
            print("NEW SIZE: {}".format(len(new_dag.keys())))
            for key in new_dag:
                if key == s.bad:
                    print("FOUND")
                if key == c.problem['bad']:
                    print("BAD KEY STILL PRESENT")

            # min_point = round(len(new_dag.keys()) / 2)
            # # print(new_dag['9ca4dd6024f4f60aa5ae77f4a6178b5a69f3464a'])
            # count = 0
            # print(c.bfs('787b49ae78ef36be38134c937756bc2738dccf35', new_dag))
            # for key in new_dag:
            #     count = count + 1
            #     print(key)
            #     # if key == s.bug:
            #     #     print("found")
            #     ancestor_count = c.bfs(key, new_dag)
            #     print(ancestor_count)
            #     print(" ")
            #     if ancestor_count == min_point:
            #         print("Found best intersection point {} with {} ancestors, searched through {} keys".format(key, ancestor_count, count))
            #         break
            print(" ")
                # break

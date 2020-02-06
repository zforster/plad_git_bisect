import json
from websocket import create_connection


class Server:
    def __init__(self):
        self.connection = create_connection("ws://129.12.44.229:1234")
        self.good = None
        self.bad = None
        self.dag = {}
        self.name = None
        self.problem = None

    def set_problem(self, problem: dict):
        self.problem = problem['Problem']
        self.good = self.problem['bad']
        self.bad = self.problem['good']
        self.name = self.problem['name']
        for commit in self.problem['dag']:
            self.dag[commit[0]] = commit[1]

    def get_problem(self):
        return self.problem

    def auth(self):
        print("Authenticating User")
        auth_msg = json.dumps({'User': 'zf31'})
        self.connection.send(auth_msg)
        print("Setting Problem Instance")
        self.set_problem(json.loads(self.connection.recv()))

    def response_to_question(self, key: str):
        self.connection.send(json.dumps({'Question': key}))
        resp = json.loads(self.connection.recv())['Answer']
        print("question asked - {}".format(resp))
        return resp.lower()

    def handle_solution(self, key: str):
        self.connection.send(json.dumps({'Solution': key}))
        resp = json.loads(self.connection.recv())
        print("FINISHED PROBLEM {}".format(self.name))
        if 'Problem' in resp.keys():
            self.set_problem(resp)
            return None
        else:
            for key in resp:
                print(resp[key])
            return resp


class Client:
    def __init__(self):
        self.problem = None
        self.tree = {}
        self.bad_ancestors = {}
        self.good_ancestors = {}

    def set_problem(self, problem: dict):
        self.problem = problem
        self.bad_ancestors = {}
        self.good_ancestors = {}

    def generate_json_tree(self):
        self.tree = {}
        for commit in self.problem['dag']:
            self.tree[commit[0]] = commit[1]

    def bfs(self, source_node: str, dag: dict, removed_keys: dict ):
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
                    if w not in visited and w not in removed_keys.keys():
                        queue.append(w)
                        visited[w] = True
        new_dag = dag.copy()
        rem = 0
        for key in dag.keys():  # go through the keys containing decendents of the bad key
            if key not in visited.keys():  # if the key is not an ancestor of our bad commit
                del new_dag[key]  # remove that key from the dag, leaving only decendents of the bad commit
                rem = rem + 1
        return new_dag

    def remove_ancestors(self, source_node: str, dag: dict, removed_keys: dict):
        starting_dag = dag
        visited = {source_node: True}
        queue = [source_node]
        while len(queue) != 0:
            vertex = queue[len(queue) - 1]
            queue.pop(len(queue) - 1)
            if vertex not in removed_keys.keys():
                visited[vertex] = True
                # print(vertex)
                parent = starting_dag[vertex]
                for w in parent:
                    if w not in visited and w not in removed_keys.keys():
                        queue.append(w)
                        visited[w] = True

        for key in visited.keys():
            del starting_dag[key]

        for key in starting_dag.keys():
            for item in starting_dag[key]:
                if item in visited.keys():
                    starting_dag[key] = [x for x in starting_dag[key] if x != item]

        return starting_dag, visited

    def pick_new_key(self, dag, removed_keys, picked):
        chosen_key = None
        if len(dag.keys()) > 20000:
            ideal = round(len(dag.keys()) / 2)
            for key in dag:
                ancestor_count = c.bfs(key, dag, removed_keys)
                key_value = min(ancestor_count, len(dag.keys()) - ancestor_count)
                if round(ideal - (ideal / 4)) <= key_value <= round(ideal + (ideal / 4)):
                    # print("picking key with value {}, ideal is {}".format(key_value, ideal)) #1000 4 and 4 also works well
                    while key in picked:
                        key = list(dag.keys())[ideal - 1]  # what if half number is
                    return key
            # print('COULDNT FIND SUITABLE KEY')
            key = list(dag.keys())[ideal]
            while key in picked:
                key = list(dag.keys())[ideal - 1]  # what if half number is
            return key
        else:
            # print("can find best key")
            best_number = round(len(dag.keys()) / 2)
            key_count = {}
            for key in dag:
                ancestor_count = c.bfs(key, dag, removed_keys)
                if ancestor_count == best_number:
                    # print("found best key during count")
                    return key
                else:
                    key_count[key] = ancestor_count
            for key in key_count.keys():
                key_count[key] = min(key_count[key], len(dag.keys()) - key_count[key])
            highest = 0
            for key in key_count.keys():
                if key_count[key] > highest:
                    highest = key_count[key]
                    chosen_key = key
        # print("best key is {}".format(chosen_key))
        return chosen_key

if __name__ == '__main__':
    s = Server()
    c = Client()
    s.auth()
    solution_response = None
    while solution_response is None:
        already_picked = []
        c.set_problem(s.get_problem())
        c.generate_json_tree()

        ret_dag, removed = c.remove_ancestors(c.problem['good'], c.tree, {})
        ret_dag = c.keep_ancestors(c.problem['bad'], ret_dag, removed)
        while len(ret_dag.keys()) > 1:
            chosen = c.pick_new_key(dag=ret_dag, removed_keys=removed, picked=already_picked)
            already_picked.append(chosen)
            if s.response_to_question(chosen) == "bad":
                # print('bad')
                ret_dag = c.keep_ancestors(chosen, ret_dag, removed)
            else:
                # print('good')
                ret_dag, removed = c.remove_ancestors(chosen, ret_dag, removed)
        for last_key in ret_dag:
            solution_response = s.handle_solution(last_key)
    print(" ")
    for i in solution_response:
        print(solution_response[i])
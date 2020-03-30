import json
import os


class Server:
    def __init__(self):
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
        if len(dag.keys()) > 1000:
            ideal = round(len(dag.keys()) / 2)
            for key in dag:
                ancestor_count = c.bfs(key, dag, removed_keys)
                key_value = min(ancestor_count, len(dag.keys()) - ancestor_count)
                if round(ideal - (ideal / 4)) <= key_value <= round(ideal + (ideal / 4)):
                    print("picking key with value {}, ideal is {}".format(key_value, ideal)) #1000 4 and 4 also works well
                    while key in picked:
                        key = list(dag.keys())[ideal - 1]  # what if half number is
                    return key
            print('COULDNT FIND SUITABLE KEY')
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
    content = None
    sum = 0
    for file in os.listdir("{}/tests/".format(os.getcwd())):
        with open("{}/tests/{}".format(os.getcwd(), file), "r") as json_file:
            already_picked = []
            problem_content = json.load(json_file)
            s.set_problem_instance(data=problem_content)
            c.set_problem(s.get_problem_instance())
            c.generate_json_tree()
            # print("OPERATING ON FILE {} WITH SIZE {}".format(file, len(c.tree.keys())))
            ret_dag, removed = c.remove_ancestors(c.problem['good'], c.tree, {})
            ret_dag = c.keep_ancestors(c.problem['bad'], ret_dag, removed)
            while len(ret_dag.keys()) > 1:
                chosen_key = c.pick_new_key(dag=ret_dag, removed_keys=removed, picked=already_picked)
                already_picked.append(chosen_key)
                if s.response_to_question({'Question': chosen_key})['Answer'] == "bad":
                    ret_dag = c.keep_ancestors(chosen_key, ret_dag, removed)
                else:
                    ret_dag, removed = c.remove_ancestors(chosen_key, ret_dag, removed)
            for remainer in ret_dag:
                resp = s.handle_solution({'Solution': remainer})
                sum = sum + resp['Score'][c.problem['name']]
                print(resp)
            print(sum)
            print(" ")
            # break
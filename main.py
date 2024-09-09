import os

import pygame, sys, random, math, datetime
from shapely.geometry import LineString, Point, Polygon
from tkinter import simpledialog
import tkinter.messagebox as mb
from ordered_set import OrderedSet

inf = 1e18


def rotate(origin, point, angle):
    angle *= math.pi / 180

    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class Button:
    def __init__(self, x, y, width, height, buttonText, onclickFunction):
        global my_font, buttons

        self.x = x + 2
        self.y = y + 2
        self.width = width - 4
        self.height = height - 4
        self.onclickFunction = onclickFunction
        self.alreadyPressed = False

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = my_font.render(buttonText, False, (20, 20, 20))

        buttons.append(self)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        pygame.draw.rect(screen, (0, 0, 0), (self.x - 2, self.y - 2, self.width + 4, self.height + 4))
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


class Edge:
    def __init__(self, parent, child, distance):
        self.parent = parent
        self.child = child
        self.distance = distance
        self.color = (0, 0, 0)
        self.text = my_font.render(str(self.distance), False, self.color)

    def get_start_and_finish(self):
        path = []

        p = Point(*self.parent.get_pos())
        c = p.buffer(25).boundary
        l = LineString([self.parent.get_pos(), self.child.get_pos()])
        i = c.intersection(l)
        if isinstance(i, LineString) and i.is_empty:
            return

        path.append((i.x, i.y))

        p = Point(*self.child.get_pos())
        c = p.buffer(25).boundary
        l = LineString([path[0], self.child.get_pos()])
        i = c.intersection(l)
        if isinstance(i, LineString) and i.is_empty:
            return

        path.append((i.x, i.y))
        return path

    def process(self):
        global screen, my_font

        path = self.get_start_and_finish()
        if path is None:
            return False

        to = (path[-1][0], path[-1][1])

        diff_x = (to[0] - path[0][0])
        diff_y = (to[1] - path[0][1])

        if abs(diff_x) + abs(diff_y) != 0:
            coff = 20 / (abs(diff_x) + abs(diff_y))
        else:
            coff = 0

        diff_x *= coff
        diff_y *= coff

        new_x = (to[0] - diff_x)
        new_y = (to[1] - diff_y)

        rotate_angle = 30

        path.append(rotate(to, (new_x, new_y), rotate_angle))
        path.append(to)
        path.append(rotate(to, (new_x, new_y), -rotate_angle))
        path.append(to)

        pygame.draw.lines(screen, self.color, True, path, 2)

        font_x = (path[0][0] + path[1][0]) / 2
        font_y = (path[0][1] + path[1][1]) / 2
        screen.blit(self.text, (font_x, font_y))

    def collision(self, pos):
        global screen

        path = self.get_start_and_finish()
        if path is None:
            return False

        start = path[0]
        finish = path[1]

        diff_x = (finish[0] - start[0])
        diff_y = (finish[1] - start[1])

        if abs(diff_x) + abs(diff_y) != 0:
            coff = 10 / (abs(diff_x) + abs(diff_y))
        else:
            coff = 0

        diff_x *= coff
        diff_y *= coff

        new_x = (start[0] + diff_x)
        new_y = (start[1] + diff_y)

        path = [rotate(start, (new_x, new_y), 90), rotate(start, (new_x, new_y), -90)]

        new_x = (finish[0] - diff_x)
        new_y = (finish[1] - diff_y)
        path.append(rotate(finish, (new_x, new_y), 90))
        path.append(rotate(finish, (new_x, new_y), -90))

        l = Polygon(path)
        return l.contains(Point(*pos))

    def set_color(self, color):
        self.color = color
        self.text = my_font.render(str(self.distance), False, self.color)

    def get_num(self):
        return self.parent.get_num(), self.child.get_num()

    def get_parent(self):
        return self.parent

    def get_child(self):
        return self.child

    def get_distance(self):
        return self.distance

    def get_color(self):
        return self.color


class Node:
    def __init__(self, number):
        global my_font, button_size

        self.number = number
        self.radius = 25
        self.edges = []

        self.x = random.choice(range(self.radius, screen.get_width() - self.radius))
        self.y = random.choice(range(self.radius + button_size[1], screen.get_height() - self.radius))
        self.color = (255, 255, 255)
        self.text = my_font.render(str(self.number), False, (0, 0, 0))

    def process(self):
        global screen

        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius - 1)
        screen.blit(self.text, (self.x - self.radius / 3, self.y - self.radius / 2))

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y):
        self.x, self.y = x, y

    def collision(self, pos):
        return (((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5) <= 25

    def set_color(self, color):
        self.color = color

    def get_num(self):
        return self.number

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def get_edges(self):
        return self.edges


class Graph:
    def __init__(self):
        self.is_drag = False
        self.frame = 0
        self.drag_x = 0
        self.drag_y = 0
        self.drag_num = 0

        f = open("input.txt", 'r')

        self.nodes = []
        self.edges = []
        self.selected_nodes = set()
        self.selected_edges = set()
        self.path = []

        self.routing_finish = 0
        self.routing_path = []
        self.tec_routing_path = []
        self.was_routing = set()
        self.routing_time = datetime.datetime.now()
        self.is_start_routing = False
        self.is_finish_routing = False

        nodes_num, edges_num = map(int, f.readline().split())
        self.nodes_num = nodes_num
        edges_dist = list(map(int, f.readline().split()))

        for i in range(nodes_num):
            self.nodes.append(Node(i + 1))

        for i in range(edges_num):
            l, r = map(int, f.readline().split())

            self.edges.append(Edge(self.nodes[l - 1], self.nodes[r - 1], edges_dist[i]))
            self.nodes[l - 1].add_edge(self.edges[-1])
            self.nodes[r - 1].add_edge(self.edges[-1])

        f.close()

    def process(self):
        if self.is_start_routing:
            self.process_routing()

        if self.is_drag:
            new_x = pygame.mouse.get_pos()[0] - self.drag_x
            new_y = pygame.mouse.get_pos()[1] - self.drag_y
            self.get_node_by_num(self.drag_num).set_pos(new_x, new_y)

        for edge in self.edges:
            if not self.is_drag and edge.get_num() not in self.selected_edges and edge.get_color() != (72, 125, 231) and not self.is_start_routing:
                if edge.collision(pygame.mouse.get_pos()):
                    edge.set_color((102, 102, 102))
                else:
                    edge.set_color((0, 0, 0))
            edge.process()

        for node in self.nodes:
            node.process()

    def drag_and_drop(self, pos):
        global frame

        for i in range(len(self.nodes) - 1, -1, -1):
            if self.nodes[i].collision(pos):
                self.is_drag = True
                self.frame = datetime.datetime.now()
                self.drag_num = self.nodes[i].get_num()
                self.drag_x = pos[0] - self.nodes[i].get_pos()[0]
                self.drag_y = pos[1] - self.nodes[i].get_pos()[1]

                return

        for i in range(len(self.edges) - 1, -1, -1):
            if self.edges[i].collision(pos):
                self.select_edge(self.edges[i].get_num())
                break

    def stop_drag_and_drop(self):
        global frame

        if self.drag_num != 0 and datetime.datetime.now() - self.frame < datetime.timedelta(seconds=0.2):
            self.select_node(self.drag_num)

        self.is_drag = False
        self.frame = 0
        self.drag_x = 0
        self.drag_y = 0
        self.drag_num = 0

    def select_node(self, node_num):
        if self.is_routing():
            return

        for i in self.path:
            i.set_color((255, 255, 255))
        self.path.clear()

        if node_num in self.selected_nodes:
            self.selected_nodes.remove(node_num)
            self.get_node_by_num(node_num).set_color((255, 255, 255))
        else:
            self.selected_nodes.add(node_num)
            self.get_node_by_num(node_num).set_color((0, 255, 0))

    def is_routing(self):
        if self.is_start_routing and (not self.is_finish_routing) and \
                mb.askquestion("Информация", "Прервать выполнение простой маршрутизации?") == 'no':
            return True
        if self.is_start_routing:
            self.clear_all_colors()
            self.is_start_routing = False
            self.is_finish_routing = False
            self.tec_routing_path.clear()

        return False

    def select_edge(self, edge_num):
        if self.is_routing():
            return

        for i in self.path:
            i.set_color((255, 255, 255))
        self.path.clear()

        if edge_num in self.selected_edges:
            self.selected_edges.remove(edge_num)
            self.get_edge_by_num(edge_num).set_color((255, 255, 255))
        else:
            self.selected_edges.add(edge_num)
            self.get_edge_by_num(edge_num).set_color((0, 255, 0))

    def get_node_by_num(self, num):
        for node in self.nodes:
            if node.get_num() == num:
                return node
        return None

    def get_edge_by_num(self, num):
        for edge in self.edges:
            if edge.get_num() == num:
                return edge
        return None

    def add_node(self):
        if self.is_routing():
            return

        self.nodes_num += 1
        self.nodes.append(Node(self.nodes_num))

    def remove_selected(self):
        if self.is_routing():
            return

        self.stop_drag_and_drop()
        if mb.askquestion("Подтверждение", f"Вы уверены что хотите удалить выбранное?") == 'no':
            return

        for edge in self.selected_edges:
            e = self.get_edge_by_num(edge)
            e.get_parent().remove_edge(e)
            e.get_child().remove_edge(e)
            self.edges.remove(e)

        self.selected_edges.clear()

        for node in self.selected_nodes:
            for i in range(len(self.edges) - 1, -1, -1):
                if self.get_node_by_num(node).get_num() in self.edges[i].get_num():
                    self.edges[i].get_parent().remove_edge(self.edges[i])
                    self.edges[i].get_child().remove_edge(self.edges[i])
                    self.edges.remove(self.edges[i])
            self.nodes.remove(self.get_node_by_num(node))

        self.selected_nodes.clear()

    def add_edge(self):
        self.stop_drag_and_drop()
        if len(self.selected_nodes) != 2 or len(self.selected_edges) != 0:
            mb.showinfo("Информация", "Для добавления ребра необходимо выбрать только 2 вершины")
            return

        parent, child = list(self.selected_nodes)
        if mb.askquestion("Главная вершина", f"Ребро идет от вершины {parent} к вершине {child}?") == 'no':
            parent, child = child, parent

        my_i = simpledialog.askinteger("Ввод длины", "Введите длину")

        if my_i is None:
            return

        self.edges.append(Edge(self.get_node_by_num(parent), self.get_node_by_num(child), my_i))
        self.get_node_by_num(parent).add_edge(self.edges[-1])
        self.get_node_by_num(child).add_edge(self.edges[-1])

    def Dijkstra(self, start):
        q = OrderedSet()
        path = {}
        for node in self.nodes:
            path[node.get_num()] = inf

        path[start] = 0

        q.add((0, start, self.get_node_by_num(start)))
        while q:
            f = q[0]
            q.remove(f)
            for edge in f[2].get_edges():
                if edge.get_parent() == f[2] and path[f[1]] + edge.get_distance() < path[edge.get_child().get_num()]:
                    path[edge.get_child().get_num()] = path[f[1]] + edge.get_distance()
                    q.add((path[f[1]] + edge.get_distance(), edge.get_child().get_num(), edge.get_child()))
        return path

    def start_one_Dijkstra(self):
        if self.is_routing():
            return

        if len(self.selected_nodes) != 2 or len(self.selected_edges) != 0:
            mb.showinfo("Информация", "Для запуска алгоритма Дейкстры необходимо выбрать только 2 вершины")
            return

        start, finish = list(self.selected_nodes)
        if mb.askquestion("Главная вершина", f"Найти путь от вершины {start} к вершине {finish}?") == 'no':
            start, finish = finish, start

        path = self.Dijkstra(start)

        if path[finish] == inf:
            mb.showinfo("Информация", "Пути нет")
            return

        self.selected_nodes.clear()

        tec = self.get_node_by_num(finish)

        self.path.append(tec)
        while tec.get_num() != start:
            for edge in tec.get_edges():
                if edge.get_child() == tec and path[edge.get_parent().get_num()] + edge.get_distance() == path[
                    tec.get_num()]:
                    self.path.append(edge)
                    tec = edge.get_parent()
                    self.path.append(tec)
                    break

        mb.showinfo("Информация", f"Длина пути {path[finish]}")

        for i in self.path:
            i.set_color((72, 125, 231))

    def start_all_pathes(self):
        if self.is_routing():
            return

        all_pathes = {}
        time = datetime.timedelta(0)
        for node in self.nodes:
            tec_num = node.get_num()
            s = datetime.datetime.now()
            path = self.Dijkstra(tec_num)
            time += datetime.datetime.now() - s
            all_pathes[(tec_num, tec_num)] = [[tec_num], 0]
            q = [node]
            while q:
                v = q.pop()
                num = v.get_num()
                for edge in v.get_edges():
                    child_num = edge.get_child().get_num()
                    if edge.get_parent() == v and path[num] + edge.get_distance() == path[child_num]:
                        all_pathes[(tec_num, child_num)] = [all_pathes[(tec_num, num)][0] + [child_num],
                                                            path[child_num]]
                        q.append(edge.get_child())
            for n in self.nodes:
                num = n.get_num()
                if (tec_num, num) not in all_pathes:
                    all_pathes[(tec_num, num)] = [["Пути нет"], -1]

        f = open('all_path_dijkstra.txt', 'w+')
        f.write('Алгоритм Дейкстры \n\n')
        f.write(f'Время выполнения Дейкстры {time} \n')
        for x, y in all_pathes.keys():
            f.write(
                f'Вершины {x, y}, путь - {" ".join(map(str, all_pathes[(x, y)][0]))}, длина пути - {all_pathes[(x, y)][1]} \n')

        all_pathes.clear()
        f.close()

        time = datetime.datetime.now()
        path = {}
        for node in self.nodes:
            num = node.get_num()
            for c_node in self.nodes:
                path[(num, c_node.get_num())] = inf
            path[(num, num)] = 0

        for edge in self.edges:
            p_num = edge.get_parent().get_num()
            c_num = edge.get_child().get_num()
            path[(p_num, c_num)] = min(path[(p_num, c_num)], edge.get_distance())

        for k in self.nodes:
            for p_node in self.nodes:
                for c_node in self.nodes:
                    k_num, p_num, c_num = k.get_num(), p_node.get_num(), c_node.get_num()
                    if path[(p_num, k_num)] < inf and path[(k_num, c_num)] < inf:
                        path[(p_num, c_num)] = min(path[(p_num, c_num)], path[(p_num, k_num)] + path[(k_num, c_num)])

        time = datetime.datetime.now() - time
        f = open('all_path_floyd.txt', 'w+')

        for node in self.nodes:
            tec_num = node.get_num()
            all_pathes[(tec_num, tec_num)] = [[tec_num], 0]
            q = [node]
            while q:
                v = q.pop()
                num = v.get_num()
                for edge in v.get_edges():
                    child_num = edge.get_child().get_num()
                    if edge.get_parent() == v and path[(tec_num, num)] + edge.get_distance() == path[
                        (tec_num, child_num)]:
                        all_pathes[(tec_num, child_num)] = [all_pathes[(tec_num, num)][0] + [child_num],
                                                            path[(tec_num, child_num)]]
                        q.append(edge.get_child())

            for n in self.nodes:
                num = n.get_num()
                if (tec_num, num) not in all_pathes:
                    all_pathes[(tec_num, num)] = [["Пути нет"], -1]

        f.write('Алгоритм Флойда \n\n')
        f.write(f'Время выполнения Флойда {time} \n')
        for x, y in all_pathes.keys():
            f.write(
                f'Вершины {x, y}, путь - {" ".join(map(str, all_pathes[(x, y)][0]))}, длина пути - {all_pathes[(x, y)][1]} \n')

        f.close()
        os.startfile('all_path_dijkstra.txt')
        os.startfile('all_path_floyd.txt')

    def clear_all_colors(self):
        for edge in self.edges:
            edge.set_color((0, 0, 0))

        for node in self.nodes:
            node.set_color((255, 255, 255))

    def start_simple_routing(self):
        if self.is_routing():
            return

        if len(self.selected_nodes) != 2 or len(self.selected_edges) != 0:
            mb.showinfo("Информация", "Для запуска алгоритма простой маршруизации необходимо выбрать только 2 вершины")
            return

        start, finish = list(self.selected_nodes)
        if mb.askquestion("Главная вершина", f"Найти путь от вершины {start} к вершине {finish}?") == 'no':
            start, finish = finish, start

        self.selected_nodes.clear()

        self.is_start_routing = True
        self.routing_path.clear()
        self.was_routing.clear()
        self.tec_routing_path.clear()

        self.routing_finish = self.get_node_by_num(finish)
        node = self.get_node_by_num(start)

        self.routing_path.append([node, 0])

    def process_routing(self):
        if datetime.datetime.now() - self.routing_time < datetime.timedelta(seconds=0.5):
            return

        self.routing_time = datetime.datetime.now()

        if not self.is_finish_routing and len(self.routing_path):
            v = self.routing_path.pop()
            if v[1] == 0:
                v[0].set_color((72, 125, 231))
                self.was_routing.add(v[0])
                self.tec_routing_path.append([v[0], v[1]])
                for edge in v[0].get_edges():
                    if edge.get_parent() == v[0] and edge.get_child() not in self.was_routing:
                        self.routing_path.append([edge.get_child(), v[1] + 1, edge])
                        self.was_routing.add(edge.get_child())
            else:
                if len(self.tec_routing_path) and self.tec_routing_path[-1][1] != v[1] - 1:
                    self.tec_routing_path.pop()[0].set_color((255, 255, 255))
                    if len(self.tec_routing_path):
                        self.tec_routing_path.pop().set_color((0, 0, 0))
                    self.routing_path.append(v)
                    return

                self.tec_routing_path.append(v[2])
                v[2].set_color((72, 125, 231))
                self.tec_routing_path.append([v[0], v[1]])
                v[0].set_color((72, 125, 231))
                if v[0] == self.routing_finish:
                    print(self.tec_routing_path)
                    for i in range(len(self.tec_routing_path)):
                        if i % 2:
                            self.tec_routing_path[i].set_color((0, 255, 0))
                        else:
                            self.tec_routing_path[i][0].set_color((0, 255, 0))

                    self.is_finish_routing = True
                    self.routing_path.clear()
                    mb.showinfo("Информация", "Путь найден")
                    return

                for edge in v[0].get_edges():
                    if edge.get_parent() == v[0] and edge.get_child() not in self.was_routing:
                        self.routing_path.append([edge.get_child(), v[1] + 1, edge])
                        self.was_routing.add(edge.get_child())

        elif not self.is_finish_routing:
            if len(self.tec_routing_path):
                self.tec_routing_path.pop()[0].set_color((255, 255, 255))
                if len(self.tec_routing_path):
                    self.tec_routing_path.pop().set_color((0, 0, 0))
                return

            self.is_finish_routing = True
            self.clear_all_colors()
            mb.showinfo("Информация", "Пути не существует")


pygame.init()
pygame.font.init()

button_size = (200, 50)
my_font = pygame.font.SysFont('Comic Sans MS', 20)
screen = pygame.display.set_mode((1300, 700))
graph = Graph()
buttons = []

frame = 0

Button(0, 0, *button_size, 'Добавить вершину', graph.add_node)
Button(200, 0, *button_size, 'Удалить выбранное', graph.remove_selected)
Button(400, 0, *button_size, 'Добавить ребро', graph.add_edge)
Button(600, 0, *button_size, 'Алгоритм Дейкстры', graph.start_one_Dijkstra)
Button(800, 0, *button_size, 'Найти все пути', graph.start_all_pathes)
Button(1000, 0, 300, 50, 'Простая маршрутизация', graph.start_simple_routing)

while True:
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            graph.drag_and_drop(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONUP:
            graph.stop_drag_and_drop()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    graph.process()

    for button in buttons:
        button.process()

    pygame.display.flip()

    frame += 1

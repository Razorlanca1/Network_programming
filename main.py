import os
from tkinter import simpledialog
from typing import Tuple, Any

import pygame, sys, random, math, datetime
from shapely.geometry import LineString, Point, Polygon
import tkinter.messagebox as mb
from ordered_set import OrderedSet
from tkinter import *

inf = 1e18


def rotate(origin, point, angle):
    angle *= math.pi / 180

    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class Table(Tk):
    def __init__(self, table, parent=None):
        Tk.__init__(self, parent)
        self.parent = parent
        self.table = table
        self.ret = []
        self.initialize()

    def initialize(self):
        self.grid()
        for i in range(len(self.table)):
            self.ret.append([])
            for j in range(len(self.table)):
                try:
                    if i == j:
                        raise Exception
                    self.ret[i].append(self.table[i][j])
                except:
                    self.ret[i].append(0)

        lines = len(self.table)

        for i in range(lines):
            for j in range(lines):
                state = NORMAL
                if i == 0 or j == 0:
                    state = DISABLED

                intvar = IntVar()
                intvar.set(self.table[i][j])
                self.table[i][j] = intvar

                self.e = Entry(self, width=5, state=state, textvariable=self.table[i][j],
                               fg='blue', font=('Arial', 16, 'bold'))

                self.e.grid(row=i, column=j)

        SubmitBtn = Button(text="OK", command=self.submit)
        SubmitBtn.grid(row=lines, column=lines // 2, sticky='W', padx=5, pady=2)

        self.title("Матрица инцидентности")
        self.resizable(False, False)
        self.mainloop()

    def submit(self):
        self.ret.clear()
        for i in range(len(self.table)):
            self.ret.append([])
            for j in range(len(self.table)):
                try:
                    if i == j:
                        raise Exception
                    self.ret[i].append(self.table[i][j].get())
                except:
                    self.ret[i].append(0)
        self.destroy()

    def get(self):
        return self.ret


class RoutingSettings(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.was_set = False
        self.initialize()

    def initialize(self):
        self.grid()

        self.packet_label = Label(self, width=20, text="Количество пакетов", fg='black', font=('Arial', 10, 'bold'))
        self.packet_label.grid(row=0, column=0, sticky='W', padx=5, pady=2, columnspan=2)

        self.packet_count = IntVar(value=1)
        self.packet = Entry(self, width=5, textvariable=self.packet_count, fg='black', font=('Arial', 10, 'bold'))
        self.packet.grid(row=0, column=2, sticky='W', padx=5, pady=2)

        self.time_label = Label(self, width=20, text="Лимит времени", fg='black', font=('Arial', 10, 'bold'))
        self.time_label.grid(row=1, column=0, sticky='W', padx=5, pady=2, columnspan=2)

        self.time_limit = IntVar(value=100)
        self.time = Entry(self, width=5, textvariable=self.time_limit, fg='black', font=('Arial', 10, 'bold'))
        self.time.grid(row=1, column=2, sticky='W', padx=5, pady=2)

        self.packet_limit_label = Label(self, width=20, text="Лимит пакетов", fg='black', font=('Arial', 10, 'bold'))
        self.packet_limit_label.grid(row=2, column=0, sticky='W', padx=5, pady=2, columnspan=2)

        self.packet_limit = IntVar(value=10)
        self.packet_limit_e = Entry(self, width=5, textvariable=self.packet_limit, fg='black', font=('Arial', 10, 'bold'))
        self.packet_limit_e.grid(row=2, column=2, sticky='W', padx=5, pady=2)

        self.protocol = StringVar(value="random")
        self.RandomRadiobutton = Radiobutton(text="Случайная маршрутизация", value="random", font=('Arial', 10, 'bold'),
                                          variable=self.protocol)
        self.RandomRadiobutton.grid(row=3, column=0, sticky='W', padx=5, pady=2)

        self.AllRadiobutton = Radiobutton(text="Лавинная маршрутизация", value="all_pathes", font=('Arial', 10, 'bold'),
                                          variable=self.protocol)
        self.AllRadiobutton.grid(row=4, column=0, sticky='W', padx=5, pady=2)

        self.MemoryRadiobutton = Radiobutton(text="Фиксированная маршрутизация", value="memory", font=('Arial', 10, 'bold'),
                                          variable=self.protocol)
        self.MemoryRadiobutton.grid(row=5, column=0, sticky='W', padx=5, pady=2)

        self.SubmitBtn = Button(text="OK", command=self.submit, width=25)
        self.SubmitBtn.grid(row=6, column=0, sticky='W', padx=5, pady=2, columnspan=2)

        self.title("Простая маршрутизация")
        self.resizable(False, False)
        self.mainloop()

    def submit(self):
        self.was_set = True

        try:
            self.packet_count = self.packet_count.get()
        except Exception:
            self.packet_count = 1

        try:
            self.time_limit = self.time_limit.get()
        except Exception:
            self.time_limit = 100

        try:
            self.packet_limit = self.packet_limit.get()
        except Exception:
            self.packet_limit = 10

        self.protocol = self.protocol.get()

        self.destroy()

    def get(self) -> tuple[int, int, int, str]:
        if self.was_set:
            return self.packet_count, self.time_limit, self.packet_limit, self.protocol
        return 0, 0, 0, ""


class Packet:
    def __init__(self, number, start_node, finish_node, method, path=None, next=None):
        global my_font

        self.number = number
        self.tec_node = start_node
        self.finish_node = finish_node
        self.path = []
        self.all_path = path
        self.last_time = datetime.datetime.now()
        self.method = method
        self.color = (255, 255, 255)
        self.text = my_font.render(str(self.number), False, (0, 0, 0))

        if next:
            self.next_node = next
        else:
            self.choose_next_node()

    def get_number(self):
        return self.number

    def choose_next_node(self):
        global graph

        self.last_time = datetime.datetime.now()
        if self.method == "memory":
            if self.all_path:
                self.next_node = self.all_path[-1]
                self.all_path.pop()
            return

        n = []
        for edge in self.tec_node.get_edges():
            if edge.get_parent() == self.tec_node:
                n.append(edge.get_child())

        if len(n) == 0:
            graph.remove_packet(self)
            return

        if self.method == "random":
            self.next_node = random.choice(n)
            return

        self.next_node = n[0]
        for i in range(1, len(n)):
            graph.add_packet(Packet(self.number, self.tec_node, self.finish_node, self.method, next=n[i]))

    def is_success(self) -> bool:
        return self.finish_node == self.tec_node

    def process(self):
        global screen, graph

        if datetime.datetime.now() - self.last_time > datetime.timedelta(seconds=1):
            self.path.append(self.tec_node)
            self.tec_node = self.next_node
            self.choose_next_node()

        if self.tec_node == self.finish_node:
            self.path.append(self.finish_node)
            graph.add_memory_path(self.path[1:])
            graph.remove_packet(self)
            return

        delta = (datetime.datetime.now() - self.last_time).microseconds / 1000000

        start_x, start_y = self.tec_node.get_pos()
        fin_x, fin_y = self.next_node.get_pos()
        x = start_x + (fin_x - start_x) * delta
        y = start_y + (fin_y - start_y) * delta

        size_x, size_y = 30, 50

        pygame.draw.rect(screen, (0, 0, 0), (x - size_x / 2, y - size_y / 2, size_x, size_y))
        pygame.draw.rect(screen, self.color, (x - size_x / 2 + 1, y - size_y / 2 + 1, size_x - 2, size_y - 2))
        screen.blit(self.text, (x - size_x / 3, y - size_y / 3))


class Button_menu:
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

    def get_num(self) -> int:
        return self.number

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def get_edges(self):
        return self.edges


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

    def collision(self, pos) -> bool:
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

    def get_num(self) -> tuple[int, int]:
        return self.parent.get_num(), self.child.get_num()

    def get_parent(self) -> Node:
        return self.parent

    def get_child(self) -> Node:
        return self.child

    def get_distance(self) -> int:
        return self.distance

    def get_color(self):
        return self.color


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

        self.packets = []
        self.packets_finished = 0
        self.packet_number = 0
        self.routing_start = 0
        self.routing_finish = 0
        self.routing_packet_count = 0
        self.routing_time_limit = 0
        self.routing_packet_limit = 0
        self.memory_path = []
        self.was_rout = set()
        self.routing_method = ""
        self.routing_start_time = datetime.datetime.now()
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

        self.label = my_font.render("", False, (20, 20, 20))

    def process(self):
        if self.is_start_routing:
            self.process_routing()

        if self.is_drag:
            new_x = pygame.mouse.get_pos()[0] - self.drag_x
            new_y = pygame.mouse.get_pos()[1] - self.drag_y
            self.get_node_by_num(self.drag_num).set_pos(new_x, new_y)

        for edge in self.edges:
            if not self.is_drag and edge.get_num() not in self.selected_edges and \
                    edge.get_color() != (72, 125, 231) and not self.is_start_routing:
                if edge.collision(pygame.mouse.get_pos()):
                    edge.set_color((102, 102, 102))
                else:
                    edge.set_color((0, 0, 0))
            edge.process()

        for node in self.nodes:
            node.process()

        for packet in self.packets:
            packet.process()

        screen.blit(self.label, (50, screen.get_height() - 50))

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

    def get_node_by_num(self, num) -> Node | None:
        for node in self.nodes:
            if node.get_num() == num:
                return node
        return None

    def get_edge_by_num(self, num) -> Edge | None:
        for edge in self.edges:
            if edge.get_num() == num:
                return edge
        return None

    def add_node(self):
        self.label = my_font.render("", False, (20, 20, 20))
        if self.is_routing():
            return

        self.nodes_num += 1
        self.nodes.append(Node(self.nodes_num))

    def remove_selected(self):
        self.label = my_font.render("", False, (20, 20, 20))
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
        self.label = my_font.render("", False, (20, 20, 20))
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
        self.label = my_font.render("", False, (20, 20, 20))
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

        text = f"{tec.get_num()}. Длина пути: {path[finish]}"
        self.path.append(tec)
        while tec.get_num() != start:
            for edge in tec.get_edges():
                if edge.get_child() == tec and \
                        path[edge.get_parent().get_num()] + edge.get_distance() == path[tec.get_num()]:
                    self.path.append(edge)
                    tec = edge.get_parent()
                    self.path.append(tec)
                    text = f"{tec.get_num()} -> " + text
                    break

        text = f"Путь: " + text
        self.label = my_font.render(text, False, (20, 20, 20))

        for i in self.path:
            i.set_color((72, 125, 231))

    def start_all_pathes(self):
        self.label = my_font.render("", False, (20, 20, 20))
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

    def add_packet(self, packet):
        self.packets.append(packet)

    def add_memory_path(self, path):
        if not self.memory_path or len(path) < len(self.memory_path):
            self.memory_path = path[::-1]

    def remove_packet(self, packet):
        if packet.is_success():
            if packet.get_number() not in self.was_rout:
                self.was_rout.add(packet.get_number())
                self.packets_finished += 1
        try:
            self.packets.remove(packet)
        except Exception:
            pass

    def start_simple_routing(self):
        if len(self.selected_nodes) != 2 or len(self.selected_edges) != 0:
            mb.showinfo("Информация", "Для запуска алгоритма простой маршруизации необходимо выбрать только 2 вершины")
            return

        start, finish = list(self.selected_nodes)
        if mb.askquestion("Главная вершина", f"Найти путь от вершины {start} к вершине {finish}?") == 'no':
            start, finish = finish, start

        self.selected_nodes.clear()

        self.label = my_font.render("", False, (20, 20, 20))
        if self.is_routing():
            return

        rot = RoutingSettings()
        data = rot.get()

        if data[0] == 0:
            self.is_start_routing = False
            self.clear_all_colors()
            self.packets.clear()
            return

        self.is_start_routing = True
        self.packets_finished = 0
        self.packet_number = 1
        self.was_rout.clear()
        self.memory_path.clear()
        self.routing_packet_count, self.routing_time_limit, self.routing_packet_limit, self.routing_method = data
        self.routing_start = self.get_node_by_num(start)
        self.routing_finish = self.get_node_by_num(finish)
        self.routing_start_time = datetime.datetime.now()

    def process_routing(self):
        self.label = my_font.render("", False, (20, 20, 20))
        if datetime.datetime.now() - self.routing_start_time > datetime.timedelta(seconds=self.routing_time_limit):
            mb.showinfo("Информация", "Время для простой маршруизации вышло. "
                                      "Успешно доставлено пакетов {self.packets_finished}")
            self.is_start_routing = False
            self.clear_all_colors()
            self.packets.clear()
            return

        if len(self.packets) > self.routing_packet_limit:
            mb.showinfo("Информация", "Превышен лимит пакетов для простой маршруизации. "
                                      "Успешно доставлено пакетов {self.packets_finished}")
            self.is_start_routing = False
            self.clear_all_colors()
            self.packets.clear()
            return

        if datetime.datetime.now() - self.routing_time < datetime.timedelta(seconds=1):
            return

        if self.packet_number > self.routing_packet_count:
            if len(self.packets) == 0:
                mb.showinfo("Информация", f"Простая маршруизация завершена. "
                                          f"Успешно доставлено пакетов {self.packets_finished}")
                self.is_start_routing = False
                self.clear_all_colors()
                self.packets.clear()
            return

        if self.routing_method == "memory" and self.packet_number <= self.routing_packet_count / 2:
            self.add_packet(Packet(self.packet_number, self.routing_start, self.routing_finish, "random"))
        else:
            if self.routing_method == "memory":
                if self.packets:
                    return
                if not self.memory_path:
                    mb.showinfo("Информация", "Фиксированная маршруизации не нашла путь.")
                    self.is_start_routing = False
                    self.clear_all_colors()
                    self.packets.clear()
                    return
                print(self.memory_path)
                self.add_packet(Packet(self.packet_number, self.routing_start, self.routing_finish,
                                       self.routing_method, self.memory_path))
            else:
                self.add_packet(Packet(self.packet_number, self.routing_start, self.routing_finish, self.routing_method))
        self.packet_number += 1
        self.routing_time = datetime.datetime.now()

    def table(self):
        self.label = my_font.render("", False, (20, 20, 20))
        if self.is_routing():
            return

        nodes = self.nodes[::]
        nodes.sort(key=lambda x: x.get_num())
        nodes_num = {}
        for i, num in enumerate(nodes):
            nodes_num[num] = i + 1

        table = [[0 for _ in range(len(nodes) + 1)] for _ in range(len(nodes) + 1)]
        for i in range(len(nodes)):
            table[0][i + 1] = nodes[i].get_num()

        for i in range(len(nodes)):
            table[i + 1][0] = nodes[i].get_num()

        for edge in self.edges:
            parent = nodes_num[edge.get_parent()]
            child = nodes_num[edge.get_child()]
            table[parent][child] = edge.get_distance()

        self.selected_edges.clear()
        self.edges.clear()
        for node in nodes:
            node.edges.clear()

        t = Table(table)
        ret = t.get()
        for i in range(1, len(ret)):
            parent = nodes[i - 1]
            for j in range(1, len(ret)):
                child = nodes[j - 1]
                if ret[i][j] != 0:
                    self.edges.append(Edge(parent, child, ret[i][j]))
                    parent.add_edge(self.edges[-1])
                    child.add_edge(self.edges[-1])


pygame.init()
pygame.font.init()

button_size = (200, 50)
my_font = pygame.font.SysFont('Comic Sans MS', 20)
screen = pygame.display.set_mode((1300, 700))
graph = Graph()
buttons = []

frame = 0

Button_menu(0, 0, 1300, 30, 'Матрица инцидентности', graph.table)
Button_menu(0, 30, 200, 30, 'Добавить вершину', graph.add_node)
Button_menu(200, 30, 200, 30, 'Удалить выбранное', graph.remove_selected)
Button_menu(400, 30, 200, 30, 'Добавить ребро', graph.add_edge)
Button_menu(600, 30, 200, 30, 'Алгоритм Дейкстры', graph.start_one_Dijkstra)
Button_menu(800, 30, 200, 30, 'Найти все пути', graph.start_all_pathes)
Button_menu(1000, 30, 300, 30, 'Простая маршрутизация', graph.start_simple_routing)

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

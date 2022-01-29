bl_info = {
    "name": "Map Export",
    "blender": (3, 00, 0),
    "category": "Object",
}
import bpy
import csv
import numpy
import os

scene = bpy.context.scene

#gets child objects
def hierachy(obj, levels):
    knode = []
    def recurse(obj, parent, depth):
        if depth > levels: 
            return
        knode.append(obj.name)         
        for chobj in obj.children:
            recurse(chobj, obj,  depth + 1)
    recurse(obj, obj.parent, 0)
    return knode

def arr(name, level):
    h = hierachy(bpy.data.objects[name],level)
    return h

def fnodearr():
    x = arr('course',1)
    del x[0]
    h = arr('route',20)
    del h[0]
    for i in range(0,len(h)):
        if(h[i][0:1] == 'F'):
           x += [h[i]]
    return x

nodearr = arr('course',1)
del nodearr[0]
node = []

routearr = arr('route',20)
route = []

fnodearr = fnodearr()
routes = []

action = '走る' 
sound = '"道"'

print(sound)

del routearr[0]
for y in routearr:
    routes += [hierachy(bpy.data.objects[y],20)]

#Level node and F node generation
for x in range(0,len(nodearr)):
    node.insert(x, [f'{x}',nodearr[x],'','','','','','',''])
for x in range(0,len(fnodearr)):
    if(fnodearr[x][0:1] == 'F'):
        node.insert(x, [f'{x}',fnodearr[x],'stop','','','','','',''])


#Route generation
for x in fnodearr:
    for y in fnodearr:
        for i, obj in enumerate(routes):
            if ((obj[0] == 'R' + x + y) and (obj[0][0:1] == 'R' and len(obj) == 1)):
                route.append([f'{obj[0]}',action,sound])
            elif((obj[0] == 'R' + x + y) and (obj[0][0:1] == 'R') and len(obj) > 1):
                l = 0
                for a in range(0,len(obj)):
                    l+=1
                for c in range(0,l):
                    if(c==0 and len(obj)-1 < 2):
                        if( obj[0][5:6] == 'F' and  obj[1][0:1] == 'F'):
                            route.append([f'{obj[0]}',action,sound])
                            break
                        elif(obj[0][5:6] == 'F' and  obj[1][0:1] == 'K'):
                            route.append([f'R{obj[0][1:5] + obj[1]}',action,sound])
                            route.append([f'R{obj[1] + obj[0][5:9]}',action,sound])
                            break
                        else:
                            route.append([f'R{obj[0][1:5] + obj[1]}',action,sound])
                            route.append([f'R{obj[1] + obj[0][5:9]}',action,sound])
                            break
                    elif(c==0 and len(obj)-1 > 1):
                        
                        route.append([f'R{obj[0][1:5] + obj[c+1]}',action,sound])
                    elif(c==len(obj)-1):
                        if(obj[c][0:1] == 'F'):
                            break
                        else:
                            route.append([f'R{obj[c] + obj[0][5:9]}',action,sound])
                    elif(c > 0 and c < len(obj)-1):
                        route.append([f'R{obj[c] + obj[c+1]}',action,sound])


dir = os.path.dirname(bpy.data.filepath)

with open(dir + '\\point.csv', 'w',encoding='shift_jis', newline='') as file:
    mywriter = csv.writer(file, delimiter=',')
    mywriter.writerows(numpy.array(node))
    
with open(dir + '\\route.csv', 'w',encoding='shift_jis', newline='') as file:
    mywriter = csv.writer(file, delimiter=',',quotechar='',escapechar='\\', quoting=csv.QUOTE_NONE)
    mywriter.writerows(numpy.array(route))
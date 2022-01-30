bl_info = {
    "name": "RouteExport",
    "blender": (3, 00, 0),
    "category": "Object",
    "author": "Huseyin the Mighty",
    "version": (0, 1),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Generates NSMB2 route and point files to simplify creating custom maps",
}

import bpy
import csv
import numpy
import os

action = '走る' 
sound = '"道"'

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

#Level node and F node generation

def generateNode():
    nodearr = arr('course',1)
    del nodearr[0]
    node = []
    for x in range(0,len(nodearr)):
        node.insert(x, [f'{x}',nodearr[x],'','','','','','',''])
    for x in range(0,len(fnodearr())):
        if(fnodearr()[x][0:1] == 'F'):
            node.insert(x, [f'{x}',fnodearr()[x],'stop','','','','','',''])
    return node


#Route generation
def generateRoute():
    routearr = arr('route',20)
    routes = []
    del routearr[0]
    for y in routearr:
        routes += [hierachy(bpy.data.objects[y],20)]
        
    route = []
    for x in fnodearr():
        for y in fnodearr():
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
    return route

def writeNode(h):
    with open(h + '\\point.csv', 'w',encoding='shift_jis', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(numpy.array(generateNode()))
    
def writeRoute(h):
    with open(h + '\\route.csv', 'w',encoding='shift_jis', newline='') as file:
        mywriter = csv.writer(file, delimiter=',',quotechar='',escapechar='\\', quoting=csv.QUOTE_NONE)
        mywriter.writerows(numpy.array(generateRoute()))



class properties(bpy.types.PropertyGroup):
        
    path : bpy.props.StringProperty(
        name="",
        description="Output for point and route files. Select an ABSOLUTE path.",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
        
    def show(self):
        print(path) 
        
        
class mainpanel(bpy.types.Panel):
    bl_label = "RouteExport"
    bl_idname = "ADDONNAME_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        row = layout.row()
        col = layout.column(align=True)
        
        row.operator("addonname.myop_operator")

        layout.prop(scene.my_tool,"path", text="Output")
        
        
class  writefiles(bpy.types.Operator):
    bl_label = "Export Route Files"
    bl_idname = "addonname.myop_operator"

        
    def execute(self,context):
            
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        if(mytool.path[1:2] == ":"):
            writeRoute(mytool.path)
            writeNode(mytool.path)
            return {"FINISHED"}
        elif(mytool.path == ""):
            return {"FINISHED"}
        else:
            mytool.path = "Hover over box!"
            return {"FINISHED"}
        

    
classes = [properties,mainpanel,writefiles]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=properties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.mytool


if __name__ == "__main__":
    register()
bl_info = {
    "name": "Map Export",
    "blender": (3, 00, 0),
    "category": "Object",
}

import bpy
import csv
import numpy
import os

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
def generateNode(event):
    nodearr = arr('course',1)
    del nodearr[0]
    node = []
    for x in range(0,len(nodearr)):
        node.insert(x, [f'{x}',nodearr[x],'','','','','','',''])
    for x in range(0,len(fnodearr())):
        if(fnodearr()[x][0:1] == 'F'):
            node.insert(x, [f'{x}',fnodearr()[x],event,'','','','','',''])
    return node


def getRoute():
    routearr = arr('route',20)
    routes = []
    routes2 = []
    del routearr[0]
    for y in routearr:
        routes += [hierachy(bpy.data.objects[y],20)]
    for x in routes:
        if(x[0][0:1]=='R'):
            routes2 += [x]
    return routes2


#Route generation
def generateRoute(routeentry, sounds, movement):
    route = []
    for x in fnodearr():
        for y in fnodearr():
            if ((routeentry[0] == 'R' + x + y) and (routeentry[0][0:1] == 'R' and len(routeentry) == 1)):
                route.append([f'{routeentry[0]}',sounds,movement])
            elif((routeentry[0] == 'R' + x + y) and (routeentry[0][0:1] == 'R') and len(routeentry) > 1):
                l = 0
                for a in range(0,len(routeentry)):
                    l+=1
                for c in range(0,l):
                    if(c==0 and len(routeentry)-1 < 2):
                        if( routeentry[0][5:6] == 'F' and  routeentry[1][0:1] == 'F'):
                            route.append([f'{routeentry[0]}',sounds,movement])
                            break
                        elif(routeentry[0][5:6] == 'F' and  routeentry[1][0:1] == 'K'):
                            route.append([f'R{routeentry[0][1:5] + routeentry[1]}',sounds,movement])
                            route.append([f'R{routeentry[1] + routeentry[0][5:9]}',sounds,movement])
                            break
                        else:
                            route.append([f'R{routeentry[0][1:5] + routeentry[1]}',sounds,movement])
                            route.append([f'R{routeentry[1] + routeentry[0][5:9]}',sounds,movement])
                            break
                    elif(c==0 and len(routeentry)-1 > 1):
                        
                        route.append([f'R{routeentry[0][1:5] + routeentry[c+1]}',sounds,movement])
                    elif(c==len(routeentry)-1):
                        if(routeentry[c][0:1] == 'F'):
                            break
                        else:
                            route.append([f'R{routeentry[c] + routeentry[0][5:9]}',sounds,movement])
                    elif(c > 0 and c < len(routeentry)-1):
                        route.append([f'R{routeentry[c] + routeentry[c+1]}',sounds,movement])
    return route


def routeGeneration():
    h = []
    for x in getRoute():
        h += generateRoute(x,movementdict[bpy.data.objects[x[0]]["Movement"][0]][0], sounddict[bpy.data.objects[x[0]]["Sound"][0]][0])
    return h
  

def writeNode(dir):
    with open(dir + '\\point.csv', 'w',encoding='shift_jis', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(numpy.array(generateNode('stop')))
    
def writeRoute(dir, routearray):
    with open(dir + '\\route.csv', 'w',encoding='shift_jis', newline='') as file:
        mywriter = csv.writer(file, delimiter=',',quotechar='',escapechar='\\', quoting=csv.QUOTE_NONE)
        mywriter.writerows(routearray)
        
        
        
        
sounddict = {
    1 : ('"道"','Road'),
    2 : ('"雪"','Snow'),
    3 : ('"砂"','Sand'),
    4 : ('"氷"','Ice - Unused'),
    5 : ('"草"','Grass'),
    6 : ('"水"','Water'),
    7 : ('"雲"','Cloud'),
    8 : ('"砂間欠泉"','Sand Geyser - Unused'),
    9 : ('"マンタ"','Mushroom'),
    10 : ('"ビーチ"','Beach - Unused'),
    11 : ('"じゅうたん"','Carpet'),
    12 : ('"葉っぱ"','Leaf - Unused'),
    13 : ('"樽"','Barrel'),
    14 : ('"水間欠泉"','Water Geyser - Unused'),
}
    

movementdict = {
    1 : ('走る','Walk'),
    2 : ('ジャンプ','Jump'),
}
    
pathtypedict = {
    1 : "Normal",
    2 : "Secret Exit",
    3 : "Both",
}




class properties(bpy.types.PropertyGroup):

    secretexit : bpy.props.BoolProperty(name = "Secret Exit")
    
    fevent : bpy.props.StringProperty(name = "Event")
        
    path : bpy.props.StringProperty(
        name="",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

class mainpanel(bpy.types.Panel):
    bl_label = "RouteExport"
    bl_idname = "ADDONNAME_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RouteExp"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        col = layout.column(align=True)
        obj = context.object
            

        layout.prop(obj, "name")
        layout.prop(scene.my_tool, "path", text="Output")
        row = layout.row()
        row.operator("routeexport.writefiles")
        row = layout.row()
        row.operator("routeexport.generateprop")
        
        if(obj.name[0:1]=='W'):
            layout.label(text="Level")
            layout.prop(mytool, "secretexit")
        if(obj.name[0:2]=='F0'):
            layout.label(text="F-Node")
            layout.prop(obj, '["Event"]')
        if(obj.name[0:1]=='R'):
            layout.label(text="Route: " + obj.name)
            
            layout.prop(obj, '["Movement"]')
            layout.label(text=movementdict[obj['Movement'][0]][1])
            layout.prop(obj, '["Sound"]')  
            layout.label(text=sounddict[obj['Sound'][0]][1])
            layout.prop(obj, '["Path Unlock Type"]')
            layout.label(text=pathtypedict[obj['Path Unlock Type'][0]])
            
        
        if(obj.name[0:1]=='K'):
            layout.label(text="K Node")
        

class generateprop(bpy.types.Operator):
    bl_label = "Generate Properties / Reset Properties"
    bl_idname = "routeexport.generateprop"
        
    def execute(self,context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        obj = context.object
         


        routes = [obj for obj in bpy.data.objects if obj.name[0:1] in ["R"]]
        for obj in routes:
            obj["Movement"] = [1]
            obj["Sound"] = [1]
            obj["Path Unlock Type"] = [1]
            
        fnodes = [obj for obj in bpy.data.objects if obj.name[0:1] in ["F"]]

        for obj in fnodes:
            obj["Event"] = 'stop'
        
        return {"FINISHED"}
    
class writefiles(bpy.types.Operator):
    bl_label = "Export Route Files"
    bl_idname = "routeexport.writefiles"

        
    def execute(self,context):    
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        
        if(mytool.path[1:2] == ":"):
            
            writeNode(mytool.path)
            writeRoute(mytool.path, routeGeneration())
            self.report({"INFO"},"Saved point.csv and route.csv in " + mytool.path)
            return {"FINISHED"}
        elif(mytool.path == ""):
            self.report({"ERROR"},"No output directory found")
            return {"FINISHED"}
        else:
            self.report({"ERROR"},"Invalid path, set a valid directory and make sure it's an absolute path.")
            return {"FINISHED"}
    


    
    
    
classes = [properties,mainpanel,generateprop,writefiles]
    
    
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


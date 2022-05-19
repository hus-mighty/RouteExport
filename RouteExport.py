bl_info = {
    "name": "Map Export",
    "blender": (3, 00, 0),
    "category": "Object",
}

import bpy
import csv
import numpy
import os


def getKNodeParent(obj):
    if(obj.parent and not obj.name[0:1] == 'R'):
        obj = obj.parent
        return getKNodeParent(obj)
    else:
        return obj

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
        for i in levelTuples():
            if(i[0]== nodearr[x]):
                node.insert(x, (f'{x}',nodearr[x],'R'+ i[0] + i[1],'','','','','','R'+ i[0] + i[1]))
        
    for x in range(0,len(fnodearr())):
        if(fnodearr()[x][0:1] == 'F'):
            node.insert(x, (f'{x}',fnodearr()[x],event,'','','','','',''))
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
def generateRoute(routeentry):
    route = []
    for x in fnodearr():
        for y in fnodearr():
            if ((routeentry[0] == 'R' + x + y) and (routeentry[0][0:1] == 'R' and len(routeentry) == 1)):
                route.append([f'{routeentry[0]}','',movementdict[bpy.data.objects[routeentry[0]]["Movement"]],sounddict[bpy.data.objects[routeentry[0]]["Sound"]]])
            elif((routeentry[0] == 'R' + x + y) and (routeentry[0][0:1] == 'R') and len(routeentry) > 1):
                l = 0
                for a in range(0,len(routeentry)):
                    l+=1
                for c in range(0,l):
                    if(c==0 and len(routeentry)-1 < 2):
                        if( routeentry[0][5:6] == 'F' and  routeentry[1][0:1] == 'F'):
                            route.append((f'{routeentry[0]}',movementdict[bpy.data.objects[routeentry[0]]["Movement"]],sounddict[bpy.data.objects[routeentry[0]]["Sound"]]))
                            break
                        elif(routeentry[0][5:6] == 'F' and  routeentry[1][0:1] == 'K'):
                            route.append((f'R{routeentry[0][1:5] + routeentry[1]}',movementdict[bpy.data.objects[routeentry[0][1:5]]["Movement"]],sounddict[bpy.data.objects[routeentry[0][1:5]]["Sound"]]))
                            route.append((f'R{routeentry[1] + routeentry[0][5:9]}',movementdict[bpy.data.objects[routeentry[1]]["Movement"]],sounddict[bpy.data.objects[routeentry[1]]["Sound"]]))
                            break
                        else:
                            route.append((f'R{routeentry[0][1:5] + routeentry[1]}',movementdict[bpy.data.objects[routeentry[0]]["Movement"]],sounddict[bpy.data.objects[routeentry[0]]["Sound"]]))
                            route.append((f'R{routeentry[1] + routeentry[0][5:9]}',movementdict[bpy.data.objects[routeentry[1]]["Movement"]],sounddict[bpy.data.objects[routeentry[1]]["Sound"]]))
                            break
                    elif(c==0 and len(routeentry)-1 > 1):
                        
                        route.append((f'R{routeentry[0][1:5] + routeentry[c+1]}',movementdict[bpy.data.objects[routeentry[0]]["Movement"]],sounddict[bpy.data.objects[routeentry[0]]["Sound"]]))
                    elif(c==len(routeentry)-1):
                        if(routeentry[c][0:1] == 'F'):
                            break
                        else:
                            route.append((f'R{routeentry[c] + routeentry[0][5:9]}',movementdict[bpy.data.objects[routeentry[c]]["Movement"]],sounddict[bpy.data.objects[routeentry[c]]["Sound"]]))
                    elif(c > 0 and c < len(routeentry)-1):
                        route.append((f'R{routeentry[c] + routeentry[c+1]}',movementdict[bpy.data.objects[routeentry[c]]["Movement"]],sounddict[bpy.data.objects[routeentry[c]]["Sound"]]))
    return route


def writeNode(dir):
    with open(dir + '\\point.csv', 'w',encoding='shift_jis', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(numpy.array(generateNode('stop')))
    
    
def writeRoute(dir, routearray):
    with open(dir + '\\route.csv', 'w',encoding='shift_jis', newline='') as file:
        mywriter = csv.writer(file, delimiter=',',quotechar='',escapechar='\\', quoting=csv.QUOTE_NONE)
        mywriter.writerows(routearray)
        

def routeGeneration():
    h = []
    for x in getRoute():
        h += generateRoute(x)
    return h
#,h[x][1], sounddict[bpy.data.objects[x[0]]["Sound"]]

def levelTuples():
    h = []
    for x in getRoute():
        h.append((x[0][1:5], x[0][5:9]))
    return h        
        
        
sounddict = {
    'Road' : '"道"',
    'Snow' : '"雪"',
    'Sand' : '"砂"',
    'Ice - Unused': '"氷"',
    'Grass' : '"草"',
    'Water' : '"水"',
    'Cloud' : '"雲"',
    'Sand Geyser - Unused' : '"砂間欠泉"',
    'Mushroom' : '"マンタ"',
    'Beach - Unused' : '"ビーチ"',
    'Carpet' : '"じゅうたん"',
    'Leaf - Unused' : '"葉っぱ"',
    'Barrel' : '"樽"',
    'Water Geyser - Unused' : '"水間欠泉"',
    '' : ""
}

movementdict = {
    'Walk' : '走る',
    'Jump' : 'ジャンプ',
    '' : ""
}
    
pathtypedict = {
    1 : "Normal",
    2 : "Secret Exit",
    3 : "Normal and Secret",
    "" : ""
}


class properties(bpy.types.PropertyGroup):
        
    path : bpy.props.StringProperty(
        name="",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
        
    soundenum : bpy.props.EnumProperty(
    name = "Sound",
    description = "",
    items = [('Road','Road',""),
             ('Snow','Snow',""),
             ('Sand','Sand',""),
             ('Ice - Unused','Ice - Unused',""),
             ('Grass','Grass',""),
             ('Water','Water',""),
             ('Cloud','Cloud',""),
             ('Sand Geyser - Unused','Sand Geyser - Unused',""),
             ('Mushroom','Mushroom',""),
             ('Beach - Unused','Beach - Unused',""),
             ('Carpet','Carpet',""),
             ('Leaf - Unused','Leaf - Unused',""),
             ('Barrel','Barrel',""),
             ('Water Geyser - Unused','Water Geyser - Unused',"")]
)

    movementenum : bpy.props.EnumProperty(
    name = "Movement",
    description = "",
    items = [('Walk','Walk',""),
             ('Jump','Jump',"")]
)

    pathenum : bpy.props.EnumProperty(
    name = "Path Unlock",
    description = "",
    items = [('Normal','Normal',""),
             ('Secret Exit','Secret Exit',""),
             ('Normal and Secret','Normal and Secret',"")]       
)


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
        row = layout.row()
        objname = bpy.context.object.name
        
        #Name, Output, Export and Generate
        layout.prop(obj, "name")
        layout.prop(scene.my_tool, "path", text="Output")
        row = layout.row()
        row.operator("routeexport.writefiles")
        row = layout.row()
        row.operator("routeexport.propgen")

        
        if(obj.name[0:1]=='W' and obj.parent.name == 'course'):
            layout.label(text="Level: " + obj.name)
            
        #F-Node
        if(obj.name[0:2]=='F0' and getKNodeParent(obj).name[0:1] == 'R'):
            
            #Route Label
            if(obj.children):
                layout.label(text='Route: ' + obj.name[0:5] + obj.children[0].name)
            else:
                layout.label(text='Route: End')
                
            
            layout.prop(mytool, "soundenum")
            layout.prop(mytool, "movementenum")

            
            row = layout.row()
            row.operator("routeexport.writeprop")
            
            layout.label(text='Sound: ' + bpy.data.objects[objname]["Sound"]) 
            layout.label(text='Movement: ' + bpy.data.objects[objname]["Movement"])


        #route
        if(obj.name[0:1]=='R' and obj.parent.name == 'route'):
            
            #Route Label
            if(obj.children):
                layout.label(text='Route: ' + obj.name[0:5] + obj.children[0].name)
            else:
                layout.label(text='Route: ' + obj.name)
                
            layout.prop(mytool, "soundenum")
            layout.prop(mytool, "movementenum")
            layout.prop(mytool, "pathenum")
            
            row = layout.row()
            row.operator("routeexport.writeprop")
            
            layout.label(text='Sound: ' + bpy.data.objects[objname]["Sound"]) 
            layout.label(text='Movement: ' + bpy.data.objects[objname]["Movement"])   
            layout.label(text='Path Type: ' + bpy.data.objects[objname]["Path Unlock Type"])


        if(obj.name[0:1]=='K' and getKNodeParent(obj).name[0:1] == 'R'):
            
            #Route Label
            if(obj.children):
                layout.label(text='Route: R' + obj.name[0:5] + obj.children[0].name)
            else:
                layout.label(text='Route: R' + obj.name + getKNodeParent(obj).name[5:9])

            layout.prop(mytool, "soundenum")
            layout.prop(mytool, "movementenum")
            
            row = layout.row()
            row.operator("routeexport.writeprop")
            
            layout.label(text='Sound: ' + bpy.data.objects[objname]["Sound"]) 
            layout.label(text='Movement: ' + bpy.data.objects[objname]["Movement"])

#button operators
#set properties
class writeprop(bpy.types.Operator):
    bl_label = "Set Properties "
    bl_idname = "routeexport.writeprop"
        
    def execute(self,context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        obj = context.object
        name = bpy.context.object.name

        
        bpy.data.objects[name]["Movement"] = bpy.context.scene.my_tool.movementenum
        bpy.data.objects[name]["Sound"] = bpy.context.scene.my_tool.soundenum
        bpy.data.objects[name]["Path Unlock Type"] = bpy.context.scene.my_tool.pathenum
    

        return {"FINISHED"}
    
#write csv files
class writefiles(bpy.types.Operator):
    bl_label = "Generate Route Files"
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

#generate the custom properties for objects
class propgen(bpy.types.Operator):
    bl_label = "Generate/Reset Properties"
    bl_idname = "routeexport.propgen"

    def execute(self,context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        obj = context.object
         
        routes = [obj for obj in bpy.data.objects if obj.name[0:1] in ["R"] and obj.parent.name == "route"]
        for obj in routes:
            obj["Movement"] = "Walk"
            obj["Sound"] = "Road"
            obj["Path Unlock Type"] = "Normal"
            
        fnodes = [obj for obj in bpy.data.objects if obj.name[0:1] in ["F"] and 
        (obj.parent.name == "route" or obj.parent.name[0:2] == "F0" or obj.parent.name[0:1] == "K" or obj.parent.name[0:1] == "R")]

        for obj in fnodes:
            obj["Event"] = 'stop'
            obj["Movement"] = "Walk"
            obj["Sound"] = "Road"
            
        fnodes = [obj for obj in bpy.data.objects if obj.name[0:1] in ["K"] and
        (obj.parent.name[0:1] == "K" or obj.parent.name[0:1] == "R")]

        for obj in fnodes:
            obj["Movement"] = "Walk"
            obj["Sound"] = "Road"
        
        return {"FINISHED"}


classes = [properties,mainpanel,writeprop,writefiles,propgen]
    
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
    

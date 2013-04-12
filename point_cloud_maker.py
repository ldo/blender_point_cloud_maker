#+
# Add-on for Blender 2.6 that generates a mesh consisting of a random
# collection of unconnected vertices according to a given probability
# density function.
#
# Copyright 2013 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-

import sys # debug
import random
import bpy
import mathutils

bl_info = \
    {
        "name" : "Point Cloud Maker",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (0, 0, 1),
        "blender" : (2, 6, 6),
        "location" : "View 3D > Add > Mesh",
        "description" :
            "Generates a mesh consisting of a random collection of unconnected"
            " vertices according to a given probability density function.",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category" : "Add Mesh",
    }

class Failure(Exception) :

    def __init__(self, msg) :
        self.msg = msg
    #end __init__

#end Failure

class MakePointCloud(bpy.types.Operator) :
    bl_idname = "mesh.add_point_cloud"
    bl_label = "Point Cloud"
    bl_options = {"REGISTER", "UNDO"}

    function = bpy.props.StringProperty \
      (
        name = "Function",
        description = "probability density function f(x, y, z) where x, y, z each ∊ [-1, 1]",
        default = "lambda x, y, z : 1.0",
      )

    imports = bpy.props.StringProperty \
      (
        name = "Imports",
        description =
            "any module(s) (separate with commas if more than one)"
            " that should be imported for defining the function",
        default = "math",
      )

    max_density = bpy.props.FloatProperty \
      (
        name = "Max Density",
        description = "max value of probability density function",
        default = 1.0,
      )

    nr_points = bpy.props.IntProperty \
      (
        name = "Nr Points",
        description = "how many points to generate",
        default = 1000,
      )

    seed = bpy.props.IntProperty \
      (
        name = "Random Seed",
        description = "seed for pseudorandom number generation, or -1 to make it random",
        default = 0,
      )

    def draw(self, context) :
        the_col = self.layout.column(align = True)
        the_col.prop(self, "function")
        the_col.prop(self, "imports")
        the_col.prop(self, "max_density")
        the_col.prop(self, "nr_points")
        the_col.prop(self, "seed")
    #end draw

    def action_common(self, context, redoing) :
        if self.seed >= 0 :
            random.seed(self.seed)
        #end if
        try :
            for m in self.imports.split(",") :
                m = m.strip()
                if len(m) != 0 :
                    exec("import " + m, locals())
                #end if
            #end for
            func = eval(self.function, locals())
            vertices = []
            for i in range(0, self.nr_points) :
                # rejection sampling algorithm <http://en.wikipedia.org/wiki/Rejection_sampling>
                x = random.uniform(-1, 1)
                y = random.uniform(-1, 1)
                z = random.uniform(-1, 1)
                if random.uniform(0, self.max_density) < func(x, y, z) :
                    vertices.append(mathutils.Vector((x, y, z)))
                #end if
            #end for
            meshname = "point_cloud"
            the_mesh = bpy.data.meshes.new(meshname)
            the_mesh.from_pydata(vertices, [], [])
            the_obj = bpy.data.objects.new(meshname, the_mesh)
            the_mesh.update()
            context.scene.objects.link(the_obj)
            bpy.ops.object.select_all(action = "DESELECT")
            bpy.data.objects[meshname].select = True
            for vertex in the_mesh.vertices :
                vertex.select = True # usual Blender default for newly-created object
            #end for
            the_mesh.update()
            # all done
            status = {"FINISHED"}
        except Failure as why :
            sys.stderr.write("Failure: %s\n" % why.msg) # debug
            self.report({"ERROR"}, why.msg)
            status = {"CANCELLED"}
        #end try
        return status
    #end action_common

    def execute(self, context) :
        return self.action_common(context, True)
    #end execute

    def invoke(self, context, event) :
        return self.action_common(context, False)
    #end invoke

#end MakePointCloud

def add_to_menu(self, context) :
    self.layout.operator("mesh.add_point_cloud", icon = "PLUGIN")
#end add_to_menu

def register() :
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(add_to_menu)
#end register

def unregister() :
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(add_to_menu)
#end unregister

if __name__ == "__main__" :
    register()
#end if
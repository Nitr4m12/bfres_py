#!/usr/bin/env python

from formats import *
from typing import List

class IndexGroup():
    def __init__(self, buffer, pos):
        self.entries = []
        get_unpacked_data(self, "IndexGroup", buffer, pos)

        for i in range(self.count):
            # Add an entry to the "entries" list
            self.entry = self.IndexEntry(buffer, (pos + 24) + (16 * i))
            self.entries.append(self.entry)

    class IndexEntry():
        def __init__(self, buffer, pos):
            get_unpacked_data(self, "IndexEntry", buffer, pos)

class FRES():
    # caFe RESource
    def __init__(self, buffer, pos):
        self.subfile_names = ("fmdl", "ftex", "fska", "fshu", "fshu", "fshu", "ftxp", "fvis", "fvis", "fsha", "fscn", "embedded_files")
        self.index_groups = {}
        self.subfiles_offsets = {}

        self.header = self.Header(buffer, pos)
        
        # Store whichever dict offset is available
        for i in range(len(self.header.dicts_offsets)):
            if self.header.dicts_offsets[i] not in [0, -1]:
                pos = self.header.dicts_offsets[i]
                self.index_groups[self.subfile_names[i]] = IndexGroup(buffer, pos)

        for i, j in self.index_groups.items():
            self.subfiles_offsets[i] = []
            if j:
                for k in j.entries:
                    self.subfiles_offsets[i].append(k.data_offset)
        for key, value in self.subfiles_offsets.items():
            exec("self.{}_files = []".format(key))
            for i in value:
                exec("self.{}_files.append(self.{}(buffer, {}))".format(key, key.upper(), i))

    class Header():
        def __init__(self, buffer, pos):
            get_unpacked_data(self, "Header", buffer, pos)

    class FMDL(): #0
        # caFe MoDeL
        def __init__(self, buffer, pos):
            self.header = self.Header(buffer, pos)
            self.skele_file = self.FSKL(buffer, self.header.fskl_offset)
            self.vertices = []
            self.shapes_dict = IndexGroup(buffer, self.header.fshp_dict_offset)
            self.shapes = []
            self.materials_dict = IndexGroup(buffer, self.header.fmat_dict_offset)
            self.materials = []
            for i in range(self.header.fvtx_count):
                self.vertices.append(self.FVTX(buffer, self.header.fvtx_offset + i * 0x20))
            for j in self.shapes_dict.entries:
                self.shapes.append(self.FSHP(buffer, j.data_offset))
            for k in self.materials_dict.entries:
                self.shapes.append(self.FMAT(buffer, k.data_offset))

        # Separate each section of the FMDL file into classes, allowing for easier association 
        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FMDLHeader", buffer, pos)

        class FVTX():
            # caFe VerTeX
            def __init__(self, buffer, pos):
                self.header = self.Header(buffer, pos)
                self.attributes = []
                self.buffers = []
                for i in range(self.header.attrib_count):
                    self.attributes.append(self.Attribute(buffer, self.header.attribs_offset + i + 0xC))
                for i in range(self.header.buffer_count):
                    self.buffers.append(self.Buffer(buffer, self.header.buffers_offset + i * 0x18))
                
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FVTXHeader", buffer, pos)

            class Attribute():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FVTXAttribute", buffer, pos)

            class Buffer():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FVTXBuffer", buffer, pos)

        class FSKL():
            # caFe SKeLeton
            def __init__(self, buffer, pos):
                self.header: self.Header = self.Header(buffer, pos)
                self.bones: List[self.Bone] = []

                for i in range(self.header.bone_count):
                    self.bones.append(self.Bone(buffer, self.header.bones_offset + i * 0x40))

                self.smooth_matrices = self.SmoothMatrix(self.header.smooth_index_count, buffer, self.header.smooth_matrix_offset)

            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FSKLHeader", buffer, pos)

            class Bone():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "Bone", buffer, pos)

            class SmoothMatrix(struct.Struct):
                def __init__(self, count, buffer, pos):
                    super().__init__(f">{count}H")

                    self.values = self.unpack_from(buffer, pos)

            class RigidMatrix(struct.Struct):
                def __init__(self, count, buffer, pos):
                    super().__init__(f">{count}H")

                    self.values = self.unpack_from(buffer, pos)

        class FSHP():
            # caFe SHaPe
            def __init__(self, buffer, pos):
                self.header = self.Header(buffer, pos)
                self.lod_mdls = []
                for i in range(self.header.lod_mdl_count):
                    self.lod_mdls.append(self.LoDModel(buffer, self.header.lod_mdls_offset + i * 0x1C))
                # TODO: FSKLIndexArray, Visibility Group, IndexBuffer
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FSHPHeader", buffer, pos)

            class LoDModel():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "LoDModel", buffer, pos)

            class FSKLIndexArray():
                def __init__(self, count, data, pos):
                    super().__init__(f">{count}H")

                    self.values = self.unpack_from(data, pos)

            class VisibilityGroup():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "VisibilityGroup", buffer, pos)

            class IndexBuffer():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FVTXBuffer", buffer, pos)

        class FMAT():
            # caFe MATerial
            def __init__(self, buffer, pos):
                self.header = self.Header(buffer, pos)
                self.tex_samplers = []
                self.material_parameters = []
                self.render_state = self.RenderState(buffer, self.header.render_state_offset)
                self.shader_assign = self.ShaderAssign(buffer, self.header.shdr_assign_offset)
                for i in range(self.header.tex_sampler_count):
                    self.tex_samplers.append(self.TextureSampler(buffer, self.header.tex_samplers_offset + i * 0x18))
                for j in range(self.header.mat_param_count):
                    self.material_parameters.append(self.MaterialParameter(buffer, self.header.mat_params_offset + i * 0x14))

            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FMATHeader", buffer, pos)

            class RenderInfo():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "RenderInfo", buffer, pos)

                    self.array_data_class = self.ArrayData()
                    self.array_data_class.set_data(self.element_type, buffer, pos + 8)
                    self.array_data = self.array_data_class.data # 0x08 - uInt[2]/float[2]/uInt

                class ArrayData():
                    def set_data(self, type_, data, pos):
                        if type_ == 0:
                            super().__init__(">2I")
                            self.data = self.unpack_from(data, pos)
                        elif type_ == 1:
                            super().__init__(">2f")
                            self.data = self.unpack_from(data, pos)
                        else:
                            super().__init__(">I")
                            self.data = self.unpack_from(data, pos)

            class TextureSampler():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "TextureSampler", buffer, pos)

            class MaterialParameter():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "MaterialParameter", buffer, pos)

            class RenderState():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "RenderState", buffer, pos)

            class ShaderAssign():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "ShaderAssign", buffer, pos)

    class FTEX(): #1
        # caFe TEXture
        def __init__(self, buffer, pos):
            self.header = self.Header(buffer, pos)

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FTEXHeader", buffer, pos)
                for i in self.mipmaps_offsets:
                    self.mipmaps_offsets[i] += self.mipmap_data_offset

    class FSKA(): #2
        # caFe SKeletal Animation
        def __init__(self, buffer, pos):
            ...

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FSKAHeader", buffer, pos)
        
        class BoneAnimation():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "BoneAnimation", buffer, pos)

            class BoneAnimationData():
                def __init__(self, buffer, pos):
                    ...
        class Curve():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FSKAHeader", buffer, pos)

        class Curve():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CurveHeader", buffer, pos)

            class Frames():
                ...

            class Keys():
                ...

            class StepCurves():
                ...

            class LinearCurves():
                ...

    class FSHU(): #3, 4, 5
        # caFe SHader parameter animation Uber
        def __init__(self, buffer, pos):
            self.header = self.Header(buffer, pos)

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FSHUHeader", buffer, pos)

        class MaterialAnimation():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "MaterialAnimation", buffer, pos)

        class ParameterAnimationInfo():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "ParameterAnimationInfo", buffer, pos)
        
        class AnimationConstant():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "AnimationConstant", buffer, pos)

        class Curve():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CurveHeader", buffer, pos)

            class Frames():
                ...

            class Keys():
                ...

            class StepCurves():
                ...

            class LinearCurves():
                ...

    class FTXP(): # 6
        # caFe TeXture Pattern animation
        def __init__(self, buffer, pos):
            self.header = self.Header(buffer, pos)

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FTXPHeader", buffer, pos)

        class MaterialPatternAnimation():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "MaterialPatternAnimation", buffer, pos)

        class PatternAnimationInfo():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "PatternAnimationInfo", buffer, pos)

        class Curve():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CurveHeader", buffer, pos)

            class Frames():
                ...

            class Keys():
                ...

            class StepCurves():
                ...

            class LinearCurves():
                ...

    class FVIS(): # 7, 8
        # caFe VISibility animation
        def __init__(self, buffer, pos):
            self.header = Header(buffer, pos)

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FVISHeader", buffer, pos)

        class Curve():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CurveHeader", buffer, pos)

            class Frames():
                ...

            class Keys():
                ...

            class StepCurves():
                ...

            class LinearCurves():
                ...

    class FSHA(): # 9
        # caFe SHape Animation
        def __init__(self, buffer, pos):
            self.header = Header(buffer, pos)

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FSHAHeader", buffer, pos)
        class VertexShapeAnimation():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "VertexShapeAnimation", buffer, pos)

            class ShapeAnimationKey():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "ShapeAnimationKey", buffer, pos)
                    
        class Curve():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CurveHeader", buffer, pos)

            class Frames():
                ...

            class Keys():
                ...

            class StepCurves():
                ...

            class LinearCurves():
                ...

    class FSCN(): # 10
        # caFe SCeNe animation
        def __init__(self, buffer, pos):
            self.header = Header(buffer, pos)

        class Header():
            def __init__(self, buffer, pos):
                get_unpacked_data(self, "FSCNHeader", buffer, pos)

        class FCAM():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FCAMHeader", buffer, pos)

            class Data():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CameraAnimationData", buffer, pos)

        class FLIT():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FLITHeader", buffer, pos)

            class Data():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "LightAnimationData", buffer, pos)    
                    
        class FFOG():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FFOGHeader", buffer, pos)

            class Data():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "FogAnimationData", buffer, pos)

        class Curve():
            class Header():
                def __init__(self, buffer, pos):
                    get_unpacked_data(self, "CurveHeader", buffer, pos)

            class Frames():
                ...

            class Keys():
                ...

            class StepCurves():
                ...

            class LinearCurves():
                ...

    class EMBEDDED_FILES(): # 11
        def __init__(self, buffer, pos):
            get_unpacked_data(self, "EmbeddedFiles", buffer, pos)

def to_absolute(unpacked_data: tuple, pos: int, fmt: str):
    # Convert every relative offset to absolute
    unpacked_data_list = list(unpacked_data)
    if len(unpacked_data) > 2:
        for i in range(len(unpacked_data)):
            unpacked_data_list[i] += pos + i * (struct.calcsize(fmt) // len(unpacked_data)) if unpacked_data_list[i] else 0
        return unpacked_data_list
    else:
        unpacked_data_list[0] += pos
        return unpacked_data_list[0]

def get_unpacked_data(self, name: str, buffer: bytes, pos: int):
    for name, fmt in structs_fmts[name].items():
        # Unpack the header structs to make them accesible from within the class
        unpacked_data = struct.unpack(fmt, buffer[pos:pos + struct.calcsize(fmt)])
        if "offset" in name:
            if name == "mipmaps_offsets":
                exec("self.{} = {}".format(name, list(unpacked_data)))
            else:
                exec("self.{} = {}".format(name, to_absolute(unpacked_data, pos, fmt)))
        else:
            exec("self.{} = {}".format(name, unpacked_data[0]))
        pos += struct.calcsize(fmt)

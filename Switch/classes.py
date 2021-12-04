#!/usr/bin/env python

from formats import *
from typing import List, Tuple
from struct import Struct

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
        self.header = self.Header(buffer, pos)

        self.subfile_offsets = {
                                "Model":                self.header.model_offset,
                                "Skeletal_Animation":   self.header.skeletal_anim_offset,
                                "Material_Animation":   self.header.material_anim_offset, 
                                "Bone_Visual_Animation":self.header.bone_vis_anim_offset, 
                                "Shape_Animation":      self.header.shape_anim_offset,
                                "Scene_Animation":      self.header.scene_anim_offset, 
                                "Embedded_Files":       self.header.ext_files_offset
                                }
            
        self.subfile_counts = {
                                "Model":                self.header.model_count,
                                "Skeletal_Animation":   self.header.skeletal_anim_count,
                                "Material_Animation":   self.header.material_anim_count, 
                                "Bone_Visual_Animation":self.header.bone_vis_anim_count, 
                                "Shape_Animation":      self.header.shape_anim_count,
                                "Scene_Animation":      self.header.scene_anim_count, 
                                "Embedded_Files":       self.header.embedded_file_count
                                }

        self.subfile_header_length = {
                                        "Model":                0x78,
                                        "Skeletal_Animation":   0x60,
                                        "Material_Animation":   0x78, 
                                        "Bone_Visual_Animation":self.bone_vis_anim_count, 
                                        "Shape_Animation":      self.shape_anim_count,
                                        "Scene_Animation":      self.scene_anim_count, 
                                        "Embedded_Files":       0x10
                                        }
        
        # Store whichever file is available
        for key, value in self.subfile_offsets.items():
            if value not in [0, -1]:
                for i in range(self.subfile_counts[key]):
                    exec("self.{}_files = []".format(key.lower()))
                    exec("self.{}_files.append(self.{}(buffer, {}))".format(
                            key.lower(), 
                            key.strip("_"), 
                            value + i * self.subfile_header_length[key]
                            )
                        )

    class Header(Struct):
        def __init__(self, buffer, pos):
            super().__init__("<4s 2I H 2B I 2H 2I 17Q 8x Q I 7H 6x")
            self.dict_offsets: List[int] = list()
            self.subfile_offsets: List[int] = list()

            self.data = self.unpack_from(buffer, pos)
            (
             self.magic, 
             self.signature,
             self.version, 
             self.bom,
             self.alignment, 
             self.target_addr_size,
             self.file_name_offset, 
             self.flags,
             self.block_offset, 
             self.reloc_table_offset,
             self.file_size, 
             self.file_name_length_offset,
             self.model_offset,
             self.model_dict_offset,
             self.skeletal_anim_offset,
             self.skeletal_anim_dict_offset, 
             self.material_anim_offset,
             self.material_anim_dict_offset,
             self.bone_vis_anim_offset,
             self.bone_vis_anim_dict_offset,
             self.shape_anim_offset,
             self.shape_anim_dict_offset,
             self.scene_anim_offset,
             self.scene_anim_dict_offset,
             self.memory_pool,
             self.buffer_section, 
             self.ext_files_offset,
             self.ext_files_dict_offset,
             self.string_table_offset, 
             self.string_table_size,
             self.model_count,
             self.skeletal_anim_count,
             self.material_anim_count,
             self.bone_vis_anim_count,
             self.shape_anim_count,
             self.scene_anim_count,
             self.embedded_file_count
            ) = self.data
            
    class Model(): #0
        # FMDL: caFe MoDeL
        def __init__(self, buffer, pos):
            self.header = self.Header(buffer, pos)
            self.skeleton = self.FSKL(buffer, self.header.skeleton_offset)

            self.vertices = []
            for i in range(self.header.vertex_count):
                self.vertices.append(self.FVTX(buffer, self.header.vertices_offset + i * 0x60))

            self.materials = []
            for i in range(self.header.material_count):
                self.materials.append(self.FMAT(buffer, self.header.materials_offset + i * 0xB8))

            self.shapes = []
            for i in range(self.header.shape_count):
                self.shapes.append(self.FSHP(buffer, self.header.shape_offset + i * 0x60))
            self.shape = self.FSHP(buffer, self.header.shape_offset)
            self.material = self.FMAT(buffer, self.header.material_offset)

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
        class Header(Struct):
            def __init__(self, buffer, pos):
                super().__init__("<4s I 10Q 16x 4H I 4x")
                
                self.data: Tuple = self.unpack_from(buffer, pos)

                (
                 self.magic,
                 self.flags,
                 self.model_name_offset,
                 self.path_name_offset,
                 self.skeleton_offset,
                 self.vertices_offset,
                 self.shape_offset,
                 self.shape_dict_offset,
                 self.material_offset,
                 self.material_dict_offset,
                 self.user_data_offset,
                 self.vertex_count,
                 self.shape_count,
                 self.material_count,
                 self.user_data_count,
                 self.total_vertex_count
                ) = self.data

    #     class FVTX():
    #         # caFe VerTeX
    #         def __init__(self, buffer, pos):
    #             self.header = self.Header(buffer, pos)
    #             self.attributes = []
    #             self.buffers = []
    #             for i in range(self.header.attrib_count):
    #                 self.attributes.append(self.Attribute(buffer, self.header.attribs_offset + i + 0xC))
    #             for i in range(self.header.buffer_count):
    #                 self.buffers.append(self.Buffer(buffer, self.header.buffers_offset + i * 0x18))
                
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FVTXHeader", buffer, pos)

    #         class Attribute():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FVTXAttribute", buffer, pos)

    #         class Buffer():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FVTXBuffer", buffer, pos)

    #     class FSKL():
    #         # caFe SKeLeton
    #         def __init__(self, buffer, pos):
    #             self.header: self.Header = self.Header(buffer, pos)
    #             self.bones: List[self.Bone] = []

    #             for i in range(self.header.bone_count):
    #                 self.bones.append(self.Bone(buffer, self.header.bones_offset + i * 0x40))

    #             self.smooth_matrices = self.SmoothMatrix(self.header.smooth_index_count, buffer, self.header.smooth_matrix_offset)

    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FSKLHeader", buffer, pos)

    #         class Bone():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "Bone", buffer, pos)

    #         class SmoothMatrix(struct.Struct):
    #             def __init__(self, count, buffer, pos):
    #                 super().__init__(f">{count}H")

    #                 self.values = self.unpack_from(buffer, pos)

    #         class RigidMatrix(struct.Struct):
    #             def __init__(self, count, buffer, pos):
    #                 super().__init__(f">{count}H")

    #                 self.values = self.unpack_from(buffer, pos)

    #     class FSHP():
    #         # caFe SHaPe
    #         def __init__(self, buffer, pos):
    #             self.header = self.Header(buffer, pos)
    #             self.lod_mdls = []
    #             for i in range(self.header.lod_mdl_count):
    #                 self.lod_mdls.append(self.LoDModel(buffer, self.header.lod_mdls_offset + i * 0x1C))
    #             # TODO: FSKLIndexArray, Visibility Group, IndexBuffer
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FSHPHeader", buffer, pos)

    #         class LoDModel():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "LoDModel", buffer, pos)

    #         class FSKLIndexArray():
    #             def __init__(self, count, data, pos):
    #                 super().__init__(f">{count}H")

    #                 self.values = self.unpack_from(data, pos)

    #         class VisibilityGroup():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "VisibilityGroup", buffer, pos)

    #         class IndexBuffer():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FVTXBuffer", buffer, pos)

    #     class FMAT():
    #         # caFe MATerial
    #         def __init__(self, buffer, pos):
    #             self.header = self.Header(buffer, pos)
    #             self.tex_samplers = []
    #             self.material_parameters = []
    #             self.render_info_params = []
    #             self.render_info_dict = IndexGroup(buffer, self.header.render_info_dict_offset)
    #             self.render_state = self.RenderState(buffer, self.header.render_state_offset)
    #             self.shader_assign = self.ShaderAssign(buffer, self.header.shdr_assign_offset)

    #             for i in range(self.header.tex_sampler_count):
    #                 self.tex_samplers.append(self.TextureSampler(buffer, self.header.tex_samplers_offset + i * 0x18))

    #             for j in range(self.header.mat_param_count):
    #                 self.material_parameters.append(self.MaterialParameter(buffer, self.header.mat_params_offset + i * 0x14))

    #             for entry in self.render_info_dict.entries:
    #                 self.render_info_params.append(self.RenderInfo(buffer, entry.data_offset))

    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FMATHeader", buffer, pos)

    #         class RenderInfo():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "RenderInfo", buffer, pos)

    #                 self.array_data_class = self.ArrayData(self.element_type, buffer, pos + 8)
    #                 self.array_data = self.array_data_class.data # 0x08 - uInt[2]/float[2]/uInt

    #             class ArrayData(struct.Struct):
    #                 def __init__(self, type_, buffer, pos):
    #                     if type_ == 0:
    #                         super().__init__(">2I")
    #                         self.data = self.unpack_from(buffer, pos)
    #                     elif type_ == 1:
    #                         super().__init__(">2f")
    #                         self.data = self.unpack_from(buffer, pos)
    #                     else:
    #                         super().__init__(">I")
    #                         self.data = self.unpack_from(buffer, pos)[0]

    #         class TextureSampler():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "TextureSampler", buffer, pos)

    #         class MaterialParameter():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "MaterialParameter", buffer, pos)

    #         class RenderState():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "RenderState", buffer, pos)

    #         class ShaderAssign():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "ShaderAssign", buffer, pos)

    # class FTEX(): #1
    #     # caFe TEXture
    #     def __init__(self, buffer, pos):
    #         self.header = self.Header(buffer, pos)
    #         self.data = buffer[self.header.data_offset:self.header.data_offset + self.header.data_length]
    #         self.mipmaps = []
    #         for i in self.header.mipmaps_offsets:
    #             self.mipmaps.append(buffer[i:i + self.header.mipmaps_data_length])

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FTEXHeader", buffer, pos)
    #             for i in range(len(self.mipmaps_offsets)):
    #                 self.mipmaps_offsets[i] += self.mipmap_data_offset

    # class SkeletalAnimation(): #2
    #     # caFe SKeletal Animation
    #     def __init__(self, buffer, pos):
    #         self.header: self.Header = self.Header(buffer, pos)
    #         self.bone_animations: List[BoneAnimation] = []
    #         self.skeleton_offset: int = self.header.skeleton_offset
    #         self.bind_index: self.BindIndex = self.BindIndex(buffer, self.header.bone_animation_count, self.header.bind_index_array)
    #         self.bind_index_data: bytearray = self.bind_index.data

    #         for i in range(self.header.bone_animation_count):
    #             self.bone_animations.append(self.BoneAnimation(buffer, self.header.bone_animation_offset + i * 0x18))

    #         # Perform bitwise operations on the flags to determine the Skeleton properties
    #         self.baked_curves = bool(self.header.flags & 0b1)
    #         self.is_looping = bool(self.header.flags & 0b100)
    #         self.scale_type = (self.header.flags & 0b1100000000) >> 8
    #         self.rotation_module = bool(self.header.flags & 0b1000000000000)

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FSKAHeader", buffer, pos)
        
    #     class BindIndex(struct.Struct):
    #         def __init__(self, buffer, count, pos):
    #             super().__init__(f">{count}H")
    #             self.data = self.unpack_from(buffer, pos)
        
    #     class BoneAnimation():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "BoneAnimation", buffer, pos)
    #             self.curves = []
    #             # xxxxSSSS Sxxxxxxx CCCCCCCC CCBBBxxx
    #             self.which_data: int = (self.flags >> 3) & 0b111
    #             self.available_curves: int = (self.flags >> 6) & 0b1111111111
    #             self.bone_transform_effect: int = (self.flags >> 23) & 0b111111

    #             self.data: self.BoneAnimationData = self.BoneAnimationData(buffer, self.which_data, self.base_data_offset)
                
    #             for i in range(self.curve_count):
    #                 # TODO: Actually append the curves to the BoneAnimation
    #                 self.curves.append(self.Curve(buffer, self.curve_array_offset + i * 0x24))
    #         class BoneAnimationData():
    #             def __init__(self, buffer, which_data, pos):
    #                 self.scaling: Tuple[float, float, float] = struct.unpack_from(">3f", buffer, pos) if which_data & 0b001 else (None)
    #                 self.rotation: Tuple[float, float, float, float] = struct.unpack_from(">4f", buffer, pos + 12 if self.scaling else pos) if which_data & 0b010 else (None)
    #                 self.translation: Tuple[float, float, float] = struct.unpack_from(">3f", buffer, pos + 24 if self.scaling and self.rotation else pos) if which_data & 0b100 else (None)

    #         class Curve():
    #             def __init__(self, buffer, pos):
    #                 self.header = self.Header(buffer, pos)

    #             class Header():
    #                 def __init__(self, buffer, pos):
    #                     get_unpacked_data(self, "CurveHeader", buffer, pos)
    #                     # xxxxxxxx xCCCKKFF
    #                     self.frame_data_flag: int = self.flags & 0b11
    #                     self.key_data_flag: int = (self.flags >> 2) & 0b11
    #                     self.curve_data_flag: int = (self.flags >> 4) & 0b111

    #             class Frames():
    #                 def __init__(self, buffer, data_flag, count, pos):
    #                     if data_flag == 0b00:
    #                         self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                     elif data_flag == 0b01:
    #                         self.data: float = float(buffer[pos:pos + 2]) / (1 << 5)
    #                     else:
    #                         self.data: int = struct.unpack_from(fmt=f">{count}B", buffer=buffer, offset=pos)

    #             class Keys():
    #                 def __init__(self, buffer, data_flag, count, pos):
    #                     if data_flag == 0b00:
    #                         self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                     elif data_flag == 0b01:
    #                         self.data: int = struct.unpack_from(fmt=f'>{count}h', buffer=buffer, offset=pos)
    #                     else:
    #                         self.data: int = struct.unpack_from(fmt=f'>{count}b', buffer=buffer, offset=pos)

    #             class StepCurves():
    #                 # TODO
    #                 ...

    #             class LinearCurves():
    #                 # TODO
    #                 ...

    # class FSHU(): #3
    #     # caFe SHader parameter animation Uber
    #     def __init__(self, buffer, pos):
    #         self.header = self.Header(buffer, pos)

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FSHUHeader", buffer, pos)

    #     class MaterialAnimation():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "MaterialAnimation", buffer, pos)

    #     class ParameterAnimationInfo():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "ParameterAnimationInfo", buffer, pos)
        
    #     class AnimationConstant():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "AnimationConstant", buffer, pos)

    #     class Curve():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "CurveHeader", buffer, pos)
    #                 # xxxxxxxx xCCCKKFF
    #                 self.frame_data_flag: int = self.flags & 0b11
    #                 self.key_data_flag: int = (self.flags >> 2) & 0b11
    #                 self.curve_data_flag: int = (self.flags >> 4) & 0b111

    #         class Frames():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: float = float(buffer[pos:pos + 2]) / (1 << 5)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f">{count}B", buffer=buffer, offset=pos)

    #         class Keys():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}h', buffer=buffer, offset=pos)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}b', buffer=buffer, offset=pos)

    #         class StepCurves():
    #             # TODO
    #             ...

    #         class LinearCurves():
    #             # TODO
    #             ...

    # class ColorAnim(FSHU): # 4
    #     ...

    # class TextureSRTAnim(FSHU): # 5
    #     ...

    # class FTXP(): # 6
    #     # caFe TeXture Pattern animation
    #     def __init__(self, buffer, pos):
    #         self.header = self.Header(buffer, pos)

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FTXPHeader", buffer, pos)

    #     class MaterialPatternAnimation():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "MaterialPatternAnimation", buffer, pos)

    #     class PatternAnimationInfo():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "PatternAnimationInfo", buffer, pos)

    #     class Curve():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "CurveHeader", buffer, pos)
    #                 # xxxxxxxx xCCCKKFF
    #                 self.frame_data_flag: int = self.flags & 0b11
    #                 self.key_data_flag: int = (self.flags >> 2) & 0b11
    #                 self.curve_data_flag: int = (self.flags >> 4) & 0b111

    #         class Frames():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: float = float(buffer[pos:pos + 2]) / (1 << 5)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f">{count}B", buffer=buffer, offset=pos)

    #         class Keys():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}h', buffer=buffer, offset=pos)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}b', buffer=buffer, offset=pos)

    #         class StepCurves():
    #             # TODO
    #             ...

    #         class LinearCurves():
    #             # TODO
    #             ...

    # class FVIS(): # 7
    #     # caFe VISibility animation
    #     def __init__(self, buffer, pos):
    #         self.header = Header(buffer, pos)

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FVISHeader", buffer, pos)

    #     class Curve():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "CurveHeader", buffer, pos)
    #                 # xxxxxxxx xCCCKKFF
    #                 self.frame_data_flag: int = self.flags & 0b11
    #                 self.key_data_flag: int = (self.flags >> 2) & 0b11
    #                 self.curve_data_flag: int = (self.flags >> 4) & 0b111

    #         class Frames():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: float = float(buffer[pos:pos + 2]) / (1 << 5)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f">{count}B", buffer=buffer, offset=pos)

    #         class Keys():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}h', buffer=buffer, offset=pos)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}b', buffer=buffer, offset=pos)

    #         class StepCurves():
    #             # TODO
    #             ...

    #         class LinearCurves():
    #             # TODO
    #             ...

    # class MaterialVisAnim(FVIS): # 8
    #     ...

    # class FSHA(): # 9
    #     # caFe SHape Animation
    #     def __init__(self, buffer, pos):
    #         self.header = Header(buffer, pos)

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FSHAHeader", buffer, pos)
    #     class VertexShapeAnimation():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "VertexShapeAnimation", buffer, pos)

    #         class ShapeAnimationKey():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "ShapeAnimationKey", buffer, pos)
                    
    #     class Curve():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "CurveHeader", buffer, pos)
    #                 # xxxxxxxx xCCCKKFF
    #                 self.frame_data_flag: int = self.flags & 0b11
    #                 self.key_data_flag: int = (self.flags >> 2) & 0b11
    #                 self.curve_data_flag: int = (self.flags >> 4) & 0b111

    #         class Frames():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: float = float(buffer[pos:pos + 2]) / (1 << 5)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f">{count}B", buffer=buffer, offset=pos)

    #         class Keys():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}h', buffer=buffer, offset=pos)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}b', buffer=buffer, offset=pos)

    #         class StepCurves():
    #             # TODO
    #             ...

    #         class LinearCurves():
    #             # TODO
    #             ...

    # class FSCN(): # 10
    #     # caFe SCeNe animation
    #     def __init__(self, buffer, pos):
    #         self.header = Header(buffer, pos)

    #     class Header():
    #         def __init__(self, buffer, pos):
    #             get_unpacked_data(self, "FSCNHeader", buffer, pos)

    #     class FCAM():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FCAMHeader", buffer, pos)

    #         class Data():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "CameraAnimationData", buffer, pos)

    #     class FLIT():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FLITHeader", buffer, pos)

    #         class Data():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "LightAnimationData", buffer, pos)    
                    
    #     class FFOG():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FFOGHeader", buffer, pos)

    #         class Data():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "FogAnimationData", buffer, pos)

    #     class Curve():
    #         class Header():
    #             def __init__(self, buffer, pos):
    #                 get_unpacked_data(self, "CurveHeader", buffer, pos)
    #                 # xxxxxxxx xCCCKKFF
    #                 self.frame_data_flag: int = self.flags & 0b11
    #                 self.key_data_flag: int = (self.flags >> 2) & 0b11
    #                 self.curve_data_flag: int = (self.flags >> 4) & 0b111

    #         class Frames():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: float = float(buffer[pos:pos + 2]) / (1 << 5)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f">{count}B", buffer=buffer, offset=pos)

    #         class Keys():
    #             def __init__(self, buffer, data_flag, count, pos):
    #                 if data_flag == 0b00:
    #                     self.data: float = struct.unpack_from(fmt=f">{count}f", buffer=buffer, offset=pos)
    #                 elif data_flag == 0b01:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}h', buffer=buffer, offset=pos)
    #                 else:
    #                     self.data: int = struct.unpack_from(fmt=f'>{count}b', buffer=buffer, offset=pos)

    #         class StepCurves():
    #             # TODO
    #             ...

    #         class LinearCurves():
    #             # TODO
    #             ...

    # class EmbeddedFiles(): # 11
    #     def __init__(self, buffer, pos):
    #         get_unpacked_data(self, "EmbeddedFiles", buffer, pos)
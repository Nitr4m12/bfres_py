#!/usr/bin/env python

import struct

# A dict composed of each structure and their respective elements
structs_fmts = {
    "Header": {
        "magic":                ">4s",      # 0x00 - char[4]
        "version":              ">I",       # 0x04 - uInt
        "bom":                  ">H",       # 0x08 - uShort
        "length":               ">H",       # 0x0A - uShort
        "file_size":            ">I",       # 0x0C - uInt
        "file_align":           ">I",       # 0x10 - uInt
        "name_offset":          ">i",       # 0x14 - int
        "string_table_length":  ">i",       # 0x18 - int
        "string_table_offset":  ">i",       # 0x1C - int
        "dicts_offsets":        ">12i",     # 0x20 - int[12]
        "dicts_counts":         ">12H",     # 0x50 - uShort[12]
        "user_pointer":         ">I"        # 0x68 - uInt
    },

    "IndexGroup": {
        "length":               ">I",
        "count":                ">I" 
    },

    "IndexEntry": {
        "search_value":         ">i",       # 0x00 - int
        "left_index":           ">H",       # 0x04 - uShort
        "right_index":          ">H",       # 0x08 - uShort
        "name_offset":          ">I",       # 0x0C - uInt
        "data_offset":          ">i"        # 0x10 - int
    },

    "FMDLHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "file_name_offset":     ">i",       # 0x04 - int
        "file_path_offset":     ">i",       # 0x08 - int
        "fskl_offset":          ">i",       # 0x0C - int
        "fvtx_offset":          ">i",       # 0x10 - int
        "fshp_dict_offset":     ">i",       # 0x14 - int
        "fmat_dict_offset":     ">i",       # 0x18 - int
        "usr_data_dict_offset": ">i",       # 0x1C - int
        "fvtx_count":           ">H",       # 0x20 - uShort
        "fshp_count":           ">H",       # 0x22 - uShort
        "fmat_count":           ">H",       # 0x24 - uShort
        "user_data_count":      ">H",       # 0x26 - uShort
        "vertex_count":         ">I",       # 0x28 - uInt
        "user_pointer":         ">I"        # 0x2C - uInt
    },

    "FVTXHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "attrib_count":         ">B",       # 0x04 - byte
        "buffer_count":         ">B",       # 0x05 - byte
        "section_index":        ">H",       # 0x06 - uShort
        "vertex_count":         ">I",       # 0x08 - uInt
        "vertex_skin_count":    ">B3x",     # 0x0C - byte, padding[3]
        "attribs_offset":       ">i",       # 0x10 - int
        "attrib_dict_offset":   ">i",       # 0x14 - int
        "buffers_offset":       ">i",       # 0x18 - int
        "user_pointer":         ">I"        # 0x1C - uInt
    },

    "FVTXAttribute": {
        "attrib_name_offset":   ">i",       # 0x00 - int
        "buffer_index":         ">Bx",      # 0x04 - byte, padding
        "buffer_offset":        ">H",       # 0x06 - uShort
        "format":               ">I"        # 0x08 - uInt
    },

    "FVTXBuffer": {
        "data_pointer":         ">I",       # 0x00 - uInt
        "length":               ">I",       # 0x04 - uInt
        "handle":               ">I",       # 0x08 - uInt
        "stride":               ">H",       # 0x0C - uShort
        "buffering_count":      ">H",       # 0x0E - uShort
        "context_pointer":      ">I",       # 0x10 - uInt
        "data_offset":          ">i"        # 0x14 - int
    },

    "FSKLHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "flags":                ">I",       # 0x04 - uInt
        "bone_count":           ">H",       # 0x06 - uShort
        "smooth_index_count":   ">H",       # 0x08 - uShort
        "rigid_index_count":    ">H2x",     # 0x0C - uShort, padding[2]
        "bone_dict_offset":     ">i",       # 0x10 - int
        "bones_offset":         ">i",       # 0x14 - int
        "smooth_index_offset":  ">i",       # 0x18 - int
        "smooth_matrix_offset": ">i",       # 0x1C - int
        "user_pointer":         ">I"        # 0x20 - uInt
    },

    "Bone": {
        "name_offset":          ">i",       # 0x00 - int
        "bone_index":           ">H",       # 0x04 - uShort
        "parent_index":         ">H",       # 0x06 - uShort
        "smooth_matrix_index":  ">h",       # 0x08 - short
        "rigid_matrix_index":   ">h",       # 0x0A - short
        "billboard_index":      ">h",       # 0x0C - short
        "user_data_count":      ">H",       # 0x0E - uShort
        "flags":                ">I",       # 0x10 - uInt
        "scale_vector_x":       ">f",       # 0x14 - float
        "scale_vector_y":       ">f",       # 0x18 - float
        "scale_vector_z":       ">f",       # 0x1C - float
        "rotation_vector_x":    ">f",       # 0x20 - float
        "rotation_vector_y":    ">f",       # 0x24 - float
        "rotation_vector_z":    ">f",       # 0x28 - float
        "rotation_vector_w":    ">f",       # 0x2C - float
        "translation_vector_x": ">f",       # 0x30 - float
        "translation_vector_y": ">f",       # 0x34 - float
        "translation_vector_z": ">f",       # 0x38 - float
        "user_data_dict_offset":">i"        # 0x3C - int
    },

    "FSHPHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "poly_name_offset":     ">i",       # 0x04 - int
        "flags":                ">I",       # 0x08 - uInt
        "section_index":        ">H",       # 0x0C - uShort
        "fmat_index":           ">H",       # 0x0E - uShort
        "fskl_index":           ">H",       # 0x10 - uShort
        "fvtx_index":           ">H",       # 0x12 - uShort
        "fskl_bone_skin_index": ">H",       # 0x14 - uShort
        "vertex_skin_count":    ">B",       # 0x16 - byte
        "lod_mdl_count":        ">B",       # 0x17 - byte
        "key_shp_count":        ">B",       # 0x18 - byte
        "target_attrib_count":  ">B",       # 0x19 - byte
        "vis_tree_node_count":  ">H",       # 0x1A - uShort
        "bounding_box_radius":  ">f",       # 0x1C - float
        "fvtx_offset":          ">i",       # 0x20 - int
        "lod_mdls_offset":      ">i",       # 0x24 - int
        "fskl_indexs_offset":   ">i",       # 0x28 - int
        "key_shp_dict":         ">i",       # 0x2C - int
        "vis_tree_ranges_offset":">i",      # 0x30 - int
        "user_pointer":         ">I"        # 0x34 - uInt
    },

    "LoDModel": {
        "primitive_type":       ">I",       # 0x00 - uInt
        "index_format":         ">I",       # 0x04 - uInt
        "point_count":          ">I",       # 0x08 - uInt
        "vis_group_count":      ">H2x",     # 0x0C - uShort, padding[2]
        "vis_group_offset":     ">i",       # 0x10 - int
        "index_buffer_offset":  ">i",       # 0x14 - int
        "vertex_skip_count":    ">I"        # 0x18 - uInt
    },

    "VisibilityGroup": {
        "index_buffer_offset":  ">I",       # 0x00 - uInt
        "count":                ">I"        # 0x04 - uInt
    },

    "FMATHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "mat_name_offset":      ">i",       # 0x04 - int
        "mat_flags":            ">I",       # 0x08 - uInt
        "section_index":        ">H",       # 0x0C - uShort
        "render_info_count":    ">H",       # 0x0E - uShort
        "tex_ref_count":        ">B",       # 0x10 - byte
        "tex_sampler_count":    ">B",       # 0x11 - byte
        "mat_param_count":      ">H",       # 0x12 - uShort
        "volatile_param_count": ">H",       # 0x14 - uShort
        "mat_param_data_length":">H",       # 0x16 - uShort
        "raw_param_data_length":">H",       # 0x18 - uShort
        "usr_data_entry_count": ">H",       # 0x1A - uShort
        "render_info_dict_offset":">i",     # 0x1C - int
        "render_state_offset":  ">i",       # 0x20 - int
        "shdr_assign_offset":   ">i",       # 0x24 - int
        "tex_refs_offset":      ">i",       # 0x28 - int
        "tex_samplers_offset":  ">i",       # 0x2C - int
        "tex_sampler_dict_offset":">i",     # 0x30 - int
        "mat_params_offset":    ">i",       # 0x34 - int
        "mat_param_dict_offset":">i",       # 0x38 - int
        "mat_param_data_offset":">i",       # 0x3C - int
        "usr_data_dict_offset": ">i",       # 0x40 - int
        "volatile_flags_offset":">i",       # 0x44 - int
        "user_pointer":         ">i"        # 0x48 - int
    },

    "RenderInfo": {
        "array_length":         ">H",       # 0x00 - uShort
        "element_type":         ">Bx",      # 0x02 - byte, padding
        "variable_name_offset": ">i"        # 0x04 - int
    },

    "TextureSampler": {
        "GX2Sampler_struct1":   ">I",       # 0x00 - uInt
        "GX2Sampler_struct2":   ">I",       # 0x04 - uInt
        "GX2Sampler_struct3":   ">I",       # 0x08 - uInt
        "handle":               ">I",       # 0x0C - uInt
        "attrib_name_offset":   ">i",       # 0x10 - int
        "element_index":        ">B3x"      # 0x14 - byte, padding[3]
    },

    "MaterialParameter": {
        "type_":                ">B",       # 0x00 - byte
        "length":               ">B",       # 0x01 - byte
        "mat_param_data_offset":">H",       # 0x02 - uShort
        "uniform_var_offset":   ">i",       # 0x04 - int
        "conversion_callback_ptr":">I",     # 0x08 - uInt
        "mat_param_index":      ">H",       # 0x0C - uShort
        "mat_param_index_copy": ">H",       # 0x0E - uShort 
        "variable_name_offset": ">i"        # 0x10 - int 
    },

    "RenderState": {
        "flags":                ">I",       # 0x00 - uInt
        "poly_ctrl":            ">I",       # 0x04 - uInt
        "depth_ctrl":           ">I",       # 0x08 - uInt
        "alpha_test1":          ">I",       # 0x0C - uInt
        "alpha_test2":          ">f",       # 0x10 - float
        "color_ctrl":           ">I",       # 0x14 - uInt
        "blend_ctrl1":          ">I",       # 0x18 - uInt
        "blend_ctrl2":          ">I",       # 0x1C - uInt
        "blend_color_r":        ">f",       # 0x20 - float
        "blend_color_g":        ">f",       # 0x24 - float
        "blend_color_b":        ">f",       # 0x28 - float
        "blend_color_a":        ">f"        # 0x2C - float
    },

    "ShaderAssign": {
        "shader_archive_name_offset":       ">i",       # 0x00 - int
        "shading_mdl_name_offset":          ">i",       # 0x04 - int
        "revision":                         ">I",       # 0x08 - uInt
        "vtx_shader_input_count":           ">B",       # 0x0C - byte
        "fragment_shader_input_count":      ">B",       # 0x0D - byte
        "param_count":                      ">H",       # 0x0E - uShort
        "vtx_shader":                       ">i",       # 0x10 - int
        "fragment_shader_input_dict_offset":">i",       # 0x14 - int
        "param_dict_offset":                ">i"        # 0x18 - int
    },

    "FTEXHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "dimension":            ">I",       # 0x04 - uInt
        "width":                ">I",       # 0x08 - uInt
        "height":               ">I",       # 0x0C - uInt
        "depth":                ">I",       # 0x10 - uInt
        "mipmap_count":         ">I",       # 0x14 - uInt
        "format":               ">I",       # 0x18 - uInt
        "aa_mode":              ">I",       # 0x1C - uInt
        "usage":                ">I",       # 0x20 - uInt
        "data_length":          ">I",       # 0x24 - uInt
        "data_pointer":         ">I",       # 0x28 - uInt
        "mipmaps_data_length":  ">I",       # 0x2C - uInt
        "mipmaps_pointer":      ">I",       # 0x30 - uInt
        "tile_mode":            ">I",       # 0x34 - uInt
        "swizzle_value":        ">I",       # 0x38 - uInt
        "alignment":            ">I",       # 0x3C - uInt
        "pitch":                ">I",       # 0x40 - uInt
        "mipmaps_offsets":      ">13I",     # 0x44 - uInt[13]
        "first_mipmap":         ">I",       # 0x78 - uInt
        "mipmap_count_copy":    ">I",       # 0x7C - uInt
        "first_slice":          ">I",       # 0x80 - uInt
        "slice_count":          ">I",       # 0x84 - uInt
        "component_selector":   ">4B",      # 0x88 - byte[4]
        "texture_registers":    ">5I",      # 0x8C - uInt[5]
        "texture_handle":       ">I",       # 0xA0 - uInt
        "array_length":         ">B 3x",    # 0xA4 - byte, padding[3]
        "file_name_offset":     ">i",       # 0xA8 - int
        "file_path_offset":     ">i",       # 0xAC - int
        "data_offset":          ">i",       # 0xB0 - int
        "mipmap_data_offset":   ">i",       # 0xB4 - int
        "user_data_dict_offset":">i",       # 0xB8 - int
        "user_data_entry_count":">H 2x",    # 0xBC - uShort, padding[2]
    },

    "FSKAHeader": {
        "magic":                ">4s",      # 0x00 - char[4]
        "file_name_offset":     ">i",       # 0x04 - int
        "file_path_offset":     ">i",       # 0x08 - int
        "flags":                ">I",       # 0x0C - uInt
        "frame_count":          ">I",       # 0x10 - uInt
        "bone_animation_count": ">H",       # 0x14 - uShort
        "user_data_entry_count":">H",       # 0x16 - uShort
        "curve_count":          ">I",       # 0x18 - uInt
        "baked_length":         ">I",       # 0x1C - uInt
        "bone_animation_offset":">i",       # 0x20 - int
        "skeleton_offset":      ">i",       # 0x24 - int
        "bind_index_array":     ">i",       # 0x28 - int
        "user_data_index_group":">i"        # 0x2C - int
    },

    "BoneAnimation": {
        "flags":                     ">I",      # 0x00 - uInt 
        "bone_name":                 ">I",      # 0x04 - uInt
        "start_rotation":            ">B",      # 0x08 - byte
        "start_translation":         ">B",      # 0x09 - byte
        "curve_count":               ">B",      # 0x0A - byte
        "base_data_translate_offset":">B",      # 0x0B - byte
        "start_curve_index":         ">B 3x",   # 0x0C - byte, padding[3]   
        "curves_offset":             ">i",      # 0x10 - int
        "base_data_offset":          ">i"       # 0x14 - int
    },

    "FSHUHeader": {
        "magic":                            ">4s",      # 0x00
        "file_name_offset":                 ">i",       # 0x04
        "file_path_offset":                 ">i",       # 0x08
        "flags":                            ">I",       # 0x0C
        "frame_count":                      ">i",       # 0x10
        "material_animation_count":         ">H",       # 0x14
        "user_data_entry_count":            ">H",       # 0x16
        "parameter_animation_info_count":   ">i",       # 0x18
        "curve_count":                      ">I",       # 0x1C
        "baked_length":                     ">I",       # 0x20
        "model_offset":                     ">i",       # 0x24
        "bind_index_offset":                ">i",       # 0x28
        "material_animation_offset":        ">i",       # 0x2C
        "user_data_dict_offset":            ">i"        # 0x30
    },

    "MaterialAnimation": {
        "parameter_animation_info_count":          ">H",        # 0x00 - uShort
        "curve_count":                             ">H",        # 0x02 - uShort
        "animation_constant_count":                ">H 2x",     # 0x04 - uShort, padding[2]
        "start_curve_index":                       ">i",        # 0x08 - int
        "start_parameter_animation_info_index":    ">i",        # 0x0C - int
        "animation_name_offset":                   ">i",        # 0x10 - int
        "parameter_animation_info_offset":         ">i",        # 0x14 - int
        "curves_offset":                           ">i",        # 0x18 - int
        "animation_constant_offset":               ">i"         # 0x1C - int
    },

    "ParameterAnimationInfo": {
        "start_curve_index":                ">H",   # 0x00 - uShort
        "float_curve_count":                ">H",   # 0x02 - uShort
        "int_curve_count":                  ">H",   # 0x04 - uShort
        "start_animation_constant_index":   ">H",   # 0x06 - uShort
        "animation_constant_count":         ">H",   # 0x08 - uShort
        "sub_bind_index":                   ">H",   # 0x0A - uShort
        "name_offset":                      ">i"    # 0x0C - int
    },

    "AnimationConstant": {
        "anim_data_offset":                 ">I",   # 0x00 - uInt  
        "value":                            ">i"    # 0x04 - int
    },

    "FTXPHeader": {
        "magic":                  ">4s",        # 0x00 - char[4]
        "file_name_offset":       ">i",         # 0x04 - int
        "file_path_offset":       ">i",         # 0x08 - int
        "flags":                  ">H",         # 0x0C - uShort
        "usr_data_entry_count":   ">H",         # 0x0E - uShort
        "frame_count":            ">i",         # 0x10 - int
        "tex_ref_count":          ">H",         # 0x14 - uShort
        "mat_pattern_anim_count": ">H",         # 0x16 - uShort
        "pattern_anim_info_count":">I",         # 0x18 - uInt
        "curve_count":            ">I",         # 0x1C - uInt
        "baked_length":           ">I",         # 0x20 - uInt
        "mdl_offset":             ">i",         # 0x24 - int
        "bind_index_offset":      ">i",         # 0x28 - int
        "mat_pattern_anim_offset":">i",         # 0x2C - int
        "tex_ref_index_gr_offset":">i",         # 0x30 - int
        "usr_data_indexg_offset": ">i"          # 0x34 - int
    },

    "MaterialPatternAnimation": {
        "pattern_anim_info_count":          ">H",     # 0x00 - uShort
        "curve_count":                      ">H",     # 0x02 - uShort
        "start_curve_index":                ">i",     # 0x04 - int
        "start_pattern_anim_info_index":    ">i",     # 0x08 - int
        "anim_name_offset":                 ">i",     # 0x0C - int
        "pattern_anim_info_array_offset":   ">i",     # 0x10 - int
        "curve_array_offset":               ">i",     # 0x14 - int
        "base_value_array_offset":          ">i",     # 0x18 - int
    },

    "PatternAnimationInfo": {
        "curve_index":           ">b",       # 0x00 - Sbyte
        "sub_bind_index":        ">b 2x",    # 0x01 - Sbyte, padding[2]
        "name_offset":           ">i"        # 0x04 - int
    },

    "FVISHeader": {
        "magic":                 ">4s",      # 0x00 - char[4]
        "file_name_offset":      ">i",       # 0x04 - int
        "file_path_offset":      ">i",       # 0x08 - int
        "flags":                 ">H",       # 0x0C - uShort
        "user_data_entry_count": ">H",       # 0x0E - uShort
        "frame_count":           ">i",       # 0x10 - int
        "animation_count":       ">H",       # 0x14 - uShort
        "curve_count":           ">H",       # 0x16 - uShort
        "baked_length":          ">I",       # 0x18 - uInt
        "model_offset":          ">i",       # 0x1C - int
        "bind_index_offset":     ">i",       # 0x20 - int
        "names_offset":          ">i",       # 0x24 - int
        "curves_offset":         ">i",       # 0x28 - int
        "base_values_offset":    ">i",       # 0x2C - int
        "user_data_dict_offset": ">i"        # 0x30 - int
    },

    "FSHAHeader": {
        "magic":                          ">4s",    # 0x00 - char[4]
        "file_name":                      ">i",     # 0x04 - int
        "file_path":                      ">i",     # 0x08 - int
        "flags":                          ">H",     # 0x0C - uShort
        "user_data_entry_count":          ">H",     # 0x0E - uShort
        "frame_count":                    ">i",     # 0x10 - int
        "vertex_shape_animation_count":   ">H",     # 0x14 - uShort
        "shape_animation_key_count":      ">H",     # 0x16 - uShort
        "curve_count":                    ">H 2x",  # 0x18 - uShort, padding[2]
        "baked_length":                   ">I",     # 0x1C - uInt
        "model_offset":                   ">i",     # 0x20 - int
        "bind_indexs_offset":             ">i",     # 0x24 - int
        "vertex_shape_animations_offset": ">i",     # 0x28 - int
        "user_data_index_group":          ">i"      # 0x2C - int
    },

    "VertexShapeAnimation": {
        "curve_count":                      ">H",   # 0x00 - uShort
        "shape_animation_key_count":        ">H",   # 0x02 - uShort
        "start_curve_index":                ">i",   # 0x04 - int
        "start_shape_animation_key_index":  ">i",   # 0x08 - int
        "name_offset":                      ">i 8x",# 0x0C - int, padding[8]
        "shape_animation_keys_offset":      ">i",   # 0x14 - int
        "curves_offset":                    ">i",   # 0x18 - int 
        "bone_transformation_data_offset":  ">i"    # 0x1C - int
    },

    "ShapeAnimationKey": {
        "curve_index":          ">b",       # 0x01 - Sbyte
        "sub_bind_index":       ">b 2x",    # 0x02 - Sbyte, padding[2]
        "name_offset":          ">i"        # 0x04 - int
    },

    "FSCNHeader": {
        "magic":                     ">4s",     # 0x00 - char[4]
        "file_name_offset":          ">i",      # 0x04 - int
        "file_path_offset":          ">i",      # 0x08 - int
        "user_data_entry_count":     ">H",      # 0x0C - uShort
        "camera_anim_count":         ">H",      # 0x0E - uShort
        "light_anim_count":          ">H",      # 0x10 - uShort
        "fog_anim_count":            ">H",      # 0x12 - uShort
        "camera_anim_dict_offset":   ">i",      # 0x14 - int
        "light_anim_dict_offset":    ">i",      # 0x18 - int
        "fog_anim_dict_offset":      ">i",      # 0x1C - int
        "user_data_dict_offset":     ">i"       # 0x20 - int
    },

    "FCAMHeader": {
        "magic":                                ">4s",      # 0x00 - char[4]
        "flags":                                ">H 2x",    # 0x04 - uShort, padding[2]
        "frame_count":                          ">i",       # 0x08 - int
        "curve_count":                          ">B x",     # 0x0C - byte, padding
        "user_data_entry_count":                ">H",       # 0x0E - uShort
        "baked_length":                         ">I",       # 0x10 - uInt
        "name_offset":                          ">i",       # 0x14 - int
        "curves_offset":                        ">i",       # 0x18 - int
        "base_cam_anim_data_offset":            ">i",       # 0x1C - int
        "user_data_index_group_offset":         ">i"        # 0x20 - int
    },

    "CameraAnimationData": {
        "near_clipping_plaen_distance":     ">f",       # 0x00 - float
        "far_clipping_plane_distance":      ">f",       # 0x04 - float
        "aspect_ratio":                     ">f",       # 0x08 - float
        "height_offset":                    ">f",       # 0x0C - float
        "position":                         ">3f",      # 0x10 - float[3]
        "rotation":                         ">3f",      # 0x1C - float[3]
        "twist":                            ">f"        # 0x28 - float
    },

    "FLITHeader": {
        "magic":                                          ">4s",    # 0x00 - char[4]
        "flags":                                          ">H",     # 0x04 - uShort
        "user_data_entry_count":                          ">H",     # 0x06 - uShort
        "frame_count":                                    ">i",     # 0x08 - int
        "curve_count":                                    ">B",     # 0x0C - byte
        "light_type":                                     ">b",     # 0x0D - Sbyte
        "distance_attenuation_function_index":            ">b",     # 0x0E - Sbyte
        "angle_attenuation_function_index":               ">b",     # 0x0F - Sbyte
        "baked_length":                                   ">I",     # 0x10 - uInt
        "name_offset":                                    ">i",     # 0x14 - int
        "light_type_name_offset":                         ">i",     # 0x18 - int
        "distance_attenuation_function_name_offset":      ">i",     # 0x1C - int
        "angle_attenuation_function_name_offset":         ">i",     # 0x20 - int
        "curves_offset":                                  ">i",     # 0x24 - int
        "base_light_animation_data_offset":               ">i",     # 0x28 - int
        "user_data_dict_offset":                          ">i"      # 0x2C - int
    },

    "LightAnimationData": {
        "on_off":                 ">i",     # 0x00 - int
        "position":               ">3f",    # 0x04 - float[3]
        "rotation":               ">3f",    # 0x10 - float[3]
        "distance_attenuation":   ">2f",    # 0x1C - float[2]
        "angle_attenuation":      ">2f",    # 0x24 - float[2]
        "first_color":            ">3f",    # 0x2C - float[3]
        "second_color":           ">3f"     # 0x38 - float[3]
    },

    "FFOGHeader": {
        "magic":                                      ">4s",        # 0x00 - char[4]
        "flags":                                      ">H 2x",      # 0x04 - uShort, padding[2]
        "frame_count":                                ">i",         # 0x08 - int
        "curve_count":                                ">B",         # 0x0C - byte
        "distance_attenuation_function_index":        ">B",         # 0x0D - byte
        "user_data_entry_count":                      ">H",         # 0x0E - uShort
        "baked_length":                               ">I",         # 0x10 - uInt
        "name_offset":                                ">i 12x",     # 0x14 - int, padding[12]
        "distance_attenuation_function_name_offset":  ">i",         # 0x18 - int
        "curves_offset":                              ">i",         # 0x24 - int
        "base_fog_animation_data_offset":             ">i",         # 0x28 - int
        "user_data_dict_offset":                      ">i"          # 0x2C - int
    },

    "FogAnimationData": {
        "distance_attenuation":    ">2f",
        "color":                   ">3f"
    },

    "CurveHeader": {
        "flags":                ">H",       # 0x00 - uShort
        "key_count":            ">H",       # 0x02 - uShort
        "anim_data_offset":     ">I",       # 0x04 - uInt
        "start_frame":          ">f",       # 0x08 - float
        "end_frame":            ">f",       # 0x0C - float
        "scale":                ">f",       # 0x10 - float
        "offset":               ">f",       # 0x14 - float
        "delta":                ">f",       # 0x18 - float
        "frames":               ">i",       # 0x1C - int
        "keys":                 ">i"        # 0x20 - int
    },

    "EmbeddedFiles": {
        "offset":               ">i",       # 0x00 - int
        "length":               ">I"        # 0x04 - uInt
    }

}
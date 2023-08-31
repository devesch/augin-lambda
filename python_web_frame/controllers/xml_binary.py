import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import array
import tracemalloc
import threading
import subprocess
import platform
import numpy as np
from os import path
from time import process_time


tracemalloc.start()

prop_tracker = 0

category_dict_array = []
value_dict_array = []
guid_dict_array = []
tag_dict_array = []

category_dict = {}
value_dict = {}
guid_dict = {}
tag_dict = {}

# Index Arrays
tags = np.full(500000, 999999999, dtype=np.compat.long)
tags_index = 0
tags_max = 0
tags_mini = np.full(500000, 999999999, dtype=np.compat.long)
tags_mini_index = 0
tags_mini_max = 0
tags_mini_types_sections = np.full(500000, 999999999, dtype=np.compat.long)
tags_mini_types_s_index = 0
tags_mini_types_s_max = 0
tags_mini_types_unique = np.full(500000, 999999999, dtype=np.compat.long)
tags_mini_types_index = 0
tags_mini_types_max = 0
tags_mini_elements_sections = np.full(500000, 999999999, dtype=np.compat.long)
tags_mini_elements_s_index = 0
tags_mini_elements_s_max = 0
tags_mini_elements_unique = np.full(500000, 999999999, dtype=np.compat.long)
tags_mini_elements_index = 0
tags_mini_elements_max = 0
units = np.full(500, 999999999, dtype=np.compat.long)
units_index = 0
units_max = 0
property_sets = np.full(300000, 999999999, dtype=np.compat.long)
property_sets_index = 0
property_set_max = 0
single_values = np.full(723433 * 4, 999999999, dtype=np.compat.long)
single_values_index = 0
single_values_max = 0
quantities = np.full(20000, 999999999, dtype=np.compat.long)
quantities_index = 0
quantities_max = 0
quantity_properties = np.full(10000, 999999999, dtype=np.compat.long)
quantity_properties_index = 0
quantity_children = np.full(20000, 999999999, dtype=np.compat.long)
quantity_children_index = 0
quantity_property_max = 0
ifc_types = np.full(10000, 999999999, dtype=np.compat.long)
ifc_types_index = 0
ifc_types_max = 0
ifc_property_links = np.full(10000, 999999999, dtype=np.compat.long)
ifc_property_links_index = 0
ifc_property_link_max = 0
layers = np.full(1000, 999999999, dtype=np.compat.long)
layers_index = 0
layers_max = 0
materials = np.full(400, 999999999, dtype=np.compat.long)
materials_index = 0
materials_max = 0
ifc_materials = np.full(200000, 999999999, dtype=np.compat.long)
ifc_materials_index = 0
ifc_materials_max = 0
projects = np.full(300000, 999999999, dtype=np.compat.long)
projects_index = 0
projects_max = 0
sites = np.full(300000, 999999999, dtype=np.compat.long)
sites_index = 0
sites_max = 0
site_property_set = np.full(300000, 999999999, dtype=np.compat.long)
site_property_set_index = 0
site_property_max = 0
buildings = np.full(300000, 999999999, dtype=np.compat.long)
buildings_index = 0
buildings_max = 0
buildings_property_set = np.full(100, 999999999, dtype=np.compat.long)
buildings_property_set_index = 0
building_property_max = 0
elements_property_set = np.full(100, 999999999, dtype=np.compat.long)
elements_property_set_index = 0
element_property_max = 0
nested_property_set = np.full(100, 999999999, dtype=np.compat.long)
nested_property_set_index = 0
nested_set_max = 0
nested_set_two = np.full(100, 999999999, dtype=np.compat.long)
nested_set_two_index = 0
nested_set_two_max = 0
nested_set_three = np.full(100, 999999999, dtype=np.compat.long)
nested_set_three_index = 0
nested_set_three_max = 0
storeys = np.full(100, 999999999, dtype=np.compat.long)
storeys_index = 0
storeys_max = 0
ifc_elements = np.full(200000, 999999999, dtype=np.compat.long)
ifc_elements_index = 0
ifc_elements_max = 0
nested_elements = np.full(200000, 999999999, dtype=np.compat.long)
nested_elements_index = 0
nested_max = 0
nested_two = np.full(200000, 999999999, dtype=np.compat.long)
nested_two_index = 0
nested_two_max = 0
nested_three = np.full(200000, 999999999, dtype=np.compat.long)
nested_three_index = 0
nested_three_max = 0

tags_groups = np.full(500000, 999999999, dtype=np.compat.long)
tags_groups_index = 0
tags_groups_max = 0

storey_groups = np.full(200000, 999999999, dtype=np.compat.long)
storey_groups_index = 0
storey_groups_max = 0

building_groups = np.full(200000, 999999999, dtype=np.compat.long)
building_groups_index = 0
building_groups_max = 0


def append_no_duplicates(array_to_append, dictionary, new_item):
    if new_item in dictionary:
        return array_to_append, dictionary, dictionary[new_item]  # list(array_to_append).index(new_item)
    else:
        array_to_append.append(new_item)
        dictionary[new_item] = len(array_to_append) - 1
    return array_to_append, dictionary, len(array_to_append) - 1


def append_cat_val(index_array, index_index, app_item, lock, val_len):
    lock.acquire()
    global category_dict_array, value_dict_array, category_dict, value_dict

    category_dict_array, category_dict, pos_c = append_no_duplicates(category_dict_array, category_dict, app_item[0])
    val_len = val_len + 1
    value_dict_array, value_dict, pos_v = append_no_duplicates(value_dict_array, value_dict, app_item[1])
    if len(index_array) < index_index + 10:
        index_array = np.append(index_array, np.full(200000, 999999999, dtype=np.compat.long))
    index_array[index_index] = pos_c
    index_index = index_index + 1
    index_array[index_index] = pos_v
    index_index = index_index + 1
    lock.release()
    return index_array, index_index, val_len


def append_group_element(index_array, index_index, app_item):
    global category_dict_array, guid_dict_array, category_dict, guid_dict

    category_dict_array, category_dict, pos_cat = append_no_duplicates(category_dict_array, category_dict, app_item[0])
    guid_dict_array, guid_dict, pos_guid = append_no_duplicates(guid_dict_array, guid_dict, app_item[1])
    if len(index_array) < index_index + 10:
        index_array = np.append(index_array, np.full(200000, 999999999, dtype=np.compat.long))
    index_array[index_index] = pos_cat
    index_index = index_index + 1
    index_array[index_index] = pos_guid
    index_index = index_index + 1

    return index_array, index_index


def append_with_guid(index_array, index_index, app_item, lock, val_len):
    lock.acquire()
    global category_dict_array, value_dict_array, guid_dict_array, category_dict, value_dict, guid_dict

    category_dict_array, category_dict, pos_cat = append_no_duplicates(category_dict_array, category_dict, app_item[0])
    val_len = val_len + 1
    if len(index_array) < index_index + 10:
        index_array = np.append(index_array, np.full(200000, 999999999, dtype=np.compat.long))
    index_array[index_index] = pos_cat
    index_index = index_index + 1
    if app_item[0] == "id":
        val_len = val_len - 1
        guid_dict_array, guid_dict, pos_id = append_no_duplicates(guid_dict_array, guid_dict, app_item[1])
        index_array[index_index] = pos_id
        index_index = index_index + 1
    else:
        value_dict_array, value_dict, pos_val = append_no_duplicates(value_dict_array, value_dict, app_item[1])
        index_array[index_index] = pos_val
        index_index = index_index + 1
    lock.release()
    return index_array, index_index, val_len


def append_with_index(index_array, index_index, idx1, idx2, app_item, lock, val_len):
    lock.acquire()
    global category_dict_array, value_dict_array, category_dict, value_dict

    category_dict_array, category_dict, pos_cat = append_no_duplicates(category_dict_array, category_dict, app_item[0])
    val_len = val_len + 1
    if len(index_array) < index_index + 10:
        index_array = np.append(index_array, np.full(200000, 999999999, dtype=np.compat.long))

    index_array[index_index] = idx1
    index_index = index_index + 1
    index_array[index_index] = idx2
    index_index = index_index + 1
    index_array[index_index] = pos_cat
    index_index = index_index + 1
    value_dict_array, value_dict, pos_val = append_no_duplicates(value_dict_array, value_dict, app_item[1])
    index_array[index_index] = pos_val
    index_index = index_index + 1
    lock.release()
    return index_array, index_index, val_len


def append_with_link(index_array, index_index, idx1, idx2, app_item, lock, val_len):
    lock.acquire()
    global category_dict_array, guid_dict_array, category_dict, guid_dict

    category_dict_array, category_dict, pos_cat = append_no_duplicates(category_dict_array, category_dict, app_item[0])
    val_len = val_len + 1
    guid_dict_array, guid_dict, pos_id = append_no_duplicates(guid_dict_array, guid_dict, app_item[1][1:])
    val_len = val_len - 1
    if len(index_array) < index_index + 10:
        index_array = np.append(index_array, np.full(200000, 999999999, dtype=np.compat.long))
    index_array[index_index] = idx1
    index_index = index_index + 1
    index_array[index_index] = idx2
    index_index = index_index + 1
    index_array[index_index] = pos_cat
    index_index = index_index + 1
    index_array[index_index] = pos_id
    index_index = index_index + 1
    lock.release()

    return index_array, index_index, val_len


def append_layer_link(index_array, index_index, link_array, link_array_index, app_item, s, i, val_len, link_state):
    global category_dict_array, value_dict_array, guid_dict_array, category_dict, value_dict, guid_dict

    category_dict_array, category_dict, pos_cat = append_no_duplicates(category_dict_array, category_dict, app_item[0])
    val_len = val_len + 1
    if app_item[1][0:1] != "#":
        link_state = True
        if len(index_array) < index_index + 10:
            index_array = np.append(index_array, np.full(200000, 999999999, dtype=np.compat.long))
        index_array[index_index] = s
        index_index = index_index + 1
        index_array[index_index] = i
        index_index = index_index + 1
        index_array[index_index] = pos_cat
        index_index = index_index + 1
        if app_item[0] == "id":
            val_len = val_len - 1
            guid_dict_array, guid_dict, pos_id = append_no_duplicates(guid_dict_array, guid_dict, app_item[1])
            index_array[index_index] = pos_id
            index_index = index_index + 1
        else:
            value_dict_array, value_dict, pos_val = append_no_duplicates(value_dict_array, value_dict, app_item[1])
            index_array[index_index] = pos_val
            index_index = index_index + 1
    else:
        link_state = False
        if len(link_array) < link_array_index + 10:
            link_array = np.append(link_array, np.full(200000, 999999999, dtype=np.compat.long))
        guid_dict_array, guid_dict, pos_id = append_no_duplicates(guid_dict_array, guid_dict, app_item[1][1:])
        val_len = val_len - 1
        link_array[link_array_index] = s
        link_array_index = link_array_index + 1
        link_array[link_array_index] = i
        link_array_index = link_array_index + 1
        link_array[link_array_index] = pos_cat
        link_array_index = link_array_index + 1
        link_array[link_array_index] = pos_id
        link_array_index = link_array_index + 1
    return index_array, index_index, link_array, link_array_index, val_len, link_state


def append_sizes(dict_array, target_file):
    write_length(len(dict_array), target_file)
    sizes = []
    for siz in dict_array:
        sizes.append(len(siz))
    return sizes


def append_tag(tag_item, tag_lock, tag_loc, val_len):
    global tag_dict_array, tag_dict, tags_index, tags
    tag_lock.acquire()
    tag_dict_array, tag_dict, pos_tag = append_no_duplicates(tag_dict_array, tag_dict, tag_item)
    if len(tags) < tags_index + 10:
        tags = np.append(tags, np.full(200000, 999999999, dtype=np.compat.long))
    tags[tags_index] = tag_loc
    tags_index = tags_index + 1
    tags[tags_index] = pos_tag
    tags_index = tags_index + 1
    tags[tags_index] = val_len
    tags_index = tags_index + 1
    tag_lock.release()


def append_tag_mini(tag_item, tag_lock, tag_loc, val_len):
    global tag_dict_array, tag_dict, tags_mini_index, tags_mini
    tag_lock.acquire()
    tag_dict_array, tag_dict, pos_tag = append_no_duplicates(tag_dict_array, tag_dict, tag_item)
    if len(tags_mini) < tags_mini_index + 10:
        tags_mini = np.append(tags_mini, np.full(200000, 999999999, dtype=np.compat.long))
    tags_mini[tags_mini_index] = tag_loc
    tags_mini_index = tags_mini_index + 1
    tags_mini[tags_mini_index] = pos_tag
    tags_mini_index = tags_mini_index + 1
    tags_mini[tags_mini_index] = val_len
    tags_mini_index = tags_mini_index + 1
    tag_lock.release()


def append_tag_group(tag_item, tag_lock, tag_loc, group_len, item_type):
    global tag_dict_array, tag_dict, tags_groups_index, tags_groups
    tag_lock.acquire()
    tag_dict_array, tag_dict, pos_tag = append_no_duplicates(tag_dict_array, tag_dict, tag_item)
    if len(tags_groups) < tags_groups_index + 10:
        tags_groups = np.append(tags_groups, np.full(200000, 999999999, dtype=np.compat.long))
    tags_groups[tags_groups_index] = tag_loc
    tags_groups_index = tags_groups_index + 1
    tags_groups[tags_groups_index] = pos_tag
    tags_groups_index = tags_groups_index + 1
    if item_type:
        tags_groups[tags_groups_index] = group_len
        tags_groups_index = tags_groups_index + 1
    else:
        tags_groups[tags_groups_index] = 0
        tags_groups_index = tags_groups_index + 1
        group_len = group_len + 1
    tag_lock.release()
    return group_len


def append_tag_unique(uniq_item, uniq_lock, uniq_loc):
    global tag_dict_array, tag_dict, tags_mini_elements_index, tags_mini_types_index, tags_mini_elements_unique, tags_mini_types_unique, tags_mini_elements_s_index, tags_mini_elements_sections, tags_mini_types_s_index, tags_mini_types_sections
    uniq_lock.acquire()
    tag_dict_array, tag_dict, pos_tag = append_no_duplicates(tag_dict_array, tag_dict, uniq_item)
    if uniq_loc > 10:
        if pos_tag not in tags_mini_elements_unique:
            if len(tags_mini_elements_unique) < tags_mini_elements_index + 10:
                tags_mini_elements_unique = np.append(tags_mini_elements_unique, np.full(200000, 999999999, dtype=np.compat.long))
            tags_mini_elements_sections[tags_mini_elements_s_index] = uniq_loc
            tags_mini_elements_s_index = tags_mini_elements_s_index + 1
            tags_mini_elements_unique[tags_mini_elements_index] = pos_tag
            tags_mini_elements_index = tags_mini_elements_index + 1
    else:
        if pos_tag not in tags_mini_types_unique:
            if len(tags_mini_types_unique) < tags_mini_types_index + 10:
                tags_mini_types_unique = np.append(tags_mini_types_unique, np.full(200000, 999999999, dtype=np.compat.long))
            # try:
            tags_mini_types_sections[tags_mini_types_s_index] = uniq_loc
            # except:
            #     print("Saindo no exit")
            #     exit()
            tags_mini_types_s_index = tags_mini_types_s_index + 1
            tags_mini_types_unique[tags_mini_types_index] = pos_tag
            tags_mini_types_index = tags_mini_types_index + 1

    uniq_lock.release()


def write_unique(uniq_loc, uniq_tag, target_file, bit_max):
    target_idx = []
    for i, idx in enumerate(uniq_loc):
        target_idx.append(idx)
        target_idx.append(uniq_tag[i])

    if bit_max == 1 or bit_max == 0:
        l_bytes = array.array("H", target_idx)
    elif bit_max == 2:
        l_bytes = array.array("H", target_idx)
    else:
        l_bytes = array.array("L", target_idx)
    l_bytes.tofile(target_file)


def write_length(len, target_file):
    lengths = array.array("I", [len])
    lengths.tofile(target_file)


def write_index(target_idx, target_file, bit_max):
    # for index in target_idx:
    # if len(target_idx) > 0:
    # print(" target_idx max:" + str(max(target_idx)))
    system = platform.system()
    if bit_max == 1 or bit_max == 0:
        h_bytes = array.array("H", target_idx)
    elif bit_max == 2:
        h_bytes = array.array("H", target_idx)
    else:
        if system == "Linux":
            h_bytes = array.array("I", target_idx)
        else:
            h_bytes = array.array("L", target_idx)
    h_bytes.tofile(target_file)


def write_index_max(target_idx, target_file):
    if len(target_idx) > 0:
        idx_max = max(target_idx)
        if idx_max <= 255:
            h_bytes = array.array("H", [1])
            h_bytes.tofile(target_file)
            return 1
        elif idx_max <= 65535:
            h_bytes = array.array("H", [2])
            h_bytes.tofile(target_file)
            return 2
        else:
            h_bytes = array.array("H", [4])
            h_bytes.tofile(target_file)
            return 4
    else:
        h_bytes = array.array("H", [0])
        h_bytes.tofile(target_file)
        return 0


def write_dict(dict_array, sizes, target_file):
    for count, dict_item in enumerate(dict_array):
        if dict_item.isascii():
            # s_bytes = array.array('H', [4])
            s_bytes = array.array("i", [sizes[count]])
            if s_bytes.itemsize != 4:
                s_bytes = array.array("l", [sizes[count]])
            s_bytes.tofile(target_file)
            dict_item = dict_item.encode("utf-8")
        else:
            s_bytes = array.array("i", [-sizes[count] * 4])
            if s_bytes.itemsize != 4:
                s_bytes = array.array("l", [-sizes[count] * 4])
            s_bytes.tofile(target_file)
            dict_item = dict_item.encode("utf-32")
        target_file.write(dict_item)


def process_unit_section(section, tag_lock, units_cat_val_lock):
    global units, units_index
    for e in section:
        # ##print(str(e))
        val_len = 0
        for item in e.items():
            units, units_index, val_len = append_cat_val(units, units_index, item, units_cat_val_lock, val_len)
        append_tag(e.tag, tag_lock, 0, val_len)
    # print("Finished Unit " + str(process_time()))


def process_properties_section(section, tag_lock, property_sets_lock, single_values_lock):
    global property_sets, property_sets_index, single_values, single_values_index, prop_tracker
    for sp, e in enumerate(section):
        # if sp % 1000 == 0:
        #   print(str(sp))
        val_len2 = 0
        for item in e.items():
            property_sets, property_sets_index, val_len2 = append_with_guid(property_sets, property_sets_index, item, property_sets_lock, val_len2)
        append_tag(e.tag, tag_lock, 1, val_len2)

        for pv, single_value in enumerate(e):
            val_len3 = 0
            for value_item in single_value.items():
                single_values, single_values_index, val_len3 = append_with_index(single_values, single_values_index, prop_tracker, pv, value_item, single_values_lock, val_len3)
            append_tag(single_value.tag, tag_lock, 2, val_len3)
        prop_tracker = prop_tracker + 1
    ##print("Finished Properties " + str(process_time()))


def process_quantities_section(section, tag_lock, quantities_lock, quantity_properties_lock):
    global quantities, quantities_index, quantity_properties, quantity_properties_index, quantity_children, quantity_children_index
    for sq, e in enumerate(section):
        # ##print(str(e))
        val_len4 = 0
        for item in e.items():
            quantities, quantities_index, val_len4 = append_with_guid(quantities, quantities_index, item, quantities_lock, val_len4)
        append_tag(e.tag, tag_lock, 3, val_len4)

        for qp, quantity_prop in enumerate(e):
            val_len5 = 0
            for quantity_item in quantity_prop.items():
                quantity_properties, quantity_properties_index, val_len5 = append_with_index(quantity_properties, quantity_properties_index, sq, qp, quantity_item, quantity_properties_lock, val_len5)
            for qc, quantity_child in enumerate(quantity_prop):
                val_len_qc = 0
                for child_item in quantity_child.items():
                    quantity_children, quantity_children_index, val_len_qc = append_with_index(quantity_children, quantity_children_index, qp, qc, child_item, quantity_properties_lock, val_len_qc)
                append_tag(quantity_child.tag, tag_lock, 26, val_len_qc)
            append_tag(quantity_prop.tag, tag_lock, 4, val_len5)

    ##print("Finished Quantities " + str(process_time()))


def process_types_section(section, tag_lock, ifc_types_lock, ifc_property_links_lock):
    global ifc_types, ifc_types_index, ifc_property_links, ifc_property_links_index
    for st, e in enumerate(section):
        # ##print(str(e))
        val_len6 = 0
        for item in e.items():
            ifc_types, ifc_types_index, val_len6 = append_with_guid(ifc_types, ifc_types_index, item, ifc_types_lock, val_len6)
        append_tag(e.tag, tag_lock, 5, val_len6)
        append_tag_mini(e.tag, tag_lock, 5, val_len6)
        append_tag_unique(e.tag, tag_lock, 5)

        for tp, ifc_type in enumerate(e):
            val_len7 = 0
            for type_item in ifc_type.items():
                ifc_property_links, ifc_property_links_index, val_len7 = append_with_link(ifc_property_links, ifc_property_links_index, st, tp, type_item, ifc_property_links_lock, val_len7)
            append_tag(ifc_type.tag, tag_lock, 6, val_len7)

    ##print("Finished Types" + str(process_time()))


def process_layers_section(section, tag_lock, layers_lock):
    global layers, layers_index
    for e in section:
        # ##print(str(e))
        val_len8 = 0
        for item in e.items():
            layers, layers_index, val_len8 = append_with_guid(layers, layers_index, item, layers_lock, val_len8)
        append_tag(e.tag, tag_lock, 7, val_len8)
    ##print("Finished Layers " + str(process_time()))


def process_materials_section(section, tag_lock, materials_lock, ifc_materials_lock):
    global materials, materials_index, ifc_materials, ifc_materials_index
    for sm, e in enumerate(section):
        val_len9 = 0
        for item in e.items():
            materials, materials_index, val_len9 = append_with_guid(materials, materials_index, item, materials_lock, val_len9)
        append_tag(e.tag, tag_lock, 8, val_len9)
        for mp, ifc_material in enumerate(e):
            val_len10 = 0
            for material_item in ifc_material.items():
                ifc_materials, ifc_materials_index, val_len10 = append_with_index(ifc_materials, ifc_materials_index, sm, mp, material_item, ifc_materials_lock, val_len10)
            append_tag(ifc_material.tag, tag_lock, 9, val_len10)

    ##print("Finished Materials " + str(process_time()))


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def run_xml_binary(xml_location, bin_location):
    file = xml_location
    try:
        print("start")
        t = ET.parse(file)
    except:
        print("sed")
        subprocess.run('cat "' + str(file) + "\" | strings -ws '' > \"" + str(file) + '.bak"', shell=True)
        # subprocess.run("cat \"" + str(file)  + "\" | tr -cd '\034-\177'  > \""+str(file) +"temp\"" , shell=True)
        t = ET.parse(str(file) + ".bak")
    root = t.getroot()
    print("Loaded xml in " + str(process_time()))
    t1_start = process_time()

    binary_file = open(bin_location, "wb")

    head, tail = path.split(bin_location)
    mini_file = open(str(head) + "/mini_" + tail, "wb")

    miniaugin = "MINAUGIN"
    for mini in miniaugin:
        header_bytes = array.array("B", [ord(mini)])
        header_bytes.tofile(mini_file)

    augin = "AUGINIFC"
    for aug in augin:
        header_bytes = array.array("B", [ord(aug)])
        header_bytes.tofile(binary_file)

    tag_lock = threading.Lock()
    units_cat_val_lock = threading.Lock()
    property_sets_lock = threading.Lock()
    single_values_lock = threading.Lock()
    quantity_properties_lock = threading.Lock()
    ifc_types_lock = threading.Lock()
    ifc_property_links_lock = threading.Lock()
    layers_lock = threading.Lock()
    ifc_materials_lock = threading.Lock()
    materials_lock = threading.Lock()
    projects_lock = threading.Lock()
    sites_lock = threading.Lock()
    properties_threads = []
    global projects, sites, storeys, buildings, ifc_elements, nested_elements, nested_two, nested_three, site_property_set, buildings_property_set, elements_property_set
    global nested_property_set, nested_set_two, nested_set_three, projects_index, sites_index, storeys_index, ifc_elements_index, tags, tags_mini, tags_index, units, property_sets
    global nested_elements_index, nested_two_index, nested_three_index, buildings_index, nested_set_three_index, nested_set_two_index, nested_property_set_index
    global single_values, quantities, quantity_properties, ifc_types, ifc_property_links, layers, materials, ifc_materials
    global buildings_property_set_index, elements_property_set_index, site_property_set_index, quantity_children, quantity_children_index
    global tags_mini_types_unique, tags_mini_types_index, tags_mini_elements_unique, tags_mini_elements_index, tags_mini_elements_sections, tags_mini_types_sections
    global storey_groups, storey_groups_index, building_groups, building_groups_index, tags_groups, tags_groups_index, tags_mini_types_s_index, tags_mini_elements_s_index

    section = root.find("units")
    unit_thread = threading.Thread(
        target=process_unit_section,
        args=(
            section,
            tag_lock,
            units_cat_val_lock,
        ),
    )
    unit_thread.start()
    unit_thread.join()

    section = root.find("properties")
    for x in list(split(section, 1)):
        properties_thread = threading.Thread(
            target=process_properties_section,
            args=(
                x,
                tag_lock,
                property_sets_lock,
                single_values_lock,
            ),
        )
        properties_thread.start()
        properties_threads.append(properties_thread)

    section = root.find("quantities")
    quantities_thread = threading.Thread(
        target=process_quantities_section,
        args=(
            section,
            tag_lock,
            property_sets_lock,
            quantity_properties_lock,
        ),
    )
    quantities_thread.start()

    section = root.find("types")
    process_types_thread = threading.Thread(
        target=process_types_section,
        args=(
            section,
            tag_lock,
            ifc_types_lock,
            ifc_property_links_lock,
        ),
    )
    process_types_thread.start()

    section = root.find("layers")
    process_layers_thread = threading.Thread(
        target=process_layers_section,
        args=(
            section,
            tag_lock,
            layers_lock,
        ),
    )
    process_layers_thread.start()

    section = root.find("materials")
    process_materials_thread = threading.Thread(
        target=process_materials_section,
        args=(
            section,
            tag_lock,
            materials_lock,
            ifc_materials_lock,
        ),
    )
    process_materials_thread.start()

    # if unit_thread is not None:
    unit_thread.join()

    # if properties_thread is not None:
    for pt in properties_threads:
        pt.join()
    properties_thread.join()
    quantities_thread.join()
    process_types_thread.join()
    process_layers_thread.join()
    process_materials_thread.join()

    decomposition_section = root.find("decomposition")
    ##print('Started processing decomposition' + str(process_time()))
    for e in decomposition_section:
        val_len11 = 0
        for item in e.items():
            projects, projects_index, val_len11 = append_with_guid(projects, projects_index, item, projects_lock, val_len11)
        append_tag(e.tag, tag_lock, 10, val_len11)
        append_tag_mini(e.tag, tag_lock, 10, val_len11)

        for site in e:
            val_len12 = 0
            if site.tag != "IfcSite":
                new_site = xml.etree.ElementTree.SubElement(e, "IfcSite", attrib={"id": "auginauginaugin"})
                new_site.append(site)
                e.remove(site)
                for site_item in new_site.items():
                    sites, sites_index, val_len12 = append_with_guid(sites, sites_index, site_item, sites_lock, val_len12)
                site = new_site
                site.tag = "IfcSite"

                append_tag(site.tag, tag_lock, 11, val_len12)
                append_tag_mini(site.tag, tag_lock, 11, val_len12)

            else:
                for site_item in site.items():
                    sites, sites_index, val_len12 = append_with_guid(sites, sites_index, site_item, sites_lock, val_len12)
                append_tag(site.tag, tag_lock, 11, val_len12)
                append_tag_mini(site.tag, tag_lock, 11, val_len12)

            for bb, building in enumerate(site):
                val_len13 = 0
                b_link = False
                building_group_len = 0
                for building_item in building.items():
                    buildings, buildings_index, site_property_set, site_property_set_index, val_len13, b_link = append_layer_link(buildings, buildings_index, site_property_set, site_property_set_index, building_item, 0, bb, val_len13, b_link)
                append_tag(building.tag, tag_lock, 12, val_len13)
                if b_link:
                    append_tag_mini(building.tag, tag_lock, 12, val_len13)

                for ss, storey in enumerate(building):
                    val_len14 = 0
                    s_link = False
                    storey_group_len = 0

                    for storey_item in storey.items():
                        storeys, storeys_index, buildings_property_set, buildings_property_set_index, val_len14, s_link = append_layer_link(storeys, storeys_index, buildings_property_set, buildings_property_set_index, storey_item, bb, ss, val_len14, s_link)

                    append_tag(storey.tag, tag_lock, 13, val_len14)
                    if s_link:
                        append_tag_mini(storey.tag, tag_lock, 13, val_len14)
                    for it, ifc_element in enumerate(storey):
                        val_len15 = 0
                        l_link = False
                        for ifc_element_item in ifc_element.items():
                            ifc_elements, ifc_elements_index, elements_property_set, elements_property_set_index, val_len15, l_link = append_layer_link(ifc_elements, ifc_elements_index, elements_property_set, elements_property_set_index, ifc_element_item, ss, it, val_len15, l_link)
                        append_tag(ifc_element.tag, tag_lock, 14, val_len15)
                        # if l_link:
                        append_tag_mini(ifc_element.tag, tag_lock, 14, val_len15)
                        append_tag_unique(ifc_element.tag, tag_lock, 14)
                        storey_groups, storey_groups_index = append_group_element(storey_groups, storey_groups_index, ifc_element.items()[0])
                        storey_group_len = append_tag_group(ifc_element.tag, tag_lock, 14, storey_group_len, False)

                        for ne, nested_element in enumerate(ifc_element):
                            val_len16 = 0
                            l2_link = False

                            for nested_item in nested_element.items():
                                nested_elements, nested_elements_index, nested_property_set, nested_property_set_index, val_len16, l2_link = append_layer_link(nested_elements, nested_elements_index, nested_property_set, nested_property_set_index, nested_item, it, ne, val_len16, l2_link)
                            append_tag(nested_element.tag, tag_lock, 15, val_len16)
                            # if l2_link:
                            append_tag_mini(nested_element.tag, tag_lock, 15, val_len16)
                            append_tag_unique(nested_element.tag, tag_lock, 15)
                            storey_groups, storey_groups_index = append_group_element(storey_groups, storey_groups_index, nested_element.items()[0])
                            storey_group_len = append_tag_group(nested_element.tag, tag_lock, 15, storey_group_len, False)

                            for tt, layer_two in enumerate(nested_element):
                                val_len17 = 0
                                l3_link = False
                                for layer_two_item in layer_two.items():
                                    nested_two, nested_two_index, nested_set_two, nested_set_two_index, val_len17, l3_link = append_layer_link(nested_two, nested_two_index, nested_set_two, nested_set_two_index, layer_two_item, ne, tt, val_len17, l3_link)
                                append_tag(layer_two.tag, tag_lock, 16, val_len17)
                                if l3_link:
                                    append_tag_mini(layer_two.tag, tag_lock, 16, val_len17)
                                    append_tag_unique(layer_two.tag, tag_lock, 16)
                                    storey_groups, storey_groups_index = append_group_element(storey_groups, storey_groups_index, layer_two.items()[0])
                                    storey_group_len = append_tag_group(layer_two.tag, tag_lock, 16, storey_group_len, False)

                                for rrr, layer_three in enumerate(layer_two):
                                    val_len18 = 0
                                    l4_link = False
                                    for layer_three_item in layer_three.items():
                                        nested_three, nested_three_index, nested_set_three, nested_set_three_index, val_len18, ph = append_layer_link(nested_three, nested_three_index, nested_set_three, nested_set_three_index, layer_three_item, tt, rrr, val_len18, l4_link)
                                    append_tag(layer_three.tag, tag_lock, 17, val_len18)

                    if s_link and storey.tag == "IfcBuildingStorey":
                        append_tag_group(storey.tag, tag_lock, 13, storey_group_len, True)
                        building_group_len = append_tag_group(storey.tag, tag_lock, 13, building_group_len, False)
                        storey_groups, storey_groups_index = append_group_element(storey_groups, storey_groups_index, storey.items()[0])
                        building_groups, building_groups_index = append_group_element(building_groups, building_groups_index, storey.items()[0])
                if b_link and building.tag == "IfcBuilding":
                    building_groups, building_groups_index = append_group_element(building_groups, building_groups_index, building.items()[0])
                    append_tag_group(building.tag, tag_lock, 12, building_group_len, True)

    tags = tags[0:tags_index]
    tags_mini = tags_mini[0:tags_mini_index]
    tags_mini_elements_unique = tags_mini_elements_unique[0:tags_mini_elements_index]
    tags_mini_elements_sections = tags_mini_elements_sections[0:tags_mini_elements_s_index]
    tags_mini_types_unique = tags_mini_types_unique[0:tags_mini_types_index]
    tags_mini_types_sections = tags_mini_types_sections[0:tags_mini_types_s_index]
    tags_groups = tags_groups[0:tags_groups_index]
    units = units[0:units_index]
    property_sets = property_sets[0:property_sets_index]
    single_values = single_values[0:single_values_index]
    quantities = quantities[0:quantities_index]
    quantity_properties = quantity_properties[0:quantity_properties_index]
    quantity_children = quantity_children[0:quantity_children_index]
    ifc_types = ifc_types[0:ifc_types_index]
    ifc_property_links = ifc_property_links[0:ifc_property_links_index]
    layers = layers[0:layers_index]
    materials = materials[0:materials_index]
    ifc_materials = ifc_materials[0:ifc_materials_index]
    projects = projects[0:projects_index]
    sites = sites[0:sites_index]
    buildings = buildings[0:buildings_index]
    storeys = storeys[0:storeys_index]
    ifc_elements = ifc_elements[0:ifc_elements_index]
    nested_elements = nested_elements[0:nested_elements_index]
    nested_two = nested_two[0:nested_two_index]
    nested_three = nested_three[0:nested_three_index]
    site_property_set = site_property_set[0:site_property_set_index]
    buildings_property_set = buildings_property_set[0:buildings_property_set_index]
    elements_property_set = elements_property_set[0:elements_property_set_index]
    nested_property_set = nested_property_set[0:nested_property_set_index]
    nested_set_two = nested_set_two[0:nested_set_two_index]
    nested_set_three = nested_set_three[0:nested_set_three_index]

    storey_groups = storey_groups[0:storey_groups_index]
    building_groups = building_groups[0:building_groups_index]

    # dictionary size write
    cat_sizes = append_sizes(category_dict_array, binary_file)
    val_sizes = append_sizes(value_dict_array, binary_file)
    id_sizes = append_sizes(guid_dict_array, binary_file)
    tag_sizes = append_sizes(tag_dict_array, binary_file)

    catM_sizes = append_sizes(category_dict_array, mini_file)
    valM_sizes = append_sizes(value_dict_array, mini_file)
    idM_sizes = append_sizes(guid_dict_array, mini_file)
    tagM_sizes = append_sizes(tag_dict_array, mini_file)

    ##print("tags")
    tags_max = write_index_max(tags, binary_file)
    tags_mini_max = write_index_max(tags_mini, mini_file)  # 1
    tags_mini_types_max = write_index_max(tags_mini_types_unique, mini_file)  # 2
    tags_mini_elements_max = write_index_max(tags_mini_elements_unique, mini_file)  # 3
    tags_groups_max = write_index_max(tags_groups, mini_file)  # 4
    ##print("units")
    units_max = write_index_max(units, binary_file)  # Category | Value
    ##print("property_sets_index")
    property_set_max = write_index_max(property_sets, binary_file)  # Category | ID ||| Category | Value 2
    ##print("single_values_index")
    single_values_max = write_index_max(single_values, binary_file)  # Section | Item | Category | Value
    ##print("quantities_index")
    quantities_max = write_index_max(quantities, binary_file)  # Category | ID ||| Category | Value 4
    ##print("quantity_properties_index")
    quantity_property_max = write_index_max(quantity_properties, binary_file)  # Section | Item | Category | Value 5
    ##print("ifc_types_index")
    ifc_types_max = write_index_max(ifc_types, binary_file)  # Category | ID ||| Category | Value 6
    write_index_max(ifc_types, mini_file)  # 5
    ##print("ifc_property_links_index")
    ifc_property_link_max = write_index_max(ifc_property_links, binary_file)  # Section | Item | Category | ID 7

    ##print("layers_index")
    layers_max = write_index_max(layers, binary_file)  # Category | Id ||| Category | Value 8
    ##print("materials_index")
    materials_max = write_index_max(materials, binary_file)  # Category | Id 9
    ##print("ifc_materials_index")
    ifc_materials_max = write_index_max(ifc_materials, binary_file)  # Category | Value
    ##print("projects_index")
    projects_max = write_index_max(projects, binary_file)  # Category | Id ||| Category | Value 11
    write_index_max(projects, mini_file)  # 6
    ##print("sites_index")
    sites_max = write_index_max(sites, binary_file)  # Category | Id ||| Category | Value 12
    write_index_max(sites, mini_file)  # 7
    ##print("buildings_index")
    buildings_max = write_index_max(buildings, binary_file)  # Category | Id ||| Category | Value 13
    write_index_max(buildings, mini_file)  # 8
    ##print("storeys_index")
    storeys_max = write_index_max(storeys, binary_file)  # Category | Id ||| Category | Value 14
    write_index_max(storeys, mini_file)  # 9
    ##print("ifc_elements_index")
    ifc_elements_max = write_index_max(ifc_elements, binary_file)  # Category | Id ||| Category | Value 15
    write_index_max(ifc_elements, mini_file)  # 10
    ##print("nested_elements_index")
    nested_max = write_index_max(nested_elements, binary_file)  # Category | Id ||| Category | Value 16
    write_index_max(nested_elements, mini_file)  # 11
    ##print("nested_two_index")
    nested_two_max = write_index_max(nested_two, binary_file)  # Category | Id ||| Category | Value 17
    write_index_max(nested_two, mini_file)  # 12
    ##print("nested_three_index")
    nested_three_max = write_index_max(nested_three, binary_file)  # Category | Id ||| Category | Value 18
    ##print("site_property_set_index")
    site_property_max = write_index_max(site_property_set, binary_file)  # Category | Id 19

    ##print("buildings_property_set_index")
    building_property_max = write_index_max(buildings_property_set, binary_file)  # Category | Id 20

    ##print("elements_property_set_index")
    element_property_max = write_index_max(elements_property_set, binary_file)  # Category | Id 21

    ##print("nested_property_set_index")
    nested_set_max = write_index_max(nested_property_set, binary_file)  # Category | Id 22

    ##print("nested_set_two_index")
    nested_set_two_max = write_index_max(nested_set_two, binary_file)  # Category | Id 23

    ##print("nested_set_three_index")
    nested_set_three_max = write_index_max(nested_set_three, binary_file)  # Category | Id 24

    storey_groups_max = write_index_max(storey_groups, mini_file)  # 13
    building_groups_max = write_index_max(building_groups, mini_file)  # 14

    quantity_children_max = write_index_max(quantity_children, binary_file)  # Id 25

    # dictionary write
    write_dict(category_dict_array, cat_sizes, binary_file)
    write_dict(value_dict_array, val_sizes, binary_file)
    write_dict(guid_dict_array, id_sizes, binary_file)
    write_dict(tag_dict_array, tag_sizes, binary_file)

    write_dict(category_dict_array, cat_sizes, mini_file)
    write_dict(value_dict_array, val_sizes, mini_file)
    write_dict(guid_dict_array, id_sizes, mini_file)
    write_dict(tag_dict_array, tag_sizes, mini_file)

    # index size write
    write_length(tags_index, binary_file)
    write_length(tags_mini_index, mini_file)
    tags_mini_types_index = tags_mini_types_index + tags_mini_types_s_index
    write_length(tags_mini_types_index, mini_file)
    tags_mini_elements_index = tags_mini_elements_index + tags_mini_elements_s_index
    write_length(tags_mini_elements_index, mini_file)
    write_length(tags_groups_index, mini_file)
    write_length(units_index, binary_file)  # Category | Value
    write_length(property_sets_index, binary_file)  # Category | ID ||| Category | Value 2
    write_length(single_values_index, binary_file)  # Section | Item | Category | Value
    write_length(quantities_index, binary_file)  # Category | ID ||| Category | Value 4
    write_length(quantity_properties_index, binary_file)  # Section | Item | Category | Value 5
    write_length(ifc_types_index, binary_file)  # Category | ID ||| Category | Value 6
    write_length(ifc_types_index, mini_file)
    write_length(ifc_property_links_index, binary_file)  # Section | Item | Category | ID 7
    write_length(layers_index, binary_file)  # Category | Id ||| Category | Value 8
    write_length(materials_index, binary_file)  # Category | Id 9
    write_length(ifc_materials_index, binary_file)  # Category | Value
    write_length(projects_index, binary_file)  # Category | Id ||| Category | Value 11
    write_length(projects_index, mini_file)
    write_length(sites_index, binary_file)  # Category | Id ||| Category | Value 12
    write_length(sites_index, mini_file)
    write_length(buildings_index, binary_file)  # Category | Id ||| Category | Value 13
    write_length(buildings_index, mini_file)
    write_length(storeys_index, binary_file)  # Category | Id ||| Category | Value 14
    write_length(storeys_index, mini_file)
    write_length(ifc_elements_index, binary_file)  # Category | Id ||| Category | Value 15
    write_length(ifc_elements_index, mini_file)
    write_length(nested_elements_index, binary_file)  # Category | Id ||| Category | Value 16
    write_length(nested_elements_index, mini_file)
    write_length(nested_two_index, binary_file)  # Category | Id ||| Category | Value 17
    write_length(nested_two_index, mini_file)
    write_length(nested_three_index, binary_file)  # Category | Id ||| Category | Value 18
    write_length(site_property_set_index, binary_file)  # Category | Id 19
    write_length(buildings_property_set_index, binary_file)  # Category | Id 20
    write_length(elements_property_set_index, binary_file)  # Category | Id 21
    write_length(nested_property_set_index, binary_file)  # Category | Id 22
    write_length(nested_set_two_index, binary_file)  # Category | Id 23
    write_length(nested_set_three_index, binary_file)  # Category | Id 24
    write_length(quantity_children_index, binary_file)

    write_length(storey_groups_index, mini_file)
    write_length(building_groups_index, mini_file)

    # index write

    write_index(tags, binary_file, tags_max)
    write_index(tags_mini, mini_file, tags_mini_max)
    write_unique(tags_mini_types_sections, tags_mini_types_unique, mini_file, tags_mini_types_max)
    write_unique(tags_mini_elements_sections, tags_mini_elements_unique, mini_file, tags_mini_elements_max)
    write_index(tags_groups, mini_file, tags_groups_max)

    write_index(units, binary_file, units_max)

    write_index(property_sets, binary_file, property_set_max)

    write_index(single_values, binary_file, single_values_max)

    write_index(quantities, binary_file, quantities_max)

    write_index(quantity_properties, binary_file, quantity_property_max)

    write_index(ifc_types, binary_file, ifc_types_max)
    write_index(ifc_types, mini_file, ifc_types_max)

    write_index(ifc_property_links, binary_file, ifc_property_link_max)

    write_index(layers, binary_file, layers_max)

    write_index(materials, binary_file, materials_max)

    write_index(ifc_materials, binary_file, ifc_materials_max)

    write_index(projects, binary_file, projects_max)
    write_index(projects, mini_file, projects_max)

    write_index(sites, binary_file, sites_max)
    write_index(sites, mini_file, sites_max)

    write_index(buildings, binary_file, buildings_max)
    write_index(buildings, mini_file, buildings_max)

    write_index(storeys, binary_file, storeys_max)
    write_index(storeys, mini_file, storeys_max)

    write_index(ifc_elements, binary_file, ifc_elements_max)
    write_index(ifc_elements, mini_file, ifc_elements_max)

    write_index(nested_elements, binary_file, nested_max)
    write_index(nested_elements, mini_file, nested_max)

    write_index(nested_two, binary_file, nested_two_max)
    write_index(nested_two, mini_file, nested_two_max)

    write_index(nested_three, binary_file, nested_three_max)

    write_index(site_property_set, binary_file, site_property_max)

    write_index(buildings_property_set, binary_file, building_property_max)

    write_index(elements_property_set, binary_file, element_property_max)

    write_index(nested_property_set, binary_file, nested_set_max)

    write_index(nested_set_two, binary_file, nested_set_two_max)

    write_index(nested_set_three, binary_file, nested_set_three_max)

    write_index(quantity_children, binary_file, quantity_children_max)

    write_index(storey_groups, mini_file, storey_groups_max)
    write_index(building_groups, mini_file, building_groups_max)

    current, peak = tracemalloc.get_traced_memory()
    ###print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    tracemalloc.stop()
    binary_file.close()
    mini_file.close()
    t1_stop = process_time()
    print("Elapsed time:", t1_stop, t1_start)
    print("Elapsed time during the whole program in seconds:" + str(t1_stop - t1_start))
    pass

import os
import json
import time
from utils.utils.Validation import Validation
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Http import Http
from utils.Config import lambda_constants
from utils.AWS.S3 import S3
from utils.AWS.Sqs import Sqs
from utils.AWS.Ses import Ses
from objects.Project import Project
from objects.Site import Site
from objects.Building import Building
from objects.Storey import Storey
from objects.Category import Category
from objects.Element import Element
from objects.SubElement import SubElement
from objects.SubSubElement import SubSubElement
from objects.NanoElement import NanoElement
from objects.Property import Property
from objects.Layer import Layer


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        Ses().send_error_email(event, "AUGIN lambda_process_xml_to_dynamo", e)


def main_lambda_handler(event, context):
    print(json.dumps(event))

    if not Validation().check_if_local_env():
        record = json.loads(event["Records"][0]["body"])
        model_id = record["model_id"]
        project_id = model_id
        zip_filename = model_id + ".zip"
        output_project_domain_name = record["output_project_domain_name"]
        reprocess = record.get("reprocess")
    else:
        record = json.loads(event["Records"][0]["body"])
        model_id = record["model_id"]
        project_id = model_id
        zip_filename = model_id + ".zip"
        output_project_domain_name = record["output_project_domain_name"]
        reprocess = record.get("reprocess")

        # record = {}
        # record["output_bucket"] = lambda_constants["processed_bucket"]
        # record["output_key"] = "dev-tqs/e0f97079-7555-49f7-b6f8-29bac10bb35d/49446d381044-xml.zip"
        # model_id = "e0f97079-7555-49f7-b6f8-29bac10bb35d"
        # project_id = model_id
        # zip_filename = model_id + ".zip"
        # output_project_domain_name = "dev-tqs.integratebim.com"

    ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])
    S3().download_file(record["output_bucket"], record["output_key"], lambda_constants["tmp_path"] + zip_filename)
    ReadWrite().extract_zip_file(lambda_constants["tmp_path"] + zip_filename, lambda_constants["tmp_path"] + model_id)
    xml_file_path = find_xml_file(lambda_constants["tmp_path"] + model_id + "/")

    start_time = time.time()

    root = ReadWrite().read_xml_file(xml_file_path)
    project_layers = get_project_layers(root)
    decomposition = root.find("decomposition")
    project_ifc_project, ifc_project = get_project_ifc_project(decomposition)
    project_item = Project(project_id, project_ifc_project, project_layers).__dict__

    site_items = []
    building_items = []
    storey_items = []
    category_items = []
    element_items = []
    sub_element_items = []
    sub_sub_element_items = []
    nano_element_items = []
    property_items = []
    layers_items = []
    property_types_set = set()

    property_classes = ["properties", "quantities", "types", "materials"]
    for property_class in property_classes:
        properties = list(root.find(property_class))
        for property in properties:
            if property.get("id"):
                property_data = {}
                for property_values in list(property):
                    if not list(property_values):
                        property_value = ""
                        property_label = ""
                        property_extras = ""
                        for key, val in property_values.attrib.items():
                            if "Value" in key:
                                property_value = val
                            elif "Name" in key:
                                property_label = val
                            else:
                                if val != "":
                                    property_extras = property_extras + " " + val
                        if property_extras != "":
                            property_data[property_label.strip() + " (" + property_extras.strip() + ")"] = property_value.strip()
                        else:
                            property_data[property_label.strip()] = property_value.strip()
                    else:
                        property_value = ""
                        property_label = ""
                        property_extras = ""
                        for key, val in property_values.attrib.items():
                            for sub_property_values in list(property_values):
                                sub_property_value = ""
                                sub_property_label = ""
                                sub_property_extras = ""
                                for sub_key, sub_val in sub_property_values.attrib.items():
                                    if "Name" in key:
                                        if "Value" in sub_key:
                                            sub_property_value = sub_val
                                        elif "Name" in sub_key:
                                            sub_property_label = val + "." + sub_val
                                        else:
                                            if sub_val != "":
                                                sub_property_extras = sub_property_extras + " " + val + "." + sub_val
                                        if sub_property_extras != "":
                                            property_data[sub_property_label.strip() + " (" + sub_property_extras.strip() + ")"] = sub_property_value.strip()
                                        else:
                                            property_data[sub_property_label.strip()] = sub_property_value.strip()

                property_types_set.add(property.tag)
                property_items.append(Property(project_id, property.get("id"), property.get("Name", "Not Informed"), property.tag, property_class, property_data).__dict__)

    if not Validation().check_if_local_env():
        insert_items(property_items, project_id)
    ifc_sites = ifc_project.findall("IfcSite")

    if not ifc_sites:
        ifc_sites = [{"id": "None", "name": "Not Informed"}]
        site_data = {}
        site_properties = []
    for site in ifc_sites:
        if site.get("id"):
            site_id = site.get("id")
            if site_id != "None":
                site_data = get_data_from_attrib(site)
                site_properties = []
                property_list = list(site)
                for property in property_list:
                    if property.tag:
                        if "{http://www.w3.org/1999/xlink}href" in property.attrib:
                            site_properties.append({"property_tag": property.tag, "property_link": property.attrib["{http://www.w3.org/1999/xlink}href"]})
                site_items.append(Site(project_id, site.get("id"), site.get("Name", "Not Informed"), site_data, site_properties).__dict__)
            else:
                site_items.append(Site(project_id, site.get("id"), site.get("Name", "Not Informed"), site_data, site_properties).__dict__)

            if site_id == "None":
                ifc_buildings = ifc_project.findall("IfcBuilding")
            else:
                ifc_buildings = site.findall("IfcBuilding")
            for building in ifc_buildings:
                if building.get("id"):
                    building_id = building.get("id")
                    building_data = get_data_from_attrib(building)
                    building_properties = []
                    property_list = list(building)
                    for property in property_list:
                        if property.tag:
                            if "{http://www.w3.org/1999/xlink}href" in property.attrib:
                                building_properties.append({"property_tag": property.tag, "property_link": property.attrib["{http://www.w3.org/1999/xlink}href"]})
                    building_items.append(Building(project_id, site_id, building_id, building.get("Name", "Not Informed"), building_data, building_properties).__dict__)

                    ifc_storeys = building.findall("IfcBuildingStorey")
                    for storey_index, storey in enumerate(ifc_storeys):
                        if storey.get("id"):
                            storey_id = storey.get("id")
                            storey_data = get_data_from_attrib(storey)
                            storey_properties = []
                            property_list = list(storey)
                            for property in property_list:
                                if property.tag:
                                    if "{http://www.w3.org/1999/xlink}href" in property.attrib:
                                        storey_properties.append({"property_tag": property.tag, "property_link": property.attrib["{http://www.w3.org/1999/xlink}href"]})
                            storey_items.append(Storey(project_id, site_id, building_id, storey_id, storey.get("Name", "Not Informed"), storey_data, storey_properties, storey_index).__dict__)

                            categories_list = list(storey)
                            categories_set = set()
                            for category in categories_list:
                                if category.tag not in property_types_set:
                                    categories_set.add(category.tag)

                            ifc_doors = []
                            ifc_windows = []
                            IfcDoor = False
                            IfcWindow = False
                            for original_category_tag in categories_set:
                                if original_category_tag != "IfcOpeningElement":
                                    category_items.append(Category(project_id, site_id, building_id, storey_id, original_category_tag).__dict__)

                                # for categories_element in storey.findall(category_tag):
                                # if "IfcOpeningElement" in categories_set:
                                #     ifc_elements = storey.findall("IfcOpeningElement")

                                ifc_elements = storey.findall(original_category_tag)
                                element_index = 0
                                for element in ifc_elements:
                                    if element.get("id"):
                                        category_tag = original_category_tag
                                        if "IfcDoor" in element.tag:
                                            ifc_doors.append(element)
                                            continue
                                        if "IfcWindow" in element.tag:
                                            ifc_windows.append(element)
                                            continue
                                        element_id = element.get("id")
                                        element_data = get_data_from_attrib(element)
                                        element_properties = []
                                        sub_element_index = -1
                                        property_list = list(element)
                                        element_has_sub_elements = False
                                        for property in property_list:
                                            if property.tag:
                                                if "{http://www.w3.org/1999/xlink}href" in property.attrib:
                                                    element_properties.append({"property_tag": property.tag, "property_link": property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                    if property.tag == "IfcPresentationLayerAssignment":
                                                        layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), element_id).__dict__)
                                                else:
                                                    sub_element = property
                                                    if "IfcDoor" in sub_element.tag:
                                                        ifc_doors.append(sub_element)
                                                        continue
                                                    if "IfcWindow" in sub_element.tag:
                                                        ifc_windows.append(sub_element)
                                                        continue
                                                    sub_element_index += 1
                                                    element_has_sub_elements = True
                                                    sub_element_id = sub_element.get("id")
                                                    sub_element_data = get_data_from_attrib(sub_element)
                                                    sub_element_properties = []
                                                    sub_sub_element_index = -1
                                                    sub_property_list = list(sub_element)
                                                    sub_element_has_sub_sub_elements = False
                                                    for sub_property in sub_property_list:
                                                        if sub_property.tag:
                                                            if "{http://www.w3.org/1999/xlink}href" in sub_property.attrib:
                                                                sub_element_properties.append({"property_tag": sub_property.tag, "property_link": sub_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                if property.tag == "IfcPresentationLayerAssignment":
                                                                    layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), sub_element_id).__dict__)
                                                            else:
                                                                sub_sub_element = sub_property
                                                                if "IfcDoor" in sub_sub_element.tag:
                                                                    ifc_doors.append(sub_sub_element)
                                                                    continue
                                                                if "IfcWindow" in sub_sub_element.tag:
                                                                    ifc_windows.append(sub_sub_element)
                                                                    continue
                                                                sub_sub_element_index += 1
                                                                sub_element_has_sub_sub_elements = True
                                                                sub_sub_element_id = sub_sub_element.get("id")
                                                                sub_sub_element_data = get_data_from_attrib(sub_sub_element)
                                                                sub_sub_element_properties = []
                                                                nano_element_index = -1
                                                                sub_sub_property_list = list(sub_sub_element)
                                                                sub_sub_element_has_nano_elements = False
                                                                for sub_sub_property in sub_sub_property_list:
                                                                    if sub_sub_property.tag:
                                                                        if "{http://www.w3.org/1999/xlink}href" in sub_sub_property.attrib:
                                                                            sub_sub_element_properties.append({"property_tag": sub_sub_property.tag, "property_link": sub_sub_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                            if property.tag == "IfcPresentationLayerAssignment":
                                                                                layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), sub_sub_element_id).__dict__)
                                                                        else:
                                                                            nano_element = sub_sub_property
                                                                            if "IfcDoor" in nano_element.tag:
                                                                                ifc_doors.append(nano_element)
                                                                                continue
                                                                            if "IfcWindow" in nano_element.tag:
                                                                                ifc_windows.append(nano_element)
                                                                                continue
                                                                            nano_element_index += 1
                                                                            sub_sub_element_has_nano_elements = True
                                                                            nano_element_id = nano_element.get("id")
                                                                            nano_element_data = get_data_from_attrib(nano_element)
                                                                            nano_element_properties = []
                                                                            nano_property_list = list(nano_element)
                                                                            for nano_property in nano_property_list:
                                                                                if nano_property.tag:
                                                                                    if "{http://www.w3.org/1999/xlink}href" in nano_property.attrib:
                                                                                        nano_element_properties.append({"property_tag": nano_property.tag, "property_link": nano_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                                        if property.tag == "IfcPresentationLayerAssignment":
                                                                                            layers_items.append(Layer(project_id, nano_property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), nano_element_id).__dict__)
                                                                                    else:
                                                                                        Ses().send_error_email(event, "lambda_process_xml_to_dynamo", "SUB NANO CATEGORY")
                                                                                        break
                                                                                # if not check_if_element_is_only_window_or_door(nano_element):
                                                                                nano_element_items.append(NanoElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_sub_element_id, nano_element_id, nano_element.get("Name", "Not Informed") + " " + nano_element.tag, nano_element_data, nano_element_properties, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index), str(nano_element_index)).__dict__)
                                                                    # if not check_if_element_is_only_window_or_door(sub_sub_element):
                                                                    sub_sub_element_items.append(
                                                                        SubSubElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_sub_element_id, sub_sub_element.get("Name", "Not Informed") + " " + sub_sub_element.tag, sub_sub_element_data, sub_sub_element_properties, sub_sub_element_has_nano_elements, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index), str(nano_element_index + 1)).__dict__
                                                                    )
                                                        # if not check_if_element_is_only_window_or_door(sub_element):
                                                        sub_element_items.append(SubElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_element.get("Name", "Not Informed") + " " + sub_element.tag, sub_element_data, sub_element_properties, sub_element_has_sub_sub_elements, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index + 1)).__dict__)
                                        # if not check_if_element_is_only_window_or_door(element):
                                        element_items.append(Element(project_id, site_id, building_id, storey_id, category_tag, element_id, element.get("Name", "Not Informed") + " " + element.tag, element_data, element_properties, element_has_sub_elements, str(storey_index), str(element_index), str(sub_element_index + 1)).__dict__)
                                        element_index += 1

                            if ifc_doors:
                                element_index = 0
                                category_tag = "IfcDoor"
                                category_items.append(Category(project_id, site_id, building_id, storey_id, category_tag).__dict__)
                                for element in ifc_doors:
                                    if element.get("id"):
                                        element_id = element.get("id")
                                        element_data = get_data_from_attrib(element)
                                        element_properties = []
                                        sub_element_index = -1
                                        property_list = list(element)
                                        element_has_sub_elements = False
                                        for property in property_list:
                                            if property.tag:
                                                if "{http://www.w3.org/1999/xlink}href" in property.attrib:
                                                    element_properties.append({"property_tag": property.tag, "property_link": property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                    if property.tag == "IfcPresentationLayerAssignment":
                                                        layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), element_id).__dict__)
                                                else:
                                                    sub_element = property
                                                    sub_element_index += 1
                                                    element_has_sub_elements = True
                                                    sub_element_id = sub_element.get("id")
                                                    sub_element_data = get_data_from_attrib(sub_element)
                                                    sub_element_properties = []
                                                    sub_sub_element_index = -1
                                                    sub_property_list = list(sub_element)
                                                    sub_element_has_sub_sub_elements = False
                                                    for sub_property in sub_property_list:
                                                        if sub_property.tag:
                                                            if "{http://www.w3.org/1999/xlink}href" in sub_property.attrib:
                                                                sub_element_properties.append({"property_tag": sub_property.tag, "property_link": sub_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                if property.tag == "IfcPresentationLayerAssignment":
                                                                    layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), sub_element_id).__dict__)
                                                            else:
                                                                sub_sub_element = sub_property
                                                                sub_sub_element_index += 1
                                                                sub_element_has_sub_sub_elements = True
                                                                sub_sub_element_id = sub_sub_element.get("id")
                                                                sub_sub_element_data = get_data_from_attrib(sub_sub_element)
                                                                sub_sub_element_properties = []
                                                                nano_element_index = -1
                                                                sub_sub_property_list = list(sub_sub_element)
                                                                sub_sub_element_has_nano_elements = False
                                                                for sub_sub_property in sub_sub_property_list:
                                                                    if sub_sub_property.tag:
                                                                        if "{http://www.w3.org/1999/xlink}href" in sub_sub_property.attrib:
                                                                            sub_sub_element_properties.append({"property_tag": sub_sub_property.tag, "property_link": sub_sub_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                            if property.tag == "IfcPresentationLayerAssignment":
                                                                                layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), sub_sub_element_id).__dict__)
                                                                        else:
                                                                            nano_element = sub_sub_property
                                                                            nano_element_index += 1
                                                                            sub_sub_element_has_nano_elements = True
                                                                            nano_element_id = nano_element.get("id")
                                                                            nano_element_data = get_data_from_attrib(nano_element)
                                                                            nano_element_properties = []
                                                                            nano_property_list = list(nano_element)
                                                                            for nano_property in nano_property_list:
                                                                                if nano_property.tag:
                                                                                    if "{http://www.w3.org/1999/xlink}href" in nano_property.attrib:
                                                                                        nano_element_properties.append({"property_tag": nano_property.tag, "property_link": nano_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                                        if property.tag == "IfcPresentationLayerAssignment":
                                                                                            layers_items.append(Layer(project_id, nano_property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), nano_element_id).__dict__)
                                                                                    else:
                                                                                        Ses().send_error_email(event, "lambda_process_xml_to_dynamo", "SUB NANO CATEGORY")
                                                                                        break
                                                                                # if not check_if_element_is_only_window_or_door(nano_element):
                                                                                nano_element_items.append(NanoElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_sub_element_id, nano_element_id, nano_element.get("Name", "Not Informed") + " " + nano_element.tag, nano_element_data, nano_element_properties, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index), str(nano_element_index)).__dict__)
                                                                    # if not check_if_element_is_only_window_or_door(sub_sub_element):
                                                                    sub_sub_element_items.append(
                                                                        SubSubElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_sub_element_id, sub_sub_element.get("Name", "Not Informed") + " " + sub_sub_element.tag, sub_sub_element_data, sub_sub_element_properties, sub_sub_element_has_nano_elements, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index), str(nano_element_index + 1)).__dict__
                                                                    )
                                                        # if not check_if_element_is_only_window_or_door(sub_element):
                                                        sub_element_items.append(SubElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_element.get("Name", "Not Informed") + " " + sub_element.tag, sub_element_data, sub_element_properties, sub_element_has_sub_sub_elements, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index + 1)).__dict__)
                                        # if not check_if_element_is_only_window_or_door(element):
                                        element_items.append(Element(project_id, site_id, building_id, storey_id, category_tag, element_id, element.get("Name", "Not Informed") + " " + element.tag, element_data, element_properties, element_has_sub_elements, str(storey_index), str(element_index), str(sub_element_index + 1)).__dict__)
                                        element_index += 1

                            if ifc_windows:
                                element_index = 0
                                category_tag = "IfcWindow"
                                category_items.append(Category(project_id, site_id, building_id, storey_id, category_tag).__dict__)
                                for element in ifc_windows:
                                    if element.get("id"):
                                        element_id = element.get("id")
                                        element_data = get_data_from_attrib(element)
                                        element_properties = []
                                        sub_element_index = -1
                                        property_list = list(element)
                                        element_has_sub_elements = False
                                        for property in property_list:
                                            if property.tag:
                                                if "{http://www.w3.org/1999/xlink}href" in property.attrib:
                                                    element_properties.append({"property_tag": property.tag, "property_link": property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                    if property.tag == "IfcPresentationLayerAssignment":
                                                        layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), element_id).__dict__)
                                                else:
                                                    sub_element = property
                                                    sub_element_index += 1
                                                    element_has_sub_elements = True
                                                    sub_element_id = sub_element.get("id")
                                                    sub_element_data = get_data_from_attrib(sub_element)
                                                    sub_element_properties = []
                                                    sub_sub_element_index = -1
                                                    sub_property_list = list(sub_element)
                                                    sub_element_has_sub_sub_elements = False
                                                    for sub_property in sub_property_list:
                                                        if sub_property.tag:
                                                            if "{http://www.w3.org/1999/xlink}href" in sub_property.attrib:
                                                                sub_element_properties.append({"property_tag": sub_property.tag, "property_link": sub_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                if property.tag == "IfcPresentationLayerAssignment":
                                                                    layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), sub_element_id).__dict__)
                                                            else:
                                                                sub_sub_element = sub_property
                                                                sub_sub_element_index += 1
                                                                sub_element_has_sub_sub_elements = True
                                                                sub_sub_element_id = sub_sub_element.get("id")
                                                                sub_sub_element_data = get_data_from_attrib(sub_sub_element)
                                                                sub_sub_element_properties = []
                                                                nano_element_index = -1
                                                                sub_sub_property_list = list(sub_sub_element)
                                                                sub_sub_element_has_nano_elements = False
                                                                for sub_sub_property in sub_sub_property_list:
                                                                    if sub_sub_property.tag:
                                                                        if "{http://www.w3.org/1999/xlink}href" in sub_sub_property.attrib:
                                                                            sub_sub_element_properties.append({"property_tag": sub_sub_property.tag, "property_link": sub_sub_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                            if property.tag == "IfcPresentationLayerAssignment":
                                                                                layers_items.append(Layer(project_id, property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), sub_sub_element_id).__dict__)
                                                                        else:
                                                                            nano_element = sub_sub_property
                                                                            nano_element_index += 1
                                                                            sub_sub_element_has_nano_elements = True
                                                                            nano_element_id = nano_element.get("id")
                                                                            nano_element_data = get_data_from_attrib(nano_element)
                                                                            nano_element_properties = []
                                                                            nano_property_list = list(nano_element)
                                                                            for nano_property in nano_property_list:
                                                                                if nano_property.tag:
                                                                                    if "{http://www.w3.org/1999/xlink}href" in nano_property.attrib:
                                                                                        nano_element_properties.append({"property_tag": nano_property.tag, "property_link": nano_property.attrib["{http://www.w3.org/1999/xlink}href"]})
                                                                                        if property.tag == "IfcPresentationLayerAssignment":
                                                                                            layers_items.append(Layer(project_id, nano_property.attrib["{http://www.w3.org/1999/xlink}href"].replace("#", ""), nano_element_id).__dict__)
                                                                                    else:
                                                                                        Ses().send_error_email(event, "lambda_process_xml_to_dynamo", "SUB NANO CATEGORY")
                                                                                        break
                                                                                # if not check_if_element_is_only_window_or_door(nano_element):
                                                                                nano_element_items.append(NanoElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_sub_element_id, nano_element_id, nano_element.get("Name", "Not Informed") + " " + nano_element.tag, nano_element_data, nano_element_properties, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index), str(nano_element_index)).__dict__)
                                                                    # if not check_if_element_is_only_window_or_door(sub_sub_element):
                                                                    sub_sub_element_items.append(
                                                                        SubSubElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_sub_element_id, sub_sub_element.get("Name", "Not Informed") + " " + sub_sub_element.tag, sub_sub_element_data, sub_sub_element_properties, sub_sub_element_has_nano_elements, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index), str(nano_element_index + 1)).__dict__
                                                                    )
                                                        # if not check_if_element_is_only_window_or_door(sub_element):
                                                        sub_element_items.append(SubElement(project_id, site_id, building_id, storey_id, category_tag, element_id, sub_element_id, sub_element.get("Name", "Not Informed") + " " + sub_element.tag, sub_element_data, sub_element_properties, sub_element_has_sub_sub_elements, str(storey_index), str(element_index), str(sub_element_index), str(sub_sub_element_index + 1)).__dict__)
                                        # if not check_if_element_is_only_window_or_door(element):
                                        element_items.append(Element(project_id, site_id, building_id, storey_id, category_tag, element_id, element.get("Name", "Not Informed") + " " + element.tag, element_data, element_properties, element_has_sub_elements, str(storey_index), str(element_index), str(sub_element_index + 1)).__dict__)
                                        element_index += 1
    for category in category_items:
        if category["category_id"] not in project_item["project_categories"]:
            project_item["project_categories"].append(category["category_id"])

    ele_items = []
    pk_ele = {}
    ele_items.extend(element_items)
    ele_items.extend(sub_element_items)
    ele_items.extend(sub_sub_element_items)
    ele_items.extend(nano_element_items)

    for item in ele_items:
        if item["pk"] not in pk_ele:
            pk_ele[item["pk"]] = 1
            pk_ele[item["pk"] + "_sks"] = []
            pk_ele[item["pk"] + "_sks"].append(item["sk"])
        else:
            if item["sk"] not in pk_ele[item["pk"] + "_sks"]:
                pk_ele[item["pk"]] += 1
                pk_ele[item["pk"] + "_sks"].append(item["sk"])

    if category_items:
        for category in category_items:
            if category["pk"] + "#" + category["category_id"] + "#element" in pk_ele:
                category["category_elements_count"] = str(pk_ele[category["pk"] + "#" + category["category_id"] + "#element"])
            else:
                category["category_elements_count"] = "0"

    if element_items:
        for element in element_items:
            if element["pk"] + "#" + element["element_id"] + "#sub_element" in pk_ele:
                element["element_sub_elements_count"] = str(pk_ele[element["pk"] + "#" + element["element_id"] + "#sub_element"])
                element["element_has_sub_elements"] = True
            else:
                element["element_sub_elements_count"] = "0"
                element["element_has_sub_elements"] = False

    if sub_element_items:
        for sub_element in sub_element_items:
            if sub_element["pk"] + "#" + sub_element["sub_element_id"] + "#sub_sub_element" in pk_ele:
                sub_element["sub_element_sub_sub_elements_count"] = str(pk_ele[sub_element["pk"] + "#" + sub_element["sub_element_id"] + "#sub_sub_element"])
                sub_element["sub_element_has_sub_sub_elements"] = True
            else:
                sub_element["sub_element_sub_sub_elements_count"] = "0"
                sub_element["sub_element_has_sub_sub_elements"] = False

    if sub_sub_element_items:
        for sub_sub_element in sub_sub_element_items:
            if sub_sub_element["pk"] + "#" + sub_sub_element["sub_sub_element_id"] + "#nano_element" in pk_ele:
                sub_sub_element["sub_sub_element_nano_elements_count"] = str(pk_ele[sub_sub_element["pk"] + "#" + sub_sub_element["sub_sub_element_id"] + "#nano_element"])
                sub_sub_element["sub_sub_element_has_nano_elements"] = True
            else:
                sub_sub_element["sub_sub_element_nano_elements_count"] = "0"
                sub_sub_element["sub_sub_element_has_nano_elements"] = False

    filtered_categorys_items = []
    for category in category_items:
        if category["category_elements_count"] != "0":
            filtered_categorys_items.append(category)
        else:
            print("Category without items")

    if reprocess:
        total_items = []
    else:
        total_items = [project_item]

    total_items.extend(site_items)
    total_items.extend(building_items)
    total_items.extend(storey_items)
    total_items.extend(filtered_categorys_items)
    total_items.extend(element_items)
    total_items.extend(sub_element_items)
    total_items.extend(sub_sub_element_items)
    total_items.extend(nano_element_items)
    total_items.extend(property_items)
    total_items.extend(layers_items)

    insert_items(total_items, project_id)

    total_time = time.time() - start_time
    data = {"model_id": model_id, "output_format": "xml_to_dynamo"}
    Http().request(method="POST", url="https://" + output_project_domain_name + "/api/update_model_process", headers={}, data=data, json_res=True)
    print("Finished")
    # email_message =  " PROJECT ID " + model_id + " TOTAL TIME " + str(total_time), "PROJECT ID " + model_id
    # Ses().send_email_simple("eugenio@devesch.com.br", email_message, "us-east-1")
    Sqs().delete_message(lambda_constants["sqs_queue_url_process_xml_to_dynamo"], event["Records"][0]["receiptHandle"])
    ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])
    return


def insert_items(items, project_id):
    import concurrent.futures

    files_per_page = 100
    total_pagination = str((len(items) + files_per_page - 1) // files_per_page)

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for index, chunk in enumerate(chunks(items, files_per_page)):
            part_number = str(index + 1)
            executor.submit(write_and_process_entry, chunk, part_number, total_pagination, lambda_constants, project_id)


def check_if_element_is_only_window_or_door(element):
    if "IfcDoor" in element.tag or "IfcWindow" in element.tag:
        return True
    if not "IfcOpening" in element.tag:
        return False
    property_list = list(element)
    property_has_tags = False
    for property in property_list:
        if property.tag:
            if not "{http://www.w3.org/1999/xlink}href" in property.attrib:
                property_has_tags = True
                if not "IfcDoor" in property.tag or not "IfcWindow" in property.tag:
                    return False
    return property_has_tags


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def write_and_process_entry(chunk, part_number, total_pagination, lambda_constants, project_id):
    json = {"files": chunk}
    file_path = lambda_constants["tmp_path"] + "jsons_parts_" + part_number + "-" + total_pagination + ".json"
    ReadWrite().write_json_file(file_path, json)
    entry = {"s3": {"bucket": lambda_constants["upload_bucket"], "key": project_id + "_jsons_parts_" + part_number + "-" + total_pagination + ".json", "file_path": file_path}, "sqs": {"queue": lambda_constants["sqs_queue_url_json5000"], "message": {"bucket": lambda_constants["upload_bucket"], "key": project_id + "_jsons_parts_" + part_number + "-" + total_pagination + ".json"}}}
    S3().upload_file(entry["s3"]["bucket"], entry["s3"]["key"], entry["s3"]["file_path"])
    Sqs().send_message(entry["sqs"]["queue"], entry["sqs"]["message"])


def get_data_from_attrib(attrib):
    attrib_data = {}
    for key, value in attrib.attrib.items():
        if key not in ["id", "Name"]:
            attrib_data[key] = value
    return attrib_data


def get_project_ifc_project(ifc_sites):
    ifc_project = ifc_sites.find("IfcProject")
    return {"IfcProject_id": ifc_project.get("id"), "IfcProject_name": ifc_project.get("Name", "Not Informed")}, ifc_project


def get_project_layers(root):
    project_layers = []
    specific_elements = root.find("layers")
    for elem in specific_elements.iter():
        if elem.get("id"):
            project_layers.append({"layer_id": elem.get("id"), "layer_name": elem.get("Name", "Not Informed")})
    return project_layers


def find_xml_file(root_directory):
    import os

    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith(".xml"):
                return os.path.join(root, file).replace("\\", "/")


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_process_xml_to_dynamo.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
    print("END")

# bpmn_utils.py

import xml.etree.ElementTree as ElTr
import os

xmlpath = "static/upload/bpmn.xml"

def parse_xml(xmlpath):
    if not os.path.exists(xmlpath):
        raise FileNotFoundError("File not found")
    tree = ElTr.parse(xmlpath)
    return tree.getroot()

def extract_elements(root):
    lanelist = []
    processlist = []
    events = []
    tasks = []
    gateways = []
    flows = []

    for child in root:
        if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}process":
            processlist.append(child)

    for process in processlist:
        for child in process:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}laneSet":
                laneSet = child
                for lane in laneSet:
                    lanelist.append(lane)

    for process in processlist:
        for child in process:
            if child.tag in [
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}startEvent",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}endEvent",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}intermediateCatchEvent",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}intermediateThrowEvent",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}boundaryEvent"
            ]:
                events.append(child)
            elif child.tag in [
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}task",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}userTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}serviceTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}scriptTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}businessRuleTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}sendTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}receiveTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}manualTask",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}callActivity",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}subProcess",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}transaction"
            ]:
                tasks.append(child)
            elif child.tag in [
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}exclusiveGateway",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}inclusiveGateway",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}parallelGateway",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}eventBasedGateway",
                "{http://www.omg.org/spec/BPMN/20100524/MODEL}complexGateway"
            ]:
                gateways.append(child)
            elif child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow":
                flows.append(child)

    return lanelist, processlist, events, tasks, gateways, flows

def calculate_data(lanelist, processlist, tasks, events, gateways):
    lanes_data = {lane.attrib['name']: 0 for lane in lanelist}
    task_data, event_data = {}, {}
    processes_data = {process.attrib['name']: 0 for process in processlist}
    total_time, cycle_time = 0, 0.0

    for task in tasks:
        for child in task:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}extensionElements":
                for child2 in child:
                    if child2.tag == "{http://camunda.org/schema/zeebe/1.0}properties":
                        current_time, current_probability = 0.0, 1.0
                        for child3 in child2:
                            if child3.tag == "{http://camunda.org/schema/zeebe/1.0}property":
                                if child3.attrib['name'] == "Probability":
                                    current_probability = float(child3.attrib['value'])
                                elif child3.attrib['name'] == "Time":
                                    task_data[task.attrib['name']] = child3.attrib['value']
                                    current_time = int(child3.attrib['value'])
                                    total_time += current_time
                                    for lane in lanelist:
                                        for child4 in lane:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}flowNodeRef" and child4.text == task.attrib['id']:
                                                lanes_data[lane.attrib['name']] += current_time
                                    for process in processlist:
                                        for child4 in process:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}task" and child4.attrib['id'] == task.attrib['id']:
                                                processes_data[process.attrib['name']] += current_time
                        cycle_time += current_time * current_probability

    for event in events:
        event_data[event.attrib['name']] = 0
        for child in event:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}extensionElements":
                for child2 in child:
                    if child2.tag == "{http://camunda.org/schema/zeebe/1.0}properties":
                        current_time, current_probability = 0.0, 1.0
                        for child3 in child2:
                            if child3.tag == "{http://camunda.org/schema/zeebe/1.0}property":
                                if child3.attrib['name'] == "Probability":
                                    current_probability = float(child3.attrib['value'])
                                elif child3.attrib['name'] == "Time":
                                    event_data[event.attrib['name']] = child3.attrib['value']
                                    current_time = int(child3.attrib['value'])
                                    total_time += current_time
                                    for lane in lanelist:
                                        for child4 in lane:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}flowNodeRef" and child4.text == event.attrib['id']:
                                                lanes_data[lane.attrib['name']] += current_time
                                    for process in processlist:
                                        for child4 in process:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}event" and child4.attrib['id'] == event.attrib['id']:
                                                processes_data[process.attrib['name']] += current_time
                        cycle_time += current_time * current_probability

    gateways_name = [gateway.attrib['name'] for gateway in gateways]

    sum_events = sum(int(value) for value in event_data.values())
    sum_tasks = sum(int(value) for value in task_data.values())
    sum_lanes = sum(int(value) for value in lanes_data.values())
    sum_processes = sum(int(value) for value in processes_data.values())

    return lanes_data, task_data, event_data, processes_data, total_time, cycle_time, gateways_name, sum_events, sum_tasks, sum_lanes, sum_processes

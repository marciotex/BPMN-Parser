from .bpmn_utils import extract_elements, calculate_data

def process_bpmn_data(myroot):
    lanelist, processlist, events, tasks, gateways, flows = extract_elements(myroot)
    lanes_data, task_data, event_data, processes_data, total_time, cycle_time, gateways_name, sum_events, sum_tasks, sum_lanes, sum_processes = calculate_data(lanelist, processlist, tasks, events, gateways)
    return lanes_data, task_data, event_data, processes_data, total_time, cycle_time, gateways_name, sum_events, sum_tasks, sum_lanes, sum_processes, flows

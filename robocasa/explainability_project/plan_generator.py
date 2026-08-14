from data_structures import plan, task, action, item
import json
import os


def generateSimplePlan(items: list[item]):
    """Function to generate the simple plan instance.

    This plan is a simplified plan representing the human expected plan for loading the dishwasher.
    It follows the simple load order "load from left to right".
    Small items go into the upper rack, large and middle size items go into the bottom rack.

    Args:
    - objects[]:List of objects to be loaded into the dishwasher
    (assumption: list is ordered from items left to right.
    First object is most left, last one is most right)

    Returns:
        plan: The simple plan instance.
    """
    upper_rack_is_pulled_out = False
    bottom_rack_is_pulled_out = False

    simplePlan = plan(tasks=[])
    #  First, create the initial prepare dishwasher task and actions and append to the plan.
    open_dw_actions = list()
    open_dw_action = action("open the dishwasher", "open_dw")
    open_dw_actions.append(open_dw_action)
    openDishwasher = task("open the dishwasher", "open_dw", open_dw_actions)
    simplePlan.tasks.append(openDishwasher)

    # Create a load task for each of the items that are inside of the scene and append the tasks to the plan in order.
    # For the simple plan, this can be done simply iterating over the list of items, since we assume the list is ordered from left to right.
    for object in items:
        load_task = task(f"load the {object.name}", "load", [])
        # Check the size of the object and create the appropriate load task and actions for it.
        # This means pulling out the corresponding rack (if not already pulled out) and also pushing in the upper rack if necessary.
        if object.size == "small" and not upper_rack_is_pulled_out:
            pull_out_upper_rack_action = action("pull out the upper rack", "pull_out_upper_rack")
            load_task.actions.append(pull_out_upper_rack_action)
            upper_rack_is_pulled_out = True

        elif object.size == "large" or object.size == "medium":
            # Items can only be put into the bottom rack if the upper rack is not in the way.
            if upper_rack_is_pulled_out:
                push_in_upper_rack_action = action("push in the upper rack", "push_in_upper_rack")
                load_task.actions.append(push_in_upper_rack_action)
                upper_rack_is_pulled_out = False

            if not bottom_rack_is_pulled_out:
                pull_out_bottom_rack_action = action("pull out the bottom rack", "pull_out_bottom_rack")
                load_task.actions.append(pull_out_bottom_rack_action)
                bottom_rack_is_pulled_out = True
        load_action = action(f"load the {object.name}", "load")
        load_task.actions.append(load_action)
        simplePlan.tasks.append(load_task)

    # Create the final close dishwasher task and actions and append to the plan.
    close_dw_actions = list()
    if upper_rack_is_pulled_out:
        push_in_upper_rack_action = action("push in the upper rack", "push_in_upper_rack")
        close_dw_actions.append(push_in_upper_rack_action)

    if bottom_rack_is_pulled_out:
        push_in_bottom_rack_action = action("push in the bottom rack", "push_in_bottom_rack")
        close_dw_actions.append(push_in_bottom_rack_action)

    close_dw_action = action("close the dishwasher", "close_dw")
    close_dw_actions.append(close_dw_action)

    closeDishwasher = task("close the dishwasher", "close_dw", close_dw_actions)
    simplePlan.tasks.append(closeDishwasher)
    return simplePlan


def generateActualPlan(items: list[item]):
    """Function to generate the plan to be executed by the robot.

    This plan is created in accordance with the rules as described in the rules.md file.


    Args:
    - objects[]:List of objects to be loaded into the dishwasher
    (assumption: list is ordered from items left to right.
    First object is most left, last one is most right)
    """
    upper_rack_is_pulled_out = False
    bottom_rack_is_pulled_out = False

    actualPlan = plan(tasks=[])
    #  First, create the initial prepare dishwasher task and actions and append to the plan.
    open_dw_actions = list()
    open_dw_action = action("open the dishwasher", "open_dw")
    open_dw_actions.append(open_dw_action)
    openDishwasher = task("open the dishwasher", "open_dw", open_dw_actions)
    actualPlan.tasks.append(openDishwasher)

    # Create a new list ordered items according to the rules as described in the rules.md file.
    ordered_items = []
    # Since the list is already ordered left to right, only the size must be considered.
    # First, add all small items to the ordered list.
    for object in items:
        if object.size == "small":
            ordered_items.append(object)
    # Then, add all medium items to the ordered list.
    for object in items:
        if object.size == "medium":
            ordered_items.append(object)
    # Finally, add all large items to the ordered list.
    for object in items:
        if object.size == "large":
            ordered_items.append(object)

    # Create a load task for each of the items that are inside of the scene and append the tasks to the plan in order.
    for object in ordered_items:
        load_task = task(f"load the {object.name}", "load", [])
        # Check the size of the object and create the appropriate load task and actions for it.
        # This means pulling out the corresponding rack (if not already pulled out) and also pushing in the upper rack if necessary.
        if object.size == "small" and not upper_rack_is_pulled_out:
            pull_out_upper_rack_action = action("pull out the upper rack", "pull_out_upper_rack")
            load_task.actions.append(pull_out_upper_rack_action)
            upper_rack_is_pulled_out = True

        elif object.size == "large" or object.size == "medium":
            # Items can only be put into the bottom rack if the upper rack is not in the way.
            if upper_rack_is_pulled_out:
                push_in_upper_rack_action = action("push in the upper rack", "push_in_upper_rack")
                load_task.actions.append(push_in_upper_rack_action)
                upper_rack_is_pulled_out = False

            if not bottom_rack_is_pulled_out:
                pull_out_bottom_rack_action = action("pull out the bottom rack", "pull_out_bottom_rack")
                load_task.actions.append(pull_out_bottom_rack_action)
                bottom_rack_is_pulled_out = True

        load_action = action(f"load the {object.name}", "load")
        load_task.actions.append(load_action)

        actualPlan.tasks.append(load_task)

    # Create the final close dishwasher task and actions and append to the plan.
    close_dw_actions = list()
    if upper_rack_is_pulled_out:
        push_in_upper_rack_action = action("push in the upper rack", "push_in_upper_rack")
        close_dw_actions.append(push_in_upper_rack_action)
    if bottom_rack_is_pulled_out:
        push_in_bottom_rack_action = action("push in the bottom rack", "push_in_bottom_rack")
        close_dw_actions.append(push_in_bottom_rack_action)
    close_dw_action = action("close the dishwasher", "close_dw")
    close_dw_actions.append(close_dw_action)
    closeDishwasher = task("close the dishwasher", "close_dw", close_dw_actions)
    actualPlan.tasks.append(closeDishwasher)
    return actualPlan


def savePlanToJSON(plan: plan, filename: str):
    """Function to save the plan to a JSON file.

    The plan is saved to the plans directory.

    Args:
    - plan: The plan to be saved.
    - filename: The name of the file to save the plan to.
    """
    dirname = os.path.dirname(__file__)
    plans_dir = os.path.join(dirname, "plans")
    os.makedirs(plans_dir, exist_ok=True)
    output_path = os.path.join(plans_dir, filename)
    with open(output_path, "w") as f:
        json.dump(plan, f, default=lambda o: o.__dict__, indent=4)


def printPlan(plan: plan):
    """Function to print the plan to the console.

    Args:
    - plan: The plan to be printed.
    """
    for task in plan.tasks:
        print(f"Task: {task.description} ({task.type})")
        for action in task.actions:
            print(f"  Action: {action.description} ({action.type})")

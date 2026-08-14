from data_structures import plan, task, action, item
from plan_generator import generateSimplePlan, generateActualPlan, savePlanToJSON, printPlan
from mismatch_finder import findMismatch
import datetime


# First, an ordered list of the items that are to be loaded into the dishwasher is created.
# At this point, we assume that information is given.

item1 = item("plate", "medium", "left", False)
item2 = item("cup", "small", "middle", True)
item3 = item("bowl", "large", "right", False)

items = [item1, item2, item3]


# Then, create two plans, one simple plan and one actual plan that is to be executed by the robot.

simplePlan = generateSimplePlan(items)
actualPlan = generateActualPlan(items)

# Then, save each plan to a JSON file.
# The file names specifying the plan type are followed by a timestamp of creation.
# The plan files are saved in the plans folder.
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
simplePlanFilename = "simple_plan.json" + timestamp
actualPlanFilename = "actual_plan.json" + timestamp
savePlanToJSON(simplePlan, simplePlanFilename)
savePlanToJSON(actualPlan, actualPlanFilename)

#printPlan(simplePlan)

# Then, compare the two plans using the mismatch finder.

#mismatches = findMismatch(actualPlan, simplePlan)

# The found mismatches are then printed to the console. 
# They are also later used for the explanation generation and the visually displayed on the web interface.

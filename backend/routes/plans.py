from flask import Blueprint, request, jsonify
import datetime
import json
import os
from plan_generator import (
    generateSimplePlan,
    generateActualPlan,
    orderItemsLeftToRight,
)
from data_structures import Item
from mismatch_finder import findMismatchDetailed

plans_bp = Blueprint('plans', __name__)

BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))
PLANS_DIR = os.path.join(BACKEND_ROOT, 'plans')


def _normalize_item(item_data):
    item_name = item_data.get('name') or item_data.get('type') or 'item'
    size = item_data.get('size', 'medium')
    position = item_data.get('position', 'left')
    fragile = bool(item_data.get('fragile', item_data.get('isFragile', False)))
    return Item(item_name, size, position, fragile)


def _serialize_target(target):
    if target is None:
        return None

    if isinstance(target, dict):
        return {
            'name': target.get('name'),
            'size': target.get('size'),
            'position': target.get('position'),
            'isFragile': target.get('isFragile', target.get('fragile', False)),
        }

    return {
        'name': getattr(target, 'name', None),
        'size': getattr(target, 'size', None),
        'position': getattr(target, 'position', None),
        'isFragile': getattr(target, 'isFragile', False),
    }


def _plan_to_dict(plan_obj):
    if plan_obj is None:
        return None

    tasks = []
    for task in getattr(plan_obj, 'tasks', []):
        task_dict = {
            'description': task.description,
            'type': task.type,
            'actions': [
                {
                    'description': action.description,
                    'type': action.type,
                }
                for action in getattr(task, 'actions', [])
            ],
        }

        serialized_target = _serialize_target(getattr(task, 'target', None))
        if serialized_target is not None:
            task_dict['target'] = serialized_target

        tasks.append(task_dict)

    return {'tasks': tasks}


def _save_plan_json(plan_dict, plan_kind, timestamp):
    os.makedirs(PLANS_DIR, exist_ok=True)
    filename = f"{plan_kind}_plan_{timestamp}.json"
    absolute_path = os.path.join(PLANS_DIR, filename)
    with open(absolute_path, 'w', encoding='utf-8') as file:
        json.dump(plan_dict, file, indent=2)

    return {
        'filename': filename,
        'path': absolute_path,
    }


@plans_bp.route('/generate-plans', methods=['POST'])
def generate_plans():
    data = request.get_json(force=True, silent=True) or {}
    items = [_normalize_item(item_data) for item_data in data.get('items', [])]
    items = orderItemsLeftToRight(items)

    if not items:
        return jsonify({"error": "No items provided."}), 400

    simple_plan = generateSimplePlan(items)
    actual_plan = generateActualPlan(items)
    simple_plan_dict = _plan_to_dict(simple_plan)
    actual_plan_dict = _plan_to_dict(actual_plan)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    simple_plan_file = _save_plan_json(simple_plan_dict, 'simple', timestamp)
    actual_plan_file = _save_plan_json(actual_plan_dict, 'actual', timestamp)

    return jsonify({
        'simplePlan': simple_plan_dict,
        'actualPlan': actual_plan_dict,
        'savedFiles': {
            'simplePlan': simple_plan_file,
            'actualPlan': actual_plan_file,
        },
    }), 200


@plans_bp.route('/find-mismatches', methods=['POST'])
def find_mismatches():
    data = request.get_json(force=True, silent=True) or {}
    actual_plan = data.get('actualPlan')
    simple_plan = data.get('simplePlan')

    if actual_plan is None or simple_plan is None:
        return jsonify({
            "error": "Both 'actualPlan' and 'simplePlan' must be provided.",
        }), 400

    mismatches, actual_paths, simple_paths = findMismatchDetailed(actual_plan, simple_plan)
    return jsonify({
        "mismatches": [
            {"message": entry.message, "explanation": entry.explanation}
            for entry in mismatches
        ],
        "actualMismatchPaths": actual_paths,
        "simpleMismatchPaths": simple_paths,
    }), 200


@plans_bp.route('/generate_simple_plan', methods=['POST'])
def create_simple_plan():
    data = request.get_json(force=True, silent=True) or {}
    items = [_normalize_item(item_data) for item_data in data.get('items', [])]
    items = orderItemsLeftToRight(items)
    simple_plan_dict = _plan_to_dict(generateSimplePlan(items))
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    plan_file = _save_plan_json(simple_plan_dict, 'simple', timestamp)

    return jsonify({
        'plan': simple_plan_dict,
        'savedFile': plan_file,
    }), 201


@plans_bp.route('/generate_actual_plan', methods=['POST'])
def create_actual_plan():
    data = request.get_json(force=True, silent=True) or {}
    items = [_normalize_item(item_data) for item_data in data.get('items', [])]
    items = orderItemsLeftToRight(items)
    actual_plan_dict = _plan_to_dict(generateActualPlan(items))
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    plan_file = _save_plan_json(actual_plan_dict, 'actual', timestamp)

    return jsonify({
        'plan': actual_plan_dict,
        'savedFile': plan_file,
    }), 201


@plans_bp.route('/plans', methods=['GET'])
def get_plans():
    os.makedirs(PLANS_DIR, exist_ok=True)
    plan_files = sorted(
        [name for name in os.listdir(PLANS_DIR) if name.endswith('.json')],
        reverse=True,
    )

    return jsonify({
        'plansDirectory': PLANS_DIR,
        'files': plan_files,
    }), 200

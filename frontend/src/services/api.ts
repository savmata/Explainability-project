import type { Plan } from '../types';

const API_BASE_URL = '/api';

type PlanItemInput = {
  name?: string;
  type?: string;
  size: string;
  position: string;
  fragile: boolean;
};

export const generatePlans = async (items: PlanItemInput[]) => {
  const normalizedItems = items.map((item) => ({
    name: item.name ?? item.type ?? 'item',
    size: item.size,
    position: item.position,
    fragile: item.fragile,
  }));

  const response = await fetch(`${API_BASE_URL}/generate-plans`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ items: normalizedItems }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Plan generation failed: ${errorText}`);
  }

  return response.json();
};

export const findMismatches = async (actualPlan: Plan, simplePlan: Plan) => {
  const response = await fetch(`${API_BASE_URL}/find-mismatches`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ actualPlan, simplePlan }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Mismatch comparison failed: ${errorText}`);
  }

  return response.json() as Promise<{
    mismatches: { message: string; explanation: string }[];
    actualMismatchPaths: string[];
    simpleMismatchPaths: string[];
  }>;
};
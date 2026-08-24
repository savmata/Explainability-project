<template>
  <div class="plan-display">
    <h2>Generated Plans</h2>

    <div class="plan-columns" v-if="simplePlan || actualPlan">
      <div v-if="actualPlan" class="plan-block">
        <h3>Actual Plan</h3>
        <ol class="task-list">
          <li v-for="(task, taskIndex) in actualPlan.tasks" :key="`actual-${taskIndex}`">
            <div class="task-head">
              <span class="task-description">{{ task.description }}</span>
            </div>
            <ul class="action-list">
              <li v-for="(action, actionIndex) in task.actions" :key="`actual-${taskIndex}-${actionIndex}`">
                {{ action.description }}
              </li>
            </ul>
          </li>
        </ol>
      </div>

      <div v-if="simplePlan" class="plan-block">
        <h3>Simple Plan</h3>
        <ol class="task-list">
          <li v-for="(task, taskIndex) in simplePlan.tasks" :key="`simple-${taskIndex}`">
            <div class="task-head">
              <span class="task-description">{{ task.description }}</span>
            </div>
            <ul class="action-list">
              <li v-for="(action, actionIndex) in task.actions" :key="`simple-${taskIndex}-${actionIndex}`">
                {{ action.description }}
              </li>
            </ul>
          </li>
        </ol>
      </div>
    </div>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import type { Plan } from '../types';

export default defineComponent({
  name: 'PlanDisplay',
  props: {
    simplePlan: {
      type: Object as PropType<Plan | null>,
      default: null,
    },
    actualPlan: {
      type: Object as PropType<Plan | null>,
      default: null,
    },
  },
  data() {
    return {
      errorMessage: '',
    };
  },
});
</script>

<style scoped>
.plan-display {
  margin-top: 24px;
}

.plan-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 16px;
}

.plan-block {
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
}

.task-list {
  margin: 0;
  padding-left: 20px;
}

.task-list > li {
  margin-bottom: 12px;
}

.task-head {
  display: flex;
  margin-bottom: 6px;
}

.task-description {
  font-weight: 600;
}

.action-list {
  margin: 0;
  padding-left: 18px;
}

.error {
  color: red;
}
</style>
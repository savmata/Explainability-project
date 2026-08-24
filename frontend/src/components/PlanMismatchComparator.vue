<template>
  <section class="mismatch-comparator">
    <h2>Find Mismatches</h2>

    <div class="upload-grid">
      <div>
        <label for="actual-plan-file">Actual Plan JSON</label>
        <input id="actual-plan-file" type="file" accept="application/json,.json" @change="onFileChange($event, 'actual')" />
      </div>
      <div>
        <label for="simple-plan-file">Simple Plan JSON</label>
        <input id="simple-plan-file" type="file" accept="application/json,.json" @change="onFileChange($event, 'simple')" />
      </div>
    </div>

    <button :disabled="!canCompare || comparing" @click="comparePlans">
      {{ comparing ? 'Comparing...' : 'Compare Plans' }}
    </button>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <div v-if="mismatchMessages.length" class="mismatch-list">
      <h3>Detected Mismatches</h3>
      <ul>
        <li v-for="(entry, index) in mismatchMessages" :key="index">
          <span class="mismatch-message">{{ entry.message }}</span>
          <span class="mismatch-explanation">{{ entry.explanation }}</span>
        </li>
      </ul>
    </div>

    <div v-if="actualPlan && simplePlan" class="plan-columns">
      <div class="plan-column">
        <h3>Actual Plan</h3>
        <div class="plan-card">
          <ul class="task-list">
            <li v-for="(task, taskIndex) in actualPlan.tasks" :key="`actual-task-${taskIndex}`">
              <div>
                <span :class="actualMismatchClass(`tasks.${taskIndex}.description`, `tasks.${taskIndex}`)">{{ task.description }}</span>
              </div>
              <div class="actions-block">
                <ul>
                  <li v-for="(action, actionIndex) in task.actions" :key="`actual-task-${taskIndex}-action-${actionIndex}`">
                    <span :class="actualMismatchClass(`tasks.${taskIndex}.actions.${actionIndex}.description`)">{{ action.description }}</span>
                  </li>
                </ul>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div class="plan-column">
        <h3>Simple Plan</h3>
        <div class="plan-card">
          <ul class="task-list">
            <li v-for="(task, taskIndex) in simplePlan.tasks" :key="`simple-task-${taskIndex}`">
              <div>
                <span :class="simpleMismatchClass(`tasks.${taskIndex}.description`, `tasks.${taskIndex}`)">{{ task.description }}</span>
              </div>
              <div class="actions-block">
                <ul>
                  <li v-for="(action, actionIndex) in task.actions" :key="`simple-task-${taskIndex}-action-${actionIndex}`">
                    <span :class="simpleMismatchClass(`tasks.${taskIndex}.actions.${actionIndex}.description`)">{{ action.description }}</span>
                  </li>
                </ul>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { Plan } from '../types';
import { findMismatches } from '../services/api';

type PlanKind = 'actual' | 'simple';

export default defineComponent({
  name: 'PlanMismatchComparator',
  data() {
    return {
      actualPlan: null as Plan | null,
      simplePlan: null as Plan | null,
      mismatchMessages: [] as { message: string; explanation: string }[],
      actualMismatchPaths: [] as string[],
      simpleMismatchPaths: [] as string[],
      comparing: false,
      errorMessage: '',
    };
  },
  computed: {
    canCompare(): boolean {
      return this.actualPlan !== null && this.simplePlan !== null;
    },
    actualMismatchPathSet(): Set<string> {
      return new Set(this.actualMismatchPaths);
    },
    simpleMismatchPathSet(): Set<string> {
      return new Set(this.simpleMismatchPaths);
    },
  },
  methods: {
    async onFileChange(event: Event, kind: PlanKind) {
      const input = event.target as HTMLInputElement;
      const file = input.files?.[0];

      if (!file) {
        return;
      }

      try {
        const text = await file.text();
        const parsed = JSON.parse(text);

        if (!parsed || !Array.isArray(parsed.tasks)) {
          throw new Error('The uploaded file is not a valid plan JSON (missing tasks array).');
        }

        if (kind === 'actual') {
          this.actualPlan = parsed;
        } else {
          this.simplePlan = parsed;
        }

        this.errorMessage = '';
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'Could not parse JSON file.';
      }
    },
    async comparePlans() {
      if (!this.actualPlan || !this.simplePlan) {
        return;
      }

      this.comparing = true;
      this.errorMessage = '';

      try {
        const response = await findMismatches(this.actualPlan, this.simplePlan);
        this.mismatchMessages = response.mismatches;
        this.actualMismatchPaths = response.actualMismatchPaths;
        this.simpleMismatchPaths = response.simpleMismatchPaths;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : 'Comparison failed.';
      } finally {
        this.comparing = false;
      }
    },
    actualMismatchClass(path: string, taskPath?: string) {
      const hit = this.actualMismatchPathSet.has(path) || (taskPath !== undefined && this.actualMismatchPathSet.has(taskPath));
      return hit ? 'is-mismatch' : '';
    },
    simpleMismatchClass(path: string, taskPath?: string) {
      const hit = this.simpleMismatchPathSet.has(path) || (taskPath !== undefined && this.simpleMismatchPathSet.has(taskPath));
      return hit ? 'is-mismatch' : '';
    },
  },
});
</script>

<style scoped>
.mismatch-comparator {
  margin-top: 24px;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.upload-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  margin-bottom: 12px;
}

.upload-grid label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}

button {
  padding: 10px 18px;
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.error {
  color: #b00020;
}

.mismatch-list {
  margin-top: 16px;
}

.plan-columns {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.plan-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  background: #fafafa;
}

.task-list {
  padding-left: 18px;
}

.task-list > li {
  margin-bottom: 10px;
}

.actions-block ul {
  margin-top: 8px;
  padding-left: 16px;
}

.mismatch-list li {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.mismatch-message {
  font-weight: 600;
  color: #b00020;
}

.mismatch-explanation {
  font-size: 0.9em;
  color: #444;
  padding-left: 8px;
  border-left: 3px solid #ddd;
  line-height: 1.5;
}


.is-mismatch {
  color: #d32f2f;
  font-weight: 700;
}
</style>
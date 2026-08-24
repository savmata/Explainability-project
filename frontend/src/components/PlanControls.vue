<template>
  <div class="plan-controls">
    <h2>Plan Controls</h2>
    <button :disabled="items.length === 0" @click="$emit('generate-plans')">
      Generate Plans
    </button>
    <div v-if="items.length" class="items-summary">
      <h3>Items</h3>
      <ul>
        <li v-for="(item, index) in items" :key="index">
          {{ item.name }} — {{ item.size }} — {{ item.position }} — {{ item.fragile ? 'fragile' : 'normal' }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import type { Item } from '../types';

export default defineComponent({
  name: 'PlanControls',
  props: {
    items: {
      type: Array as PropType<Item[]>,
      required: true,
    },
  },
});
</script>

<style scoped>
.plan-controls {
  margin: 20px 0;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.items-summary {
  margin-top: 16px;
}
button {
  padding: 10px 18px;
  cursor: pointer;
}
button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
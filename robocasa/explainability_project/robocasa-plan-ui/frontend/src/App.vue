<template>
  <div id="app">
    <h1>Plan Generator</h1>
    <ItemForm @add-item="addItem" />
    <PlanControls :items="items" @generate-plans="generatePlans" />
    <PlanDisplay :simple-plan="simplePlan" :actual-plan="actualPlan" />
    <PlanMismatchComparator />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import ItemForm from './components/ItemForm.vue';
import PlanControls from './components/PlanControls.vue';
import PlanDisplay from './components/PlanDisplay.vue';
import PlanMismatchComparator from './components/PlanMismatchComparator.vue';
import type { Item, Plan } from './types';
import { generatePlans as requestPlans } from './services/api';

export default defineComponent({
  name: 'App',
  components: {
    ItemForm,
    PlanControls,
    PlanDisplay,
    PlanMismatchComparator,
  },
  setup() {
    const items = ref<Item[]>([]);
    const simplePlan = ref<Plan | null>(null);
    const actualPlan = ref<Plan | null>(null);

    const addItem = (item: Item) => {
      items.value.push(item);
    };

    const generatePlans = async () => {
      if (!items.value.length) {
        return;
      }

      const payloadItems = items.value.map((entry: any) => ({
        name: entry.name ?? entry.type ?? 'item',
        size: entry.size,
        position: entry.position,
        fragile: Boolean(entry.fragile),
      }));

      const data = await requestPlans(payloadItems);
      simplePlan.value = data.simplePlan;
      actualPlan.value = data.actualPlan;
    };

    return {
      items,
      simplePlan,
      actualPlan,
      addItem,
      generatePlans,
    };
  },
});
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

h1 {
  margin-bottom: 20px;
}
</style>
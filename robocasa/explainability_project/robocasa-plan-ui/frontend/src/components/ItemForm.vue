<template>
  <div class="item-form">
    <h2>Create Item</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="name">Name:</label>
        <input id="name" type="text" v-model="item.name" required />
      </div>
      <div>
        <label for="size">Size:</label>
        <select id="size" v-model="item.size" required>
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
        </select>
      </div>
      <div>
        <label for="position">Position:</label>
        <select id="position" v-model="item.position" required>
          <option value="left">Left</option>
          <option value="middle">Middle</option>
          <option value="right">Right</option>
        </select>
      </div>
      <div>
        <label for="fragile">Fragile:</label>
        <input id="fragile" type="checkbox" v-model="item.fragile" />
      </div>
      <button type="submit">Add Item</button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      item: {
        name: '',
        size: 'small',
        position: 'left',
        fragile: false,
      },
    };
  },
  methods: {
    submitForm() {
      this.$emit('add-item', { ...this.item });
      this.resetForm();
    },
    resetForm() {
      this.item = {
        name: '',
        size: 'small',
        position: 'left',
        fragile: false,
      };
    },
  },
});
</script>

<style scoped>
.item-form {
  margin: 20px 0;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.item-form label {
  display: block;
  margin: 8px 0 4px;
}
.item-form input,
.item-form select {
  width: 200px;
  margin-bottom: 12px;
  padding: 8px;
}
button {
  padding: 8px 16px;
  cursor: pointer;
}
</style>
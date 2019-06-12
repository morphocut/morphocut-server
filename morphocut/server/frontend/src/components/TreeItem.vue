<template>
  <div class="tree-item">
    <p class="no-margin">
      <strong>{{ item_key }}:&nbsp;</strong>
      <span v-if="!isFolder">{{ item }}</span>
      <span
        v-else-if="item==undefined || item==null || Object.keys(item).length == 0"
      >No Metadata available</span>
    </p>
    <b-card class="no-margin" v-if="isFolder && Object.keys(item).length > 0">
      <div v-for="(key, index) in Object.keys(item)" :key="index">
        <tree-item :key="index" :item="item[key]" :item_key="key.toString()"></tree-item>
      </div>
    </b-card>
  </div>
</template>
<style>
body {
  font-family: Menlo, Consolas, monospace;
  color: #444;
}
.item {
  cursor: pointer;
}
ul {
  padding-left: 1em;
  line-height: 1.5em;
  list-style-type: dot;
}
.tree-item {
  text-align: left;
  font-size: 0.8rem;
}
.no-margin {
  margin: 0;
}

.tree-item .card {
  margin: 0;
  margin-left: 1rem;
}
</style>

<script>
// define the tree-item component
export default {
  name: "tree-item",
  props: {
    item_key: String,
    item: null
  },
  data: function() {
    return {
      isOpen: false
    };
  },
  computed: {
    isFolder: function() {
      var isFolder = this.item.constructor == Object;
      return isFolder;
    }
  },
  methods: {
    toggle: function() {
      if (this.isFolder) {
        this.isOpen = !this.isOpen;
      }
    },
    makeFolder: function() {
      if (!this.isFolder) {
        this.$emit("make-folder", this.item);
        this.isOpen = true;
      }
    }
  }
};
</script>
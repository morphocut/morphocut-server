<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Datasets</h1>
        <hr>
        <br>
        <br>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.dataset-modal>Add Dataset</button>
        <br>
        <br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Objects</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(dataset, index) in datasets" :key="index">
              <td>{{ dataset.id }}</td>
              <td>{{ dataset.name }}</td>
              <td>{{ dataset.objects }}</td>
              <td>
                <b-button
                  type="button"
                  class="btn btn-warning btn-sm"
                  :to="{ name: 'Upload', params: { dataset_id: dataset.id }}"
                >Edit
                  <!-- <router-link :to="{ name: 'Upload', params: { dataset: 123 }}">Edit</router-link> -->
                  <!-- @Christian: :to="{ name: 'Upload', params: { dataset_id: dataset.id }} -->
                </b-button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="removeDataset(dataset.id)"
                >Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addDatasetModal" id="dataset-modal" title="Add a new dataset" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <!-- <b-form-group id="form-id-group" label="ID:" label-for="form-id-input">
          <b-form-input
            id="form-id-input"
            type="number"
            v-model="addDatasetForm.id"
            required
            placeholder="Enter ID"
          ></b-form-input>
        </b-form-group>-->
        <b-form-group id="form-name-group" label="Name:" label-for="form-name-input">
          <b-form-input
            id="form-name-input"
            type="text"
            v-model="addDatasetForm.name"
            required
            placeholder="Enter name"
          ></b-form-input>
        </b-form-group>
        <!-- <b-form-group id="form-objects-group" label="Objects:" label-for="form-objects-input">
          <b-form-input
            id="form-objects-input"
            type="text"
            v-model="addDatasetForm.objects"
            required
            placeholder="Enter objects"
          ></b-form-input>
        </b-form-group>-->
        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      datasets: [],
      addDatasetForm: {
        id: 0,
        name: "",
        objects: 0
      }
    };
  },
  // props: {
  //   dataset
  // },
  methods: {
    getDatasets() {
      const path = "/api/datasets";
      axios
        .get(path)
        .then(res => {
          this.datasets = res.data.datasets;
          console.log(this.datasets);
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addDataset(payload) {
      const path = "/api/datasets";
      axios
        .post(path, payload)
        .then(() => {
          this.getDatasets();
        })
        .catch(error => {
          // eslint-disable-next-line
          console.log(error);
          this.getDatasets();
        });
    },
    removeDataset(id) {
      console.log("remove dataset: " + id);
    },
    initForm() {
      this.addDatasetForm.id = 0;
      this.addDatasetForm.name = "";
      this.addDatasetForm.objects = 0;
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addDatasetModal.hide();
      const payload = {
        id: this.addDatasetForm.id,
        name: this.addDatasetForm.name,
        objects: this.addDatasetForm.objects
      };
      this.addDataset(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addDatasetModal.hide();
      this.initForm();
    }
  },
  created() {
    this.getDatasets();
  }
};
</script>
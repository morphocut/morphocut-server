<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Projects</h1>
        <hr>
        <br>
        <br>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.dataset-modal>Add Project</button>
        <br>
        <br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Objects</th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dataset in datasets" :key="dataset.id">
              <td>{{ dataset.id }}</td>
              <td>{{ dataset.name }}</td>
              <td>{{ dataset.objects }}</td>
              <td>
                <div v-if="dataset.download_running" style="display: flex;">
                  <div class="loader"></div>
                  <p style="width: 10px;"></p>
                  <p>Processing...</p>
                </div>
                <div v-if="dataset.download_path && !dataset.download_running">
                  <p>Download Ready!</p>
                </div>
              </td>
              <td>
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="processDataset(dataset)"
                >Process</button>
                <b-button
                  type="button"
                  class="btn btn-warning btn-sm"
                  style="margin-left: 0.5rem;"
                  v-if="dataset.download_path"
                  :href="dataset.download_path"
                >Download</b-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addDatasetModal" id="dataset-modal" title="Add a new dataset" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <b-form-group id="form-name-group" label="Name:" label-for="form-name-input">
          <b-form-input
            id="form-name-input"
            type="text"
            v-model="addDatasetForm.name"
            required
            placeholder="Enter name"
          ></b-form-input>
        </b-form-group>
        <!-- <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>-->
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
      //   download_complete: true,
      //   download_path: "",
      addDatasetForm: {
        id: 0,
        name: "",
        objects: 0
      }
    };
  },
  methods: {
    getDatasets() {
      const path = "/api/datasets";
      axios
        .get(path)
        .then(res => {
          this.datasets = res.data.datasets;
          console.log("datasets:");
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
    processDataset(dataset) {
      const path = "/api/datasets/" + dataset.id + "/process";
      this.$set(dataset, "download_complete", false);
      this.$set(dataset, "download_running", true);
      axios.get(path).then(res => {
        // this.$set(dataset, "download_complete", true);
        // this.$set(dataset, "download_running", false);
        // console.log("download path: " + res.data.download_path);
        // dataset.download_path = res.data.download_path;
        console.log(res);
        const job_id = res.data.job_id;
        console.log(job_id);
        this.getStatus(job_id);
      });
    },
    getStatus(job_id) {
      const path = "/api/jobs/" + job_id;
      axios.get(path).then(res => {
        const jobStatus = res.data.job_status;
        console.log(res);

        if (jobStatus === "finished" || jobStatus === "failed") {
          console.log(res.data.job_result);
          return false;
        }
        setTimeout(
          function() {
            this.getStatus(res.data.job_id);
          }.bind(this),
          1000
        );
      });
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

<style>
.loader {
  border: 3px solid #f3f3f3; /* Light grey */
  border-top: 3px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 25px;
  height: 25px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
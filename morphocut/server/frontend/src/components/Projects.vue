<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Projects</h1>
        <hr>
        <br>
        <br>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.project-modal>Add Project</button>
        <br>
        <br>
        <table class="table table-hover">
          <thead>
            <tr>
              <!-- <th scope="col">ID</th> -->
              <th scope="col">Name</th>
              <th scope="col">Objects</th>
              <th scope="col">Creation Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(project, index) in projects" :key="index">
              <!-- <td>{{ project.id }}</td> -->
              <!-- :to="{ name: 'Upload', params: { project_id: project.project_id }}" -->
              <td>
                <b-link
                  :to="{ name: 'Project', params: { project_id: project.project_id }}"
                >{{ project.name }}</b-link>
              </td>
              <td>{{ project.object_count }}</td>
              <td>{{ project.creation_date }}</td>
              <td>
                <!-- <b-button
                  type="button"
                  class="btn btn-warning btn-sm"
                  :to="{ name: 'Upload', params: { project_id: project.project_id }}"
                >
                  Edit
                </b-button>-->
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="removeProject(project.project_id)"
                >Delete</button>
                <!-- <div v-if="project.download_running" style="display: flex;">
                  <div class="loader"></div>
                  <p style="width: 10px;"></p>
                  <p>Processing...</p>
                </div>
                <div v-if="project.download_path && !project.download_running">
                  <p>Download Ready!</p>
                </div>-->
                <!-- <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="processProject(project)"
                >Process</button>-->
                <!-- <b-button
                  type="button"
                  class="btn btn-warning btn-sm"
                  style="margin-left: 0.5rem;"
                  v-if="project.download_path"
                  :href="project.download_path"
                >Download</b-button>-->
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addProjectModal" id="project-modal" title="Add a new project" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <!-- <b-form-group id="form-id-group" label="ID:" label-for="form-id-input">
          <b-form-input
            id="form-id-input"
            type="number"
            v-model="addProjectForm.id"
            required
            placeholder="Enter ID"
          ></b-form-input>
        </b-form-group>-->
        <b-form-group id="form-name-group" label="Name:" label-for="form-name-input">
          <b-form-input
            id="form-name-input"
            type="text"
            v-model="addProjectForm.name"
            required
            placeholder="Enter name"
          ></b-form-input>
        </b-form-group>
        <!-- <b-form-group id="form-objects-group" label="Objects:" label-for="form-objects-input">
          <b-form-input
            id="form-objects-input"
            type="text"
            v-model="addProjectForm.objects"
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
      projects: [],
      addProjectForm: {
        id: 0,
        name: "",
        objects: 0
      }
    };
  },
  // props: {
  //   project
  // },
  methods: {
    getProjects() {
      const path = "/api/projects";
      axios
        .get(path)
        .then(res => {
          this.projects = res.data.projects;
          console.log(this.projects);
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addProject(payload) {
      const path = "/api/projects";
      axios
        .post(path, payload)
        .then(() => {
          this.getProjects();
        })
        .catch(error => {
          // eslint-disable-next-line
          console.log(error);
          this.getProjects();
        });
    },
    removeProject(id) {
      console.log("remove project: " + id);
    },
    processProject(project) {
      const path = "/api/projects/" + project.project_id + "/process";
      this.$set(project, "download_complete", false);
      this.$set(project, "download_running", true);
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
      this.addProjectForm.id = 0;
      this.addProjectForm.name = "";
      this.addProjectForm.objects = 0;
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addProjectModal.hide();
      const payload = {
        id: this.addProjectForm.id,
        name: this.addProjectForm.name,
        objects: this.addProjectForm.objects
      };
      this.addProject(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addProjectModal.hide();
      this.initForm();
    }
  },
  created() {
    this.getProjects();
  }
};
</script>
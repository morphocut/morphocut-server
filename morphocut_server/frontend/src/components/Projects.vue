<template>
  <div class="project">
    <vue-headful title="Projects | MorphoCut"/>
    <div style="margin-top: 1rem; margin-bottom: 1rem;">
      <h2 id="project-title" class="project-title">
        <b-badge>Projects</b-badge>
      </h2>
      <div class="project-divider"></div>
    </div>

    <p>Here you can see all of your projects. Click on the project name to access the project.</p>

    <b-button type="button" class="btn btn-success project-button" v-b-modal.project-modal>
      <font-awesome-icon icon="plus"></font-awesome-icon>&nbsp;Add Project
    </b-button>

    <div class="row">
      <div class="col-6" style="margin: auto;">
        <table class="table table-hover table-sm">
          <thead class="thead-light">
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Creator</th>
              <th scope="col">Objects</th>
              <th scope="col">Creation Date</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(project, index) in projects" :key="index">
              <td>
                <b-link
                  :to="{ name: 'Project', params: { project_id: project.project_id }}"
                >{{ project.name }}</b-link>
              </td>
              <td>{{ project.email }}</td>
              <td>{{ project.object_count }}</td>
              <td>{{ (new Date(project.creation_date)).toUTCString() }}</td>
              <td>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="removeProject(project.project_id)"
                >
                  <font-awesome-icon icon="trash"/>&nbsp;Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addProjectModal" id="project-modal" title="Add a new project" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <b-form-group id="form-name-group" label="Name:" label-for="form-name-input">
          <b-form-input
            id="form-name-input"
            type="text"
            v-model="addProjectForm.name"
            required
            placeholder="Enter name"
          ></b-form-input>
        </b-form-group>
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
    removeProject(project_id) {
      this.$dialog
        .confirm("Please confirm to continue")
        .then(
          function(dialog) {
            const path = "/api/projects/" + project_id + "/remove";
            axios.get(path).then(res => {
              this.getProjects();
            });
          }.bind(this)
        )
        .catch(function() {});
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
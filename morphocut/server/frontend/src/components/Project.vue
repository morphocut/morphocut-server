<template>
  <div class="project">
    <b-button
      type="button"
      class="btn btn-primary float-right"
      v-if="project"
      :to="{ name: 'Upload', params: { project_id: project.project_id }}"
    >Upload Data</b-button>
    <b-button
      type="button"
      class="btn btn-primary float-right"
      v-if="project"
      v-on:click="processProject(project)"
    >Process</b-button>
    <h2 id="project-title" class="project-title" v-if="project">
      <b>Project:</b>
      {{project.name}}
    </h2>

    <div class="project-divider"></div>

    <div class="row">
      <div class="col-6">
        <h4 id="project-title" class="project-title" v-if="project">
          <b>Running Tasks:</b>
        </h4>
        <table class="table table-hover">
          <thead>
            <tr>
              <!-- <th scope="col">ID</th> -->
              <th scope="col">Name</th>
              <th scope="col">Description</th>
              <th scope="col">Status</th>
              <th scope="col">Started At</th>
              <th scope="col">Completed</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(task, index) in running_tasks" :key="index">
              <td>{{ task.name }}</td>
              <td>{{ task.description }}</td>
              <td>{{ task.status }}</td>
              <td>{{ task.started_at }}</td>
              <td>{{ task.complete }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="col-6">
        <h4 id="project-title" class="project-title" v-if="project">
          <b>Finished Tasks:</b>
        </h4>
        <table class="table table-hover">
          <thead>
            <tr>
              <!-- <th scope="col">ID</th> -->
              <th scope="col">Name</th>
              <th scope="col">Description</th>
              <th scope="col">Completed</th>
              <th scope="col">Download</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(task, index) in finished_tasks" :key="index">
              <td>{{ task.name }}</td>
              <td>{{ task.description }}</td>
              <td>{{ task.complete }}</td>
              <td>
                <b-button
                  type="button"
                  class="btn btn-warning btn-sm"
                  style="margin-left: 0.5rem;"
                  v-if="task.download_path"
                  :href="task.download_path"
                >Download</b-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- <div class="row" v-for="(file, index) in project_files" :key="index">
      <div class="col-2">
        <img :src="file.filepath">
      </div>
    </div>-->
  </div>
</template>
<style>
.project .project-title {
  margin-bottom: 0.3rem;
  text-align: left;
}

.project .project-divider {
  height: 1px;
  background: darkgrey;
}

.project {
  margin-left: 2rem;
  margin-right: 2rem;
}
</style>

<script>
import axios from "axios";
export default {
  data() {
    return {
      project: null,
      project_files: [],
      running_tasks: [],
      finished_tasks: []
    };
  },

  methods: {
    getProject() {
      const path = "/api/projects/" + this.$route.params.project_id;
      axios
        .get(path)
        .then(res => {
          this.project = res.data.project;
          console.log(this.project);
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    getProjectFiles() {
      const path = "/api/projects/" + this.$route.params.project_id + "/files";
      axios
        .get(path)
        .then(res => {
          this.project_files = res.data.project_files;
          console.log(this.project_files);
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    processProject(project) {
      const path = "/api/projects/" + project.project_id + "/process";
      axios.get(path).then(res => {
        this.getTaskStatus(project.project_id);
      });
    },
    getTaskStatus(project_id) {
      const path = "/api/jobs/" + project_id;
      axios.get(path).then(res => {
        this.finished_tasks = res.data.finished_tasks;
        this.running_tasks = res.data.running_tasks;
        console.log(res);

        var unfinished_task = false;

        this.running_tasks.forEach(element => {
          if (element.complete === false && element.status != "failed") {
            unfinished_task = true;
          }
        });

        if (!unfinished_task) {
          //   console.log(res.data.job_result);
          return false;
        }
        console.log("start repeating");

        setTimeout(
          function() {
            this.getTaskStatus(project_id);
          }.bind(this),
          2000
        );
      });
    }
  },
  created() {
    this.getProject();
    // this.getProjectFiles();
    this.getTaskStatus(this.$route.params.project_id);
  }
};
</script>
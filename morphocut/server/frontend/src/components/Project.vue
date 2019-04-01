<template>
  <div class="project">
    <div style="margin-top: 1rem; margin-bottom: 1rem;">
      <h2 id="project-title" class="project-title" v-if="project">
        <b-badge>{{project.name}}</b-badge>
      </h2>
      <div class="project-divider"></div>
    </div>

    <div class="row">
      <div class="col-12">
        <b-tabs content-class="mt-3" small v-model="tabIndex">
          <b-tab active title="Files">
            <div class="row">
              <div
                class="col-12"
                v-if="!project_files.length"
              >This project does not contain any files yet.</div>
              <div class="col-2" v-for="(file, index) in project_files" :key="index">
                <b-card :title="file.filename" :img-src="file.filepath">
                  <!-- <b-card-img-lazy :src="file.filepath"></b-card-img-lazy>
                  <b-card-img-lazy :src="file.filepath" alt="Image" bottom></b-card-img-lazy>-->
                </b-card>
              </div>
            </div>
          </b-tab>

          <b-tab title="Upload">
            <Upload></Upload>
          </b-tab>

          <b-tab title="Process">
            <b-button
              type="button"
              variant="primary"
              class="btn btn-primary"
              v-if="project"
              v-on:click="processProject(project)"
              :to="{ name: 'Tasks' }"
            >Process</b-button>
          </b-tab>

          <b-tab title="Tasks">
            <div v-if="project">
              <Tasks :getAction="getProjectTasksPath()"></Tasks>
            </div>
          </b-tab>
        </b-tabs>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Upload from "@/components/Upload.vue";
import Tasks from "@/components/Tasks.vue";
export default {
  components: {
    Upload,
    Tasks
  },
  data() {
    return {
      project: null,
      project_files: [],
      running_tasks: [],
      finished_tasks: [],
      tabIndex: 0
    };
  },
  watch: {
    // watch the tabIndex, so that when the user clicks on tab 'files' which has tabIndex 0, the project files get reloaded
    tabIndex(value) {
      if (value === 0) {
        this.getProjectFiles();
      }
    }
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
    getProjectTasksPath() {
      return "/api/projects/" + this.$route.params.project_id + "/jobs";
    },
    getProjectFiles() {
      const path = "/api/projects/" + this.$route.params.project_id + "/files";
      axios
        .get(path)
        .then(res => {
          this.project_files = res.data.project_files;
          // console.log(this.project_files);
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
    }
  },
  created() {
    this.getProject();
    this.getProjectFiles();
  }
};
</script>
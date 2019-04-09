<template>
  <div class="project" id="app">
    <div style="margin-top: 1rem; margin-bottom: 1rem;">
      <h2 id="project-title" class="project-title" v-if="project">
        <b-badge>{{project.name}}</b-badge>
      </h2>
      <div class="project-divider"></div>
    </div>

    <div class="row">
      <div class="col-12">
        <b-tabs content-class="mt-3" small v-model="tabIndex">
          <b-tab active title="Upload">
            <Upload></Upload>
          </b-tab>

          <b-tab title="File View">
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

          <b-tab title="Process">
            <div class="row">
              <div class="col-4" style="margin-left: auto; margin-right: auto;">
                <!-- <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator> -->
              </div>
            </div>

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
import VueFormGenerator from "vue-form-generator";
// import Multiselect from "vue-multiselect";

import "vue-form-generator/dist/vfg.css"; // optional full css additions

export default {
  components: {
    Upload,
    Tasks,
    // Multiselect,
    "vue-form-generator": VueFormGenerator.component
  },
  data() {
    var fieldObject = [
      {
        type: "input",
        inputType: "text",
        label: "ID",
        model: "id",
        readonly: true,
        featured: false,
        disabled: true
      },
      {
        type: "vueMultiSelect",
        model: "name",
        label: "Name",
        placeholder: "Select your favorite names",
        required: true,
        selectOptions: {
          multiple: true,
          key: "name",
          label: "name",
          searchable: true,
          clearOnSelect: false,
          closeOnSelect: false,
          limit: 2 // limits the visible results to 2
        },
        values: [
          {
            name: "Peter",
            language: "JavaScript"
          },
          {
            name: "Cassandra",
            language: "Ruby"
          },
          {
            name: "Ruby",
            language: "Ruby"
          }
        ]
      },
      {
        type: "input",
        inputType: "password",
        label: "Password",
        model: "password",
        min: 6,
        required: true,
        hint: "Minimum 6 characters",
        validator: VueFormGenerator.validators.string
      },
      {
        type: "input",
        inputType: "number",
        label: "Age",
        model: "age",
        min: 18,
        validator: VueFormGenerator.validators.number
      },
      {
        type: "input",
        inputType: "email",
        label: "E-mail",
        model: "email",
        placeholder: "User's e-mail address",
        validator: VueFormGenerator.validators.email
      },
      {
        type: "checklist",
        label: "Skills",
        model: "skills",
        multi: true,
        required: true,
        multiSelect: true,
        values: [
          "HTML5",
          "Javascript",
          "CSS3",
          "CoffeeScript",
          "AngularJS",
          "ReactJS",
          "VueJS"
        ]
      },
      {
        type: "switch",
        label: "Status",
        model: "status",
        multi: true,
        readonly: false,
        featured: false,
        disabled: false,
        default: true,
        textOn: "Active",
        textOff: "Inactive"
      }
    ];
    return {
      project: null,
      project_files: [],
      running_tasks: [],
      finished_tasks: [],
      tabIndex: 0,
      model: {
        id: 1,
        name: "John Doe",
        password: "J0hnD03!x4",
        age: 35,
        skills: ["Javascript", "VueJS"],
        email: "john.doe@gmail.com",
        status: true
      },
      fieldObject,
      schema: {
        fields: fieldObject
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    };
  },
  watch: {
    // watch the tabIndex, so that when the user clicks on tab 'files' which has tabIndex 0, the project files get reloaded
    tabIndex(value) {
      if (value === 0 || value === 1) {
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
    },
    getProcessFields() {}
  },
  created() {
    this.getProject();
    this.getProjectFiles();
  }
};
</script>
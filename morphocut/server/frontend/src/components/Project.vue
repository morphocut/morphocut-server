<template>
  <div class="project" id="app">
    <vue-headful v-if="project" :title="'Project - '+project.name+' | MorphoCut'"/>
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
            <b-button
              type="button"
              variant="primary"
              class="btn btn-primary"
              size="lg"
              v-if="project"
              v-on:click="processProject(project)"
              :to="{ name: 'Tasks' }"
            >Process</b-button>
            <!-- :to="{ name: 'Tasks' }" -->
            <div
              class="project-divider"
              style="margin-top: 1rem; margin-bottom: 1rem; margin-left: 10rem; margin-right: 10rem;"
            ></div>
            <h4 id="tasks-title" class="tasks-title">
              <b>Process Settings:</b>
            </h4>
            <div class="row">
              <div class="col-4" style="margin-left: auto; margin-right: auto;">
                <div
                  v-for="(node, index) in ['DataLoader', 'VignetteCorrector', 'BGR2Gray', 'ThresholdOtsu', 'ExtractRegions', 'FadeBackground', 'DrawContours', 'ObjectScale', 'Exporter']"
                  :key="index"
                >
                  <b-button
                    v-b-toggle="'collapse-'+index"
                    variant="outline-secondary"
                    style="width: 100%;"
                    size="sm"
                  >{{ node }}</b-button>
                  <b-collapse :id="'collapse-'+index" class="mt-2">
                    <b-card>
                      <vue-form-generator
                        :schema="schema[node]"
                        :model="models[node]"
                        :options="formOptions"
                      ></vue-form-generator>
                    </b-card>
                  </b-collapse>
                </div>
              </div>
            </div>
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

import "vue-form-generator/dist/vfg.css"; // optional full css additions

export default {
  components: {
    Upload,
    Tasks,
    "vue-form-generator": VueFormGenerator.component
  },
  data() {
    return {
      project: null,
      project_files: [],
      running_tasks: [],
      finished_tasks: [],
      tabIndex: 0,
      models: {
        DataLoader: {
          image_extensions: [".jpeg", ".jpg", ".png", ".gif", ".tif", ".JPG"]
        },
        VignetteCorrector: {},
        BGR2Gray: {},
        ThresholdOtsu: {},
        ExtractRegions: {
          min_area: 0,
          padding: 0
        },
        FadeBackground: {
          alpha: 0.5,
          bg_color: 1.0
        },
        DrawContours: {
          dilate_rel: 0.0,
          dilate_abs: 0.0
        },
        ObjectScale: {},
        Exporter: {
          img_facets: [
            "color",
            "gray",
            "mask",
            "bg_white",
            "color_contours",
            "color_contours_scale"
          ],
          img_ext: ".jpg"
        }
      },
      schema: {
        DataLoader: {
          fields: [
            {
              type: "checklist",
              label: "Image Extensions",
              model: "image_extensions",
              multi: true,
              multiSelect: true,
              values: [".jpeg", ".jpg", ".png", ".gif", ".tif", ".JPG"]
            }
          ]
        },
        VignetteCorrector: { fields: [] },
        BGR2Gray: { fields: [] },
        ThresholdOtsu: { fields: [] },
        ExtractRegions: {
          fields: [
            {
              type: "input",
              inputType: "number",
              label: "Minimum Object Area",
              model: "min_area",
              validator: VueFormGenerator.validators.number
            },
            {
              type: "input",
              inputType: "number",
              label: "Padding",
              model: "padding",
              validator: VueFormGenerator.validators.number
            }
          ]
        },
        FadeBackground: {
          fields: [
            {
              type: "input",
              inputType: "number",
              label: "Background Alpha",
              model: "alpha",
              validator: VueFormGenerator.validators.number
            },
            {
              type: "input",
              inputType: "number",
              label: "Background Color",
              model: "bg_color",
              validator: VueFormGenerator.validators.number
            }
          ]
        },
        DrawContours: {
          fields: [
            {
              type: "input",
              inputType: "number",
              label: "Dilation (Relative to the object area)",
              model: "dilate_rel",
              validator: VueFormGenerator.validators.number
            },
            {
              type: "input",
              inputType: "number",
              label: "Dilation (Absolute)",
              model: "dilate_abs",
              validator: VueFormGenerator.validators.number
            }
          ]
        },
        ObjectScale: { fields: [] },
        Exporter: {
          fields: [
            {
              type: "checklist",
              label: "Exported Images",
              model: "img_facets",
              multi: true,
              multiSelect: true,
              values: [
                { value: "color", name: "Color Image" },
                { value: "gray", name: "Gray Image" },
                { value: "mask", name: "Object Mask Image" },
                { value: "bg_white", name: "Faded Background Image" },
                { value: "color_contours", name: "Color Image with Contours" },
                {
                  value: "color_contours_scale",
                  name: "Color Image with Contours and Scale"
                }
              ]
            },
            {
              type: "radios",
              label: "Extension of the Exported Images",
              model: "img_ext",
              values: [".jpeg", ".jpg", ".png", ".gif", ".tif", ".JPG"]
            }
          ]
        }
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
      axios
        .post(path, {
          params: this.models
        })
        .then(res => {
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

<style>
fieldset {
  border: 0;
}

.panel {
  margin-bottom: 20px;
  background-color: #fff;
  border: 1px solid transparent;
  border-radius: 4px;
  -webkit-box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
  border-color: #ddd;
}

.panel-heading {
  color: #333;
  background-color: #f5f5f5;
  border-color: #ddd;

  padding: 10px 15px;
  border-bottom: 1px solid transparent;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
}

.panel-body {
  padding: 15px;
}

.field-checklist .wrapper {
  width: 100%;
}

.vue-form-generator {
  text-align: left;
}
</style>
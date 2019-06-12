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
          <b-tab active>
            <template slot="title">
              <font-awesome-icon icon="upload"></font-awesome-icon>&nbsp;Upload
            </template>
            <p>Here you can upload new files to the project.</p>
            <Upload></Upload>
          </b-tab>

          <b-tab>
            <template slot="title">
              <font-awesome-icon icon="images"></font-awesome-icon>&nbsp;File View
            </template>
            <p>Here you can see the files of this project.</p>
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

          <b-tab>
            <template slot="title">
              <font-awesome-icon icon="cogs"></font-awesome-icon>&nbsp;Processing
            </template>

            <p>Here you can process the files. The files are processed by following the pipeline shown below. To start, configure the settings and press "Process".</p>

            <h4 id="tasks-title" class="tasks-title">
              <b>Process Settings:</b>
            </h4>
            <div class="row">
              <div class="col-4" style="margin-left: auto; margin-right: auto;">
                <div v-for="(node, index) in nodes" :key="index">
                  <b-button
                    v-b-toggle="'collapse-'+index"
                    variant="outline-secondary"
                    style="width: 100%;"
                    size="sm"
                  >{{ node['name'] }}</b-button>
                  <b-collapse :id="'collapse-'+index" class="mt-2">
                    <b-card>
                      <p>{{ node['description'] }}</p>
                      <vue-form-generator
                        :ref="'vfg-'+node['name']"
                        :schema="schema[node['name']]"
                        :model="models[node['name']]"
                        :options="formOptions"
                        :data-form-name="node['name']"
                      ></vue-form-generator>
                    </b-card>
                  </b-collapse>
                </div>
              </div>
            </div>

            <div
              class="project-divider"
              style="margin-top: 1rem; margin-bottom: 1rem; margin-left: 10rem; margin-right: 10rem;"
            ></div>

            <b-button
              type="button"
              variant="primary"
              class="btn btn-primary"
              size="lg"
              v-if="project"
              v-on:click="processProject(project)"
              style="margin-bottom: 5%;"
            >Process</b-button>
          </b-tab>

          <b-tab>
            <template slot="title">
              <font-awesome-icon icon="file-download"></font-awesome-icon>&nbsp;Tasks
            </template>
            <p>Here you can see the tasks of this project. You can see the progress of the running tasks and download the results of the finished tasks.</p>
            <div v-if="project">
              <Tasks ref="tasks-component" :getAction="getProjectTasksPath()"></Tasks>
            </div>
          </b-tab>
        </b-tabs>
      </div>
    </div>
    <b-modal ref="invalid-modal" hide-footer title="Invalid Input">
      <div class="d-block text-center">
        <p>Can not start processing. Please check that all input parameters are filled in and valid. Found invalid inputs in the following settings:</p>
        <p
          class="no-margin"
          v-for="(node, index) in settingsErrors"
          :key="index"
        >{{node.node}} &rarr; {{node.setting}}</p>
      </div>
      <b-button class="mt-3" variant="secondary" block @click="hideModal">Close</b-button>
    </b-modal>
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
      allSettingsValid: false,
      validSettings: {},
      settingsErrors: [],
      nodes: [
        {
          name: "DataLoader",
          description:
            "This node loads the images with the specified extensions for further processing."
        },
        {
          name: "VignetteCorrector",
          description:
            "This node is responsible for correcting any form of vignetting effects in the image to ensure that the background is consistent throughout the image."
        },
        {
          name: "BGR2Gray",
          description:
            "This node converts the images from the RGB colorspace into grey-value images."
        },
        {
          name: "ThresholdOtsu",
          description:
            "This node performs thresholding using the Otsu method. This is the most crucial step, as it separates the objects from the image background."
        },
        {
          name: "ExtractRegions",
          description:
            "This node extracts the segmented objects from the image. Additionally, all of the image features are calculated here."
        },
        {
          name: "FadeBackground",
          description:
            "This node generates an image with a faded background in order to have a better view of the object."
        },
        {
          name: "DrawContours",
          description:
            "This node generates an image with contours around the object to have a better view of its shape."
        },
        {
          name: "ObjectScale",
          description:
            "This node generates an image with a scale bar showing the object size in milimeters."
        },
        {
          name: "Exporter",
          description:
            "This node exports the generated images into an Ecotaxa compatible zipfile."
        }
      ],
      models: {
        Started_UTC: null,
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
        ObjectScale: {
          pixels_per_mm: null,
          scale_size: 0.1
        },
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
              help: "The minimum area in pixels for an object to be segmented",
              hint: "in pixels",
              label: "Minimum Area",
              model: "min_area",
              validator: [VueFormGenerator.validators.number, "positiveNumber"]
            },
            {
              type: "input",
              inputType: "number",
              help: "The padding in pixels around the object in the image",
              hint: "in pixels",
              label: "Padding",
              model: "padding",
              validator: [VueFormGenerator.validators.number, "positiveNumber"]
            }
          ]
        },
        FadeBackground: {
          fields: [
            {
              type: "input",
              inputType: "number",
              label: "Background Transparency",
              help: "Range 0 to 1 from normal to fully colored background",
              hint: "number in the range from 0 to 1",
              model: "alpha",
              validator: [VueFormGenerator.validators.number, "range01"]
            },
            {
              type: "input",
              inputType: "number",
              label: "Background Color",
              help: "Range 0 to 1 from black to white",
              hint: "number in the range from 0 to 1",
              model: "bg_color",
              validator: [VueFormGenerator.validators.number, "range01"]
            }
          ]
        },
        DrawContours: {
          fields: [
            {
              type: "input",
              inputType: "number",
              label: "Relative Dilation",
              help:
                "The distance from the contour to the object, relative to the object area",
              hint: "in % of the object area",
              model: "dilate_rel",
              validator: [VueFormGenerator.validators.number, "positiveNumber"]
            },
            {
              type: "input",
              inputType: "number",
              label: "Absolute Dilation",
              help:
                "The distance from the contour to the object in pixels, independent from the object area",
              hint: "in pixels",
              model: "dilate_abs",
              validator: [VueFormGenerator.validators.number, "positiveNumber"]
            }
          ]
        },
        ObjectScale: {
          fields: [
            {
              type: "input",
              inputType: "number",
              label: "Pixels per Milimeter",
              help: "The pixels per millimeter scale of the image",
              hint: "in pixels/mm",
              model: "pixels_per_mm",
              required: true,
              validator: [VueFormGenerator.validators.number, "positiveNumber"]
            },
            {
              type: "input",
              inputType: "number",
              label: "Scale Size",
              help: "The width of the scale bar in mm",
              hint: "in mm",
              model: "scale_size",
              required: true,
              validator: [VueFormGenerator.validators.number, "positiveNumber"]
            }
          ]
        },
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
              hint:
                "Note: Choosing .png or .tif can lead to substantially larger filesizes.",
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
    showModal() {
      this.$refs["invalid-modal"].show();
    },
    hideModal() {
      this.$refs["invalid-modal"].hide();
    },
    checkFormValidation() {
      /* 
      hacky code to check if there are errors.
      find elements with the error class, as those are instantiated, when the vue-form-generator validation fails.
      */
      var errors = this.$el.querySelectorAll(".error");
      var errorLocations = [];
      if (!(errors == null || errors == undefined)) {
        console.log("Invalid Input: ", errors);

        // hacky code to find the error locations
        errors.forEach(element => {
          var v = element.closest(".vue-form-generator");
          var s = element.firstChild.firstChild;
          errorLocations.push({
            node: v.dataset.formName,
            setting: s.innerHTML
          });
        });
      }
      this.settingsErrors = errorLocations;
      return this.settingsErrors;
    },
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
      var errors = this.checkFormValidation();
      if (errors.length > 0) {
        this.showModal();
        return false;
      }
      const path = "/api/projects/" + project.project_id + "/process";
      console.log("process project");
      this.models.Started_UTC = new Date();
      axios
        .post(path, {
          params: this.models
        })
        .then(res => {
          // jump to tasks tab and fetch task status from server
          this.tabIndex = 3;
          this.$refs["tasks-component"].getTaskStatus();
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
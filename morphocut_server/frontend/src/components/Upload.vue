<template>
  <div class="example-full">
    <!-- Drop Modal that shows up, when hovering above the page with files -->
    <div v-show="$refs.upload && $refs.upload.dropActive" class="drop-active">
      <h3>
        <font-awesome-icon icon="arrow-down"></font-awesome-icon>&nbsp;Drop files to upload
      </h3>
    </div>
    <div class="upload" v-show="!isOption">
      <h4>
        <strong>Drop files onto this page and click on Start Upload!</strong>
      </h4>

      <div class="table-responsive" style="height: 60vh;">
        <table class="table table-hover table-sm">
          <thead class="thead-light">
            <tr>
              <th>Thumb</th>
              <th>Name</th>
              <th>Progress</th>
              <th>Size</th>
              <th>Speed</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(file, index) in files" :key="file.id">
              <!-- <td>{{index}}</td> -->
              <td>
                <img v-if="file.thumb" :src="file.thumb" width="40" height="auto" />
                <span v-else>No Image</span>
                <!-- <div class="filename">{{file.fileObject}}</div> -->
              </td>
              <td>
                <div class="filename">{{file.name}}</div>
              </td>
              <td>
                <div class="progress" v-if="file.active || file.progress !== '0.00'">
                  <div
                    :class="{'progress-bar': true, 'progress-bar-striped': true, 'bg-danger': file.error, 'progress-bar-animated': file.active}"
                    role="progressbar"
                    :style="{width: file.progress + '%'}"
                  >{{file.progress}}%</div>
                </div>
              </td>
              <td>{{file.size | formatFileSize}}</td>
              <!-- <td>{{file.speed}}</td> -->
              <td>{{file.speed | formatFileSize}}</td>

              <td v-if="file.error">{{showFileError(file.error)}}</td>
              <td v-else-if="file.success">success</td>
              <td v-else-if="file.active">active</td>
              <td v-else></td>
              <td>
                <div>
                  <button
                    class="btn btn-secondary btn-sm"
                    href="#"
                    :disabled="file.error && file.error !== 'compressing' && $refs.upload.features.html5"
                    @click.prevent="$refs.upload.update(file, {active: true, error: '', progress: '0.00'})"
                  >Retry upload</button>
                </div>
              </td>
            </tr>

            <tr class="tr-success" v-for="(file, index) in project_files" :key="file.id">
              <!-- <td>{{index}}</td> -->
              <td>
                <!-- <pic-zoom
                  v-if="file.filepath"
                  :url="file.filepath"
                  :scale="3"
                  width="40"
                  height="auto"
                ></pic-zoom>-->
                <img v-if="file.filepath" :src="file.filepath" width="40" height="auto" />
                <span v-else>No Image</span>
                <!-- <viewer inline="false" fullscreen="true" zoomable="true">
                  <img :src="file.filepath" :key="file.filepath">
                </viewer>-->
                <!-- <div class="filename">{{file.fileObject}}</div> -->
              </td>
              <td>
                <div class="filename">{{file.filename}}</div>
              </td>
              <td>
                <div class="progress">
                  <div
                    :class="{'progress-bar': true, 'progress-bar-striped': true, 'bg-danger': file.error, 'progress-bar-animated': file.active}"
                    role="progressbar"
                    :style="{width: '100%'}"
                  >100%</div>
                </div>
              </td>
              <td>---</td>
              <!-- <td>{{file.speed}}</td> -->
              <td>---</td>

              <td>On Server</td>
              <td>
                <div>
                  <button
                    type="button"
                    class="btn btn-danger btn-sm"
                    style="margin-left: 0.5rem;"
                    v-on:click="removeFile(file.object_id)"
                  >
                    <font-awesome-icon icon="trash"/>&nbsp;Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div>
          <p
            v-if="!project_files.length && !files.length"
          >This project does not contain any files yet.</p>
        </div>
      </div>
      <div class="example-foorer">
        <div class="btn-group">
          <file-upload
            class="btn btn-primary dropdown-toggle"
            :post-action="postAction"
            :put-action="putAction"
            :extensions="extensions"
            :accept="accept"
            :multiple="multiple"
            :directory="directory"
            :size="size || 0"
            :thread="thread < 1 ? 1 : (thread > 5 ? 5 : thread)"
            :headers="headers"
            :data="data"
            :drop="drop"
            :drop-directory="dropDirectory"
            :add-index="addIndex"
            v-model="files"
            @input-filter="inputFilter"
            @input-file="inputFile"
            ref="upload"
          >
            <i class="fa fa-plus"></i>
            Select
          </file-upload>
          <div class="dropdown-menu">
            <label class="dropdown-item" :for="name">Add files</label>
            <a class="dropdown-item" href="#" @click="onAddFolder">Add folder</a>
            <a class="dropdown-item" href="#" @click.prevent="addData.show = true">Add data</a>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-success"
          v-if="!$refs.upload || !$refs.upload.active"
          @click.prevent="$refs.upload.active = true"
        >
          <font-awesome-icon icon="upload"/>&nbsp;Start Upload
        </button>
        <button
          type="button"
          class="btn btn-danger"
          v-else
          @click.prevent="$refs.upload.active = false"
        >
          <font-awesome-icon icon="stop"/>&nbsp;
          Stop Upload
        </button>

        <!-- <div v-if="$refs.upload && $refs.upload.active"> -->
        <div v-if="$refs.upload && $refs.upload.active" style="margin-top: 2rem;">
          <div class="progress">
            <div
              :class="{'progress-bar': true, 'progress-bar-striped': true, 'bg-info':true}"
              role="progressbar"
              aria-valuemin="0"
              aria-valuemax="100"
              :style="{width: percentUploadedFiles + '%'}"
            >
              <span
                class="justify-content-center d-flex position-absolute w-100"
                style="color: black;"
              >
                <b>{{percentUploadedFiles.toFixed(2)}}% - Uploaded {{numberUploadedFiles}}/{{files.length}} files</b>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div :class="{'modal-backdrop': true, 'fade': true, show: addData.show}"></div>
    <div
      :class="{modal: true, fade: true, show: addData.show}"
      id="modal-add-data"
      tabindex="-1"
      role="dialog"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add data</h5>
            <button type="button" class="close" @click.prevent="addData.show = false">
              <span>&times;</span>
            </button>
          </div>
          <form @submit.prevent="onAddData">
            <div class="modal-body">
              <div class="form-group">
                <label for="name">Name:</label>
                <input
                  type="text"
                  class="form-control"
                  required
                  id="name"
                  placeholder="Please enter a file name"
                  v-model="addData.name"
                />
                <small class="form-text text-muted">
                  Such as
                  <code>filename.txt</code>
                </small>
              </div>
              <div class="form-group">
                <label for="type">Type:</label>
                <input
                  type="text"
                  class="form-control"
                  required
                  id="type"
                  placeholder="Please enter the MIME type"
                  v-model="addData.type"
                />
                <small class="form-text text-muted">
                  Such as
                  <code>text/plain</code>
                </small>
              </div>
              <div class="form-group">
                <label for="content">Content:</label>
                <textarea
                  class="form-control"
                  required
                  id="content"
                  rows="3"
                  placeholder="Please enter the file contents"
                  v-model="addData.content"
                ></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click.prevent="addData.show = false"
              >Close</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div :class="{'modal-backdrop': true, 'fade': true, show: editFile.show}"></div>
    <div
      :class="{modal: true, fade: true, show: editFile.show}"
      id="modal-edit-file"
      tabindex="-1"
      role="dialog"
    >
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit file</h5>
            <button type="button" class="close" @click.prevent="editFile.show = false">
              <span>&times;</span>
            </button>
          </div>
          <form @submit.prevent="onEditorFile">
            <div class="modal-body">
              <div class="form-group">
                <label for="name">Name:</label>
                <input
                  type="text"
                  class="form-control"
                  required
                  id="name"
                  placeholder="Please enter a file name"
                  v-model="editFile.name"
                />
              </div>
              <div
                class="form-group"
                v-if="editFile.show && editFile.blob && editFile.type && editFile.type.substr(0, 6) === 'image/'"
              >
                <label>Image:</label>
                <div class="edit-image">
                  <img :src="editFile.blob" ref="editImage" />
                </div>

                <div class="edit-image-tool">
                  <div class="btn-group" role="group">
                    <button
                      type="button"
                      class="btn btn-primary"
                      @click="editFile.cropper.rotate(-90)"
                      title="cropper.rotate(-90)"
                    >
                      <i class="fa fa-undo" aria-hidden="true"></i>
                    </button>
                    <button
                      type="button"
                      class="btn btn-primary"
                      @click="editFile.cropper.rotate(90)"
                      title="cropper.rotate(90)"
                    >
                      <i class="fa fa-repeat" aria-hidden="true"></i>
                    </button>
                  </div>
                  <div class="btn-group" role="group">
                    <button
                      type="button"
                      class="btn btn-primary"
                      @click="editFile.cropper.crop()"
                      title="cropper.crop()"
                    >
                      <i class="fa fa-check" aria-hidden="true"></i>
                    </button>
                    <button
                      type="button"
                      class="btn btn-primary"
                      @click="editFile.cropper.clear()"
                      title="cropper.clear()"
                    >
                      <i class="fa fa-remove" aria-hidden="true"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click.prevent="editFile.show = false"
              >Close</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
.example-full .btn-group .dropdown-menu {
  display: block;
  visibility: hidden;
  transition: all 0.2s;
}
.example-full .btn-group:hover > .dropdown-menu {
  visibility: visible;
}

.example-full label.dropdown-item {
  margin-bottom: 0;
}

.example-full .btn-group .dropdown-toggle {
  margin-right: 0.6rem;
}

.example-full .filename {
  margin-bottom: 0.3rem;
}

.example-full .btn-is-option {
  margin-top: 0.25rem;
}
.example-full .example-foorer {
  padding: 0.5rem 0;
  border-top: 1px solid #e9ecef;
}

.example-full .edit-image img {
  max-width: 100%;
}

.example-full .edit-image-tool {
  margin-top: 0.6rem;
}

.example-full .edit-image-tool .btn-group {
  margin-right: 0.6rem;
}

.example-full .footer-status {
  padding-top: 0.4rem;
}

.example-full .drop-active {
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
  position: fixed;
  z-index: 9999;
  opacity: 0.6;
  text-align: center;
  background: #000;
}

.example-full .drop-active h3 {
  margin: -0.5em 0 0;
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  -webkit-transform: translateY(-50%);
  -ms-transform: translateY(-50%);
  transform: translateY(-50%);
  font-size: 40px;
  color: #fff;
  padding: 0;
}

.image {
  width: calc(20% - 10px);
  cursor: pointer;
  margin: 5px;
  display: inline-block;
}
</style>

<script>
import Cropper from "cropperjs";
import ImageCompressor from "@xkeshi/image-compressor";
import FileUpload from "vue-upload-component";
import "viewerjs/dist/viewer.css";
import Viewer from "v-viewer";
import Vue from "vue";
import axios from "axios";

Vue.use(Viewer, {
  debug: true,
  defaultOptions: {
    zIndex: 9999
  }
});

export default {
  components: {
    FileUpload
    // PicZoom
  },

  data() {
    return {
      project: null,
      files: [],
      project_files: [],
      accept: "image/png,image/gif,image/jpeg,image/webp",
      extensions: "gif,jpg,jpeg,png,webp",
      minSize: 10,
      size: 1024 * 1024 * 10,
      multiple: true,
      directory: false,
      drop: true,
      dropDirectory: true,
      addIndex: false,
      thread: 3,
      name: "file",
      postAction: "/api/projects/" + this.$route.params.project_id + "/upload",
      putAction: "",
      headers: {
        "X-Csrf-Token": "xxxx"
      },
      data: {
        _csrf_token: "xxxxxx"
      },

      autoCompress: 1024 * 1024,
      uploadAuto: false,
      isOption: false,

      addData: {
        show: false,
        name: "",
        type: "",
        content: ""
      },

      editFile: {
        show: false,
        name: ""
      },

      options: {
        toolbar: true,
        url: "data-source"
      }
    };
  },

  computed: {
    percentUploadedFiles: function() {
      var n = this.numberUploadedFiles;
      var percentage = 0;
      if (this.files.length > 0) {
        percentage = (n / this.files.length) * 100;
      }

      return percentage;
    },
    numberUploadedFiles: function() {
      var n = 0;
      this.files.forEach(element => {
        if (element.success) {
          n += 1;
        }
      });

      return n;
    }
  },

  watch: {
    "editFile.show"(newValue, oldValue) {
      // 关闭了 自动删除 error
      if (!newValue && oldValue) {
        console.log("EditFile Error: ", this.editFile.error);
        this.$refs.upload.update(this.editFile.id, {
          error: this.editFile.error || ""
        });
      }

      if (newValue) {
        this.$nextTick(function() {
          if (!this.$refs.editImage) {
            return;
          }
          let cropper = new Cropper(this.$refs.editImage, {
            autoCrop: false
          });
          this.editFile = {
            ...this.editFile,
            cropper
          };
        });
      }
    },

    "addData.show"(show) {
      if (show) {
        this.addData.name = "";
        this.addData.type = "";
        this.addData.content = "";
      }
    }
  },

  methods: {
    showFileError(error) {
      switch (error) {
        case "size":
          return "The file is too small";
        case "extension":
          return "The file has an invalid extension";
        case "timeout":
          return "Timeout during transmission";
        case "abort":
          return "The transmission has been aborted";
        case "network":
          return "Network error";
        case "server":
          return "Server error";
        case "denied":
          return "The file was denied by the server";
        default:
          return "Unknown Error";
      }
    },
    show() {
      const viewer = this.$el.querySelector(".images").$viewer;
      viewer.show();
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
    inputFilter(newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        // Before adding a file

        // Filter system files or hide files
        if (/(\/|^)(Thumbs\.db|desktop\.ini|\..+)$/.test(newFile.name)) {
          return prevent();
        }

        // Filter php html js file
        if (/\.(php5?|html?|jsx?)$/i.test(newFile.name)) {
          return prevent();
        }
      }

      if (newFile && (!oldFile || newFile.file !== oldFile.file)) {
        // Create a blob field
        newFile.blob = "";
        let URL = window.URL || window.webkitURL;
        if (URL && URL.createObjectURL) {
          newFile.blob = URL.createObjectURL(newFile.file);
        }

        // Thumbnails
        newFile.thumb = "";
        if (newFile.blob && newFile.type.substr(0, 6) === "image/") {
          newFile.thumb = newFile.blob;
        }
      }
    },

    // add, update, remove File Event
    inputFile(newFile, oldFile) {
      console.log("inputfile");

      if (newFile && !oldFile) {
        // add
        console.log("add", newFile);
        // console.log("inputfile add");
      }

      if (newFile && oldFile) {
        // update

        if (newFile.active && !oldFile.active) {
          // beforeSend

          // min size
          if (
            newFile.size >= 0 &&
            this.minSize > 0 &&
            newFile.size < this.minSize
          ) {
            // this.alert("inputfile upload update");
            this.$refs.upload.update(newFile, { error: "size" });
          }
        }

        if (newFile.progress !== oldFile.progress) {
          // progress
          console.log("inputfile progress: " + newFile.progress);
        }

        if (newFile.error && !oldFile.error) {
          // error
          console.log("inputfile error: " + newFile.error);
        }

        if (newFile.success && !oldFile.success) {
          // success
          console.log("inputfile success: " + newFile.success);
        }
      }

      if (!newFile && oldFile) {
        // remove
        if (oldFile.success && oldFile.response.id) {
          // $.ajax({
          //   type: 'DELETE',
          //   url: '/upload/delete?id=' + oldFile.response.id,
          // })
        }
      }

      // Automatically activate upload
      if (
        Boolean(newFile) !== Boolean(oldFile) ||
        oldFile.error !== newFile.error
      ) {
        if (this.uploadAuto && !this.$refs.upload.active) {
          this.$refs.upload.active = true;
        }
      }
    },

    alert(message) {
      alert(message);
    },

    onEditFileShow(file) {
      this.editFile = { ...file, show: true };
      this.$refs.upload.update(file, { error: "edit" });
    },

    onEditorFile() {
      if (!this.$refs.upload.features.html5) {
        this.alert("Your browser does not support");
        this.editFile.show = false;
        return;
      }

      let data = {
        name: this.editFile.name
      };
      if (this.editFile.cropper) {
        let binStr = atob(
          this.editFile.cropper
            .getCroppedCanvas()
            .toDataURL(this.editFile.type)
            .split(",")[1]
        );
        let arr = new Uint8Array(binStr.length);
        for (let i = 0; i < binStr.length; i++) {
          arr[i] = binStr.charCodeAt(i);
        }
        data.file = new File([arr], data.name, { type: this.editFile.type });
        data.size = data.file.size;
      }
      this.$refs.upload.update(this.editFile.id, data);
      this.editFile.error = "";
      this.editFile.show = false;
    },

    // add folader
    onAddFolder() {
      if (!this.$refs.upload.features.directory) {
        this.alert("Your browser does not support");
        return;
      }

      let input = this.$refs.upload.$el.querySelector("input");
      input.directory = true;
      input.webkitdirectory = true;
      this.directory = true;

      input.onclick = null;
      input.click();
      input.onclick = e => {
        this.directory = false;
        input.directory = false;
        input.webkitdirectory = false;
      };
    },

    onAddData() {
      this.addData.show = false;
      if (!this.$refs.upload.features.html5) {
        this.alert("Your browser does not support");
        return;
      }

      let file = new window.File([this.addData.content], this.addData.name, {
        type: this.addData.type
      });

      this.$refs.upload.add(file);
    },

    removeFile(object_id) {
      this.$dialog
        .confirm("Please confirm to continue")
        .then(
          function(dialog) {
            const path = "/api/objects/" + object_id + "/remove";
            axios.get(path).then(res => {
              this.getProjectFiles();
            });
          }.bind(this)
        )
        .catch(function() {});
    }
  },
  filters: {
    formatFileSize: function(value) {
      if (!value) return "";

      var sizeName = "kb";
      value = value / 1000;
      if (value > 1000) {
        value = value / 1000;
        sizeName = "mb";
      }
      if (value > 1000) {
        value = value / 1000;
        sizeName = "gb";
      }

      value = value.toFixed(2);
      return value + " " + sizeName;
    }
  },
  created() {
    this.getProject();
    this.getProjectFiles();
  }
};
</script>